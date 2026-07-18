import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
from sentence_transformers import SentenceTransformer
from datetime import datetime, timedelta
from django.db.models import Count, Q
from news.models import News, UserBehavior, Category, Like, Bookmark, Comment
from django.contrib.auth import get_user_model
import joblib
import os
from django.conf import settings
import logging
from collections import defaultdict
import json

logger = logging.getLogger(__name__)
User = get_user_model()

class AdvancedNewsRecommender:
    """Advanced recommendation engine with hybrid approach"""
    
    def __init__(self):
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')  # BERT-like embeddings
        self.scaler = StandardScaler()
        self.news_embeddings = None
        self.news_data = None
        self.user_profiles = {}
        self.category_weights = {}
        
    def load_or_create_embeddings(self):
        """Load news embeddings or create them"""
        embedding_path = settings.AI_MODEL_PATH / 'news_embeddings.npy'
        
        if os.path.exists(embedding_path):
            self.news_embeddings = np.load(embedding_path)
            self.news_data = pd.read_csv(settings.AI_MODEL_PATH / 'news_data.csv')
            logger.info("Loaded existing embeddings")
        else:
            self.create_embeddings()
    
    def create_embeddings(self):
        """Create embeddings for all news articles"""
        news_queryset = News.objects.all().select_related('category')
        
        if not news_queryset:
            logger.warning("No news articles found")
            return
        
        # Prepare data
        data = {
            'id': [],
            'title': [],
            'description': [],
            'content': [],
            'category': [],
            'category_id': [],
            'views': [],
            'likes': [],
            'saves': [],
            'comments': [],
            'published_date': [],
            'days_old': []
        }
        
        for news in news_queryset:
            data['id'].append(news.id)
            data['title'].append(news.title)
            data['description'].append(news.description)
            data['content'].append(news.content)
            data['category'].append(news.category.name)
            data['category_id'].append(news.category.id)
            data['views'].append(news.views)
            data['likes'].append(news.likes_count)
            data['saves'].append(news.saves_count)
            data['comments'].append(news.comments_count)
            data['published_date'].append(news.published_date)
            data['days_old'].append((datetime.now().date() - news.published_date.date()).days)
        
        self.news_data = pd.DataFrame(data)
        
        # Create embeddings
        texts = []
        for _, row in self.news_data.iterrows():
            text = f"{row['title']} {row['description']} {row['content']}"
            texts.append(text[:512])  # Limit for BERT
        
        logger.info("Creating embeddings for {} articles".format(len(texts)))
        self.news_embeddings = self.sentence_model.encode(texts)
        
        # Save embeddings
        os.makedirs(settings.AI_MODEL_PATH, exist_ok=True)
        np.save(settings.AI_MODEL_PATH / 'news_embeddings.npy', self.news_embeddings)
        self.news_data.to_csv(settings.AI_MODEL_PATH / 'news_data.csv', index=False)
        
        logger.info("Embeddings created and saved")
    
    def get_user_profile(self, user):
        """Build user profile from interactions"""
        logger.info(f"Building profile for user: {user.username}")
        
        # Get user interactions
        likes = Like.objects.filter(user=user)
        saves = Bookmark.objects.filter(user=user)
        comments = Comment.objects.filter(user=user)
        views = UserBehavior.objects.filter(user=user, behavior_type='VIEW')
        
        # Category preferences
        category_scores = defaultdict(float)
        news_scores = defaultdict(float)
        
        # Score likes (weight: 5)
        for like in likes:
            if like.news:
                news_scores[like.news.id] += 5
                if like.news.category:
                    category_scores[like.news.category.id] += 5
        
        # Score saves (weight: 3)
        for save in saves:
            if save.news:
                news_scores[save.news.id] += 3
                if save.news.category:
                    category_scores[save.news.category.id] += 3
        
        # Score views (weight: 1)
        for view in views[:100]:
            if view.news:
                news_scores[view.news.id] += 1
                if view.news.category:
                    category_scores[view.news.category.id] += 1
        
        # Score comments (weight: 4)
        for comment in comments:
            if comment.news:
                news_scores[comment.news.id] += 4
                if comment.news.category:
                    category_scores[comment.news.category.id] += 4
        
        # User selected interests (weight: 10)
        if user.interests:
            interest_category = Category.objects.filter(name=user.interests).first()
            if interest_category:
                category_scores[interest_category.id] += 10
        
        # Get top categories
        top_categories = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Get liked news IDs
        liked_news_ids = list(news_scores.keys())
        
        # Calculate user embedding (average of liked news embeddings)
        user_embedding = None
        if liked_news_ids and self.news_embeddings is not None:
            liked_indices = self.news_data[self.news_data['id'].isin(liked_news_ids)].index
            if len(liked_indices) > 0:
                liked_embeddings = self.news_embeddings[liked_indices]
                user_embedding = np.mean(liked_embeddings, axis=0)
        
        profile = {
            'user': user,
            'liked_news': liked_news_ids,
            'saved_news': [save.news.id for save in saves if save.news],
            'viewed_news': [view.news.id for view in views[:100] if view.news],
            'top_categories': [cat_id for cat_id, score in top_categories],
            'category_scores': dict(category_scores),
            'news_scores': dict(news_scores),
            'user_embedding': user_embedding,
            'total_interactions': len(likes) + len(saves) + len(views) + len(comments)
        }
        
        logger.info(f"Profile built: {len(liked_news_ids)} liked news, {len(top_categories)} top categories")
        return profile
    
    def score_articles(self, user_profile, news_ids, n_recommendations=20):
        """Score articles based on multiple factors"""
        scores = {}
        
        for news_id in news_ids:
            news = News.objects.filter(id=news_id).first()
            if not news:
                continue
            
            score = 0
            days_old = (datetime.now().date() - news.published_date.date()).days
            
            # 1. Content similarity (30%)
            if user_profile['user_embedding'] is not None and self.news_embeddings is not None:
                news_idx = self.news_data[self.news_data['id'] == news_id].index
                if len(news_idx) > 0:
                    news_embedding = self.news_embeddings[news_idx[0]]
                    similarity = cosine_similarity(
                        user_profile['user_embedding'].reshape(1, -1),
                        news_embedding.reshape(1, -1)
                    )[0][0]
                    score += similarity * 0.3
            
            # 2. Category match (25%)
            if news.category_id in user_profile['category_scores']:
                category_score = user_profile['category_scores'][news.category_id]
                max_score = max(user_profile['category_scores'].values()) or 1
                normalized_score = category_score / max_score
                score += normalized_score * 0.25
            
            # 3. Freshness (20%)
            freshness_score = max(0, 30 - days_old) / 30
            score += freshness_score * 0.2
            
            # 4. Popularity (15%)
            popularity = (
                news.views * 0.3 + 
                news.likes_count * 0.4 + 
                news.saves_count * 0.2 +
                news.comments_count * 0.1
            ) / 100
            score += min(popularity, 1) * 0.15
            
            # 5. Diversity (10%) - Prefer less common categories
            category_count = News.objects.filter(category=news.category).count()
            if category_count > 0:
                diversity_score = 1 / (category_count / 100 + 1)
                score += diversity_score * 0.1
            
            scores[news_id] = score
        
        # Sort and return top recommendations
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [news_id for news_id, score in sorted_scores[:n_recommendations]]
    
    def get_recommendations(self, user, n_recommendations=20):
        """Get personalized recommendations"""
        try:
            # Load embeddings if not loaded
            if self.news_embeddings is None:
                self.load_or_create_embeddings()
            
            # Get user profile
            user_profile = self.get_user_profile(user)
            
            # If user has no interactions, return trending + latest
            if user_profile['total_interactions'] == 0:
                logger.info(f"New user {user.username}, returning trending + latest")
                return self.get_trending_and_latest(n_recommendations)
            
            # Get candidate articles (all except interacted)
            interacted_ids = user_profile['liked_news'] + user_profile['saved_news'] + user_profile['viewed_news']
            candidates = News.objects.exclude(id__in=interacted_ids).values_list('id', flat=True)[:100]
            
            if not candidates:
                return self.get_trending_and_latest(n_recommendations)
            
            # Score candidates
            recommendations = self.score_articles(user_profile, candidates, n_recommendations)
            
            # If not enough recommendations, add trending
            if len(recommendations) < n_recommendations:
                trending = self.get_trending_and_latest(n_recommendations)
                for news_id in trending:
                    if news_id not in recommendations:
                        recommendations.append(news_id)
                    if len(recommendations) >= n_recommendations:
                        break
            
            logger.info(f"Generated {len(recommendations)} recommendations for {user.username}")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error in recommendations: {e}")
            return self.get_trending_and_latest(n_recommendations)
    
    def get_trending_and_latest(self, n_recommendations):
        """Get trending and latest news for new users"""
        latest = News.objects.order_by('-published_date')[:n_recommendations//2]
        trending = News.objects.order_by('-views', '-likes_count')[:n_recommendations//2]
        
        combined = list(latest.values_list('id', flat=True))
        combined.extend(trending.values_list('id', flat=True))
        
        return list(set(combined))[:n_recommendations]
    
    def update_user_embedding(self, user):
        """Update user embedding after new interactions"""
        profile = self.get_user_profile(user)
        # Save profile to cache for faster access
        self.user_profiles[user.id] = profile
        return profile