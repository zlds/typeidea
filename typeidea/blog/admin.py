from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.shortcuts import reverse
from django.utils.html import format_html
from .adminforms import PostAdmin
from .custom_site import custom_site


import sys
sys.path.append("..")

from .models import Category, Tag, Post
from comment.models import Comment
from config.models import Link, SideBar
from .base_admin import BaseOwnerAdmin
# Register your models here.






class CategoryOwnerFilter(admin.SimpleListFilter):
    '''自定义过滤器只展示当前用户分类'''

    title = '分类过滤器'
    parameter_name = 'owner_category'

    def lookups(self, request, model_admin):
        return Category.objects.filter(owner=request.user).values_list('id', 'name')

    def queryset(self, request, queryset):
        category_id = self.value()
        if category_id:
            return queryset.filter(category_id=self.value())
        return queryset


@admin.register(Category, site=custom_site)
class CategoryAdmin(admin.ModelAdmin):
    #list_display 展示字段
    list_display = ('name', 'status', 'is_nav', 'created_time', 'post_count')
    #编辑页面字段
    fields = ('name', 'status', 'is_nav')

    def post_count(self, obj):
        return obj.post_set.count()
    post_count.short_description = "文章数量"

@admin.register(Tag, site=custom_site)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'created_time', 'owner')
    fields = ('name', 'status')

@admin.register(Post, site=custom_site)
class PostAdmin(admin.ModelAdmin):
    form = PostAdmin
    list_display = [
        'title', 'category', 'status',
        'created_time', 'owner', 'operator'
    ]
    list_filter = [CategoryOwnerFilter]
    list_display_links = []
    #可以通过那些字段可以搜索
    search_fields = ['title', 'category__name']

    actions_on_top = True
    actions_on_bottom = False
    #编辑页面
    # fields = (
    #     'category',
    #     'title',
    #     'desc',
    #     'status',
    #     'content',
    #     'tag',
    # )
    filter_horizontal = ('tag',)
    fieldsets = (
        ('基础配置', {'description': '基础配置描述',
                  'fields': (
                      ('title', 'category'),
                      'status',
                  ),}
         ),
        ('内容', {
            'fields': (
                'desc',
                'content',
            ),
        }),
        ('额外信息', {
            'classes': ('collapse', ),
            'fields': ('tag', ),
        })
    )

    def operator(self, obj):
        print('obj= %s' % obj)
        return format_html(
            '<a herf="{}">编辑</a>',
            reverse('cus_admin:blog_post_change', args=(obj.id,))
        )
    operator.short_description = '操作'

    def get_queryset(self, request):
        qs = super(PostAdmin, self).get_queryset(request)
        return qs.filter(owner=request.user)

    class Media:
        css = {
            'all': ('https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css',),
        }
        js = ('https://cdn.bootcss.com/bootstrap/4.0.0-beta.2/js/bootstrap.bundle.js',)

@admin.register(Comment, site=custom_site)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('target', 'nickname', 'content', 'website', 'created_time')

@admin.register(Link, site=custom_site)
class LinkAdmin(admin.ModelAdmin):
    list_display = ('title', 'href', 'status', 'weight', 'created_time')
    fields = ('title', 'href', 'status', 'weight')

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        return super(Link, self).save_model(request, obj, form, change)

@admin.register(SideBar, site=custom_site)
class SideBarAdmin(admin.ModelAdmin):
    list_display = ('title', 'display_type', 'content', 'created_time')
    fields = ('title', 'display_type', 'content')

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        return super(SideBar, self).save_model(request, obj, form, change)

@admin.register(LogEntry, site=custom_site)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ['object_repr', 'object_id', 'action_flag', 'user',
                    'change_message']