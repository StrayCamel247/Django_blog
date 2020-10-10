#!/usr/bin/python
# -*- coding: utf-8 -*-
# __author__ : stray_camel
# __description__ : http405报错判断
# __REFERENCES__ :
# __date__: 2020/09/23 12

from django.contrib.auth.decorators import login_required
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.conf.urls import url
from django.http import request
from apps.api_exception import ParameterException
import json
from apps.utils.wsme.signature import get_dataformat
# F:\Envs\env\Lib\site-packages\rest_framework\status.py
from rest_framework.status import HTTP_405_METHOD_NOT_ALLOWED
from apps.apis.urls import urlpatterns
from django.http.response import HttpResponseNotAllowed
import logging
from apps.api_exception import InsufficientPermissionsError, NeedLogin, InvalidJwtToken, ResponseNotAllowed
from apps.accounts.handler import token_refresh_sliding_handler
log = logging.getLogger('apps')

def require_http_methods(path, name=None, methods:
                         "用户指定url和request methods，并将url注册到apis连接下" = [], login_required: "用户指定是否开启request.user校验" = False, perm: "user拥有的权限" = (), token_required: "用户指定是否开启request.jwt校验" = False, **check):
    """
        指定访问url的user的限制
        参考:django/contrib/auth/decorators.py; django/views/decorators/http.py
    """
    if not path:
        raise ParameterException('请传入url')
    name = path if not name else name

    def decorator(func):
        def inner(request, *args, **kwargs):
            # methods校验
            methods_check(request, methods)
            # request.user校验
            request_user_check(request, login_required, perm)
            # NOTE:推荐
            # request.token校验，更新token并通过接口返回
            res = request_token_check(
                request, func, token_required, *args, **kwargs)
            return res if res else func(request, *args, **kwargs)

        urlpatterns.append(
            url(r'^{path}/$'.format(path=path), inner, name=name))
        return inner
    return decorator


def user_check(user: 'checks that the user is logged in', perm: 'checks whether a user has a particular permission enabled' = None, raise_exception=True):
    """校验request中的user"""
    if not perm:
        return user.is_authenticated
    if isinstance(perm, str):
        perms = (perm,)
    else:
        perms = perm
    # First check if the user has the permission (even anon users)
    if user.has_perms(perms):
        return True
    # In case the 403 handler should be called raise the exception
    if raise_exception:
        raise InsufficientPermissionsError
    # As the last resort, show the login form
    return False


def methods_check(request, methods):
    try:
        assert request.method in methods
    except AssertionError:
        message = 'Method Not Allowed ({method}): {path}'.format(
            method=request.method, path=request.path)
        log.WARNING(message)
        raise ResponseNotAllowed(detail=message)
        # dataformat = get_dataformat(request)

        # r = dict(status_code=HTTP_405_METHOD_NOT_ALLOWED,
        #          detail=message)
        # response = HttpResponseNotAllowed(
        #     methods, json.dumps(r), content_type=dataformat.content_type)
        # log.warn(message)
        # return response


def request_user_check(request, login_required, perm):
    try:
        assert login_required
        user_check(request.user, perm)
    except AssertionError:
        pass
    except InsufficientPermissionsError:
        message = 'user get no permission (perm:{perm})'.format(
            perm=perm)
        log.warn(message)
        raise InsufficientPermissionsError(detail=message)


def request_token_check(request, func, token_required, *args, **kwargs):
    try:
        assert token_required
        token = request.headers._store.get('token')[1]
        new_token = token_refresh_sliding_handler(token)
        res = func(request, *args, **kwargs)
        res.content = json.dumps(
            dict(json.loads(res.content), **new_token))
        return res
    except AssertionError:
        pass
    except IndexError:
        message = 'headers need token'
        log.warn(message)
        raise InvalidJwtToken(detail=message)
    except:
        message = 'user not authentication'
        log.warn(message)
        raise InvalidJwtToken(detail=message)


