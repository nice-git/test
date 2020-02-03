from django.shortcuts import render,HttpResponse,redirect,reverse
from app01.myforms import MyRegForm
from app01 import models
from django.http import JsonResponse
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from app01 import models
from app01.utils.mypage import Pagination


# Create your views here.
def register(request):
    form_obj = MyRegForm()
    # print(request.is_ajax())  # 判断当前请求是否是ajax请求
    if request.method == 'POST':
        # 定义一个与ajax回调函数交互的字典
        back_dic = {"code":1000,'msg':""}

        # 校验数据  用户名 密码 确认密码
        form_obj = MyRegForm(request.POST)
        if form_obj.is_valid():
            clean_data = form_obj.cleaned_data  # 用变量接收正确的结果 clean_data = {'username'   'password'  'confirm_password' 'email'}
            # 将确认密码键值对删除
            clean_data.pop('confirm_password')
            # 获取用户头像文件
            avatar_obj = request.FILES.get('avatar')
            # 判断用户头像是否为空
            if avatar_obj:
                # 添加到clean_data中
                clean_data['avatar'] = avatar_obj  # clean_data = {'username'  'password'  'email' 'avatar'}
            models.UserInfo.objects.create_user(**clean_data)
            back_dic['msg'] = '注册成功'
            back_dic['url'] = '/login/'
        else:
            back_dic['code'] = 2000
            back_dic['msg'] = form_obj.errors
        return JsonResponse(back_dic)
    return render(request,'register.html',locals())


def login(request):
    if request.method == 'POST':
        back_dic = {"code": 1000, "msg": ''}

        username = request.POST.get('username')
        password = request.POST.get('password')
        code = request.POST.get('code')
        print(username, password, code)
        if request.session.get('code').upper() == code.upper():
            auth_obj = auth.authenticate(username=username, password=password)
            if auth_obj:
                auth.login(request, auth_obj)
                back_dic['msg'] = '登陆成功'
                back_dic['url'] = '/home/'
                # return HttpResponse('登陆成功')
                return JsonResponse(back_dic)
            else:
                back_dic['code'] = '2000'
                back_dic['msg'] = "用户名或密码错误"
                return JsonResponse(back_dic)
        else:
            back_dic['code'] = '3000'
            back_dic['msg'] = '验证码错误'
            return JsonResponse(back_dic)
    return render(request, 'login.html')


from PIL import Image, ImageDraw, ImageFont
"""
Image:  产生图片
ImageDraw：  在图片上写字
ImageFont：  控制图片上字体样式
"""
from io import BytesIO, StringIO
"""
BytesIO  能够临时帮你保存数据 获取的时候以二进制方式返回给你
StringIO   能够临时帮你保存数据 获取的时候以字符串方式返回给你
"""

import random
def get_random():
    return random.randint(0,255), random.randint(0, 255), random.randint(0, 255)

def get_code(request):
    # 在图片上写字
    img_obj = Image.new('RGB', (350, 35), get_random())
    # 产生针对该图片的画笔对象
    img_draw = ImageDraw.Draw(img_obj)
    # 产生一个字体样式对象
    img_font = ImageFont.truetype(r'app01\static\font\新叶念体.otf', 35)
    io_obj = BytesIO()

    code = ''
    for i in range(5):
        upper_str = chr(random.randint(65, 90))
        lower_str = chr(random.randint(97, 122))
        random_int = str(random.randint(0, 9))

        temp_str = random.choice([upper_str, lower_str, random_int])
        # 写到图片上
        img_draw.text((45+i*60, -2), temp_str, get_random(), font=img_font)

        code += temp_str
    print(code)

    img_obj.save(io_obj, 'png')
    # 将产生的随机验证码存储到session中  以便于后面的验证码校验
    request.session['code'] = code
    return HttpResponse(io_obj.getvalue())


def home(request):
    article_list = models.Article.objects.all()

    current_page = request.GET.get('page', 1)
    all_count = article_list.count()
    # 1 现生成一个自定义分页器类对象
    page_obj = Pagination(current_page=current_page,all_count=all_count,pager_count=2)
    # 2 针对真实的queryset数据进行切片操作
    page_queryset = article_list[page_obj.start:page_obj.end]
    return render(request, 'home.html', locals())

