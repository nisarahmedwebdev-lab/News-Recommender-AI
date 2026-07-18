"""
Image utility functions for news articles
Handles image loading, validation, and fallback strategies
"""

import requests
import logging
from urllib.parse import urljoin, urlparse
from django.core.files.base import ContentFile
from PIL import Image
from io import BytesIO

logger = logging.getLogger(__name__)


class ImageHandler:
    """Handle image loading, validation, and processing"""
    
    # Default placeholder images for different scenarios
    PLACEHOLDER_COLORS = {
        'default': '#667eea',
        'error': '#ef4444',
        'loading': '#f59e0b',
    }
    
    @staticmethod
    def is_valid_image_url(url):
        """
        Check if a URL is a valid image URL
        
        Args:
            url (str): The URL to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not url:
            return False
        
        # Check if URL starts with http
        if not url.startswith(('http://', 'https://')):
            return False
        
        # Parse URL
        try:
            parsed = urlparse(url)
            if not parsed.netloc:
                return False
        except:
            return False
        
        # Check if URL has image extension or is a known image service
        image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp')
        if url.lower().endswith(image_extensions):
            return True
        
        # Check if it's from a known image service
        image_hosts = (
            'unsplash.com',
            'pexels.com',
            'pixabay.com',
            'imgur.com',
            'imageserver',
            'images',
            'cdn',
        )
        
        if any(host in url.lower() for host in image_hosts):
            return True
        
        return False
    
    @staticmethod
    def verify_image_url(url, timeout=5):
        """
        Verify that an image URL is accessible
        
        Args:
            url (str): The URL to verify
            timeout (int): Request timeout in seconds
            
        Returns:
            bool: True if accessible, False otherwise
        """
        if not ImageHandler.is_valid_image_url(url):
            return False
        
        try:
            response = requests.head(url, timeout=timeout, allow_redirects=True)
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                if 'image' in content_type:
                    return True
            else:
                # Try GET request if HEAD fails
                response = requests.get(url, timeout=timeout, allow_redirects=True, stream=True)
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '')
                    if 'image' in content_type:
                        return True
        except requests.exceptions.RequestException as e:
            logger.warning(f"Could not verify image URL {url}: {e}")
        except Exception as e:
            logger.error(f"Error verifying image URL {url}: {e}")
        
        return False
    
    @staticmethod
    def get_image_from_url(url, timeout=5):
        """
        Download image from URL and return PIL Image object
        
        Args:
            url (str): The image URL
            timeout (int): Request timeout in seconds
            
        Returns:
            PIL.Image: Image object or None if failed
        """
        try:
            response = requests.get(url, timeout=timeout, allow_redirects=True, stream=True)
            response.raise_for_status()
            
            # Verify it's an image
            content_type = response.headers.get('content-type', '')
            if 'image' not in content_type:
                logger.warning(f"URL {url} is not an image (content-type: {content_type})")
                return None
            
            # Open image
            img = Image.open(BytesIO(response.content))
            
            # Validate image
            img.verify()
            
            # Reopen since verify() closes the image
            img = Image.open(BytesIO(response.content))
            
            return img
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Could not download image from {url}: {e}")
        except Exception as e:
            logger.error(f"Error processing image from {url}: {e}")
        
        return None
    
    @staticmethod
    def get_best_image_url(news):
        """
        Get the best available image URL for a news article
        Priority:
        1. External image_url
        2. Uploaded image
        3. None (will use placeholder)
        
        Args:
            news (News): News object
            
        Returns:
            str: Best available image URL or None
        """
        # Priority 1: External URL if it exists and is valid
        if news.image_url and ImageHandler.is_valid_image_url(news.image_url):
            return news.image_url
        
        # Priority 2: Uploaded image
        if news.image and hasattr(news.image, 'url'):
            return news.image.url
        
        # No valid image
        return None
    
    @staticmethod
    def get_image_placeholder_url(color='default'):
        """
        Get a placeholder image URL
        
        Args:
            color (str): Color key ('default', 'error', 'loading')
            
        Returns:
            str: SVG placeholder URL
        """
        hex_color = ImageHandler.PLACEHOLDER_COLORS.get(color, '#667eea')
        
        # Create simple SVG placeholder
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="400" height="300" viewBox="0 0 400 300">
            <rect width="400" height="300" fill="{hex_color}"/>
            <text x="50%" y="50%" font-size="24" font-family="Arial" fill="white" text-anchor="middle" dominant-baseline="middle">
                Image Not Available
            </text>
        </svg>'''
        
        return f"data:image/svg+xml;base64,{__import__('base64').b64encode(svg.encode()).decode()}"


# Utility functions for templates
def get_image_url(news):
    """Template filter to get best image URL for news"""
    return ImageHandler.get_best_image_url(news) or ImageHandler.get_image_placeholder_url()


def image_url_or_placeholder(image_url):
    """Template filter to validate image URL or return placeholder"""
    if ImageHandler.is_valid_image_url(image_url):
        return image_url
    return ImageHandler.get_image_placeholder_url()
