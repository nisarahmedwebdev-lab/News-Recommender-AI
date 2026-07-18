import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import LabelEncoder
import joblib
import os
from django.conf import settings
from news.models import News, UserBehavior, Category, Like, Bookmark
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from .preprocess import TextPreprocessor
from datetime import datetime, timedelta
import logging
from collections import defaultdict
import random
import traceback

# At the top of recommender.py
import nltk
import logging

# Download NLTK resources if not available
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')
    
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

logger = logging.getLogger(__name__)
User = get_user_model()

class NewsRecommender:
    def __init__(self):
        self.preprocessor = TextPreprocessor()
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=5000, 
            stop_words='english',
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.8
        )
        self.similarity_matrix = None
        self.news_data = None
        self.tfidf_matrix = None
        self.label_encoder = LabelEncoder()
        self.user_profiles = {}
        self.category_vectors = {}
        self.category_weight = {}
        self.last_trained = None
        
    def load_and_preprocess_news(self, force_reload=False):
        """Load news data and preprocess with caching"""
        print("=" * 80)
        print("LOADING NEWS DATA")
        print("=" * 80)
        
        # Get all news from database
        news_queryset = News.objects.all().select_related('category')
        total_news = news_queryset.count()
        print(f"📊 Total news in database: {total_news}")
        
        if total_news == 0:
            print("⚠️ No news found in database!")
            return pd.DataFrame()
        
        data = {
            'id': [],
            'title': [],
            'description': [],
            'content': [],
            'category': [],
            'category_id': [],
            'category_name': [],
            'author': [],
            'views': [],
            'likes': [],
            'saves': [],
            'comments': [],
            'published_date': [],
            'days_old': [],
            'processed_text': []
        }
        
        current_date = datetime.now().date()
        
        for news in news_queryset:
            data['id'].append(news.id)
            data['title'].append(news.title)
            data['description'].append(news.description)
            data['content'].append(news.content)
            data['category'].append(news.category.name)
            data['category_id'].append(news.category.id)
            data['category_name'].append(news.category.name)
            data['author'].append(news.author)
            data['views'].append(news.views)
            data['likes'].append(news.likes_count)
            data['saves'].append(news.saves_count)
            data['comments'].append(news.comments_count)
            data['published_date'].append(news.published_date)
            
            # Calculate days old
            days_old = (current_date - news.published_date.date()).days
            data['days_old'].append(days_old)
            
            # Combine title, description, and content for better features
            text = f"{news.title} {news.description} {news.content}"
            data['processed_text'].append(self.preprocessor.preprocess(text))
        
        self.news_data = pd.DataFrame(data)
        print(f"✅ Loaded {len(self.news_data)} news articles")
        print(f"📅 Date range: oldest={self.news_data['days_old'].max()} days, newest={self.news_data['days_old'].min()} days")
        print(f"📂 Categories: {self.news_data['category'].unique().tolist()}")
        print("=" * 80)
        
        return self.news_data
    
    def build_tfidf_matrix(self):
        """Build TF-IDF matrix"""
        print("=" * 80)
        print("BUILDING TF-IDF MATRIX")
        print("=" * 80)
        
        if self.news_data is None or len(self.news_data) == 0:
            print("❌ No news data available!")
            return None, None
        
        print(f"📊 Processing {len(self.news_data)} articles...")
        
        # Create TF-IDF matrix
        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(
            self.news_data['processed_text']
        )
        
        # Compute similarity matrix
        self.similarity_matrix = cosine_similarity(self.tfidf_matrix, self.tfidf_matrix)
        
        print(f"✅ TF-IDF matrix shape: {self.tfidf_matrix.shape}")
        print(f"✅ Similarity matrix shape: {self.similarity_matrix.shape}")
        print("=" * 80)
        
        return self.tfidf_matrix, self.similarity_matrix
    
    def build_category_vectors(self):
        """Build category preference vectors"""
        print("=" * 80)
        print("BUILDING CATEGORY VECTORS")
        print("=" * 80)
        
        if self.news_data is None or len(self.news_data) == 0:
            print("❌ No news data available!")
            return
        
        categories = Category.objects.filter(is_active=True)
        print(f"📊 Processing {categories.count()} categories...")
        
        for category in categories:
            category_news = self.news_data[self.news_data['category_id'] == category.id]
            if len(category_news) > 0:
                indices = category_news.index.tolist()
                weights = []
                for idx in indices:
                    days_old = self.news_data.iloc[idx]['days_old']
                    recency_weight = max(0, 30 - days_old) / 30 * 0.5
                    popularity_weight = (
                        self.news_data.iloc[idx]['views'] * 0.1 +
                        self.news_data.iloc[idx]['likes'] * 0.3 +
                        self.news_data.iloc[idx]['saves'] * 0.2
                    )
                    weight = 1 + recency_weight + popularity_weight
                    weights.append(max(1, weight))
                
                weighted_vectors = []
                for idx, weight in zip(indices, weights):
                    vector = np.array(self.tfidf_matrix[idx]).flatten()
                    weighted_vectors.append(vector * weight)
                
                if weighted_vectors:
                    category_vector = np.mean(weighted_vectors, axis=0)
                    self.category_vectors[category.id] = category_vector
                    self.category_weight[category.id] = np.sum(weights)
                    print(f"✅ Category '{category.name}': {len(category_news)} articles, weight: {self.category_weight[category.id]:.2f}")
        
        print(f"✅ Built vectors for {len(self.category_vectors)} categories")
        print("=" * 80)
    
    def analyze_user_behavior(self, user):
        """Deep analysis of user behavior with debug"""
        print("=" * 80)
        print(f"ANALYZING USER BEHAVIOR: {user.username}")
        print("=" * 80)
        
        # Get all user behaviors
        behaviors = UserBehavior.objects.filter(user=user)
        likes = Like.objects.filter(user=user).select_related('news')
        saves = Bookmark.objects.filter(user=user).select_related('news')
        views = behaviors.filter(
            behavior_type='VIEW',
            timestamp__gte=datetime.now() - timedelta(days=30)
        ).select_related('news')
        
        print(f"📊 User Stats:")
        print(f"  - Likes: {likes.count()}")
        print(f"  - Saves: {saves.count()}")
        print(f"  - Views (last 30 days): {views.count()}")
        
        if likes.count() == 0 and saves.count() == 0 and views.count() == 0:
            print("⚠️ User has NO interactions!")
            return {
                'user': user,
                'liked_news': [],
                'saved_news': [],
                'viewed_news': [],
                'top_categories': [],
                'category_scores': {},
                'category_percentages': {},
                'category_view_count': {},
                'category_like_count': {},
                'category_save_count': {},
                'news_scores': {},
                'interests': user.interests,
                'total_interactions': 0
            }
        
        # Initialize scores
        category_scores = defaultdict(float)
        news_scores = defaultdict(float)
        category_view_count = defaultdict(int)
        category_like_count = defaultdict(int)
        category_save_count = defaultdict(int)
        
        # 1. Score based on LIKES (Highest weight: 10)
        for like in likes:
            if like.news:
                news_scores[like.news.id] += 10
                if like.news.category:
                    category_scores[like.news.category.id] += 10
                    category_like_count[like.news.category.id] += 1
        
        # 2. Score based on SAVES (High weight: 7)
        for save in saves:
            if save.news:
                news_scores[save.news.id] += 7
                if save.news.category:
                    category_scores[save.news.category.id] += 7
                    category_save_count[save.news.category.id] += 1
        
        # 3. Score based on VIEWS (Medium weight: 3)
        for view in views[:100]:
            if view.news:
                news_scores[view.news.id] += 3
                if view.news.category:
                    category_scores[view.news.category.id] += 3
                    category_view_count[view.news.category.id] += 1
        
        # 4. Score based on USER INTERESTS from profile (Weight: 15)
        if user.interests:
            interest_category = Category.objects.filter(name=user.interests).first()
            if interest_category:
                category_scores[interest_category.id] += 15
                print(f"🎯 User interest: {user.interests} (+15 points)")
        
        # Sort categories by score
        sorted_categories = sorted(
            category_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        print(f"📊 Category Scores:")
        for cat_id, score in sorted_categories[:5]:
            cat_name = Category.objects.get(id=cat_id).name
            print(f"  - {cat_name}: {score:.2f}")
        
        top_categories = [cat_id for cat_id, score in sorted_categories[:5]]
        
        profile = {
            'user': user,
            'liked_news': list(news_scores.keys()),
            'saved_news': [save.news.id for save in saves if save.news],
            'viewed_news': [view.news.id for view in views[:100] if view.news],
            'top_categories': top_categories,
            'category_scores': dict(category_scores),
            'category_percentages': {},
            'category_view_count': dict(category_view_count),
            'category_like_count': dict(category_like_count),
            'category_save_count': dict(category_save_count),
            'news_scores': dict(news_scores),
            'interests': user.interests,
            'total_interactions': likes.count() + saves.count() + views.count()
        }
        
        print("=" * 80)
        return profile
    
    def get_hybrid_recommendations(self, user, n_recommendations=20):
        """Get hybrid recommendations with full debug"""
        print("=" * 80)
        print(f"GENERATING RECOMMENDATIONS FOR: {user.username}")
        print(f"Requested: {n_recommendations} recommendations")
        print("=" * 80)
        
        try:
            # Analyze user behavior
            user_profile = self.analyze_user_behavior(user)
            
            # If user has no interactions, return latest + trending
            if user_profile['total_interactions'] == 0:
                print("⚠️ No interactions found, returning latest + trending")
                result = self.get_trending_and_latest(n_recommendations)
                print(f"✅ Returning {len(result)} recommendations")
                return result
            
            # Get all news IDs (excluding interacted)
            interacted_ids = user_profile['liked_news'] + user_profile['saved_news']
            print(f"📊 Interacted news: {len(interacted_ids)}")
            
            # Get latest news first (for freshness)
            latest_news = self.get_latest_news_ids(n_recommendations * 2)
            print(f"📰 Latest news available: {len(latest_news)}")
            
            # Get trending news
            trending_ids = self.get_trending_news_ids(n_recommendations)
            print(f"🔥 Trending news: {len(trending_ids)}")
            
            # Get category-based recommendations
            category_recs = self.get_category_based_recommendations(
                user_profile,
                n_recommendations=n_recommendations
            )
            print(f"📂 Category-based: {len(category_recs)}")
            
            # Get content-based recommendations
            content_recs = self.get_content_based_recommendations(
                user_profile,
                n_recommendations=n_recommendations
            )
            print(f"📄 Content-based: {len(content_recs)}")
            
            # Combine recommendations with weights
            combined_scores = defaultdict(float)
            
            # Category-based (weight: 0.4)
            for news_id in category_recs:
                combined_scores[news_id] += 0.4
            
            # Content-based (weight: 0.3)
            for news_id in content_recs:
                combined_scores[news_id] += 0.3
            
            # Trending (weight: 0.2)
            for news_id in trending_ids:
                combined_scores[news_id] += 0.2
            
            # Latest (weight: 0.1)
            for news_id in latest_news:
                combined_scores[news_id] += 0.1
            
            # Add freshness bonus for recent news
            for news_id in list(combined_scores.keys()):
                news = News.objects.filter(id=news_id).first()
                if news:
                    days_old = (datetime.now().date() - news.published_date.date()).days
                    if days_old <= 1:
                        combined_scores[news_id] += 0.5  # Very recent
                    elif days_old <= 3:
                        combined_scores[news_id] += 0.3  # Recent
                    elif days_old <= 7:
                        combined_scores[news_id] += 0.1  # Week old
            
            # Remove interacted news
            for news_id in interacted_ids:
                if news_id in combined_scores:
                    del combined_scores[news_id]
            
            # Sort by score
            sorted_recs = sorted(
                combined_scores.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            print(f"\n📊 Top 10 Scores:")
            for i, (news_id, score) in enumerate(sorted_recs[:10]):
                news = News.objects.filter(id=news_id).first()
                if news:
                    days_old = (datetime.now().date() - news.published_date.date()).days
                    print(f"  {i+1}. {news.title[:40]}... (score: {score:.3f}, days: {days_old})")
            
            # Get final recommendations
            final_recs = []
            seen_categories = set()
            
            for news_id, score in sorted_recs:
                news = News.objects.filter(id=news_id).first()
                if news:
                    # Ensure diversity: limit 3 per category
                    if news.category_id in seen_categories:
                        if len([n for n in final_recs if News.objects.filter(id=n).first().category_id == news.category_id]) >= 3:
                            continue
                    else:
                        seen_categories.add(news.category_id)
                    
                    final_recs.append(news_id)
                    if len(final_recs) >= n_recommendations:
                        break
            
            # If not enough, add latest news
            if len(final_recs) < n_recommendations:
                print(f"⚠️ Only {len(final_recs)} recommendations, adding latest news...")
                for news_id in latest_news:
                    if news_id not in final_recs and news_id not in interacted_ids:
                        final_recs.append(news_id)
                    if len(final_recs) >= n_recommendations:
                        break
            
            # If still not enough, add trending
            if len(final_recs) < n_recommendations:
                print(f"⚠️ Still only {len(final_recs)} recommendations, adding trending...")
                for news_id in trending_ids:
                    if news_id not in final_recs and news_id not in interacted_ids:
                        final_recs.append(news_id)
                    if len(final_recs) >= n_recommendations:
                        break
            
            print(f"\n✅ Final recommendations: {len(final_recs)}")
            print("=" * 80)
            
            return final_recs
            
        except Exception as e:
            print(f"❌ ERROR in hybrid recommendations: {str(e)}")
            print(traceback.format_exc())
            return self.get_trending_and_latest(n_recommendations)
    
    def get_content_based_recommendations(self, user_profile, n_recommendations=20):
        """Get content-based recommendations"""
        liked_news_ids = user_profile['liked_news'] + user_profile['saved_news']
        
        if not liked_news_ids or self.similarity_matrix is None:
            return []
        
        # Get indices of liked news
        indices = self.news_data[self.news_data['id'].isin(liked_news_ids)].index.tolist()
        
        if not indices:
            return []
        
        # Calculate similarity scores with weights
        similarity_scores = np.zeros(len(self.news_data))
        
        for idx in indices:
            news_id = self.news_data.iloc[idx]['id']
            weight = user_profile['news_scores'].get(news_id, 1)
            similarity_scores += self.similarity_matrix[idx] * weight
        
        # Sort by similarity
        similarity_scores = list(enumerate(similarity_scores))
        similarity_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Get top recommendations (excluding already interacted)
        recommended_ids = []
        for i, score in similarity_scores[:n_recommendations*3]:
            news_id = self.news_data.iloc[i]['id']
            if news_id not in liked_news_ids:
                recommended_ids.append(news_id)
                if len(recommended_ids) >= n_recommendations:
                    break
        
        return recommended_ids
    
    def get_category_based_recommendations(self, user_profile, n_recommendations=20):
        """Get category-based recommendations"""
        top_categories = user_profile['top_categories']
        category_scores = user_profile['category_scores']
        
        if not top_categories:
            # Fallback to most popular categories
            top_categories = Category.objects.annotate(
                news_count=Count('news')
            ).order_by('-news_count').values_list('id', flat=True)[:5]
        
        # Get news from top categories
        category_news = {}
        interacted_ids = user_profile['liked_news'] + user_profile['saved_news']
        
        for cat_id in top_categories[:3]:
            news_list = News.objects.filter(
                category_id=cat_id
            ).exclude(
                id__in=interacted_ids
            ).order_by('-published_date', '-views')[:n_recommendations]
            
            weight = category_scores.get(cat_id, 1)
            for news in news_list:
                category_news[news.id] = {
                    'news': news,
                    'score': weight * (
                        news.views * 0.2 + 
                        news.likes_count * 0.4 + 
                        news.saves_count * 0.2 +
                        max(0, 10 - (datetime.now().date() - news.published_date.date()).days) * 0.2
                    )
                }
        
        sorted_news = sorted(
            category_news.items(),
            key=lambda x: x[1]['score'],
            reverse=True
        )
        
        return [news_id for news_id, data in sorted_news[:n_recommendations]]
    
    def get_trending_news_ids(self, n_recommendations):
        """Get trending news IDs"""
        trending = News.objects.filter(
            published_date__gte=datetime.now() - timedelta(days=7)
        ).order_by('-views', '-likes_count', '-saves_count')[:n_recommendations]
        return list(trending.values_list('id', flat=True))
    
    def get_latest_news_ids(self, n_recommendations):
        """Get latest news IDs"""
        latest = News.objects.order_by('-published_date')[:n_recommendations]
        return list(latest.values_list('id', flat=True))
    
    def get_trending_and_latest(self, n_recommendations):
        """Get mix of trending and latest news"""
        trending = self.get_trending_news_ids(n_recommendations // 2)
        latest = self.get_latest_news_ids(n_recommendations // 2)
        combined = list(set(trending + latest))
        return combined[:n_recommendations]
    
    def get_recommendations_for_user(self, user, n_recommendations=10):
        """Get personalized news recommendations for a user"""
        print("=" * 80)
        print(f"GET_RECOMMENDATIONS_FOR_USER: {user.username}")
        print("=" * 80)
        
        try:
            # Load data if not loaded
            if self.similarity_matrix is None:
                print("📊 Loading data and building matrices...")
                self.load_and_preprocess_news()
                self.build_tfidf_matrix()
                self.build_category_vectors()
            
            # Get hybrid recommendations
            recommended_ids = self.get_hybrid_recommendations(user, n_recommendations)
            
            print(f"✅ Returning {len(recommended_ids)} recommendations for {user.username}")
            print("=" * 80)
            
            return recommended_ids
            
        except Exception as e:
            print(f"❌ Error in get_recommendations_for_user: {str(e)}")
            print(traceback.format_exc())
            return self.get_trending_and_latest(n_recommendations)
    
    def retrain_model(self):
        """Retrain the recommendation model with latest data"""
        print("=" * 80)
        print("RETRAINING MODEL")
        print("=" * 80)
        
        try:
            # Load latest news
            self.load_and_preprocess_news()
            
            # Rebuild TF-IDF matrix
            self.build_tfidf_matrix()
            
            # Rebuild category vectors
            self.build_category_vectors()
            
            # Update last trained timestamp
            self.last_trained = datetime.now()
            
            # Save model
            model_path = settings.AI_MODEL_PATH / 'recommendation.pkl'
            self.save_model(model_path)
            
            print("✅ Model retrained successfully!")
            print("=" * 80)
            return True
            
        except Exception as e:
            print(f"❌ Error retraining model: {str(e)}")
            print(traceback.format_exc())
            return False
    
    def save_model(self, model_path):
        """Save the trained model"""
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        model_data = {
            'tfidf_vectorizer': self.tfidf_vectorizer,
            'tfidf_matrix': self.tfidf_matrix,
            'similarity_matrix': self.similarity_matrix,
            'news_data': self.news_data,
            'category_vectors': self.category_vectors,
            'category_weight': self.category_weight,
            'label_encoder': self.label_encoder,
            'last_trained': self.last_trained
        }
        joblib.dump(model_data, model_path)
        print(f"✅ Model saved to {model_path}")
    
    def load_model(self, model_path):
        """Load a trained model"""
        if os.path.exists(model_path):
            try:
                model_data = joblib.load(model_path)
                self.tfidf_vectorizer = model_data['tfidf_vectorizer']
                self.tfidf_matrix = model_data['tfidf_matrix']
                self.similarity_matrix = model_data['similarity_matrix']
                self.news_data = model_data['news_data']
                self.category_vectors = model_data.get('category_vectors', {})
                self.category_weight = model_data.get('category_weight', {})
                self.label_encoder = model_data.get('label_encoder', LabelEncoder())
                self.last_trained = model_data.get('last_trained')
                print(f"✅ Model loaded from {model_path}")
                print(f"📊 Loaded {len(self.news_data)} articles")
                return True
            except Exception as e:
                print(f"❌ Error loading model: {e}")
                return False
        return False