@login_required
def logout(request):
    auth.logout(request)
    return redirect(reverse('_home'))

@login_required()
def set_password(request):
    if request.is_ajax():
        back_dic = {"code": 1000, 'msg': ''}
        old_pwd = request.POST.get('old_pwd')
        new_pwd = request.POST.get('new_pwd')
        confirm_pwd = request.POST.get('confirm_pwd')
        print(old_pwd, new_pwd, confirm_pwd)
        if new_pwd == confirm_pwd:
            is_right = request.user.check_password(old_pwd)
            if is_right:
                request.user.set_password(confirm_pwd)
                request.user.save()
                back_dic['msg'] = '修改成功'
                back_dic['url'] = '/login/'
                # back_dic['url'] = reverse('_login')
                return JsonResponse(back_dic)
            else:
                back_dic['code'] = '2000'
                back_dic['msg'] = '原密码错误'
                return JsonResponse(back_dic)
        else:
            back_dic['code'] = '3000'
            back_dic['msg'] = '两次密码不一致'
            return JsonResponse(back_dic)

from django.db.models.functions import TruncMonth
from django.db.models import Count, Max, Min, Sum, Avg
def site(request, username, *args, **kwargs):
    username_obj = models.UserInfo.objects.filter(username=username).first()
    if not username_obj:
        return render(request, 'error.html')
    blog = username_obj.blog
    article_list = models.Article.objects.filter(blog=blog)

    if kwargs:
        print(kwargs)
        condition = kwargs.get('condition')  # category  tag  archive
        param = kwargs.get('param')  # 1   2     2019-11
        if condition == 'category':
            article_list = article_list.filter(category_id=param)
        elif condition == 'tag':
            article_list = article_list.filter(tags__pk=param)
        else:
            year, month = param.split('-')
            article_list = article_list.filter(create_time__year=year, create_time__month=month)

    current_page = request.GET.get('page', 1)
    all_count = article_list.count()
    # 1 现生成一个自定义分页器类对象
    page_obj = Pagination(current_page=current_page, all_count=all_count, pager_count=2)
    # 2 针对真实的queryset数据进行切片操作
    page_queryset = article_list[page_obj.start:page_obj.end]

    # 查看当前用户的分类及每个分类下的文章数
    category_list = models.Category.objects.filter(blog=blog).annotate(c=Count('article')).values('c', 'name', 'pk')

    # 查询当前用户的标签及每个标签下的文章数
    tag_list = models.Tag.objects.filter(blog=blog).annotate(c=Count('article')).values('c', 'name', 'pk')

    date_list = models.Article.objects.filter(blog=blog).annotate(month=TruncMonth('create_time')).values('month').annotate(c=Count('pk')).values('c', 'month')
    print(date_list)
    # date_list = models.Article.objects.filter(blog=blog).annotate(month=TruncMonth('create_time')).values('month').annotate(c=Count('pk')).values('c','month')


    return render(request, 'site.html', locals())


def article_detail(request, username, article_id):
    username_obj = models.UserInfo.objects.filter(username=username).first()
    if not username_obj:
        return render(request, 'error.html')
    blog = username_obj.blog
    article_obj = models.Article.objects.filter(pk=article_id, blog=blog).first()
    if not article_obj:
        return render(request, 'error.html')
    comment_list = models.Comment.objects.filter(article_id=article_obj).all()
    return render(request, 'article_detail.html', locals())

