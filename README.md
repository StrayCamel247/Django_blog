# windows10项目启动
- 准备好工具python3.x和git。下载好git上的文件，进入django_blogback目录，安装虚拟环境`pip install virtualenv`命名为**env** `virtualenv env`。win系统启动虚拟机：` .\env\Scripts\activate`
- 以后部署网站就在 虚拟机上进行。方便些
- 安装需求文件`pip -install -r requirement.txt`再启动项目`python manage.py runserver`

# 服务器部署项目
https://boywithacoin.cn/article/nginx-gunicorn-fu-wu-qi-pei-zhi-django/

### 项目源码：
**克隆项目:**
```
~# git clone https://github.com/Freen247/django_blogback.git
~# pwd
/home/django_blogback
```

#### 创建虚拟环境
**虚拟环境是个好东西**,我选择的是在django项目中创建,方便处理。
```shell
~# cd .\django_blogback\
~# virtualenv django_env
~# source /django_env/bin/activate
~# pip install -r requirement.txt
```

### NGINX

尝试运行django项目：`python manage.py runserver`
成功！
注意ALLOWED_HOSTS的值：`[‘127.0.0.1’, ‘localhost’, ‘域名’]或者[*]`

#### 安装配置 Nginx
安装nginx：
- 安装nginx依赖工具PCRE，让nginx有rewrite功能：
1. 安装PCRE依赖工具`yum -y install make zlib zlib-devel gcc-c++ libtool  openssl openssl-devel`
2. cd /usr/local/src/ && wget http://downloads.sourceforge.net/project/pcre/pcre/8.35/pcre-8.35.tar.gz && tar zxvf pcre-8.35.tar.gz && cd pcre-8.35 &&./configure && make && make install

- 下载nginx并安装：`cd /usr/local/src/ &&wget http://nginx.org/download/nginx-1.6.2.tar.gz && tar zxvf nginx-1.6.2.tar.gz && cd nginx-1.6.2 &&`
` ./configure --prefix=/usr/local/webserver/nginx --with-http_stub_status_module --with-http_ssl_module --with-pcre=/usr/local/src/pcre-8.35&& make &&  make install`
- 在/usr/local/webserver/nginx/目录x下就是我们安装好的nginx了。
修改一下/usr/local/webserver/nginx/conf/nginx.conf 配置文件，不要使用默认的那个：

```shell
[root@VM_101_141_centos ~]# cat /usr/local/webserver/nginx/conf/nginx.conf

#user  nobody;
worker_processes  1;

error_log  logs/error.log;
#error_log  logs/error.log  notice;
#error_log  logs/error.log  info;

pid        logs/nginx.pid;


events {
    worker_connections  1024;
}


http {
    include       mime.types;
    default_type  application/octet-stream;

    #log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
    #                  '$status $body_bytes_sent "$http_referer" '
    #                  '"$http_user_agent" "$http_x_forwarded_for"';

    access_log  logs/access.log ;

    sendfile        on;
    #tcp_nopush     on;

    #keepalive_timeout  0;
    keepalive_timeout  65;

    #gzip  on;
        upstream app_server {

    # for UNIX domain socket setups
    server unix:/home/django_blogback/gunicorn.sock fail_timeout=0;

    }
    server {
        charset utf-8;
        listen       80;
        server_name  bpywithacoin.cn;

        #charset koi8-r;

        #access_log  logs/host.access.log  main;
         # static 和 media 的地址
        location /static {#注意!!!：static后面不能有/斜杠，否则会导致静态文件404
            alias /home/django_blogback/static;
        }
        location /media {
            alias /home/django_blogback/media;
        }


        location / {
           proxy_pass http://app_server;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }

        #error_page  404              /404.html;

        # redirect server error pages to the static page /50x.html
        #
        error_page   500 502 503 504  /50x.html;
        location = /50x.html {
            root   html;
        }
}
}
```
#### 连接 Nginx 配置
Systemd服务文件以.service结尾，比如现在要建立nginx为开机启动，如果用yum install命令安装的，yum命令会自动创建nginx.service文件，直接用命令

`systemcel enable nginx.service`

