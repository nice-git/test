from django.template import Library
from app01 import models
from django.db.models.functions import TruncMonth
from django.db.models import Count
from django.shortcuts import render




register = Library()  # 注意变量名必须为register,不可改变

@register.inclusion_tag('left_menu.html', name='my_left')
def index(username):
    username_obj = models.UserInfo.objects.filter(username=username).first()
    blog = username_obj.blog
    article_list = models.Article.objects.filter(blog=blog)
    # 查看当前用户的分类及每个分类下的文章数
    category_list = models.Category.objects.filter(blog=blog).annotate(c=Count('article')).values('c', 'name', 'pk')
    # 查询当前用户的标签及每个标签下的文章数
    tag_list = models.Tag.objects.filter(blog=blog).annotate(c=Count('article')).values('c', 'name', 'pk')
    date_list = models.Article.objects.filter(blog=blog).annotate(month=TruncMonth('create_time')).values(
        'month').annotate(c=Count('pk')).values('c', 'month')
    return locals()