from django.db.models import F
import json
def up_or_down(request):
    back_dic = {'code':1000, 'msg': ''}
    if request.is_ajax():
        article_id = request.POST.get('article_id')
        is_up = request.POST.get('is_up')
        is_up = json.loads(is_up)
        """
        1.判断当前用户是否登录
        2.当前文章是否是当前用户自己写的
        3.当前用户是否已经给当前文章点过赞或踩了
        4.操作数据库
            操作两张表
                数据库优化字段
        """
        if request.user.is_authenticated():
            article_obj = models.Article.objects.filter(pk=article_id).first()
            if not article_obj.blog.userinfo == request.user:
                is_click = models.UpAndDown.objects.filter(user=request.user, article=article_obj)
                if not is_click:
                    if is_up:
                        models.Article.objects.filter(pk=article_id).update(up_num=F('up_num')+1)
                        back_dic['msg'] = '点赞成功'
                    else:
                        models.Article.objects.filter(pk=article_id).update(down_num=F('down_num')+1)
                    models.UpAndDown.objects.create(user=request.user, article=article_obj, is_up=is_up)
                else:
                    back_dic['code'] = 2000
                    back_dic['msg'] = '您已经支持过'
            else:
                back_dic['code'] = 3000
                back_dic['msg'] = '不能给自己点赞'
        else:
            back_dic['code'] = 4000
            back_dic['msg'] = '请先<a href="/login/">登陆</a>'
        return JsonResponse(back_dic)


def comment(request):
    back_dic = {'code': 1000, 'msg': ''}
    if request.is_ajax():
        article_id = request.POST.get('article_id')
        content = request.POST.get('content')
        parent_id = request.POST.get('parent_id')
        article_obj = models.Article.objects.filter(pk=article_id).first()
        print(type(article_obj))
        if request.user.is_authenticated():
            models.Article.objects.filter(pk=article_id).update(comment_num=F('comment_num')+1)
            # 如果是对象，直接用models字段存，不是就用数据库里的字段存
            models.Comment.objects.create(content=content, article_id=article_id, user=request.user, parent_id=parent_id)
            back_dic['msg'] = '评论成功'
            return JsonResponse(back_dic)

from bs4 import BeautifulSoup
@login_required
def backend(request):
    article_list = models.Article.objects.filter(blog=request.user.blog).all()

    current_page = request.GET.get('page', 1)
    all_count = article_list.count()
    page_obj = Pagination(current_page=current_page, all_count=all_count, pager_count=9, per_page_num=3)
    page_queryset = article_list[page_obj.start:page_obj.end]
    return render(request, 'backend/backend.html', locals())

@login_required
def add_article(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        category_id = request.POST.get('category')
        tag_list = request.POST.getlist('tag')
        # 先生成一个该模块的对象
        soup = BeautifulSoup(content, 'html.parser')
        for tag in soup.find_all():
            # 筛选出script标签直接删除
            if tag.name == 'script':
                tag.decompose()  # 删除该标签
        desc = soup.text[0:150]
        # 写入数据
        article_obj = models.Article.objects.create(title=title, desc=desc, content=str(soup), category_id=category_id, blog=request.user.blog)
        print(article_obj)
        # 手动操作文章与标签的第三张表
        b_list = []
        for tag_id in tag_list:
            b_list.append(models.Article2Tag(article=article_obj, tag_id=tag_id))
        models.Article2Tag.objects.bulk_create(b_list)
        return redirect(reverse('_backend'))
    categoty_list = models.Category.objects.filter(blog=request.user.blog)
    tag_list = models.Tag.objects.filter(blog=request.user.blog)


    return render(request, 'backend/add_article.html', locals())


import os
from day60 import settings
@login_required
def upload_image(request):
    back_dic = {'error': 0}
    if request.method == "POST":
        file_obj = request.FILES.get('imgFile')
        file_dir = os.path.join(settings.BASE_DIR, 'media', 'article_image')
        if not os.path.isdir(file_dir):
            os.mkdir(file_dir)
        file_path = os.path.join(file_dir, file_obj.name)
        with open(file_path, 'wb') as f:
            for chunk in file_obj.chunks():
                f.write(chunk)
        # // 成功时
        # {
        #     "error": 0,
        #     "url": "http://www.example.com/path/to/file.ext"
        # }
        # // 失败时
        # {
        #     "error": 1,
        #     "message": "错误信息"
        # }
        back_dic['url'] = f'/media/article_image/{file_obj.name}'
        return JsonResponse(back_dic)


def set_avatar(request):
    if request.method == 'POST':
        avatar_obj = request.FILES.get('myfile')
        # models.UserInfo.objects.filter(pk=request.user.pk).update(avatar=avatar_obj)
        request.user.avatar = avatar_obj
        request.user.save()
    return render(request, 'set_avatar.html', locals())