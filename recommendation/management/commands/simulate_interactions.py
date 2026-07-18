from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from news.models import News, Like, Bookmark, UserBehavior
from django.utils import timezone
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Simulate user interactions for testing recommendations'

    def handle(self, *args, **options):
        self.stdout.write('Simulating user interactions...')
        
        # Get users
        users = User.objects.filter(is_superuser=False)
        if not users:
            self.stdout.write('No users found!')
            return
        
        # Get all news
        all_news = list(News.objects.all())
        if not all_news:
            self.stdout.write('No news found!')
            return
        
        for user in users:
            # Get user's interest category
            if user.interests:
                interest_news = [n for n in all_news if n.category.name.lower() == user.interests.lower()]
            else:
                interest_news = all_news
            
            # Simulate interactions
            if interest_news:
                # Like some news from interest category
                for news in random.sample(interest_news, min(5, len(interest_news))):
                    Like.objects.get_or_create(user=user, news=news)
                    self.stdout.write(f'{user.username} liked: {news.title[:30]}...')
                
                # Save some news
                for news in random.sample(interest_news, min(3, len(interest_news))):
                    Bookmark.objects.get_or_create(user=user, news=news)
                    self.stdout.write(f'{user.username} saved: {news.title[:30]}...')
                
                # View some news
                for news in random.sample(interest_news, min(10, len(interest_news))):
                    UserBehavior.objects.create(
                        user=user,
                        news=news,
                        behavior_type='VIEW',
                        timestamp=timezone.now()
                    )
                    self.stdout.write(f'{user.username} viewed: {news.title[:30]}...')
        
        self.stdout.write(self.style.SUCCESS('Interactions simulated successfully!'))