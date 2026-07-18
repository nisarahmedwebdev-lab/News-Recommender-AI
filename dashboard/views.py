from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from news.models import News, Category, Like, Bookmark, UserBehavior
from recommendation.ai_engine.simple_recommender import SimpleRecommender
import logging

logger = logging.getLogger(__name__)

@login_required
def home(request):
    """Main dashboard view - Shows all news in full width"""
    
    print("=" * 60)
    print("📊 DASHBOARD VIEW CALLED")
    print(f"👤 User: {request.user.username}")
    print("=" * 60)
    
    # Get all news ordered by latest
    news_list = News.objects.all().order_by('-published_date')
    
    print(f"📰 Total news in database: {news_list.count()}")
    
    # Show first 5 news titles
    print("📰 Latest 5 news:")
    for news in news_list[:5]:
        print(f"   - {news.title[:50]}... ({news.published_date.strftime('%Y-%m-%d %H:%M')})")
    
    # Pagination - 10 news per page
    paginator = Paginator(news_list, 10)
    page = request.GET.get('page', 1)
    news = paginator.get_page(page)
    
    print(f"📄 Page {page} has {len(news)} items")
    
    # Get categories for filter
    categories = Category.objects.all()
    
    # Get user stats
    user_stats = {
        'total_likes': Like.objects.filter(user=request.user).count(),
        'total_bookmarks': Bookmark.objects.filter(user=request.user).count(),
        'total_views': UserBehavior.objects.filter(user=request.user, behavior_type='VIEW').count(),
    }
    
    # Get liked and saved news for the user
    liked_news = Like.objects.filter(user=request.user).values_list('news_id', flat=True)
    saved_news = Bookmark.objects.filter(user=request.user).values_list('news_id', flat=True)
    
    # Get related news suggestions
    related_news = []
    try:
        if news and len(news) > 0:
            first_article = news[0]
            recommender = SimpleRecommender()
            related_news = recommender.get_related_news(first_article, n_recommendations=6)
    except Exception as e:
        logger.warning(f"Could not fetch related news: {e}")
        # Fallback to recent articles from same category
        if news and len(news) > 0:
            related_news = News.objects.filter(
                category=news[0].category
            ).exclude(id=news[0].id).order_by('-published_date')[:6]
    
    print(f"❤️ User likes: {user_stats['total_likes']}")
    print(f"📌 User bookmarks: {user_stats['total_bookmarks']}")
    print("=" * 60)
    
    context = {
        'news': news,
        'categories': categories,
        'user_stats': user_stats,
        'liked_news': liked_news,
        'saved_news': saved_news,
        'related_news': related_news,
        'is_dashboard': True,
    }
    
    return render(request, 'dashboard/home.html', context)