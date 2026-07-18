from django.core.management.base import BaseCommand
from news.fetcher import sync_news
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Synchronize news from external APIs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--once',
            action='store_true',
            help='Run sync only once and exit',
        )

    def handle(self, *args, **options):
        self.stdout.write('🔄 Starting news synchronization...')
        
        try:
            added = sync_news()
            self.stdout.write(self.style.SUCCESS(f'✅ Added {added} new articles'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error: {str(e)}'))