设置开机启动即可。
在这里我是用源码编译安装的，所以要手动创建nginx.service服务文件。
开机没有登陆情况下就能运行的程序，存在系统服务（system）里，即：
`/lib/systemd/system/`
在系统服务目录创建nginx.service
`vi /lib/systemd/system/nginx.service`
```shell
[Unit]
Description=nginx
After=network.target
  
[Service]
Type=forking
ExecStart=/usr/local/webserver/nginx/sbin/nginx
ExecReload=/usr/local/webserver/nginx/sbin/nginxnginx -s reload
ExecStop=/usr/local/webserver/nginx/sbin/nginxnginx -s quit
PrivateTmp=true
  
[Install]
WantedBy=multi-user.target
```
有的的服务的目录实在etc/systemd/system/,,如果失败了k可以再试一下

上面的配置检查好之后，使用下面的命令来将这个配置跟 Nginx 建立连接，使用命令：
`ln -s /usr/local/nginx/conf/nginx nginx安装dir/nginx/sites-enabled`
测试是否配置成功：
 `/usr/local/webserver/nginx/sbin/nginx -t`

没报错的话，重启一下 Nginx：`systemctl restart nginx`

好了，重启 Nginx 之后可以登录自己配置的域名，看看自己的项目是不是已经成功的运行了呢！
### gunicorn

#### 安装和配置

`安装： pip install gunicorn`
尝试用gunicorn开启我们的项目：
`gunicorn django_blogback.wsgi:application --bind 0.0.0.0:8000`
```shell
[2019-06-30 14:26:04 +0800] [19524] [INFO] Starting gunicorn 19.9.0
[2019-06-30 14:26:04 +0800] [19524] [INFO] Listening at: http://0.0.0.0:8000 (19524)
[2019-06-30 14:26:04 +0800] [19524] [INFO] Using worker: sync
[2019-06-30 14:26:04 +0800] [19527] [INFO] Booting worker with pid: 1952
```
返回结果成功！这样我们就可以通过gunicorn开启我们的项目。
编写gunicorn_start.sh脚本，`chmod +x gunicorn_start.sh`便于nohup工具后台持续运行.
```shell
[root@VM_101_141_centos home]# cat gunicorn_start.sh
#!/bin/bash
NAME='django_blogback' #应用的名称i
DJANGODIR=/home/django_blogback #django项目的目录
SOCKFILE=/home/django_blogback/gunicorn.sock #使用这个sock来通信
USER=root #运行此应用的用户
GROUP=root #运行此应用的组
NUM_WORKERS=3 #gunicorn使用的工作进程数
DJANGO_SETTINGS_MODULE=django_blogback.settings #django的配置文件
DJANGO_WSGI_MODULE=django_blogback.wsgi #wsgi模块
LOG_DIR=/home/logs #日志目录

echo "starting $NAME as `whoami`"

#激活python虚拟运行环境
cd $DJANGODIR
source /envblog/bin/activate
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$DJANGODIR:$PYTHONPATH

#如果gunicorn.sock所在目录不存在则创建
RUNDIR=$(dirname $SOCKFILE)
test -d $RUNDIR || mkdir -p $RUNDIR

#启动Django

exec gunicorn ${DJANGO_WSGI_MODULE}:application \
    --name $NAME \
    --workers $NUM_WORKERS \
    --user=$USER --group=$GROUP \
    --log-level=debug \
    --bind=unix:$SOCKFILE \
    --access-logfile=${LOG_DIR}/gunicorn_access.log
```
有一个日志文件夹和nohup日志文件需要创建：
```shell
[root@VM_101_141_centos home]# ls
django_blogback  gunicorn_start.sh  logs  nohup.log
```
LOG_DIR=/home/logs #日志目录  和 nohup.log #日志文件
#### 启动配置文件

文件配置完成之后，使用nohup的命令启动服务：
后台持续运行:`nohup ./gunicorn_start.sh > nohup.log`
成功！：
```shell
(envblog) [root@VM_101_141_centos home]# nohup ./gunicorn_start.sh > nohup.log
nohup: ignoring input and redirecting stderr to stdout
```
可能会发现这时候终端无法输入指令，直接退出就好。

### 维护、更改文件之后后续操作

