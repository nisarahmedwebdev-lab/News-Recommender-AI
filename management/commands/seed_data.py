from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from news.models import Category, News
from django.utils import timezone
from faker import Faker
import random

User = get_user_model()
fake = Faker()

class Command(BaseCommand):
    help = 'Seed database with sample data'
    
    def handle(self, *args, **options):
        self.stdout.write('Seeding database...')
        
        # Create categories
        categories = [
            'AI', 'Technology', 'Sports', 'Business',
            'Health', 'Education', 'Entertainment', 'Politics'
        ]
        
        for cat_name in categories:
            Category.objects.get_or_create(
                name=cat_name,
                defaults={'description': f'All about {cat_name}'}
            )
        
        self.stdout.write('Categories created.')
        
        # Create sample users
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        
        for i in range(10):
            User.objects.get_or_create(
                username=f'user{i}',
                defaults={
                    'email': f'user{i}@example.com',
                    'password': 'password123',
                    'interests': random.choice(categories)
                }
            )
        
        self.stdout.write('Users created.')
        
        # Create sample news
        categories_list = list(Category.objects.all())
        
        for i in range(50):
            category = random.choice(categories_list)
            News.objects.get_or_create(
                title=fake.sentence(),
                defaults={
                    'description': fake.paragraph(),
                    'content': fake.text(max_nb_chars=500),
                    'image': 'news/default.jpg',  # You need to add a default image
                    'category': category,
                    'author': fake.name(),
                    'source': fake.company(),
                    'published_date': timezone.now() - timezone.timedelta(days=random.randint(0, 30))
                }
            )
        
        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))