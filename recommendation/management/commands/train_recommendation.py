from django.core.management.base import BaseCommand
from django.conf import settings
from recommendation.ai_engine.simple_recommender import SimpleRecommender
from news.models import News, Category
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Train the recommendation model with latest data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force retraining even if model exists',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting recommendation model training...'))
        
        try:
            # Check if news exists
            total_news = News.objects.count()
            self.stdout.write(f'📊 Found {total_news} news articles in database')
            
            if total_news == 0:
                self.stdout.write(self.style.WARNING('⚠️ No news found! Please add news first.'))
                self.stdout.write('Run: python manage.py add_demo_news')
                return
            
            # Initialize recommender
            from recommendation.ai_engine.simple_recommender import SimpleRecommender
            recommender = SimpleRecommender()
            
            # Load and preprocess news
            self.stdout.write('📂 Loading news data...')
            recommender.load_news_data()
            
            # Build TF-IDF matrix
            self.stdout.write('🔨 Building TF-IDF matrix...')
            recommender.build_tfidf_matrix()
            
            # Build category vectors
            self.stdout.write('📊 Building category vectors...')
            recommender.build_category_vectors()
            
            # Save model
            model_path = settings.AI_MODEL_PATH / 'recommendation.pkl'
            self.stdout.write(f'💾 Saving model to {model_path}...')
            recommender.save_model(model_path)
            
            self.stdout.write(self.style.SUCCESS('✅ Model training completed successfully!'))
            self.stdout.write(self.style.SUCCESS(f'📊 Total news processed: {total_news}'))
            self.stdout.write(self.style.SUCCESS(f'📂 Categories: {Category.objects.count()}'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error during training: {e}'))
            import traceback
            traceback.print_exc()
            logger.error(f"Training error: {e}")