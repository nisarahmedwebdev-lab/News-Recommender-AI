import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from django.db.models import Count, Q
from news.models import News, Category, Like, Bookmark, UserBehavior
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
import logging
from collections import defaultdict
import random
import joblib
import os

logger = logging.getLogger(__name__)
User = get_user_model()

class SimpleRecommender:
    """Simple but effective recommendation engine"""
    
    def __init__(self):
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=3000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.tfidf_matrix = None
        self.news_data = None
        self.category_vectors = {}
        self.category_weight = {}
        
    def load_news_data(self):
        """Load news data for recommendation"""
        print("📊 Loading news data for recommendations...")
        
        news_queryset = News.objects.all().select_related('category')
        
        if not news_queryset:
            print("⚠️ No news articles found")
            logger.warning("No news articles found")
            return None
        
        print(f"📰 Total news in database: {news_queryset.count()}")
        
        data = {
            'id': [],
            'title': [],
            'description': [],
            'content': [],
            'category_id': [],
            'category_name': [],
            'views': [],
            'likes': [],
            'saves': [],
            'published_date': [],
            'source': [],
            'days_old': []
        }
        
        current_date = datetime.now().date()
        
        for news in news_queryset:
            data['id'].append(news.id)
            data['title'].append(news.title)
            data['description'].append(news.description)
            data['content'].append(news.content or '')
            data['category_id'].append(news.category.id)
            data['category_name'].append(news.category.name)
            data['views'].append(news.views)
            data['likes'].append(news.likes_count)
            data['saves'].append(news.saves_count)
            data['published_date'].append(news.published_date)
            data['source'].append(news.source or 'Unknown')
            
            # Calculate days old
            days_old = (current_date - news.published_date.date()).days
            data['days_old'].append(days_old)
        
        self.news_data = pd.DataFrame(data)
        
        print(f"✅ Loaded {len(self.news_data)} articles")
        print(f"📂 Categories: {self.news_data['category_name'].unique().tolist()}")
        
        # Create TF-IDF matrix
        texts = []
        for _, row in self.news_data.iterrows():
            text = f"{row['title']} {row['description']} {row['content']}"
            texts.append(text[:500])
        
        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(texts)
        print(f"✅ TF-IDF matrix created: {self.tfidf_matrix.shape}")
        
        return self.news_data
    
    def build_tfidf_matrix(self):
        """Build TF-IDF matrix"""
        if self.news_data is None:
            self.load_news_data()
        
        if self.news_data is None or len(self.news_data) == 0:
            return None, None
        
        print("📊 Building TF-IDF matrix...")
        
        # Create TF-IDF matrix
        texts = []
        for _, row in self.news_data.iterrows():
            text = f"{row['title']} {row['description']} {row['content']}"
            texts.append(text[:500])
        
        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(texts)
        print(f"✅ TF-IDF matrix shape: {self.tfidf_matrix.shape}")
        
        return self.tfidf_matrix, None
    
    def build_category_vectors(self):
        """Build category vectors"""
        print("📊 Building category vectors...")
        
        if self.news_data is None:
            return
        
        categories = Category.objects.all()
        print(f"📊 Processing {categories.count()} categories...")
        
        for category in categories:
            category_news = self.news_data[self.news_data['category_name'] == category.name]
            if len(category_news) > 0:
                indices = category_news.index.tolist()
                weights = []
                for idx in indices:
                    weight = (
                        self.news_data.iloc[idx]['views'] * 0.3 +
                        self.news_data.iloc[idx]['likes'] * 0.5 +
                        self.news_data.iloc[idx]['saves'] * 0.2
                    )
                    weights.append(max(1, weight))
                
                weighted_vectors = []
                for idx, weight in zip(indices, weights):
                    vector = np.array(self.tfidf_matrix[idx]).flatten()
                    weighted_vectors.append(vector * weight)
                
                if weighted_vectors:
                    category_vector = np.mean(weighted_vectors, axis=0)
                    self.category_vectors[category.id] = category_vector
                    self.category_weight[category.id] = np.sum(weights)
                    print(f"✅ Category '{category.name}': {len(category_news)} articles")
        
        print(f"✅ Built vectors for {len(self.category_vectors)} categories")
    
    def get_recommendations(self, user, n_recommendations=20):
        """Get personalized recommendations based on user interests and behavior"""
        try:
            # Load data if not loaded
            if self.news_data is None:
                self.load_news_data()
            
            if self.news_data is None or len(self.news_data) == 0:
                print("⚠️ No news data available")
                return []
            
            print(f"🎯 Getting recommendations for user: {user.username}")
            
            # Get user interactions
            liked_news = list(Like.objects.filter(user=user).values_list('news_id', flat=True)[:20])
            saved_news = list(Bookmark.objects.filter(user=user).values_list('news_id', flat=True)[:20])
            viewed_news = list(UserBehavior.objects.filter(
                user=user,
                behavior_type='VIEW'
            ).values_list('news_id', flat=True)[:50].distinct())
            
            interacted_ids = set(liked_news + saved_news + viewed_news)
            
            print(f"📊 User interactions: {len(liked_news)} likes, {len(saved_news)} saves, {len(viewed_news)} views")
            
            # If user has no interactions, return trending + latest
            if not liked_news and not saved_news and not viewed_news:
                print("📊 New user - showing trending + latest articles")
                return self.get_trending_and_latest(n_recommendations)
            
            # Build category preferences
            category_prefs = {}
            category_weights = defaultdict(float)
            
            # Priority 1: User's selected interests (highest weight)
            if user.interests:
                interests_list = [i.strip() for i in user.interests.split(',') if i.strip()]
                for interest in interests_list:
                    cat = Category.objects.filter(name__iexact=interest).first()
                    if cat:
                        category_prefs[cat.id] = 5.0
                        category_weights[cat.id] += 5.0
                        print(f"✨ User interest found: {cat.name}")
            
            # Priority 2: Categories from liked articles (high weight)
            for news_id in liked_news:
                try:
                    news = News.objects.filter(id=news_id).first()
                    if news:
                        category_prefs[news.category.id] = category_prefs.get(news.category.id, 0) + 3.0
                        category_weights[news.category.id] += 3.0
                except:
                    pass
            
            # Priority 3: Categories from bookmarked articles (medium-high weight)
            for news_id in saved_news:
                try:
                    news = News.objects.filter(id=news_id).first()
                    if news:
                        category_prefs[news.category.id] = category_prefs.get(news.category.id, 0) + 2.0
                        category_weights[news.category.id] += 2.0
                except:
                    pass
            
            # Priority 4: Categories from viewed articles (medium weight)
            for news_id in viewed_news[:30]:
                try:
                    news = News.objects.filter(id=news_id).first()
                    if news:
                        category_prefs[news.category.id] = category_prefs.get(news.category.id, 0) + 1.0
                        category_weights[news.category.id] += 1.0
                except:
                    pass
            
            print(f"🎯 Category preferences: {dict(category_prefs)}")
            
            # Get candidate news (exclude already interacted)
            candidates = News.objects.exclude(id__in=interacted_ids).order_by('-published_date')[:200]
            
            # Score candidates
            scored_news = []
            
            for news in candidates:
                score = 0.0
                
                # Category match (40% weight)
                if news.category.id in category_prefs:
                    score += category_prefs[news.category.id] * 0.4
                else:
                    # Small bonus for any category if no preferences
                    score += 0.1 * 0.4
                
                # Freshness (25% weight) - prioritize recent articles
                days_old = (datetime.now().date() - news.published_date.date()).days
                freshness = max(0, 14 - days_old) / 14  # Maximum 14 days freshness
                score += freshness * 0.25
                
                # Popularity (20% weight) - use liked articles as indicator
                engagement = (
                    news.views * 0.1 +
                    news.likes_count * 0.5 +
                    news.saves_count * 0.4
                )
                popularity = min(engagement / 100, 1.0)
                score += popularity * 0.2
                
                # Recency bonus for very recent articles (10% weight)
                if days_old <= 3:
                    score += 0.10
                elif days_old <= 7:
                    score += 0.05
                
                # Quality bonus for well-engaged articles
                if news.likes_count > 10 or news.saves_count > 5:
                    score += 0.05
                
                scored_news.append((news.id, score))
            
            # Sort by score descending
            scored_news.sort(key=lambda x: x[1], reverse=True)
            
            # Extract recommendation IDs
            recommendations = [news_id for news_id, score in scored_news[:n_recommendations]]
            
            print(f"✅ Generated {len(recommendations)} personalized recommendations")
            if scored_news:
                top_scores = scored_news[:5]
                print(f"🏆 Top recommendations (with scores):")
                for news_id, score in top_scores:
                    try:
                        news = News.objects.get(id=news_id)
                        print(f"   - {news.title[:50]}: {score:.2f}")
                    except:
                        pass
            
            # If not enough recommendations, add trending
            if len(recommendations) < n_recommendations:
                print(f"📈 Adding trending articles to fill recommendations...")
                trending = self.get_trending_and_latest(n_recommendations * 2)
                for news_id in trending:
                    if news_id not in recommendations and news_id not in interacted_ids:
                        recommendations.append(news_id)
                    if len(recommendations) >= n_recommendations:
                        break
            
            return recommendations
            
        except Exception as e:
            print(f"❌ Error in recommendations: {e}")
            import traceback
            traceback.print_exc()
            return self.get_trending_and_latest(n_recommendations)
    
    def get_trending_and_latest(self, n_recommendations):
        """Get trending and latest news"""
        latest = list(News.objects.order_by('-published_date')[:n_recommendations//2].values_list('id', flat=True))
        trending = list(News.objects.order_by('-views', '-likes_count')[:n_recommendations//2].values_list('id', flat=True))
        
        combined = list(set(latest + trending))
        random.shuffle(combined)
        return combined[:n_recommendations]
    
    def get_related_news(self, news_article, n_recommendations=5):
        """Get related news articles based on content similarity"""
        try:
            print(f"🔗 Finding related articles for: {news_article.title[:50]}")
            
            if self.tfidf_matrix is None:
                self.load_news_data()
                self.build_tfidf_matrix()
            
            if self.news_data is None or len(self.news_data) == 0:
                print("⚠️ No news data available")
                return []
            
            # Find the article index
            article_indices = self.news_data[self.news_data['id'] == news_article.id].index.tolist()
            if not article_indices:
                print(f"⚠️ Article {news_article.id} not found in data")
                return self._get_related_by_category(news_article, n_recommendations)
            
            article_idx = article_indices[0]
            
            # Get the article's TF-IDF vector
            article_vector = self.tfidf_matrix[article_idx]
            
            # Calculate similarity with all other articles
            similarities = cosine_similarity(article_vector, self.tfidf_matrix)[0]
            
            # Create list of (article_id, similarity_score)
            scored_articles = []
            for idx, similarity in enumerate(similarities):
                if idx != article_idx:  # Exclude the article itself
                    article_id = self.news_data.iloc[idx]['id']
                    
                    # Don't include if already viewed by user
                    if hasattr(self, 'current_user') and self.current_user:
                        if Like.objects.filter(user=self.current_user, news_id=article_id).exists():
                            similarity *= 0.5  # Reduce score if already liked
                    
                    scored_articles.append((article_id, similarity))
            
            # Sort by similarity
            scored_articles.sort(key=lambda x: x[1], reverse=True)
            
            # Get related articles
            related_ids = [article_id for article_id, score in scored_articles[:n_recommendations]]
            
            # Fallback: if not enough by similarity, use category-based
            if len(related_ids) < n_recommendations:
                fallback_ids = self._get_related_by_category(news_article, n_recommendations - len(related_ids))
                related_ids.extend(fallback_ids)
            
            print(f"✅ Found {len(related_ids)} related articles")
            return related_ids
            
        except Exception as e:
            print(f"❌ Error finding related news: {e}")
            return self._get_related_by_category(news_article, n_recommendations)
    
    def _get_related_by_category(self, news_article, n_recommendations=5):
        """Get related news by category (fallback method)"""
        try:
            # Get other articles in same category
            related = News.objects.filter(
                category=news_article.category
            ).exclude(
                id=news_article.id
            ).order_by('-published_date', '-views', '-likes_count')[:n_recommendations]
            
            related_ids = list(related.values_list('id', flat=True))
            
            print(f"📂 Using category-based related articles: {len(related_ids)} found")
            
            # If still not enough, add trending articles
            if len(related_ids) < n_recommendations:
                trending = News.objects.exclude(
                    id__in=[news_article.id] + related_ids
                ).order_by('-views', '-likes_count')[:n_recommendations - len(related_ids)]
                
                related_ids.extend(list(trending.values_list('id', flat=True)))
            
            return related_ids
            
        except Exception as e:
            print(f"⚠️ Error in category-based related articles: {e}")
            return []
    
    def save_model(self, model_path):
        """Save the trained model"""
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        model_data = {
            'tfidf_vectorizer': self.tfidf_vectorizer,
            'tfidf_matrix': self.tfidf_matrix,
            'news_data': self.news_data,
            'category_vectors': self.category_vectors,
            'category_weight': self.category_weight,
            'last_trained': datetime.now()
        }
        joblib.dump(model_data, model_path)
        print(f"✅ Model saved to {model_path}")   
    def load_model(self, model_path):
        """Load a trained model"""
        if os.path.exists(model_path):
            try:
                model_data = joblib.load(model_path)
                self.tfidf_vectorizer = model_data.get('tfidf_vectorizer', self.tfidf_vectorizer)
                self.tfidf_matrix = model_data.get('tfidf_matrix')
                self.news_data = model_data.get('news_data')
                self.category_vectors = model_data.get('category_vectors', {})
                self.category_weight = model_data.get('category_weight', {})
                self.last_trained = model_data.get('last_trained')
                print(f"✅ Model loaded from {model_path}")
                print(f"📊 Loaded {len(self.news_data) if self.news_data is not None else 0} articles")
                return True
            except Exception as e:
                print(f"❌ Error loading model: {e}")
                return False
        return False