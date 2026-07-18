from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .forms import (
    CustomUserCreationForm, UserProfileForm, 
    ForgotPasswordForm, OTPVerificationForm, ResetPasswordForm
)
from .models import CustomUser, PasswordResetOTP
import json
import random
import string

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to News AI!')
            return redirect('dashboard:home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return HttpResponseRedirect(reverse('dashboard:home'))
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('landing')

@login_required
def profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'accounts/profile.html', {'form': form})

# ========== PASSWORD RESET WITH OTP ==========

def forgot_password(request):
    """Step 1: User enters email to receive OTP"""
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = CustomUser.objects.get(email=email)
            
            # Create OTP
            otp = PasswordResetOTP.create_otp(user)
            
            # Send OTP via email
            try:
                send_mail(
                    subject='Password Reset OTP - News AI',
                    message=f"""
Dear {user.username},

You have requested to reset your password for your News AI account.

Your OTP for password reset is: {otp.otp}

This OTP is valid for 10 minutes.

If you did not request this, please ignore this email.

Best regards,
The News AI Team
""",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,
                )
                
                # Store email in session for OTP verification
                request.session['reset_email'] = email
                request.session['reset_otp_created'] = timezone.now().isoformat()
                
                messages.success(request, 'A verification code has been sent to your email.')
                return redirect('accounts:verify_otp')
                
            except Exception as e:
                messages.error(request, f'Failed to send OTP. Please try again. Error: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ForgotPasswordForm()
    
    return render(request, 'accounts/forgot_password.html', {'form': form})

def verify_otp(request):
    """Step 2: User verifies OTP"""
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    
    # Check if email is in session
    email = request.session.get('reset_email')
    if not email:
        messages.error(request, 'Please request a password reset first.')
        return redirect('accounts:forgot_password')
    
    try:
        user = CustomUser.objects.get(email=email)
    except CustomUser.DoesNotExist:
        messages.error(request, 'User not found. Please try again.')
        return redirect('accounts:forgot_password')
    
    if request.method == 'POST':
        form = OTPVerificationForm(request.POST, user=user)
        if form.is_valid():
            otp_record = form.otp_record
            otp_record.mark_used()
            
            # Store user ID in session for password reset
            request.session['reset_user_id'] = user.id
            
            messages.success(request, 'OTP verified successfully! Please set your new password.')
            return redirect('accounts:reset_password')
        else:
            messages.error(request, 'Invalid OTP. Please try again.')
    else:
        form = OTPVerificationForm(user=user)
    
    # Get remaining time for OTP
    otp_record = PasswordResetOTP.objects.filter(
        user=user,
        is_used=False,
        expires_at__gt=timezone.now()
    ).first()
    
    remaining_time = 0
    if otp_record:
        remaining_time = int((otp_record.expires_at - timezone.now()).total_seconds())
    
    context = {
        'form': form,
        'email': email,
        'remaining_time': remaining_time
    }
    return render(request, 'accounts/verify_otp.html', context)

def resend_otp(request):
    """Resend OTP to user's email"""
    if request.user.is_authenticated:
        return JsonResponse({'error': 'Already logged in'}, status=400)
    
    email = request.session.get('reset_email')
    if not email:
        return JsonResponse({'error': 'No email found in session'}, status=400)
    
    try:
        user = CustomUser.objects.get(email=email)
    except CustomUser.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=400)
    
    # Check cooldown (60 seconds)
    otp_created = request.session.get('reset_otp_created')
    if otp_created:
        created_time = timezone.datetime.fromisoformat(otp_created)
        if (timezone.now() - created_time).total_seconds() < 60:
            return JsonResponse({
                'error': 'Please wait 60 seconds before requesting a new OTP.'
            }, status=429)
    
    # Create new OTP
    otp = PasswordResetOTP.create_otp(user)
    
    # Send OTP via email
    try:
        send_mail(
            subject='New Password Reset OTP - News AI',
            message=f"""
Dear {user.username},

You have requested a new OTP for password reset.

Your new OTP is: {otp.otp}

This OTP is valid for 10 minutes.

If you did not request this, please ignore this email.

Best regards,
The News AI Team
""",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        
        # Update session
        request.session['reset_otp_created'] = timezone.now().isoformat()
        
        return JsonResponse({
            'success': True,
            'message': 'New OTP sent to your email.'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def reset_password(request):
    """Step 3: User sets new password after OTP verification"""
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    
    # Check if user ID is in session
    user_id = request.session.get('reset_user_id')
    if not user_id:
        messages.error(request, 'Please verify your OTP first.')
        return redirect('accounts:forgot_password')
    
    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        messages.error(request, 'User not found. Please try again.')
        return redirect('accounts:forgot_password')
    
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            
            # Set new password
            user.set_password(new_password)
            user.save()
            
            # Clear session
            request.session.pop('reset_email', None)
            request.session.pop('reset_user_id', None)
            request.session.pop('reset_otp_created', None)
            
            messages.success(request, 'Your password has been reset successfully. Please log in with your new password.')
            return redirect('accounts:login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ResetPasswordForm()
    
    return render(request, 'accounts/reset_password.html', {'form': form})

def check_otp_status(request):
    """AJAX endpoint to check OTP status"""
    if request.user.is_authenticated:
        return JsonResponse({'error': 'Already logged in'}, status=400)
    
    email = request.session.get('reset_email')
    if not email:
        return JsonResponse({'error': 'No email found'}, status=400)
    
    try:
        user = CustomUser.objects.get(email=email)
    except CustomUser.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=400)
    
    otp_record = PasswordResetOTP.objects.filter(
        user=user,
        is_used=False,
        expires_at__gt=timezone.now()
    ).first()
    
    if otp_record:
        remaining_time = int((otp_record.expires_at - timezone.now()).total_seconds())
        return JsonResponse({
            'exists': True,
            'remaining_time': remaining_time,
            'attempts': otp_record.attempts,
            'max_attempts': otp_record.max_attempts
        })
    else:
        return JsonResponse({'exists': False})