from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from news.models import News, UserBehavior, Like, Bookmark
from django.conf import settings
import threading
import os

def retrain_model_async():
    """Retrain model in background thread"""
    try:
        from .ai_engine.recommender import NewsRecommender
        recommender = NewsRecommender()
        recommender.retrain_model()
        print("Model retrained successfully")
    except Exception as e:
        print(f"Error retraining model: {e}")

@receiver(post_save, sender=News)
def news_post_save(sender, instance, created, **kwargs):
    """Retrain model when new news is added"""
    if created:
        # Retrain in background
        thread = threading.Thread(target=retrain_model_async)
        thread.daemon = True
        thread.start()

@receiver(post_save, sender=UserBehavior)
def behavior_post_save(sender, instance, created, **kwargs):
    """Retrain model when user behavior changes"""
    if created and instance.behavior_type in ['LIKE', 'SAVE', 'VIEW']:
        # Retrain in background if significant changes
        thread = threading.Thread(target=retrain_model_async)
        thread.daemon = True
        thread.start()

@receiver(post_save, sender=Like)
def like_post_save(sender, instance, created, **kwargs):
    """Retrain model when user likes news"""
    if created:
        thread = threading.Thread(target=retrain_model_async)
        thread.daemon = True
        thread.start()