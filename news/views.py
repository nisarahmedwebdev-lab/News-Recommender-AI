from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import News, Category, Like, Bookmark, UserBehavior, Comment
from .forms import NewsForm, CommentForm, CategoryForm
import json
import logging
import traceback

logger = logging.getLogger(__name__)

# ========== NEWS LIST VIEWS ==========

@login_required
def news_list(request):
    category = request.GET.get('category')
    search = request.GET.get('search')
    
    news_queryset = News.objects.all()
    
    if category:
        news_queryset = news_queryset.filter(category__id=category)
    
    if search:
        news_queryset = news_queryset.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search) |
            Q(content__icontains=search)
        )
    
    categories = Category.objects.all()
    
    paginator = Paginator(news_queryset, 12)
    page = request.GET.get('page')
    news = paginator.get_page(page)
    
    liked_news = Like.objects.filter(user=request.user).values_list('news_id', flat=True)
    saved_news = Bookmark.objects.filter(user=request.user).values_list('news_id', flat=True)
    
    context = {
        'news': news,
        'categories': categories,
        'selected_category': category,
        'search_query': search,
        'liked_news': liked_news,
        'saved_news': saved_news,
    }
    return render(request, 'news/list.html', context)

@login_required
def news_detail(request, slug):
    """View news detail by slug"""
    if slug == 'add':
        return redirect('news:add')
    
    news = get_object_or_404(News, slug=slug)
    
    # Record view behavior
    UserBehavior.objects.create(
        user=request.user,
        news=news,
        behavior_type='VIEW'
    )
    
    news.views += 1
    news.save()
    
    comments = news.comments.filter(is_approved=True)
    
    if request.method == 'POST' and 'comment_submit' in request.POST:
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.news = news
            comment.user = request.user
            comment.save()
            news.comments_count += 1
            news.save()
            messages.success(request, 'Your comment has been added!')
            return redirect('news:detail', slug=news.slug)
    else:
        form = CommentForm()
    
    # Get related news using improved recommendation
    try:
        from recommendation.ai_engine.simple_recommender import SimpleRecommender
        recommender = SimpleRecommender()
        related_news_ids = recommender.get_related_news(news, n_recommendations=4)
        related_news = News.objects.filter(id__in=related_news_ids)
        
        # Maintain order from recommender
        news_dict = {news_obj.id: news_obj for news_obj in related_news}
        related_news = [news_dict[id] for id in related_news_ids if id in news_dict]
    except Exception as e:
        print(f"⚠️ Could not get recommended related news: {e}")
        # Fallback to category-based
        related_news = News.objects.filter(
            category=news.category
        ).exclude(id=news.id).order_by('-published_date')[:4]
    
    is_liked = Like.objects.filter(user=request.user, news=news).exists()
    is_bookmarked = Bookmark.objects.filter(user=request.user, news=news).exists()
    
    # Permission checks
    is_owner = news.is_owner(request.user)
    can_edit = is_owner or request.user.is_superuser or request.user.is_staff
    
    context = {
        'news': news,
        'related_news': related_news,
        'comments': comments,
        'form': form,
        'is_liked': is_liked,
        'is_bookmarked': is_bookmarked,
        'is_owner': is_owner,
        'can_edit': can_edit,
    }
    return render(request, 'news/detail.html', context)

@login_required
def search_news(request):
    query = request.GET.get('q', '')
    news_list = []
    
    if query:
        news_list = News.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(content__icontains=query) |
            Q(category__name__icontains=query)
        ).distinct()
        
        if request.user.is_authenticated and news_list.exists():
            for news in news_list[:5]:
                UserBehavior.objects.create(
                    user=request.user,
                    news=news,
                    behavior_type='SEARCH'
                )
    
    paginator = Paginator(news_list, 12)
    page = request.GET.get('page')
    news = paginator.get_page(page)
    
    return render(request, 'news/search.html', {
        'query': query,
        'news': news
    })

@login_required
def saved_news(request):
    bookmarks = Bookmark.objects.filter(user=request.user).select_related('news')
    paginator = Paginator(bookmarks, 12)
    page = request.GET.get('page')
    saved_news = paginator.get_page(page)
    return render(request, 'news/saved.html', {'saved_news': saved_news})

@login_required
def category_list(request):
    categories = Category.objects.annotate(
        news_count=Count('news')
    ).filter(news_count__gt=0)
    return render(request, 'news/categories.html', {'categories': categories})

# ========== LIKE AND SAVE VIEWS (FIXED) ==========

@login_required
def like_news(request, news_id):
    """Toggle like for a news article"""
    try:
        news = get_object_or_404(News, id=news_id)
        
        # Check if already liked
        like = Like.objects.filter(user=request.user, news=news).first()
        
        if like:
            # Unlike
            like.delete()
            liked = False
            message = "Unliked!"
        else:
            # Like
            Like.objects.create(user=request.user, news=news)
            liked = True
            message = "Liked!"
            
            # Record behavior
            UserBehavior.objects.create(
                user=request.user,
                news=news,
                behavior_type='LIKE'
            )
        
        # Get updated count
        likes_count = Like.objects.filter(news=news).count()
        news.likes_count = likes_count
        news.save(update_fields=['likes_count'])
        
        return JsonResponse({
            'success': True,
            'liked': liked,
            'likes_count': likes_count,
            'news_id': news.id,
            'message': message
        })
        
    except Exception as e:
        print(f"LIKE ERROR: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'message': 'Failed to process like'
        }, status=500)

