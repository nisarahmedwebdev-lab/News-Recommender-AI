# 📰 AI-Powered Personalized News Feed Recommender System

A Django-based intelligent news recommendation platform that uses machine learning to deliver personalized news content based on user behavior, interests, and reading history. Similar to Twitter, Facebook, TikTok, and YouTube recommendation algorithms.

![Django](https://img.shields.io/badge/Django-5.0-green)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)
![AI](https://img.shields.io/badge/AI-Machine_Learning-purple)
![Frontend](https://img.shields.io/badge/Frontend-Bootstrap_5-orange)

---

## 📌 Features

### 🔐 Authentication & User Management
- User Registration & Login
- Password Reset with OTP
- User Profile Management
- Profile Picture Upload
- Interest Selection

### 📰 News Feed
- Personalized AI-Powered Recommendations
- Category-based Filtering
- Search Functionality
- Full-width News Cards
- Read More / Detail View
- Trending News Section

### 💬 User Engagement
- Like/Unlike Posts (AJAX)
- Save/Unsave Posts (Bookmark)
- Comment System
- Reading Time Tracking
- View Counter

### 🤖 AI Recommendation Engine
- TF-IDF Vectorization
- Cosine Similarity
- Content-Based Filtering
- User Behavior Analysis
- Category Preference Learning
- Hybrid Recommendation Approach
- Sentence Transformers (BERT)

### 📊 Analytics Dashboard
- User Reading Statistics
- Category Preferences
- Reading History
- Engagement Metrics

### 🛠️ Admin Panel
- Manage Users
- Manage Categories
- Manage News
- View Reports
- AI Model Training

### 🌐 News Integration
- Automatic News Fetching from APIs
- NewsAPI Integration
- GNews Integration
- MediaStack Integration

---

## 🏗️ Technology Stack

| Category | Technology |
|----------|------------|
| **Backend** | Django 5.0 |
| **Frontend** | HTML5, CSS3, Bootstrap 5 |
| **Database** | SQLite (Development) / PostgreSQL (Production) |
| **AI/ML** | Scikit-learn, Pandas, NumPy, NLTK |
| **Recommendation** | TF-IDF, Cosine Similarity, Sentence Transformers |
| **Authentication** | Django Authentication |
| **Charts** | Chart.js |
| **Notifications** | SweetAlert2 |
| **Icons** | Font Awesome 6 |
| **API Integration** | Requests Library |
| **Version Control** | Git |

---

## 🚀 Installation & Setup

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Virtual Environment (recommended)
- Git (for cloning)

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/News-Recommender-AI.git
cd News-Recommender-AI

# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate

# Install all dependencies
pip install -r requirements.txt

# If requirements.txt not found, install manually
pip install Django==5.0.6
pip install pandas==2.2.2
pip install numpy==1.26.4
pip install scikit-learn==1.4.2
pip install nltk==3.8.1
pip install joblib==1.4.2
pip install Pillow==10.3.0
pip install python-decouple==3.8
pip install django-crispy-forms==2.1
pip install crispy-bootstrap5==0.7
pip install requests==2.31.0
pip install Faker==25.8.0


# Make migrations
python manage.py makemigrations accounts
python manage.py makemigrations news
python manage.py makemigrations recommendation
python manage.py makemigrations dashboard

# Apply migrations
python manage.py migrate

python manage.py createsuperuser

# Add demo news articles
python manage.py add_demo_news

# Train the recommendation model
python manage.py train_recommendation

# Sync news from APIs (requires API keys)
python manage.py sync_news


python manage.py collectstatic

# Run the Server
python manage.py runserver

# Add Dummy News
python manage.py add_demo_news

# Train Recommendation Model

# Auto Sync News (Every 30 minutes)
python manage.py auto_sync_news --loop
