import pandas as pd
import numpy as np
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import string
import logging

logger = logging.getLogger(__name__)

# Download required NLTK data with error handling
def download_nltk_resources():
    """Download NLTK resources with error handling"""
    resources = ['punkt', 'punkt_tab', 'stopwords', 'wordnet']
    for resource in resources:
        try:
            nltk.data.find(f'tokenizers/{resource}')
        except LookupError:
            try:
                nltk.download(resource, quiet=True)
                print(f"✅ Downloaded NLTK resource: {resource}")
            except Exception as e:
                print(f"⚠️ Could not download {resource}: {e}")

# Download resources on import
download_nltk_resources()

class TextPreprocessor:
    def __init__(self):
        self.stemmer = PorterStemmer()
        try:
            self.stop_words = set(stopwords.words('english'))
        except:
            # Fallback stopwords if NLTK fails
            self.stop_words = set(['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves',
                                 'you', "you're", "you've", "you'll", "you'd", 'your', 'yours',
                                 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she',
                                 "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself',
                                 'they', 'them', 'their', 'theirs', 'themselves', 'am', 'is', 'are',
                                 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having',
                                 'do', 'does', 'did', 'doing', 'will', 'would', 'shall', 'should',
                                 'may', 'might', 'must', 'a', 'an', 'the', 'and', 'but', 'if', 'or',
                                 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with',
                                 'without', 'after', 'before', 'upon', 'between', 'into', 'through',
                                 'during', 'including', 'among', 'to', 'from', 'in', 'on', 'off',
                                 'about', 'than', 'so', 'then', 'now', 'only', 'just', 'more', 'very',
                                 'too', 'also', 'well', 'over', 'under', 'above', 'below'])
        
        # Register custom tokenizer for safe fallback
        self.tokenizer = None
        try:
            # Try to load Punkt tokenizer
            self.tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
        except:
            logger.warning("Punkt tokenizer not available, using fallback tokenizer")
    
    def clean_text(self, text):
        """Clean and preprocess text"""
        if pd.isna(text):
            return ""
        
        # Convert to lowercase
        text = str(text).lower()
        
        # Remove URLs
        text = re.sub(r'https?://\S+|www\.\S+', '', text)
        
        # Remove special characters and digits
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def tokenize(self, text):
        """Tokenize text into words with fallback"""
        if not text:
            return []
        
        try:
            # Try using NLTK tokenizer
            return word_tokenize(text)
        except:
            # Fallback: simple split tokenizer
            return text.split()
    
    def remove_stopwords(self, tokens):
        """Remove stopwords from token list"""
        return [token for token in tokens if token not in self.stop_words]
    
    def stem_words(self, tokens):
        """Stem tokens"""
        try:
            return [self.stemmer.stem(token) for token in tokens]
        except:
            return tokens
    
    def preprocess(self, text):
        """Complete preprocessing pipeline"""
        try:
            text = self.clean_text(text)
            tokens = self.tokenize(text)
            tokens = self.remove_stopwords(tokens)
            tokens = self.stem_words(tokens)
            return ' '.join(tokens)
        except Exception as e:
            logger.error(f"Error in preprocess: {e}")
            return text
    
    def preprocess_dataframe(self, df, text_column='content'):
        """Preprocess a dataframe column"""
        df['processed_text'] = df[text_column].apply(self.preprocess)
        return df