@login_required
def save_news(request, news_id):
    """Toggle save/bookmark for a news article"""
    try:
        news = get_object_or_404(News, id=news_id)
        
        # Check if already saved
        bookmark = Bookmark.objects.filter(user=request.user, news=news).first()
        
        if bookmark:
            # Unsave
            bookmark.delete()
            saved = False
            message = "Unsaved!"
        else:
            # Save
            Bookmark.objects.create(user=request.user, news=news)
            saved = True
            message = "Saved!"
            
            # Record behavior
            UserBehavior.objects.create(
                user=request.user,
                news=news,
                behavior_type='SAVE'
            )
        
        # Get updated count
        saves_count = Bookmark.objects.filter(news=news).count()
        news.saves_count = saves_count
        news.save(update_fields=['saves_count'])
        
        return JsonResponse({
            'success': True,
            'saved': saved,
            'saves_count': saves_count,
            'news_id': news.id,
            'message': message
        })
        
    except Exception as e:
        print(f"SAVE ERROR: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'message': 'Failed to process save'
        }, status=500)

@login_required
def get_like_status(request, news_id):
    """Get like status for a news article"""
    try:
        news = get_object_or_404(News, id=news_id)
        
        is_liked = Like.objects.filter(user=request.user, news=news).exists()
        is_saved = Bookmark.objects.filter(user=request.user, news=news).exists()
        
        return JsonResponse({
            'success': True,
            'is_liked': is_liked,
            'is_saved': is_saved,
            'likes_count': news.likes_count,
            'saves_count': news.saves_count
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

# ========== NEWS MANAGEMENT VIEWS ==========

@login_required
def add_news(request):
    """Add new news article - Only staff/superuser can add"""
    if not request.user.is_superuser and not request.user.is_staff:
        messages.error(request, 'You do not have permission to add news.')
        return redirect('dashboard:home')
    
    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES)
        if form.is_valid():
            news = form.save(user=request.user, commit=False)
            if not news.published_date:
                news.published_date = timezone.now()
            news.save()
            messages.success(request, f'News "{news.title}" added successfully!')
            return redirect('news:detail', slug=news.slug)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = NewsForm()
    
    categories = Category.objects.all()
    context = {
        'form': form,
        'categories': categories,
        'is_editing': False,
    }
    return render(request, 'news/add_news.html', context)

@login_required
def edit_news(request, slug):
    """Edit existing news article"""
    news = get_object_or_404(News, slug=slug)
    
    if not news.is_owner(request.user) and not request.user.is_superuser and not request.user.is_staff:
        messages.error(request, 'You do not have permission to edit this news.')
        return redirect('news:detail', slug=news.slug)
    
    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES, instance=news)
        if form.is_valid():
            form.save()
            messages.success(request, f'News "{news.title}" updated successfully!')
            return redirect('news:detail', slug=news.slug)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = NewsForm(instance=news)
    
    categories = Category.objects.all()
    context = {
        'form': form,
        'categories': categories,
        'news': news,
        'is_editing': True,
    }
    return render(request, 'news/add_news.html', context)

@login_required
def delete_news(request, slug):
    """Delete news article"""
    news = get_object_or_404(News, slug=slug)
    
    if not news.is_owner(request.user) and not request.user.is_superuser and not request.user.is_staff:
        messages.error(request, 'You do not have permission to delete this news.')
        return redirect('news:detail', slug=news.slug)
    
    if request.method == 'POST':
        title = news.title
        news.delete()
        messages.success(request, f'News "{title}" deleted successfully!')
        return redirect('news:list')
    
    context = {
        'news': news,
    }
    return render(request, 'news/delete_news.html', context)

# ========== COMMENT MANAGEMENT VIEWS ==========

@login_required
def delete_comment(request, comment_id):
    """Delete comment - Only owner or admin can delete"""
    comment = get_object_or_404(Comment, id=comment_id)
    news_slug = comment.news.slug
    
    if not comment.is_owner(request.user) and not request.user.is_superuser:
        messages.error(request, 'You do not have permission to delete this comment.')
        return redirect('news:detail', slug=news_slug)
    
    if request.method == 'POST':
        comment.delete()
        comment.news.comments_count = max(0, comment.news.comments_count - 1)
        comment.news.save()
        messages.success(request, 'Comment deleted successfully!')
    
    return redirect('news:detail', slug=news_slug)

# ========== CATEGORY MANAGEMENT VIEWS (Admin Only) ==========

@staff_member_required
def manage_categories(request):
    categories = Category.objects.all().annotate(
        news_count=Count('news')
    ).order_by('-news_count')
    
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Category "{category.name}" created successfully!')
            return redirect('news:manage_categories')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CategoryForm()
    
    context = {
        'categories': categories,
        'form': form,
    }
    return render(request, 'news/manage_categories.html', context)

@staff_member_required
def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, f'Category "{category.name}" updated successfully!')
            return redirect('news:manage_categories')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CategoryForm(instance=category)
    
    context = {
        'form': form,
        'category': category,
        'is_editing': True,
    }
    return render(request, 'news/manage_categories.html', context)

@staff_member_required
def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        name = category.name
        category.delete()
        messages.success(request, f'Category "{name}" deleted successfully!')
        return redirect('news:manage_categories')
    
    context = {
        'category': category,
    }
    return render(request, 'news/delete_category.html', context)