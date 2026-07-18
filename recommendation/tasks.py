from celery import shared_task
from django.contrib.auth import get_user_model
from news.models import Category, UserBehavior, Like, Bookmark
from .ai_engine.recommender import NewsRecommender
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

@shared_task
def update_user_preferences(user_id, category_id, action_type, is_add):
    """Update user preferences for AI model"""
    try:
        logger.info(f"Updating user preferences: user={user_id}, category={category_id}, action={action_type}, add={is_add}")
        
        # Get user and category
        user = User.objects.get(id=user_id)
        category = Category.objects.get(id=category_id)
        
        # Retrain model with updated data
        recommender = NewsRecommender()
        recommender.retrain_model()
        
        logger.info(f"User preferences updated successfully for {user.username}")
        return True
        
    except Exception as e:
        logger.error(f"Error updating user preferences: {e}")
        return False

@shared_task
def retrain_recommendation_model():
    """Retrain the recommendation model"""
    try:
        logger.info("Starting model retraining from task...")
        recommender = NewsRecommender()
        recommender.retrain_model()
        logger.info("Model retrained successfully")
        return True
    except Exception as e:
        logger.error(f"Error retraining model: {e}")
        return False