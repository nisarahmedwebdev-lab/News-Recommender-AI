from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.text import slugify
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class News(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    content = models.TextField()
    image = models.ImageField(upload_to='news/', blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='news')
    author = models.CharField(max_length=100)
    author_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='news_posts', null=True, blank=True)
    source = models.CharField(max_length=200, blank=True)
    source_url = models.URLField(blank=True)
    published_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Engagement metrics
    views = models.IntegerField(default=0)
    likes_count = models.IntegerField(default=0)
    saves_count = models.IntegerField(default=0)
    comments_count = models.IntegerField(default=0)
    
    class Meta:
        verbose_name_plural = 'News'
        ordering = ['-published_date']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('news:detail', kwargs={'slug': self.slug})
    
    def get_image_url(self):
        """Get image URL from either image field or image_url"""
        if self.image_url and self.image_url.startswith('http'):
            return self.image_url
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        return None            
    def get_reading_time(self):
        """Calculate reading time in minutes"""
        # Average reading speed: 200 words per minute
        word_count = len(self.content.split())
        minutes = max(1, round(word_count / 200))
        return minutes
    
    def is_owner(self, user):
        """Check if the given user is the owner of this news post"""
        if not user.is_authenticated:
            return False
        if self.author_user:
            return self.author_user == user
        return False

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'news']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} likes {self.news.title[:30]}"

class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')
    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name='bookmarks')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'news']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} saved {self.news.title[:30]}"

class Comment(models.Model):
    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.news.title[:30]}"
    
    def is_owner(self, user):
        """Check if the given user is the owner of this comment"""
        if not user.is_authenticated:
            return False
        return self.user == user or user.is_superuser

class UserBehavior(models.Model):
    BEHAVIOR_TYPES = [
        ('VIEW', 'View'),
        ('LIKE', 'Like'),
        ('SAVE', 'Save'),
        ('SEARCH', 'Search'),
        ('CLICK', 'Click'),
        ('READ', 'Read'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='behaviors')
    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name='behaviors', null=True, blank=True)
    behavior_type = models.CharField(max_length=10, choices=BEHAVIOR_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    duration = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.user.username} - {self.behavior_type}"

# ========== SIGNALS FOR UPDATES ==========

@receiver(post_save, sender=Like)
def like_post_save(sender, instance, created, **kwargs):
    """Update news likes count and create behavior record"""
    try:
        news = instance.news
        
        if created:
            # Update news likes count
            news.likes_count = Like.objects.filter(news=news).count()
            news.save(update_fields=['likes_count', 'updated_at'])
            
            # Create behavior record if not exists
            UserBehavior.objects.get_or_create(
                user=instance.user,
                news=news,
                behavior_type='LIKE',
                defaults={'timestamp': timezone.now()}
            )
            
            logger.info(f"Signal: User {instance.user.username} liked news {news.id}")
                
    except Exception as e:
        logger.error(f"Error in like_post_save signal: {e}")

@receiver(post_delete, sender=Like)
def like_post_delete(sender, instance, **kwargs):
    """Update news likes count when like is removed"""
    try:
        news = instance.news
        
        # Update news likes count
        news.likes_count = Like.objects.filter(news=news).count()
        news.save(update_fields=['likes_count', 'updated_at'])
        
        # Remove behavior record
        UserBehavior.objects.filter(
            user=instance.user,
            news=news,
            behavior_type='LIKE'
        ).delete()
        
        logger.info(f"Signal: User {instance.user.username} unliked news {news.id}")
            
    except Exception as e:
        logger.error(f"Error in like_post_delete signal: {e}")

@receiver(post_save, sender=Bookmark)
def bookmark_post_save(sender, instance, created, **kwargs):
    """Update news saves count and create behavior record"""
    try:
        news = instance.news
        
        if created:
            # Update news saves count
            news.saves_count = Bookmark.objects.filter(news=news).count()
            news.save(update_fields=['saves_count', 'updated_at'])
            
            # Create behavior record if not exists
            UserBehavior.objects.get_or_create(
                user=instance.user,
                news=news,
                behavior_type='SAVE',
                defaults={'timestamp': timezone.now()}
            )
            
            logger.info(f"Signal: User {instance.user.username} saved news {news.id}")
                
    except Exception as e:
        logger.error(f"Error in bookmark_post_save signal: {e}")

@receiver(post_delete, sender=Bookmark)
def bookmark_post_delete(sender, instance, **kwargs):
    """Update news saves count when bookmark is removed"""
    try:
        news = instance.news
        
        # Update news saves count
        news.saves_count = Bookmark.objects.filter(news=news).count()
        news.save(update_fields=['saves_count', 'updated_at'])
        
        # Remove behavior record
        UserBehavior.objects.filter(
            user=instance.user,
            news=news,
            behavior_type='SAVE'
        ).delete()
        
        logger.info(f"Signal: User {instance.user.username} unsaved news {news.id}")
            
    except Exception as e:
        logger.error(f"Error in bookmark_post_delete signal: {e}")

@receiver(post_save, sender=Comment)
def comment_post_save(sender, instance, created, **kwargs):
    """Update news comments count when comment is added"""
    try:
        news = instance.news
        if created:
            news.comments_count = Comment.objects.filter(news=news, is_approved=True).count()
            news.save(update_fields=['comments_count', 'updated_at'])
            logger.info(f"Signal: Comment added to news {news.id}")
    except Exception as e:
        logger.error(f"Error in comment_post_save signal: {e}")

@receiver(post_delete, sender=Comment)
def comment_post_delete(sender, instance, **kwargs):
    """Update news comments count when comment is deleted"""
    try:
        news = instance.news
        news.comments_count = Comment.objects.filter(news=news, is_approved=True).count()
        news.save(update_fields=['comments_count', 'updated_at'])
        logger.info(f"Signal: Comment deleted from news {news.id}")
    except Exception as e:
        logger.error(f"Error in comment_post_delete signal: {e}")

@receiver(post_save, sender=News)
def news_post_save(sender, instance, created, **kwargs):
    """Retrain model when new news is added"""
    if created:
        logger.info(f"New news added: {instance.title}, triggering model retraining...")
        try:
            # Import here to avoid circular import
            from recommendation.ai_engine.simple_recommender import SimpleRecommender
            import threading
            
            def retrain_in_background():
                try:
                    recommender = SimpleRecommender()
                    recommender.load_news_data()
                    logger.info("Recommender data reloaded successfully after new news")
                except Exception as e:
                    logger.error(f"Error reloading recommender data: {e}")
            
            # Retrain in background thread
            thread = threading.Thread(target=retrain_in_background)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            logger.error(f"Error triggering retraining: {e}")