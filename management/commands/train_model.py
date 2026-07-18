from django.core.management.base import BaseCommand
from django.conf import settings
from recommendation.ai_engine.recommender import NewsRecommender

class Command(BaseCommand):
    help = 'Train the recommendation model'
    
    def handle(self, *args, **options):
        self.stdout.write('Starting model training...')
        
        try:
            # Initialize recommender
            recommender = NewsRecommender()
            
            # Load and preprocess data
            self.stdout.write('Loading news data...')
            recommender.load_and_preprocess_news()
            
            # Build TF-IDF matrix
            self.stdout.write('Building TF-IDF matrix...')
            recommender.build_tfidf_matrix()
            
            # Save model
            model_path = settings.AI_MODEL_PATH / 'recommendation.pkl'
            self.stdout.write(f'Saving model to {model_path}...')
            recommender.save_model(model_path)
            
            self.stdout.write(self.style.SUCCESS('Model training completed successfully!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error during training: {e}'))