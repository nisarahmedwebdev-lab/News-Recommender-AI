from django.urls import path
from . import views

app_name = 'news'

urlpatterns = [
    # Public views
    path('', views.news_list, name='list'),
    path('search/', views.search_news, name='search'),
    path('saved/', views.saved_news, name='saved'),
    path('category/', views.category_list, name='categories'),
    
    # Like and Save - AJAX endpoints
    path('like/<int:news_id>/', views.like_news, name='like'),
    path('save/<int:news_id>/', views.save_news, name='save'),
    path('status/<int:news_id>/', views.get_like_status, name='status'),
    
    # Comment Management
    path('comment/delete/<int:comment_id>/', views.delete_comment, name='delete_comment'),
    
    # News Management (with permission checks)
    path('add/', views.add_news, name='add'),
    path('edit/<slug:slug>/', views.edit_news, name='edit'),
    path('delete/<slug:slug>/', views.delete_news, name='delete'),
    
    # Category Management (Admin only)
    path('categories/manage/', views.manage_categories, name='manage_categories'),
    path('categories/edit/<int:category_id>/', views.edit_category, name='edit_category'),
    path('categories/delete/<int:category_id>/', views.delete_category, name='delete_category'),
    
    # News Detail (LAST)
    path('<slug:slug>/', views.news_detail, name='detail'),
]