from django.core.management.base import BaseCommand
from recommendation.ai_engine.advanced_recommender import AdvancedNewsRecommender

class Command(BaseCommand):
    help = 'Update news embeddings'

    def handle(self, *args, **options):
        self.stdout.write('Updating news embeddings...')
        
        recommender = AdvancedNewsRecommender()
        recommender.create_embeddings()
        
        self.stdout.write(self.style.SUCCESS('Embeddings updated successfully'))