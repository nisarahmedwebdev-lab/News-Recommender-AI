   
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import random
import string
class CustomUser(AbstractUser):
    INTEREST_CHOICES = [
        ('AI', 'Artificial Intelligence'),
        ('TECH', 'Technology'),
        ('SPORTS', 'Sports'),
        ('BUSINESS', 'Business'),
        ('HEALTH', 'Health'),
        ('EDUCATION', 'Education'),
        ('ENTERTAINMENT', 'Entertainment'),
        ('POLITICS', 'Politics'),
        ('SCIENCE', 'Science'),
        ('ENVIRONMENT', 'Environment'),
        ('TRAVEL', 'Travel'),
    ]
    
    email = models.EmailField(_('email address'), unique=True)
    profile_picture = models.ImageField(upload_to='profile/', null=True, blank=True)
    interests = models.CharField(max_length=100, choices=INTEREST_CHOICES, blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    
    # User behavior tracking fields
    reading_time = models.IntegerField(default=0)
    total_likes = models.IntegerField(default=0)
    total_saves = models.IntegerField(default=0)
    total_searches = models.IntegerField(default=0)
    
        
    email = models.EmailField(_('email address'), unique=True)
    profile_picture = models.ImageField(upload_to='profile/', null=True, blank=True)
    interests = models.CharField(max_length=100, choices=INTEREST_CHOICES, blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    
    # User behavior tracking fields
    reading_time = models.IntegerField(default=0)
    total_likes = models.IntegerField(default=0)
    total_saves = models.IntegerField(default=0)
    total_searches = models.IntegerField(default=0)
    
    def __str__(self):
        return self.username
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username

class PasswordResetOTP(models.Model):
    """Model to store OTP for password reset"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reset_otps')
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    attempts = models.IntegerField(default=0)
    max_attempts = models.IntegerField(default=5)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.otp} - {'Used' if self.is_used else 'Active'}"
    
    def is_valid(self):
        """Check if OTP is valid (not expired and not used)"""
        return not self.is_used and timezone.now() < self.expires_at
    
    def is_expired(self):
        """Check if OTP is expired"""
        return timezone.now() > self.expires_at
    
    def increment_attempts(self):
        """Increment failed attempts"""
        self.attempts += 1
        self.save()
        return self.attempts
    
    def mark_used(self):
        """Mark OTP as used"""
        self.is_used = True
        self.save()
    
    @staticmethod
    def generate_otp():
        """Generate a 6-digit OTP"""
        return ''.join(random.choices(string.digits, k=6))
    
    @staticmethod
    def create_otp(user):
        """Create a new OTP for user"""
        # Delete old unused OTPs for this user
        PasswordResetOTP.objects.filter(
            user=user,
            is_used=False,
            expires_at__lt=timezone.now()
        ).delete()
        
        # Generate OTP
        otp_code = PasswordResetOTP.generate_otp()
        
        # Create OTP with 10 minutes expiry
        otp = PasswordResetOTP.objects.create(
            user=user,
            otp=otp_code,
            expires_at=timezone.now() + timezone.timedelta(minutes=10)
        )
        
        return otp