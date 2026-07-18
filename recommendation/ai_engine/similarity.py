import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def calculate_article_similarity(news_item1, news_item2):
    """Calculate similarity between two news items"""
    # This function would be used for comparing specific articles
    # If we had the processed text, we could compute similarity
    pass

def find_similar_articles(news_id, news_data, similarity_matrix, n_similar=5):
    """Find similar articles to a given news item"""
    # Get index of the news item
    indices = news_data[news_data['id'] == news_id].index
    
    if len(indices) == 0:
        return []
    
    idx = indices[0]
    
    # Get similarity scores
    similarity_scores = list(enumerate(similarity_matrix[idx]))
    similarity_scores.sort(key=lambda x: x[1], reverse=True)
    
    # Get top similar articles (excluding self)
    similar_articles = []
    for i, score in similarity_scores[1:n_similar+1]:
        similar_articles.append({
            'id': news_data.iloc[i]['id'],
            'similarity_score': score
        })
    
    return similar_articles

def calculate_user_news_similarity(user_preferences, news_features):
    """Calculate similarity between user preferences and news features"""
    if not user_preferences or not news_features:
        return 0.0
    
    # Convert to numpy arrays
    user_vector = np.array(user_preferences).reshape(1, -1)
    news_vector = np.array(news_features).reshape(1, -1)
    
    # Calculate cosine similarity
    similarity = cosine_similarity(user_vector, news_vector)[0][0]
    return float(similarity)