之后的项目维护中：
- 如果更改了 gunicorn 的sh文件，需要重新使用nohup命令启动。

- 如果修改了 Nginx 的配置文件，先测试以配置是否成功` /usr/local/webserver/nginx/sbin/nginx -t `再重启`systemctl restart nginx`

- 如果调用了新的django类似jet、xadmin、django-mdeditor包添加组件当需要另外调用js\css样式的时候，需要运行`python manage.py collectstatic`

-如果更改models更改注册的模型，需要增删改数据库等，需要运行
`python manage.py makemigrations`和`python manage.py migrate`

有疑问欢迎
mail aboyinsky@outlook.com 
qq 1351975058
qq群 706340320


    db.sqlite3  //数据库文件
    manage.py   //django 管理文件
    requirements.txt    //项目pip需要的安装包 pip install -r requirements.txt

    apps    //项目定义的所有的包
        api     //apps的api
            permissions.py
            serializers.py
            views.py

        blog    //apps-blog
            admin.py    //将app blog注册到后台admin中去
            adminx.py   //将app blog注册到后台adminx中去
            apps.py     //对blog应用进行命名
            forms.py    //自动生成HTML表单元素，检查表单数据的合法性，如果验证错误，数据类型转换（字符类型的数据转换成相应的Python类型）
            models.py   //blog的一些模型 定义blog里面所需要的类
            search_indexes.py   //Django Haystack: 要想对某个 app 下的数据进行全文检索，就要在该 app 下创建一 search_indexes.py 文件，然后创建一个 XXIndex 类（XX 为含有被检索数据的模型，如这里的 Article），并且继承 SearchIndex 和 Indexable
            silian.xml      //blog里的死链存放
            sitemaps.py     //将blog里的链接生成并非放入sitemap.xml文件中
            urls.py     //定义blog中的url指向到xxView中去
            views.py    //blog的视图文件，定义各个页面的视图设置
            whoosh_cn_backend.py    //django-haystack全文检索需要使用jieba分词的文件，将文件whoosh_backend.py（该文件路径为python路径/lib/python3/site-packages/haystack/backends/whoosh_backend.py）拷贝到app下面，并重命名为whoosh_cn_backend.py，例如blog/whoosh_cn_backend.py
            migrations  //blog的迁移文件，每次修改模型视图后进行数据迁移（到数据库）会生成记录
            templatetags    //blog包的tags模板，Custom template tags and filters
                blog_tags.py    //app的tags文件，可从数据库传数据进入页面，在页面用模板函数方法调用数据

        comment
            admin.py    //将app blog注册到后台admin中去
            apps.py     //对comment应用进行命名
            models.py   //comment的一些模型 定义blog里面所需要的类
            tests.py    //测试文件
            urls.py     //定义comment中的url指向到xxView中去
            views.py    //comment的视图文件，定义各个页面的视图设置
            __init__.py     //默认生成的文件
            
            migrations  //comment的数据迁移文件，每次修改模型视图后进行数据迁移（到数据库）会生成记录
                
            templatetags    //comment包的tags模板，Custom template tags and filters
                comment_tags.py     //app的tags文件，可从数据库传数据进入页面，在页面用模板函数方法调用数据
                
        tool      //网站工具箱，开发中ing
            admin.py    //将app blog注册到后台admin中去
            adminx.py   //将app blog注册到后台adminx中去
            apps.py     //对comment应用进行命名
            models.py   //tool的一些模型 定义blog里面所需要的类
            tests.py    //测试文件
            urls.py     //定义tool中的url指向到xxView中去
            views.py    //tool的视图文件，定义各个页面的视图设置

            apis    //tool的apis
                bd_push.py
                links_test.py
                useragent.py
                    
            migrations  //tool的数据迁移文件，每次修改模型视图后进行数据迁移（到数据库）会生成记录
               
                    
            static      //工具箱界面的独立static文件
                tool
                    css
                        tool.css
                    js
                        tool.js
                        
            templates   //工具箱独立的前端模板文件
                tool
                    base_tool.html
                    bd_push.html
                    bd_push_site.html
                    characters.html
                    link_test.html
                    regex.html
                    tool.html
                    useragent.html
                    
                    tags
                        tool_list.html
                        
            templatetags    //工具箱的tags模板，Custom template tags and filters
                tool_tags.py    //app的tags文件，可从数据库传数据进入页面，在页面用模板函数方法调用数据

        user
            admin.py    //将app blog注册到后台admin中去
            adminx.py   //将app blog注册到后台adminx中去
            apps.py     //对comment应用进行命名
            forms.py    //自动生成HTML表单元素，检查表单数据的合法性，如果验证错误，数据类型转换（字符类型的数据转换成相应的Python类型）
            models.py   //user的一些模型 定义blog里面所需要的类
            tests.py    //测试文件
            urls.py     //定义user中的url指向到xxView中去
            views.py    //user的视图文件，定义各个页面的视图设置
            
            migrations  //comment的数据迁移文件，每次修改模型视图后进行数据迁移（到数据库）会生成记录
                    
            templatetags    //user包的tags模板，Custom template tags and filters
                oauth_tags.py     //app的tags文件，可从数据库传数据进入页面，在页面用模板函数方法调用数据
                
    django_blog
        settings.py     //项目的设置文件
        urls.py     //管理项目的所有的url的定向文件，指向xx包对应的url下的xx视图
        wsgi.py     //建立服务器与django程序的桥梁，可以wsgi+nginx部署上服务器（本网站暂时没使用）
        
            
    env //项目虚拟环境，（文件夹里的文件已删除，太大了）

    static  //项目前端的所有media，css，js文件
        account
            account.css     
            
        admin   //admin后端的样式文件
            css
                cs-skin-elastic.css
                flag-icon.min.css
                pe-icon-7-filled.css
                style.css
                themify-icons.css
                
            fonts
                fontawesome-webfont.eot
                fontawesome-webfont.svg
                fontawesome-webfont.ttf
                fontawesome-webfont.woff
                fontawesome-webfont.woff2
                FontAwesome.otf
                Pe-icon-7-stroke.eot
                Pe-icon-7-stroke.ttf
                Pe-icon-7-stroke.woff
                themify.eot
                themify.svg
                themify.ttf
                themify.woff
                
                icomoon
                    icomoon.eot
                    icomoon.svg
                    icomoon.ttf
                    icomoon.woff
                    index.html
                    
            images
                .gitignore
                admin.jpg
                default.png
                favicon.png
                logo.png
                logo.psd
                logo2.png
                
                avatar
                    1.jpg
                    2.jpg
                    3.jpg
                    4.jpg
                    5.jpg
                    6.jpg
                    7.jpg
                    8.jpg
                    default.jpg
                    
            js
                canvas.js
                contacts.js
                main.js
                plugins.js
                popper.min.js
                
        comment     //评论的样式文件
            css
                base_comment.css
                notification.css
                
            emoji
                +1.png
                angry.png
                anguished.png
                blush.png
                broken_heart.png
                clap.png
                cold_sweat.png
                confounded.png
                cry.png
                disappointed_relieved.png
                dizzy_face.png
                dog.png
                fearful.png
                fist.png
                flushed.png
                frowning.png
                grin.png
                heart.png
                heartbeat.png
                heart_eyes.png
                hushed.png
                innocent.png
                joy.png
                kissing_closed_eyes.png
                kissing_heart.png
                mask.png
                no_mouth.png
                pensive.png
                persevere.png
                pray.png
                relieved.png
                scream.png
                sleepy.png
                smile.png
                smiley.png
                smirk.png
                sob.png
                sparkling_heart.png
                stuck_out_tongue.png
                stuck_out_tongue_closed_eyes.png
                stuck_out_tongue_winking_eye.png
                sunglasses.png
                sweat.png
                sweat_smile.png
                unamused.png
                v.png
                worried.png
                yum.png
                
            js
                activate-power.js
                editor.js
                notification.js
                
        css
            accounts_admin.css
            blog.css
            slick.css
            style.css
            
        fonts   //awsomefont文件
            fontawesome-webfont.eot
            fontawesome-webfont.svg
            fontawesome-webfont.ttf
            fontawesome-webfont.woff
            fontawesome-webfont.woff2
            FontAwesome.otf
            
        image
            avatar.png
            favicon.ico
            fontawesome.jpg
            logo.png
            
        images
            logo.png
            summary.jpg
            
        js
            ajax-contact-form.js
            backcanvas.js
            contacts.js
            custom.js
            MdEditor.js
            panel.js
            reading-position-indicator.js
            salvattore.min.js
            slick.min.js
            
        mdeditor    //md编辑器的需求文件
            css
                editormd.css
                editormd.logo.css
                editormd.logo.min.css
                editormd.min.css
                editormd.preview.css
                editormd.preview.min.css
                style.css
                
            fonts
                editormd-logo.eot
                editormd-logo.svg
                editormd-logo.ttf
                editormd-logo.woff
                fontawesome-webfont.eot
                fontawesome-webfont.svg
                fontawesome-webfont.ttf
                fontawesome-webfont.woff
                fontawesome-webfont.woff2
                FontAwesome.otf
                
            images
                loading.gif
                loading@2x.gif
                loading@3x.gif
                
                logos
                    editormd-favicon-16x16.ico
                    editormd-favicon-24x24.ico
                    editormd-favicon-32x32.ico
                    editormd-favicon-48x48.ico
                    editormd-favicon-64x64.ico
                    editormd-logo-114x114.png
                    editormd-logo-120x120.png
                    editormd-logo-144x144.png
                    editormd-logo-16x16.png
                    editormd-logo-180x180.png
                    editormd-logo-240x240.png
                    editormd-logo-24x24.png
                    editormd-logo-320x320.png
                    editormd-logo-32x32.png
                    editormd-logo-48x48.png
                    editormd-logo-57x57.png
                    editormd-logo-64x64.png
                    editormd-logo-72x72.png
                    editormd-logo-96x96.png
                    vi.png
                    
            js
                editormd.js
                editormd.min.js
                jquery.min.js
                
                lib
                    flowchart.min.js
                    jquery.flowchart.min.js
                    marked.min.js
                    prettify.min.js
                    raphael.min.js
                    sequence-diagram.min.js
                    underscore.min.js
                    
                    codemirror
                        addons.min.js
                        AUTHORS
                        bower.json
                        codemirror.min.css
                        codemirror.min.js
                        LICENSE
                        modes.min.js
                        package.json
                        README.md
                        
                        addon
                            comment
                                comment.js
                                continuecomment.js
                                
                            dialog
                                dialog.css
                                dialog.js
                                
                            display
                                fullscreen.css
                                fullscreen.js
                                panel.js
                                placeholder.js
                                rulers.js
                                
                            edit
                                closebrackets.js
                                closetag.js
                                continuelist.js
                                matchbrackets.js
                                matchtags.js
                                trailingspace.js
                                
                            fold
                                brace-fold.js
                                comment-fold.js
                                foldcode.js
                                foldgutter.css
                                foldgutter.js
                                indent-fold.js
                                markdown-fold.js
                                xml-fold.js
                                
                            hint
                                anyword-hint.js
                                css-hint.js
                                html-hint.js
                                javascript-hint.js
                                show-hint.css
                                show-hint.js
                                sql-hint.js
                                xml-hint.js
                                
                            lint
                                coffeescript-lint.js
                                css-lint.js
                                javascript-lint.js
                                json-lint.js
                                lint.css
                                lint.js
                                yaml-lint.js
                                
                            merge
                                merge.css
                                merge.js
                                
                            mode
                                loadmode.js
                                multiplex.js
                                multiplex_test.js
                                overlay.js
                                simple.js
                                
                            runmode
                                colorize.js
                                runmode-standalone.js
                                runmode.js
                                runmode.node.js
                                
                            scroll
                                annotatescrollbar.js
                                scrollpastend.js
                                simplescrollbars.css
                                simplescrollbars.js
                                
                            search
                                match-highlighter.js
                                matchesonscrollbar.css
                                matchesonscrollbar.js
                                search.js
                                searchcursor.js
                                
                            selection
                                active-line.js
                                mark-selection.js
                                selection-pointer.js
                                
                            tern
                                tern.css
                                tern.js
                                worker.js
                                
                            wrap
                                hardwrap.js
                                
                        lib
                            codemirror.css
                            codemirror.js
                            
                        mode
                            index.html
                            meta.js
                            
                            apl
                                apl.js
                                index.html
                                
                            asterisk
                                asterisk.js
                                index.html
                                
                            clike
                                clike.js
                                index.html
                                scala.html
                                
                            clojure
                                clojure.js
                                index.html
                                
                            cobol
                                cobol.js
                                index.html
                                
                            coffeescript
                                coffeescript.js
                                index.html
                                
                            commonlisp
                                commonlisp.js
                                index.html
                                
                            css
                                css.js
                                index.html
                                less.html
                                less_test.js
                                scss.html
                                scss_test.js
                                test.js
                                
                            cypher
                                cypher.js
                                index.html
                                
                            d
                                d.js
                                index.html
                                
                            dart
                                dart.js
                                index.html
                                
                            diff
                                diff.js
                                index.html
                                
                            django
                                django.js
                                index.html
                                
                            dockerfile
                                dockerfile.js
                                index.html
                                
                            dtd
                                dtd.js
                                index.html
                                
                            dylan
                                dylan.js
                                index.html
                                
                            ebnf
                                ebnf.js
                                index.html
                                
                            ecl
                                ecl.js
                                index.html
                                
                            eiffel
                                eiffel.js
                                index.html
                                
                            erlang
                                erlang.js
                                index.html
                                
                            forth
                                forth.js
                                index.html
                                
                            fortran
                                fortran.js
                                index.html
                                
                            gas
                                gas.js
                                index.html
                                
                            gfm
                                gfm.js
                                index.html
                                test.js
                                
                            gherkin
                                gherkin.js
                                index.html
                                
                            go
                                go.js
                                index.html
                                
                            groovy
                                groovy.js
                                index.html
                                
                            haml
                                haml.js
                                index.html
                                test.js
                                
                            haskell
                                haskell.js
                                index.html
                                
                            haxe
                                haxe.js
                                index.html
                                
                            htmlembedded
                                htmlembedded.js
                                index.html
                                
                            htmlmixed
                                htmlmixed.js
                                index.html
                                
                            http
                                http.js
                                index.html
                                
                            idl
                                idl.js
                                index.html
                                
                            jade
                                index.html
                                jade.js
                                
                            javascript
                                index.html
                                javascript.js
                                json-ld.html
                                test.js
                                typescript.html
                                
                            jinja2
                                index.html
                                jinja2.js
                                
                            julia
                                index.html
                                julia.js
                                
                            kotlin
                                index.html
                                kotlin.js
                                
                            livescript
                                index.html
                                livescript.js
                                
                            lua
                                index.html
                                lua.js
                                
                            markdown
                                index.html
                                markdown.js
                                test.js
                                
                            mirc
                                index.html
                                mirc.js
                                
                            mllike
                                index.html
                                mllike.js
                                
                            modelica
                                index.html
                                modelica.js
                                
                            nginx
                                index.html
                                nginx.js
                                
                            ntriples
                                index.html
                                ntriples.js
                                
                            octave
                                index.html
                                octave.js
                                
                            pascal
                                index.html
                                pascal.js
                                
                            pegjs
                                index.html
                                pegjs.js
                                
                            perl
                                index.html
                                perl.js
                                
                            php
                                index.html
                                php.js
                                test.js
                                
                            pig
                                index.html
                                pig.js
                                
                            properties
                                index.html
                                properties.js
                                
                            puppet
                                index.html
                                puppet.js
                                
                            python
                                index.html
                                python.js
                                
                            q
                                index.html
                                q.js
                                
                            r
                                index.html
                                r.js
                                
                            rpm
                                index.html
                                rpm.js
                                
                                changes
                                    index.html
                                    
                            rst
                                index.html
                                rst.js
                                
                            ruby
                                index.html
                                ruby.js
                                test.js
                                
                            rust
                                index.html
                                rust.js
                                
                            sass
                                index.html
                                sass.js
                                
                            scheme
                                index.html
                                scheme.js
                                
                            shell
                                index.html
                                shell.js
                                test.js
                                
                            sieve
                                index.html
                                sieve.js
                                
                            slim
                                index.html
                                slim.js
                                test.js
                                
                            smalltalk
                                index.html
                                smalltalk.js
                                
                            smarty
                                index.html
                                smarty.js
                                
                            smartymixed
                                index.html
                                smartymixed.js
                                
                            solr
                                index.html
                                solr.js
                                
                            soy
                                index.html
                                soy.js
                                
                            sparql
                                index.html
                                sparql.js
                                
                            spreadsheet
                                index.html
                                spreadsheet.js
                                
                            sql
                                index.html
                                sql.js
                                
                            stex
                                index.html
                                stex.js
                                test.js
                                
                            stylus
                                index.html
                                stylus.js
                                
                            tcl
                                index.html
                                tcl.js
                                
                            textile
                                index.html
                                test.js
                                textile.js
                                
                            tiddlywiki
                                index.html
                                tiddlywiki.css
                                tiddlywiki.js
                                
                            tiki
                                index.html
                                tiki.css
                                tiki.js
                                
                            toml
                                index.html
                                toml.js
                                
                            tornado
                                index.html
                                tornado.js
                                
                            turtle
                                index.html
                                turtle.js
                                
                            vb
                                index.html
                                vb.js
                                
                            vbscript
                                index.html
                                vbscript.js
                                
                            velocity
                                index.html
                                velocity.js
                                
                            verilog
                                index.html
                                test.js
                                verilog.js
                                
                            xml
                                index.html
                                test.js
                                xml.js
                                
                            xquery
                                index.html
                                test.js
                                xquery.js
                                
                            yaml
                                index.html
                                yaml.js
                                
                            z80
                                index.html
                                z80.js
                                
                        theme
                            3024-day.css
                            3024-night.css
                            ambiance-mobile.css
                            ambiance.css
                            base16-dark.css
                            base16-light.css
                            blackboard.css
                            cobalt.css
                            colorforth.css
                            eclipse.css
                            elegant.css
                            erlang-dark.css
                            lesser-dark.css
                            mbo.css
                            mdn-like.css
                            midnight.css
                            monokai.css
                            neat.css
                            neo.css
                            night.css
                            paraiso-dark.css
                            paraiso-light.css
                            pastel-on-dark.css
                            rubyblue.css
                            solarized.css
                            the-matrix.css
                            tomorrow-night-bright.css
                            tomorrow-night-eighties.css
                            twilight.css
                            vibrant-ink.css
                            xq-dark.css
                            xq-light.css
                            zenburn.css
                            
                plugins
                    plugin-template.js
                    
                    code-block-dialog
                        code-block-dialog.js
                        
                    emoji-dialog
                        emoji-dialog.js
                        emoji.json
                        
                    goto-line-dialog
                        goto-line-dialog.js
                        
                    help-dialog
                        help-dialog.js
                        help.md
                        
                    html-entities-dialog
                        html-entities-dialog.js
                        html-entities.json
                        
                    image-dialog
                        image-dialog.js
                        
                    link-dialog
                        link-dialog.js
                        
                    preformatted-text-dialog
                        preformatted-text-dialog.js
                        
                    reference-link-dialog
                        reference-link-dialog.js
                        
                    table-dialog
                        table-dialog.js
                        
                    test-plugin
                        test-plugin.js
                        
            languages
                en.js
                
        media      //网站所有媒体文件
            default.png
            TOP.png
            
            avatar
                default.png
                
                2019
                    06
                        24
                            logo.png
                            ssh.jpg
                            ssh_ybKsqz1.jpg
                            
                        25
                            summary.jpg
                            
                    07
                        03
                            -66b454a2fe4c030f.jpg
                            TIM ͼ20190703223050.png
                            
            category_img
                apps.py
                avatar.png
                C_C_C.png
                default.png
                java.png
                javasrcipt.png
                linux.png
                logo.png
                mysql.png
                python.png
                
            editor
                QQͼƬ20190222153954_20190222154056465872.png
                QQͼƬ20190321073614_20190321073632603995.png
                QQͼƬ20190321073652_20190321073831294406.png
                QQͼƬ20190321073652_20190321073938371347.png
                QQ ͼ20190321073819_20190321073907463693.png
                QQ ͼ20190321074645_20190321074655642171.png
                QQ ͼ20190321075012_20190321075021168820.png
                TIMͼƬ20190703111820_20190703111836630161.png
                 �ݵ ߼ ṹ  ϸ  _20190703133152605358.png
                 �ݵ ߼ ṹ  ϸ  _20190703133228766861.png
                 �ݵ ߼ ṹ  ϸ  _20190703133251337819.png
                ʱ�临�Ӷ �Ҫ ʱ    Ĺ�ģ  �_20190703134439564372.png
                ʱ�临�ӶȵĹ�ϵ_20190703134950941340.png
                �㷨   �1_20190703134134971142.png
                 �Խṹ_20190703132820257616.png
                 �Ա   _20190703142946314998.png
                 �Ա �߼ ṹͼ_20190703143309058949.png
                 �Ӵ  λ _20190703133849378668.png
                ˳ 洢  λ   _20190703133735953936.png
                ˳ 洢  �Ա�_20190703143631560068.png
                
            media
                6874.png
                6874_bHngGN3.png
                back.jpg
                backback.jpg
                backback_eWPDp2K.jpg
                bsblog.png
                bsblog_XoexjWJ.png
                datastru.jpg
                functionvsclass.jpg
                java-jdbc.jpg
                markdown.png
                pythonpip.jpg
                qianduanhouduanyunwei.jpg
                qianduanxuexi.jpg
                qianduanxuexi_azUYlmF.jpg
                SEO.jpg
                SEO_a2C6n9x.jpg
                sitemap.jpg
                sitemap_12x7SJx.jpg
                sitemap_5l3bUQr.jpg
                ssh.jpg
                th.jpg
                th_spider.jpg
                virtualenv.png
                xamdin.jpg
                    �ύ �ӵ�ַ ȫ.jpg
                    �ύ �ӵ�ַ ȫ_w19I8si.jpg
                    �_YXOYKqe.jpg
                
            user_img
        notifications   //通知的js文件
            notice.js
            
        range_filter
            css
                style.css
                
        uploads     //上传的媒体文件
            
    templates   //前端的html文件
        archive.html    //归档界面，开发中ing
        article.html    //文章界面，继承base，包含comment
        auther_box.html     //作者用户框的文件，加载在index主页中
        base.html   //主文件
        category.html   //分类文件，继承base文件，原理和index一样，只是选择相同类别的文章
        contacts.html   //通讯录文件，通讯录聊天室开发中ing
        index.html  //主文件，显示网站的主网页，继承base
        post.html   //每个文章的小卡片样式，用于index category文件中
        
        account //用户界面啊样式文件，加载在网站的各个页面中
            account_inactive.html
            admin.html
            base.html   //主界面
            change_profile.html
            delete_user.html
            email.html
            email_confirm.html
            login.html
            logout.html
            password_change.html
            password_reset.html
            password_reset_done.html
            password_reset_from_key.html
            password_reset_from_key_done.html
            password_set.html
            profile.html
            signup.html
            signup_closed.html
            user_avatar.html
            verification_sent.html
            verified_email_required.html
            
            email
                password_reset_key_message.txt
                
        blog
            archive.html
            category.html
            post.html
            
        comment //评论界面，加载在文章界面中
            comment_form.html   //评论编辑的界面
            comment_list.html   //显示各个评论的界面
            notification.html   //评论通知界面，开发中ing
            
        registration    //注册的界面
            logged_out.html
            password_change_done.html
            password_change_form.html
            password_reset_complete.html
            password_reset_confirm.html
            password_reset_done.html
            password_reset_email.html
            password_reset_form.html
            
        search  //搜索的界面
            search.html
            
            indexes
                blog
                    article_text.txt
                    
        tools_html  //工具箱的界面，开发中ing
            md2html.html
            upload.php
            
    whoosh_index    //查询的文件，django-haystack+whoosh+jieba实现中文全文搜索
        MAIN_avwdcjdhnjnleti1.seg
        MAIN_WRITELOCK
        MAIN_y2pohnobpf8qhshh.seg
        _MAIN_421.toc
        
