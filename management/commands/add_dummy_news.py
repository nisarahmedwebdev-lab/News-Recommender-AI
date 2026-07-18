from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify
from news.models import Category, News
from django.contrib.auth import get_user_model
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Add dummy news articles to the database'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to add dummy news...'))
        
        # Get or create default user
        user, created = User.objects.get_or_create(
            username='nisar',
            defaults={
                'email': 'nisar@example.com',
                'first_name': 'Nisar',
                'last_name': 'News',
                'is_staff': True,
                'is_active': True
            }
        )
        if created:
            user.set_password('nisar123456')
            user.save()
            self.stdout.write(self.style.SUCCESS(f'User "nisar" created with password "nisar123456"'))
        
        # Get or create categories
        category_names = ['Technology', 'Sports', 'Health', 'Business', 'Education', 
                         'Science', 'Entertainment', 'Environment', 'Politics', 'Travel']
        
        categories = {}
        for cat_name in category_names:
            category, created = Category.objects.get_or_create(
                name=cat_name,
                defaults={
                    'description': f'All about {cat_name}',
                    'is_active': True
                }
            )
            categories[cat_name] = category
            if created:
                self.stdout.write(self.style.SUCCESS(f'Category "{cat_name}" created'))
        
        # Dummy news data
        dummy_news = [
            {
                'title': 'AI-Powered Smart Glasses Set to Transform Daily Life',
                'category': 'Technology',
                'author': 'Nisar News Desk',
                'published_date': timezone.now() - timezone.timedelta(days=0),
                'description': 'Artificial Intelligence continues to reshape the technology industry with the introduction of next-generation smart glasses capable of translating conversations, recognizing objects, and providing real-time navigation.',
                'content': """Artificial Intelligence continues to reshape the technology industry with the introduction of next-generation smart glasses capable of translating conversations, recognizing objects, and providing real-time navigation. Technology companies are investing billions of dollars in wearable devices that combine augmented reality with AI-powered assistants.

The new generation of smart glasses features voice commands, gesture recognition, and cloud-based processing. Users can ask questions, receive directions, identify landmarks, and even summarize meetings without touching a smartphone. Experts believe these devices could replace smartphones for many everyday tasks within the next decade.

Despite the excitement, privacy experts have raised concerns regarding facial recognition and continuous recording. Governments around the world are expected to introduce regulations to ensure responsible use of wearable AI technology."""
            },
            {
                'title': 'Local Football Club Wins National Championship After Dramatic Final',
                'category': 'Sports',
                'author': 'Sports Reporter',
                'published_date': timezone.now() - timezone.timedelta(days=1),
                'description': 'Thousands of fans celebrated after the city\'s football club secured the National Championship with a thrilling 3-2 victory in the final match.',
                'content': """Thousands of fans celebrated after the city's football club secured the National Championship with a thrilling 3-2 victory in the final match. The winning goal was scored during extra time, ending one of the most exciting championship games in recent years.

The team's coach praised the players for their discipline, teamwork, and determination throughout the tournament. Supporters gathered across the city to celebrate the historic victory with parades, fireworks, and community events.

Sports analysts described the final as a perfect example of competitive football and predicted that several players from the winning squad could receive international opportunities."""
            },
            {
                'title': 'Doctors Encourage Healthy Lifestyle to Reduce Heart Disease',
                'category': 'Health',
                'author': 'Health Correspondent',
                'published_date': timezone.now() - timezone.timedelta(days=2),
                'description': 'Medical professionals are encouraging people to adopt healthier lifestyles after recent studies highlighted the growing number of heart disease cases worldwide.',
                'content': """Medical professionals are encouraging people to adopt healthier lifestyles after recent studies highlighted the growing number of heart disease cases worldwide. Experts recommend regular exercise, balanced nutrition, reduced sugar intake, and routine medical checkups.

Hospitals have launched awareness campaigns emphasizing the importance of early diagnosis and preventive healthcare. Specialists advise adults to monitor blood pressure, cholesterol levels, and blood sugar regularly.

Healthcare organizations believe that small lifestyle improvements can significantly reduce the risk of cardiovascular diseases while improving overall quality of life."""
            },
            {
                'title': 'Small Businesses Experience Strong Growth Through Online Commerce',
                'category': 'Business',
                'author': 'Business Desk',
                'published_date': timezone.now() - timezone.timedelta(days=3),
                'description': 'Small businesses continue expanding their customer base through digital marketplaces and social media platforms.',
                'content': """Small businesses continue expanding their customer base through digital marketplaces and social media platforms. Entrepreneurs are increasingly investing in online stores, digital payment systems, and targeted advertising campaigns.

Business experts report that consumers now prefer convenient online shopping experiences, creating new opportunities for startups and local retailers. Many companies have successfully expanded internationally using e-commerce platforms.

Financial advisors encourage business owners to focus on customer service, product quality, and digital marketing to remain competitive in the evolving marketplace."""
            },
            {
                'title': 'Universities Introduce AI Courses to Prepare Future Professionals',
                'category': 'Education',
                'author': 'Education Desk',
                'published_date': timezone.now() - timezone.timedelta(days=4),
                'description': 'Universities are expanding their computer science programs by introducing Artificial Intelligence, Machine Learning, and Data Science courses.',
                'content': """Universities are expanding their computer science programs by introducing Artificial Intelligence, Machine Learning, and Data Science courses. The goal is to prepare students for the rapidly growing technology sector.

Faculty members believe practical projects, internships, and industry collaborations will help students gain valuable real-world experience before graduation. Educational institutions are also investing in AI laboratories and research centers.

Students have welcomed the initiative, saying the new curriculum will improve career opportunities and enhance technical skills."""
            },
            {
                'title': 'Scientists Discover New Eco-Friendly Battery Technology',
                'category': 'Science',
                'author': 'Science Reporter',
                'published_date': timezone.now() - timezone.timedelta(days=5),
                'description': 'Researchers have announced a breakthrough in battery technology that could significantly improve renewable energy storage.',
                'content': """Researchers have announced a breakthrough in battery technology that could significantly improve renewable energy storage. The newly developed batteries use environmentally friendly materials while offering longer lifespan and faster charging speeds.

Scientists believe the innovation could benefit electric vehicles, solar energy systems, and portable electronics. Initial laboratory tests have shown promising efficiency and safety results.

Further research and commercial production are expected over the coming years before the technology reaches consumers worldwide."""
            },
            {
                'title': 'International Film Festival Celebrates Emerging Young Directors',
                'category': 'Entertainment',
                'author': 'Entertainment News',
                'published_date': timezone.now() - timezone.timedelta(days=6),
                'description': 'The annual International Film Festival attracted filmmakers from over fifty countries, showcasing creative storytelling and innovative cinematography.',
                'content': """The annual International Film Festival attracted filmmakers from over fifty countries, showcasing creative storytelling and innovative cinematography. Young directors received recognition for producing films addressing social issues, environmental challenges, and cultural diversity.

Audiences praised the festival's diverse selection of documentaries, dramas, and animated films. Industry professionals believe such events help emerging talent gain international recognition.

Organizers announced plans to expand next year's festival with additional workshops and networking opportunities."""
            },
            {
                'title': 'Nationwide Tree Plantation Campaign Aims to Improve Air Quality',
                'category': 'Environment',
                'author': 'Environmental Desk',
                'published_date': timezone.now() - timezone.timedelta(days=7),
                'description': 'Environmental organizations have launched a nationwide tree plantation campaign encouraging schools, universities, and local communities to participate.',
                'content': """Environmental organizations have launched a nationwide tree plantation campaign encouraging schools, universities, and local communities to participate in increasing green spaces.

Experts explain that planting trees helps reduce pollution, improve biodiversity, and minimize the effects of climate change. Thousands of volunteers joined the campaign during its opening week.

Officials hope the initiative will inspire long-term environmental responsibility and encourage sustainable urban development."""
            },
            {
                'title': 'Government Announces New Digital Public Service Initiative',
                'category': 'Politics',
                'author': 'Political Correspondent',
                'published_date': timezone.now() - timezone.timedelta(days=8),
                'description': 'Government officials introduced a nationwide digital services platform designed to simplify access to public services.',
                'content': """Government officials introduced a nationwide digital services platform designed to simplify access to public services. Citizens will be able to submit applications, track requests, and receive official notifications through a centralized online portal.

The initiative aims to improve transparency, reduce paperwork, and increase efficiency across government departments. Authorities stated that cybersecurity and data privacy remain top priorities.

Public feedback will be collected during the pilot phase before nationwide implementation."""
            },
            {
                'title': 'Tourism Industry Sees Significant Increase in Domestic Travelers',
                'category': 'Travel',
                'author': 'Travel Desk',
                'published_date': timezone.now() - timezone.timedelta(days=9),
                'description': 'The tourism sector has experienced strong growth as more families choose domestic destinations for vacations.',
                'content': """The tourism sector has experienced strong growth as more families choose domestic destinations for vacations. Hotels, restaurants, and local businesses have reported increased bookings throughout the summer season.

Travel experts attribute the growth to improved transportation infrastructure, affordable travel packages, and promotional campaigns highlighting historical landmarks and natural attractions.

Industry leaders expect the positive trend to continue as travelers increasingly seek safe, affordable, and culturally rich experiences within the country."""
            }
        ]

        # Add news
        added_count = 0
        for data in dummy_news:
            category = categories.get(data['category'])
            if not category:
                self.stdout.write(self.style.WARNING(f'Category "{data["category"]}" not found, skipping...'))
                continue
            
            # Create slug from title
            slug = slugify(data['title'])
            
            # Check if news already exists
            if News.objects.filter(slug=slug).exists():
                self.stdout.write(self.style.WARNING(f'News "{data["title"]}" already exists, skipping...'))
                continue
            
            # Create news
            news = News(
                title=data['title'],
                slug=slug,
                description=data['description'],
                content=data['content'],
                category=category,
                author=data['author'],
                author_user=user,
                published_date=data['published_date'],
                views=random.randint(10, 1000),
                likes_count=random.randint(5, 500),
                saves_count=random.randint(2, 200),
                comments_count=random.randint(1, 50)
            )
            news.save()
            added_count += 1
            self.stdout.write(self.style.SUCCESS(f'Added: {news.title}'))

        self.stdout.write(self.style.SUCCESS(f'\n✅ Successfully added {added_count} dummy news articles!'))
        self.stdout.write(self.style.SUCCESS(f'📊 Total news in database: {News.objects.count()}'))