from django.urls import path
from . import views

app_name = 'recommendation'

urlpatterns = [
    path('feed/', views.get_recommendations, name='feed'),
    path('similar/<int:news_id>/', views.similar_news, name='similar'),
    path('trending/', views.trending_news, name='trending'),
    path('analytics/', views.analytics_dashboard, name='analytics'),
    # Remove debug URL if not needed
    # path('debug/', views.debug_recommendations, name='debug'),
]