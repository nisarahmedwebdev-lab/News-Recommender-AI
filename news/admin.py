from django.contrib import admin
from django.utils.html import format_html
from .models import Category, News, Comment, Like, Bookmark, UserBehavior

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'author', 'author_user', 'published_date', 'views', 'likes_count']
    list_filter = ['category', 'published_date', 'author']
    search_fields = ['title', 'description', 'content']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['views', 'likes_count', 'saves_count', 'comments_count', 'created_at', 'updated_at']
    
    def save_model(self, request, obj, form, change):
        if not obj.author_user:
            obj.author_user = request.user
            obj.author = request.user.get_full_name() or request.user.username
        super().save_model(request, obj, form, change)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'news', 'content_preview', 'created_at', 'is_approved']
    list_filter = ['is_approved', 'created_at']
    search_fields = ['user__username', 'content']
    actions = ['approve_comments', 'reject_comments']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Comment'
    
    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)
    approve_comments.short_description = 'Approve selected comments'
    
    def reject_comments(self, request, queryset):
        queryset.update(is_approved=False)
    reject_comments.short_description = 'Reject selected comments'

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'news', 'created_at']
    list_filter = ['created_at']

@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ['user', 'news', 'created_at']
    list_filter = ['created_at']

@admin.register(UserBehavior)
class UserBehaviorAdmin(admin.ModelAdmin):
    list_display = ['user', 'news', 'behavior_type', 'timestamp']
    list_filter = ['behavior_type', 'timestamp']