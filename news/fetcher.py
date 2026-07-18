import requests
import json
import logging
from datetime import datetime, timedelta
from django.utils import timezone
from django.utils.text import slugify
from .models import News, Category
import hashlib
import os
from decouple import config
import re

logger = logging.getLogger(__name__)

class NewsFetcher:
    """Fetch news from various APIs"""
    
    def __init__(self):
        self.apis = {}
        
        # Check for API keys and add only those that exist
        newsapi_key = config('NEWSAPI_KEY', default='')
        if newsapi_key:
            self.apis['newsapi'] = {
                'url': 'https://newsapi.org/v2/top-headlines',
                'key': newsapi_key,
            }
        
        gnews_key = config('GNEWS_KEY', default='')
        if gnews_key:
            self.apis['gnews'] = {
                'url': 'https://gnews.io/api/v4/top-headlines',
                'key': gnews_key,
            }
        
        mediastack_key = config('MEDIASTACK_KEY', default='')
        if mediastack_key:
            self.apis['mediastack'] = {
                'url': 'http://api.mediastack.com/v1/news',
                'key': mediastack_key,
            }
        
        if not self.apis:
            logger.warning("⚠️ No API keys configured")
            print("\n" + "="*60)
            print("⚠️  NO API KEYS CONFIGURED!")
            print("="*60)
    
    def validate_image_url(self, url):
        """Validate and clean image URL"""
        if not url:
            return None
        
        # Remove any extra quotes or whitespace
        url = url.strip().strip('"').strip("'")
        
        # Check if it's a valid URL
        if not url.startswith(('http://', 'https://')):
            return None
        
        # Check for common invalid patterns
        invalid_patterns = [
            r'\.svg$',
            r'\.gif$',
            r'data:image',
            r'googleapis\.com.*staticmap',
            r'gravatar\.com',
            r'facebook\.com.*tr:',
            r'twitter\.com.*profile_image',
        ]
        
        for pattern in invalid_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return None
        
        # Check if URL is too long (likely invalid)
        if len(url) > 500:
            return None
        
        return url
    
    def fetch_articles(self, api_name='newsapi', categories=None):
        """Fetch articles from specific API"""
        if api_name not in self.apis:
            logger.error(f"API {api_name} not configured")
            return []
        
        api_config = self.apis[api_name]
        articles = []
        
        try:
            params = {
                'language': 'en',
                'pageSize': 100,
            }
            
            # Different APIs have different parameter names for API key
            if api_name == 'newsapi':
                params['apiKey'] = api_config['key']
            elif api_name == 'gnews':
                params['token'] = api_config['key']
            elif api_name == 'mediastack':
                params['access_key'] = api_config['key']
            
            if categories:
                params['category'] = ','.join(categories)
            
            print(f"📡 Fetching from {api_name}...")
            response = requests.get(api_config['url'], params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if api_name == 'newsapi':
                    articles = data.get('articles', [])
                elif api_name == 'gnews':
                    articles = data.get('articles', [])
                elif api_name == 'mediastack':
                    articles = data.get('data', [])
                
                print(f"✅ {api_name}: Fetched {len(articles)} articles")
                logger.info(f"Fetched {len(articles)} articles from {api_name}")
            else:
                print(f"❌ {api_name}: Error {response.status_code}")
                logger.error(f"API error: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ {api_name}: {str(e)}")
            logger.error(f"Error fetching from {api_name}: {e}")
        
        return articles
    
    def fetch_all_sources(self):
        """Fetch from all configured sources"""
        all_articles = []
        
        if not self.apis:
            return []
        
        print(f"\n📡 Fetching from {len(self.apis)} sources...")
        print("-" * 40)
        
        for api_name in self.apis:
            articles = self.fetch_articles(api_name)
            all_articles.extend(articles)
        
        print("-" * 40)
        print(f"📊 Total articles fetched: {len(all_articles)}")
        
        return all_articles
    
    def process_article(self, article_data, source_api='newsapi'):
        """Process and save a single article with unique image handling"""
        try:
            # Extract data based on API source
            if source_api == 'newsapi':
                title = article_data.get('title', '')
                description = article_data.get('description', '') or article_data.get('content', '')[:200]
                content = article_data.get('content', '') or article_data.get('description', '')
                image_url_raw = article_data.get('urlToImage', '')
                author = article_data.get('author', 'Unknown')
                source = article_data.get('source', {}).get('name', 'Unknown')
                url = article_data.get('url', '')
                published_at = article_data.get('publishedAt')
                category = 'General'
                
            elif source_api == 'gnews':
                title = article_data.get('title', '')
                description = article_data.get('description', '')
                content = article_data.get('content', '') or description
                image_url_raw = article_data.get('image', '')
                author = article_data.get('source', {}).get('name', 'Unknown') or 'Unknown'
                source = article_data.get('source', {}).get('name', 'Unknown')
                url = article_data.get('url', '')
                published_at = article_data.get('publishedAt')
                category = article_data.get('category', {}).get('name', 'General')
                
            elif source_api == 'mediastack':
                title = article_data.get('title', '')
                description = article_data.get('description', '')
                content = article_data.get('description', '')
                image_url_raw = article_data.get('image', '')
                author = article_data.get('author', 'Unknown')
                source = article_data.get('source', 'Unknown')
                url = article_data.get('url', '')
                published_at = article_data.get('published_at')
                category = article_data.get('category', 'General')
            
            else:
                title = article_data.get('title', '')
                description = article_data.get('description', '')
                content = article_data.get('content', '')
                image_url_raw = article_data.get('image', '')
                author = article_data.get('author', 'Unknown')
                source = article_data.get('source', 'Unknown')
                url = article_data.get('url', '')
                published_at = article_data.get('publishedAt')
                category = article_data.get('category', 'General')
            
            # Skip if no title or URL
            if not title or not url:
                print(f"⚠️ Skipping: Missing title or URL")
                return None
            
            # Validate and clean image URL
            image_url = self.validate_image_url(image_url_raw)
            
            # Generate a unique ID for this article
            article_id = hashlib.md5(f"{url}{title}".encode()).hexdigest()
            
            # Check if article already exists by source_url
            existing = News.objects.filter(source_url=url).first()
            if existing:
                # Update image if missing
                if image_url and not existing.image_url:
                    existing.image_url = image_url
                    existing.save()
                    print(f"🔄 Updated image for: {title[:50]}...")
                return None
            
            # Get or create category
            category_obj, created = Category.objects.get_or_create(
                name=category,
                defaults={'description': f'News from {category} category'}
            )
            if created:
                print(f"📂 Created new category: {category}")
            
            # Process date
            if published_at:
                try:
                    if 'Z' in published_at:
                        published_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                    else:
                        published_date = datetime.fromisoformat(published_at)
                except:
                    published_date = timezone.now()
            else:
                published_date = timezone.now()
            
            # Create slug
            slug = slugify(title)[:100]
            if News.objects.filter(slug=slug).exists():
                slug = f"{slug}-{article_id[:8]}"
            
            print(f"📸 Image URL: {image_url if image_url else 'No image'}")
            
            # Create news article with unique image
            news = News.objects.create(
                title=title[:200],
                slug=slug,
                description=description[:500] if description else 'No description available',
                content=content[:5000] if content else 'No content available',
                image_url=image_url,  # Each article gets its own unique image
                category=category_obj,
                author=author[:100] if author else 'Unknown',
                source=source[:100] if source else 'Unknown',
                source_url=url,
                published_date=published_date,
                created_at=timezone.now(),
                updated_at=timezone.now()
            )
            
            print(f"✅ Added: {news.title[:50]}... (Image: {'Yes' if image_url else 'No'})")
            return news
            
        except Exception as e:
            print(f"❌ Error processing article: {str(e)}")
            logger.error(f"Error processing article: {e}")
            return None
    
    def sync_news(self):
        """Synchronize news from all sources"""
        print("\n" + "="*60)
        print("🔄 STARTING NEWS SYNCHRONIZATION")
        print("="*60)
        
        if not self.apis:
            print("❌ No API keys configured!")
            return 0
        
        articles = self.fetch_all_sources()
        print(f"\n📝 Processing {len(articles)} articles...")
        print("-" * 40)
        
        added_count = 0
        updated_count = 0
        skipped_count = 0
        
        for article in articles:
            result = self.process_article(article)
            if result:
                added_count += 1
            else:
                skipped_count += 1
        
        print("-" * 40)
        print("\n" + "="*60)
        print("📊 SYNC COMPLETE")
        print("="*60)
        print(f"✅ Added: {added_count} new articles")
        print(f"🔄 Updated: {updated_count} articles")
        print(f"⏭️  Skipped: {skipped_count} articles")
        print(f"📰 Total news in database: {News.objects.count()}")
        print("="*60)
        
        logger.info(f"Added {added_count} new articles")
        return added_count

def sync_news():
    fetcher = NewsFetcher()
    return fetcher.sync_news()