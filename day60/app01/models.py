from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
# 用户表继承auth模块里面的auth_user


class UserInfo(AbstractUser):
    phone = models.BigIntegerField(null=True,blank=True)  # blank告诉后台管理该字段可以为空
    # 用户头像  该字段接收到用户头像文件会自动存放到avatar文件夹下 用户没有传则全部使用默认头像
    avatar = models.FileField(upload_to='avatar/',default='avatar/default.png')
    create_time = models.DateField(auto_now_add=True)

    blog = models.OneToOneField(to='Blog',null=True)  # 防止我们录入数据报错


    class Meta:
        verbose_name_plural = '用户表'

    def __str__(self):
        return self.username

class Blog(models.Model):
    site_name = models.CharField(max_length=32)
    site_title = models.CharField(max_length=64)
    # 该字段用来模拟 每个人都可以有每个人个人站点样式
    site_theme = models.CharField(max_length=64)
    class Meta:
        verbose_name_plural = 'Blog站点表'
    def __str__(self):
        return self.site_name

class Category(models.Model):
    name = models.CharField(max_length=32)

    blog = models.ForeignKey(to='Blog',null=True)
    class Meta:
        verbose_name_plural = 'Category分类表'
    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=32)
    blog = models.ForeignKey(to='Blog',null=True)
    class Meta:
        verbose_name_plural = 'Tag标签表'

    def __str__(self):
        return self.name

class Article(models.Model):
    title = models.CharField(max_length=64)
    desc = models.CharField(max_length=254)
    content = models.TextField()  # 存大段文本
    create_time = models.DateField(auto_now_add=True)

    # 一对多分类表
    category = models.ForeignKey(to='Category',null=True)
    # 多对多标签表
    tags = models.ManyToManyField(to='Tag',through='Article2Tag',through_fields=('article','tag'))
    # 一对多个人站点
    blog = models.ForeignKey(to='Blog',null=True)

    # 数据库优化设计  面试可以说的点
    comment_num = models.BigIntegerField(null=True,default=0)
    up_num = models.BigIntegerField(null=True,default=0)
    down_num = models.BigIntegerField(null=True,default=0)
    class Meta:
        verbose_name_plural = 'Article文章表'
    def __str__(self):
        return self.title

class Article2Tag(models.Model):
    article = models.ForeignKey(to='Article')
    tag = models.ForeignKey(to='Tag')
    class Meta:
        verbose_name_plural = 'Article2Tag文章标签表'

class UpAndDown(models.Model):
    user = models.ForeignKey(to='UserInfo')
    article = models.ForeignKey(to='Article')
    is_up = models.BooleanField()  # 传布尔值 存0/1
    class Meta:
        verbose_name_plural = '点赞点踩表'

class Comment(models.Model):
    user = models.ForeignKey(to='UserInfo')
    article = models.ForeignKey(to='Article')
    content = models.CharField(max_length=254)
    comment_time = models.DateField(auto_now_add=True)
    # 自关联字段   根评论与子评论
    parent = models.ForeignKey(to='self',null=True)  # 该字段存的是父评论的主键值
    # 如果有值 说明当前评论是子评论  如果没有值 说明当前评论是根评论
    class Meta:
        verbose_name_plural = 'Comment评论表'


