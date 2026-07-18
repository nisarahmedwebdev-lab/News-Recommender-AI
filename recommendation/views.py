from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Count
from news.models import News, Category, Like, Bookmark, UserBehavior
from .ai_engine.simple_recommender import SimpleRecommender
import logging
from collections import Counter

logger = logging.getLogger(__name__)

# Initialize recommender
recommender = SimpleRecommender()

@login_required
def get_recommendations(request):
    """Get personalized recommendations for the user"""
    print("=" * 80)
    print("🤖 AI FEED - Personalized Recommendations")
    print(f"👤 User: {request.user.username}")
    print(f"📌 Interests from profile: {request.user.interests}")
    print("=" * 80)
    
    try:
        # Load model
        from django.conf import settings
        import os
        model_path = settings.AI_MODEL_PATH / 'recommendation.pkl'
        
        # Load or create model
        if not os.path.exists(model_path):
            print("📊 Model not found, creating new...")
            recommender.load_news_data()
            recommender.build_tfidf_matrix()
            recommender.build_category_vectors()
            recommender.save_model(model_path)
        else:
            print("📂 Loading existing model...")
            recommender.load_model(model_path)
        
        # Check for new news
        if hasattr(recommender, 'last_trained') and recommender.last_trained:
            new_news_count = News.objects.filter(
                created_at__gt=recommender.last_trained
            ).count()
            if new_news_count > 0:
                print(f"📊 {new_news_count} new articles found, reloading data...")
                recommender.load_news_data()
                recommender.build_tfidf_matrix()
                recommender.build_category_vectors()
                recommender.save_model(model_path)
        
        # Get user interactions
        likes = Like.objects.filter(user=request.user).count()
        saves = Bookmark.objects.filter(user=request.user).count()
        
        print(f"❤️ User likes: {likes}")
        print(f"📌 User saves: {saves}")
        
        # Get recommendations
        recommended_ids = recommender.get_recommendations(
            request.user,
            n_recommendations=20
        )
        
        print(f"\n📊 Recommended IDs: {recommended_ids[:10]}...")
        
        # Fetch news objects
        recommended_news = News.objects.filter(id__in=recommended_ids)
        
        # Maintain order
        news_dict = {news.id: news for news in recommended_news}
        ordered_news = []
        for id in recommended_ids:
            if id in news_dict:
                ordered_news.append(news_dict[id])
        
        print(f"\n📰 Found {len(ordered_news)} news articles")
        
        # Get category distribution
        if ordered_news:
            categories = [news.category.name for news in ordered_news]
            category_dist = Counter(categories)
            print(f"📊 Category Distribution:")
            for cat, count in category_dist.most_common():
                print(f"   - {cat}: {count}")
        
        # Pagination
        paginator = Paginator(ordered_news, 10)
        page = request.GET.get('page', 1)
        news_page = paginator.get_page(page)
        
        return render(request, 'recommendation/feed.html', {
            'news': news_page,
            'is_personalized': True,
            'total_recommendations': len(ordered_news),
            'user_interest': request.user.interests,
        })
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Fallback to latest news
        latest_news = News.objects.order_by('-published_date')[:20]
        paginator = Paginator(latest_news, 10)
        page = request.GET.get('page', 1)
        news_page = paginator.get_page(page)
        
        return render(request, 'recommendation/feed.html', {
            'news': news_page,
            'is_personalized': False,
            'error': 'Could not generate recommendations'
        })

@login_required
def similar_news(request, news_id):
    """Get similar news articles"""
    try:
        original_news = get_object_or_404(News, id=news_id)
        similar = News.objects.filter(
            category=original_news.category
        ).exclude(id=news_id)[:10]
        
        return render(request, 'recommendation/similar.html', {
            'news': similar,
            'original_news': original_news,
            'original_news_id': news_id
        })
    except News.DoesNotExist:
        return render(request, 'recommendation/similar.html', {
            'news': [],
            'original_news_id': news_id,
            'error': 'News not found'
        })

@login_required
def trending_news(request):
    """Get trending news articles"""
    trending = News.objects.order_by('-views', '-likes_count', '-saves_count')[:20]
    paginator = Paginator(trending, 10)
    page = request.GET.get('page', 1)
    news_page = paginator.get_page(page)
    
    return render(request, 'recommendation/trending.html', {
        'news': news_page
    })

@login_required
def analytics_dashboard(request):
    """Show recommendation analytics for the user"""
    behaviors = UserBehavior.objects.filter(user=request.user)
    
    stats = {
        'total_views': behaviors.filter(behavior_type='VIEW').count(),
        'total_likes': behaviors.filter(behavior_type='LIKE').count(),
        'total_saves': behaviors.filter(behavior_type='SAVE').count(),
        'total_searches': behaviors.filter(behavior_type='SEARCH').count(),
    }
    
    liked_news = Like.objects.filter(user=request.user).values_list('news_id', flat=True)
    category_preferences = News.objects.filter(
        id__in=liked_news
    ).values('category__name').annotate(
        count=Count('category')
    ).order_by('-count')
    
    reading_history = behaviors.filter(
        behavior_type='VIEW'
    ).select_related('news').order_by('-timestamp')[:20]
    
    context = {
        'stats': stats,
        'category_preferences': category_preferences,
        'reading_history': reading_history,
        'user_interests': request.user.interests,
    }
    
    return render(request, 'recommendation/analytics.html', context)

# Optional: Debug view (if needed)
@login_required
def debug_recommendations(request):
    """Debug view to check recommendation status"""
    print("=" * 80)
    print("🐛 DEBUG RECOMMENDATIONS")
    print("=" * 80)
    
    try:
        # Get all news
        total_news = News.objects.count()
        latest_news = News.objects.order_by('-published_date')[:10]
        
        # Get user interactions
        likes = Like.objects.filter(user=request.user).count()
        saves = Bookmark.objects.filter(user=request.user).count()
        views = UserBehavior.objects.filter(user=request.user, behavior_type='VIEW').count()
        
        # Get category preferences
        liked_news = Like.objects.filter(user=request.user).values_list('news_id', flat=True)
        category_prefs = News.objects.filter(id__in=liked_news).values('category__name').annotate(
            count=Count('category')
        ).order_by('-count')
        
        # Get model status
        from django.conf import settings
        import os
        model_path = settings.AI_MODEL_PATH / 'recommendation.pkl'
        model_exists = os.path.exists(model_path)
        
        # Get recommendations
        recommender.load_news_data()
        recommended_ids = recommender.get_recommendations(
            request.user, 
            n_recommendations=10
        )
        
        print(f"📊 Total news: {total_news}")
        print(f"📂 Model exists: {model_exists}")
        print(f"❤️ Likes: {likes}")
        print(f"📌 Saves: {saves}")
        print(f"👁️ Views: {views}")
        print(f"🤖 Recommendations: {len(recommended_ids)}")
        
        return render(request, 'recommendation/debug.html', {
            'total_news': total_news,
            'latest_news': latest_news,
            'likes': likes,
            'saves': saves,
            'views': views,
            'category_prefs': category_prefs,
            'model_exists': model_exists,
            'recommended_ids': recommended_ids,
            'recommended_news': News.objects.filter(id__in=recommended_ids)[:10]
        })
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)