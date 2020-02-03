"""day60 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from app01 import views
from django.views.static import serve
from day60 import settings



urlpatterns = [
    url(r'^admin/', admin.site.urls),
    # 1  注册功能
    url(r'^register/', views.register, name='_register'),
    # 2  登陆功能
    url(r'^login/', views.login, name='_login'),
    # 3  图片验证码相关
    url(r'^get_code/', views.get_code),
    # 4  首页相关
    url(r'^home/', views.home, name='_home'),
    # 5  注销功能
    url(r'^logout/', views.logout, name='_logout'),
    # 6  修改密码
    url(r'^set_pwd/', views.set_password, name='_set_pwd'),
    # 7  暴露任意后端资源配置
    url(r'^media/(?P<path>.*)', serve, {"document_root": settings.MEDIA_ROOT}),

    # 11  点赞点踩
    url(r'^up_or_down/', views.up_or_down, name='updown'),

    # 12  文章评论
    url(r'^comment/', views.comment, name='_comment'),

    # 13  后台管理
    url(r'^backend/', views.backend, name='_backend'),

    # 14 添加文章
    url(r'^add_article/', views.add_article, name='_add_article'),

    # 15 编辑器上传图片
    url(r'^upload_image/', views.upload_image, name='_upload_image'),

    # 16  修改头像
    url(r'^set_avatar/', views.set_avatar, name='_set_avatar'),

    # 8  个人站点
    url(r'^(?P<username>\w+)/$', views.site, name='_site'),
    # 9  侧边栏筛选
    url(r'^(?P<username>\w+)/(?P<condition>category|tag|archive)/(?P<param>.*)/', views.site),
    # 10  文章详情页
    url(r'^(?P<username>\w+)/article/(?P<article_id>\d+)/', views.article_detail)
]
