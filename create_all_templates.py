import os

# Create necessary directories
directories = [
    'templates',
    'accounts/templates/accounts',
    'news/templates/news',
    'recommendation/templates/recommendation',
    'dashboard/templates/dashboard',
]

for dir_path in directories:
    os.makedirs(dir_path, exist_ok=True)
    print(f"Created: {dir_path}")

# ============================================
# 1. BASE TEMPLATE (already exists, but let's ensure it's complete)
# ============================================
with open('templates/base.html', 'w', encoding='utf-8') as f:
    f.write('''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}News AI - Personalized News Feed{% endblock %}</title>
    
    <!-- Bootstrap 5 -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Font Awesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    
    {% load static %}
    <link rel="stylesheet" href="{% static 'css/style.css' %}">
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary sticky-top">
        <div class="container">
            <a class="navbar-brand" href="{% url 'dashboard:home' %}">
                <i class="fas fa-newspaper me-2"></i>News AI
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav me-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="{% url 'dashboard:home' %}">
                            <i class="fas fa-home"></i> Dashboard
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{% url 'recommendation:feed' %}">
                            <i class="fas fa-robot"></i> AI Feed
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{% url 'news:list' %}">
                            <i class="fas fa-list"></i> All News
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{% url 'news:categories' %}">
                            <i class="fas fa-tags"></i> Categories
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{% url 'news:saved' %}">
                            <i class="fas fa-bookmark"></i> Saved
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{% url 'recommendation:trending' %}">
                            <i class="fas fa-fire"></i> Trending
                        </a>
                    </li>
                </ul>
                
                <!-- Search -->
                <form class="d-flex me-3" action="{% url 'news:search' %}" method="get">
                    <input class="form-control me-2" type="search" name="q" placeholder="Search news..." aria-label="Search">
                    <button class="btn btn-outline-light" type="submit">
                        <i class="fas fa-search"></i>
                    </button>
                </form>
                
                <!-- User Menu -->
                <ul class="navbar-nav">
                    {% if user.is_authenticated %}
                        <li class="nav-item dropdown">
                            <a class="nav-link dropdown-toggle" href="#" id="userDropdown" role="button" data-bs-toggle="dropdown">
                                {% if user.profile_picture %}
                                    <img src="{{ user.profile_picture.url }}" class="rounded-circle" width="32" height="32" alt="Profile">
                                {% else %}
                                    <i class="fas fa-user-circle fa-2x"></i>
                                {% endif %}
                            </a>
                            <ul class="dropdown-menu dropdown-menu-end">
                                <li><a class="dropdown-item" href="{% url 'accounts:profile' %}">
                                    <i class="fas fa-user me-2"></i>Profile
                                </a></li>
                                <li><a class="dropdown-item" href="{% url 'recommendation:analytics' %}">
                                    <i class="fas fa-chart-bar me-2"></i>Analytics
                                </a></li>
                                <li><hr class="dropdown-divider"></li>
                                <li><a class="dropdown-item text-danger" href="{% url 'accounts:logout' %}">
                                    <i class="fas fa-sign-out-alt me-2"></i>Logout
                                </a></li>
                            </ul>
                        </li>
                    {% else %}
                        <li class="nav-item">
                            <a class="nav-link" href="{% url 'accounts:login' %}">
                                <i class="fas fa-sign-in-alt me-1"></i>Login
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{% url 'accounts:register' %}">
                                <i class="fas fa-user-plus me-1"></i>Register
                            </a>
                        </li>
                    {% endif %}
                </ul>
            </div>
        </div>
    </nav>

    <!-- Messages -->
    <div class="container mt-3">
        {% if messages %}
            {% for message in messages %}
                <div class="alert alert-{{ message.tags }} alert-dismissible fade show" role="alert">
                    <i class="fas fa-{% if message.tags == 'success' %}check-circle{% elif message.tags == 'error' %}times-circle{% elif message.tags == 'warning' %}exclamation-triangle{% else %}info-circle{% endif %} me-2"></i>
                    {{ message }}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            {% endfor %}
        {% endif %}
    </div>

    <!-- Main Content -->
    <main class="py-4">
        {% block content %}{% endblock %}
    </main>

    <!-- Footer -->
    <footer class="bg-dark text-white py-4 mt-5">
        <div class="container text-center">
            <p class="mb-0">© 2024 AI-Powered News Recommender System</p>
            <small class="text-muted">Built with Django, AI & Machine Learning</small>
        </div>
    </footer>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <!-- Custom JS -->
    <script src="{% static 'js/main.js' %}"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>''')
print("✅ Created: templates/base.html")

# ============================================
# 2. ACCOUNTS TEMPLATES
# ============================================

# login.html
with open('accounts/templates/accounts/login.html', 'w', encoding='utf-8') as f:
    f.write('''{% extends 'base.html' %}

{% block title %}Login - News AI{% endblock %}

{% block content %}
<div class="container">
    <div class="row justify-content-center">
        <div class="col-md-6 col-lg-5">
            <div class="card shadow fade-in-up">
                <div class="card-header bg-primary text-white text-center py-3">
                    <h4 class="mb-0"><i class="fas fa-sign-in-alt me-2"></i>Login</h4>
                </div>
                <div class="card-body p-4">
                    <form method="post" novalidate>
                        {% csrf_token %}
                        
                        <div class="mb-3">
                            <label for="username" class="form-label">Username</label>
                            <div class="input-group">
                                <span class="input-group-text"><i class="fas fa-user"></i></span>
                                <input type="text" name="username" id="username" class="form-control" 
                                       placeholder="Enter username" required autofocus>
                            </div>
                        </div>
                        
                        <div class="mb-3">
                            <label for="password" class="form-label">Password</label>
                            <div class="input-group">
                                <span class="input-group-text"><i class="fas fa-lock"></i></span>
                                <input type="password" name="password" id="password" class="form-control" 
                                       placeholder="Enter password" required>
                            </div>
                        </div>
                        
                        <div class="d-grid gap-2">
                            <button type="submit" class="btn btn-primary btn-lg">
                                <i class="fas fa-sign-in-alt me-2"></i>Login
                            </button>
                        </div>
                    </form>
                    
                    <hr class="my-4">
                    
                    <div class="text-center">
                        <p class="mb-2">
                            <a href="{% url 'accounts:password_reset' %}" class="text-decoration-none">
                                <i class="fas fa-key me-1"></i>Forgot Password?
                            </a>
                        </p>
                        <p class="mb-0">
                            Don't have an account? 
                            <a href="{% url 'accounts:register' %}" class="text-decoration-none fw-bold">
                                Register Here
                            </a>
                        </p>
                    </div>
                </div>
            </div>
            
            <div class="text-center mt-3">
                <small class="text-muted">
                    <i class="fas fa-robot me-1"></i>
                    Demo: Use admin/admin123 or register new account
                </small>
            </div>
        </div>
    </div>
</div>
{% endblock %}''')
print("✅ Created: accounts/templates/accounts/login.html")

# register.html
with open('accounts/templates/accounts/register.html', 'w', encoding='utf-8') as f:
    f.write('''{% extends 'base.html' %}

{% block title %}Register - News AI{% endblock %}

{% block content %}
<div class="container">
    <div class="row justify-content-center">
        <div class="col-md-8 col-lg-6">
            <div class="card shadow fade-in-up">
                <div class="card-header bg-success text-white text-center py-3">
                    <h4 class="mb-0"><i class="fas fa-user-plus me-2"></i>Create Account</h4>
                </div>
                <div class="card-body p-4">
                    <form method="post" novalidate>
                        {% csrf_token %}
                        
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label for="id_first_name" class="form-label">First Name</label>
                                <input type="text" name="first_name" id="id_first_name" class="form-control" 
                                       placeholder="First name" value="{{ form.first_name.value|default:'' }}">
                            </div>
                            <div class="col-md-6 mb-3">
                                <label for="id_last_name" class="form-label">Last Name</label>
                                <input type="text" name="last_name" id="id_last_name" class="form-control" 
                                       placeholder="Last name" value="{{ form.last_name.value|default:'' }}">
                            </div>
                        </div>
                        
                        <div class="mb-3">
                            <label for="id_username" class="form-label">Username <span class="text-danger">*</span></label>
                            <div class="input-group">
                                <span class="input-group-text"><i class="fas fa-user"></i></span>
                                <input type="text" name="username" id="id_username" class="form-control" 
                                       placeholder="Choose a username" required value="{{ form.username.value|default:'' }}">
                            </div>
                            {% if form.username.errors %}
                                <div class="text-danger small">
                                    {% for error in form.username.errors %}{{ error }}{% endfor %}
                                </div>
                            {% endif %}
                        </div>
                        
                        <div class="mb-3">
                            <label for="id_email" class="form-label">Email <span class="text-danger">*</span></label>
                            <div class="input-group">
                                <span class="input-group-text"><i class="fas fa-envelope"></i></span>
                                <input type="email" name="email" id="id_email" class="form-control" 
                                       placeholder="Enter email address" required value="{{ form.email.value|default:'' }}">
                            </div>
                            {% if form.email.errors %}
                                <div class="text-danger small">
                                    {% for error in form.email.errors %}{{ error }}{% endfor %}
                                </div>
                            {% endif %}
                        </div>
                        
                        <div class="mb-3">
                            <label for="id_interests" class="form-label">Interests</label>
                            <select name="interests" id="id_interests" class="form-select">
                                <option value="">Select your primary interest</option>
                                <option value="AI" {% if form.interests.value == 'AI' %}selected{% endif %}>Artificial Intelligence</option>
                                <option value="TECH" {% if form.interests.value == 'TECH' %}selected{% endif %}>Technology</option>
                                <option value="SPORTS" {% if form.interests.value == 'SPORTS' %}selected{% endif %}>Sports</option>
                                <option value="BUSINESS" {% if form.interests.value == 'BUSINESS' %}selected{% endif %}>Business</option>
                                <option value="HEALTH" {% if form.interests.value == 'HEALTH' %}selected{% endif %}>Health</option>
                                <option value="EDUCATION" {% if form.interests.value == 'EDUCATION' %}selected{% endif %}>Education</option>
                                <option value="ENTERTAINMENT" {% if form.interests.value == 'ENTERTAINMENT' %}selected{% endif %}>Entertainment</option>
                                <option value="POLITICS" {% if form.interests.value == 'POLITICS' %}selected{% endif %}>Politics</option>
                            </select>
                        </div>
                        
                        <div class="mb-3">
                            <label for="id_password1" class="form-label">Password <span class="text-danger">*</span></label>
                            <div class="input-group">
                                <span class="input-group-text"><i class="fas fa-lock"></i></span>
                                <input type="password" name="password1" id="id_password1" class="form-control" 
                                       placeholder="Enter password" required>
                            </div>
                            <small class="text-muted">Password must be at least 8 characters</small>
                            {% if form.password1.errors %}
                                <div class="text-danger small">
                                    {% for error in form.password1.errors %}{{ error }}{% endfor %}
                                </div>
                            {% endif %}
                        </div>
                        
                        <div class="mb-3">
                            <label for="id_password2" class="form-label">Confirm Password <span class="text-danger">*</span></label>
                            <div class="input-group">
                                <span class="input-group-text"><i class="fas fa-lock"></i></span>
                                <input type="password" name="password2" id="id_password2" class="form-control" 
                                       placeholder="Confirm password" required>
                            </div>
                            {% if form.password2.errors %}
                                <div class="text-danger small">
                                    {% for error in form.password2.errors %}{{ error }}{% endfor %}
                                </div>
                            {% endif %}
                        </div>
                        
                        <div class="d-grid gap-2">
                            <button type="submit" class="btn btn-success btn-lg">
                                <i class="fas fa-user-plus me-2"></i>Register
                            </button>
                        </div>
                    </form>
                    
                    <hr class="my-4">
                    
                    <div class="text-center">
                        <p class="mb-0">
                            Already have an account? 
                            <a href="{% url 'accounts:login' %}" class="text-decoration-none fw-bold">
                                Login Here
                            </a>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}''')
print("✅ Created: accounts/templates/accounts/register.html")

# profile.html
with open('accounts/templates/accounts/profile.html', 'w', encoding='utf-8') as f:
    f.write('''{% extends 'base.html' %}

{% block title %}Profile - News AI{% endblock %}

{% block content %}
<div class="container">
    <div class="row">
        <div class="col-md-4 mb-4">
            <div class="card shadow">
                <div class="card-body text-center">
                    {% if user.profile_picture %}
                        <img src="{{ user.profile_picture.url }}" alt="{{ user.username }}" 
                             class="rounded-circle mb-3" style="width: 150px; height: 150px; object-fit: cover;">
                    {% else %}
                        <div class="bg-secondary rounded-circle d-flex align-items-center justify-content-center mx-auto mb-3" 
                             style="width: 150px; height: 150px; color: white; font-size: 4rem;">
                            <i class="fas fa-user"></i>
                        </div>
                    {% endif %}
                    
                    <h4 class="mb-1">{{ user.get_full_name|default:user.username }}</h4>
                    <p class="text-muted">@{{ user.username }}</p>
                    
                    {% if user.interests %}
                        <span class="badge bg-primary category-badge">{{ user.get_interests_display }}</span>
                    {% endif %}
                    
                    <hr>
                    
                    <div class="row">
                        <div class="col-6">
                            <div class="text-muted small">Joined</div>
                            <div>{{ user.date_joined|date:"M d, Y" }}</div>
                        </div>
                        <div class="col-6">
                            <div class="text-muted small">Articles Read</div>
                            <div>{{ user.total_likes|add:user.total_saves }}</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="col-md-8">
            <div class="card shadow">
                <div class="card-header bg-primary text-white">
                    <h5 class="mb-0"><i class="fas fa-edit me-2"></i>Edit Profile</h5>
                </div>
                <div class="card-body">
                    <form method="post" enctype="multipart/form-data">
                        {% csrf_token %}
                        
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label for="id_first_name" class="form-label">First Name</label>
                                <input type="text" name="first_name" id="id_first_name" class="form-control" 
                                       value="{{ form.first_name.value|default:'' }}">
                            </div>
                            <div class="col-md-6 mb-3">
                                <label for="id_last_name" class="form-label">Last Name</label>
                                <input type="text" name="last_name" id="id_last_name" class="form-control" 
                                       value="{{ form.last_name.value|default:'' }}">
                            </div>
                        </div>
                        
                        <div class="mb-3">
                            <label for="id_email" class="form-label">Email</label>
                            <input type="email" name="email" id="id_email" class="form-control" 
                                   value="{{ form.email.value|default:'' }}" required>
                        </div>
                        
                        <div class="mb-3">
                            <label for="id_interests" class="form-label">Interests</label>
                            <select name="interests" id="id_interests" class="form-select">
                                <option value="">Select your primary interest</option>
                                <option value="AI" {% if form.interests.value == 'AI' %}selected{% endif %}>Artificial Intelligence</option>
                                <option value="TECH" {% if form.interests.value == 'TECH' %}selected{% endif %}>Technology</option>
                                <option value="SPORTS" {% if form.interests.value == 'SPORTS' %}selected{% endif %}>Sports</option>
                                <option value="BUSINESS" {% if form.interests.value == 'BUSINESS' %}selected{% endif %}>Business</option>
                                <option value="HEALTH" {% if form.interests.value == 'HEALTH' %}selected{% endif %}>Health</option>
                                <option value="EDUCATION" {% if form.interests.value == 'EDUCATION' %}selected{% endif %}>Education</option>
                                <option value="ENTERTAINMENT" {% if form.interests.value == 'ENTERTAINMENT' %}selected{% endif %}>Entertainment</option>
                                <option value="POLITICS" {% if form.interests.value == 'POLITICS' %}selected{% endif %}>Politics</option>
                            </select>
                        </div>
                        
                        <div class="mb-3">
                            <label for="id_bio" class="form-label">Bio</label>
                            <textarea name="bio" id="id_bio" rows="3" class="form-control" 
                                      placeholder="Tell us about yourself">{{ form.bio.value|default:'' }}</textarea>
                        </div>
                        
                        <div class="mb-3">
                            <label for="id_profile_picture" class="form-label">Profile Picture</label>
                            <input type="file" name="profile_picture" id="id_profile_picture" class="form-control">
                            {% if user.profile_picture %}
                                <small class="text-muted">Current: {{ user.profile_picture.name }}</small>
                            {% endif %}
                        </div>
                        
                        <div class="d-grid">
                            <button type="submit" class="btn btn-primary">
                                <i class="fas fa-save me-2"></i>Update Profile
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}''')
print("✅ Created: accounts/templates/accounts/profile.html")

# password_reset.html
with open('accounts/templates/accounts/password_reset.html', 'w', encoding='utf-8') as f:
    f.write('''{% extends 'base.html' %}

{% block title %}Reset Password - News AI{% endblock %}

{% block content %}
<div class="container">
    <div class="row justify-content-center">
        <div class="col-md-6 col-lg-5">
            <div class="card shadow fade-in-up">
                <div class="card-header bg-warning text-dark text-center py-3">
                    <h4 class="mb-0"><i class="fas fa-key me-2"></i>Reset Password</h4>
                </div>
                <div class="card-body p-4">
                    <p class="text-muted">Enter your email address and we'll send you a link to reset your password.</p>
                    
                    <form method="post">
                        {% csrf_token %}
                        
                        <div class="mb-3">
                            <label for="id_email" class="form-label">Email Address</label>
                            <div class="input-group">
                                <span class="input-group-text"><i class="fas fa-envelope"></i></span>
                                <input type="email" name="email" id="id_email" class="form-control" 
                                       placeholder="Enter your email" required>
                            </div>
                        </div>
                        
                        <div class="d-grid">
                            <button type="submit" class="btn btn-warning">
                                <i class="fas fa-paper-plane me-2"></i>Send Reset Link
                            </button>
                        </div>
                    </form>
                    
                    <hr class="my-4">
                    
                    <div class="text-center">
                        <a href="{% url 'accounts:login' %}" class="text-decoration-none">
                            <i class="fas fa-arrow-left me-1"></i>Back to Login
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}''')
print("✅ Created: accounts/templates/accounts/password_reset.html")

# password_reset_done.html
with open('accounts/templates/accounts/password_reset_done.html', 'w', encoding='utf-8') as f:
    f.write('''{% extends 'base.html' %}

{% block title %}Reset Link Sent - News AI{% endblock %}

{% block content %}
<div class="container">
    <div class="row justify-content-center">
        <div class="col-md-6 col-lg-5">
            <div class="card shadow fade-in-up">
                <div class="card-header bg-success text-white text-center py-3">
                    <h4 class="mb-0"><i class="fas fa-check-circle me-2"></i>Email Sent</h4>
                </div>
                <div class="card-body p-4 text-center">
                    <i class="fas fa-envelope-open-text fa-4x text-success mb-3"></i>
                    <p>We've emailed you instructions for setting your password.</p>
                    <p class="text-muted">If you don't receive an email, please make sure you've entered the correct email address.</p>
                    
                    <a href="{% url 'accounts:login' %}" class="btn btn-primary">
                        <i class="fas fa-sign-in-alt me-2"></i>Return to Login
                    </a>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}''')
print("✅ Created: accounts/templates/accounts/password_reset_done.html")

# password_reset_confirm.html
with open('accounts/templates/accounts/password_reset_confirm.html', 'w', encoding='utf-8') as f:
    f.write('''{% extends 'base.html' %}

{% block title %}Set New Password - News AI{% endblock %}

{% block content %}
<div class="container">
    <div class="row justify-content-center">
        <div class="col-md-6 col-lg-5">
            <div class="card shadow fade-in-up">
                <div class="card-header bg-primary text-white text-center py-3">
                    <h4 class="mb-0"><i class="fas fa-lock me-2"></i>Set New Password</h4>
                </div>
                <div class="card-body p-4">
                    <form method="post">
                        {% csrf_token %}
                        
                        <div class="mb-3">
                            <label for="id_new_password1" class="form-label">New Password</label>
                            <div class="input-group">
                                <span class="input-group-text"><i class="fas fa-lock"></i></span>
                                <input type="password" name="new_password1" id="id_new_password1" class="form-control" 
                                       placeholder="Enter new password" required>
                            </div>
                        </div>
                        
                        <div class="mb-3">
                            <label for="id_new_password2" class="form-label">Confirm New Password</label>
                            <div class="input-group">
                                <span class="input-group-text"><i class="fas fa-lock"></i></span>
                                <input type="password" name="new_password2" id="id_new_password2" class="form-control" 
                                       placeholder="Confirm new password" required>
                            </div>
                        </div>
                        
                        <div class="d-grid">
                            <button type="submit" class="btn btn-primary">
                                <i class="fas fa-save me-2"></i>Change Password
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}''')
print("✅ Created: accounts/templates/accounts/password_reset_confirm.html")

# password_reset_complete.html
with open('accounts/templates/accounts/password_reset_complete.html', 'w', encoding='utf-8') as f:
    f.write('''{% extends 'base.html' %}

{% block title %}Password Reset Complete - News AI{% endblock %}

{% block content %}
<div class="container">
    <div class="row justify-content-center">
        <div class="col-md-6 col-lg-5">
            <div class="card shadow fade-in-up">
                <div class="card-header bg-success text-white text-center py-3">
                    <h4 class="mb-0"><i class="fas fa-check-circle me-2"></i>Password Reset Complete</h4>
                </div>
                <div class="card-body p-4 text-center">
                    <i class="fas fa-check-circle fa-4x text-success mb-3"></i>
                    <p>Your password has been set successfully.</p>
                    <p>You can now log in with your new password.</p>
                    
                    <a href="{% url 'accounts:login' %}" class="btn btn-success">
                        <i class="fas fa-sign-in-alt me-2"></i>Login Now
                    </a>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}''')
print("✅ Created: accounts/templates/accounts/password_reset_complete.html")

# ============================================
# 3. NEWS TEMPLATES
# ============================================

# news/list.html
with open('news/templates/news/list.html', 'w', encoding='utf-8') as f:
    f.write('''{% extends 'base.html' %}
{% load static %}

{% block title %}News - News AI{% endblock %}

{% block content %}
<div class="container">
    <div class="row mb-4">
        <div class="col-md-8">
            <h2><i class="fas fa-newspaper me-2"></i>Latest News</h2>
        </div>
        <div class="col-md-4">
            <div class="dropdown">
                <button class="btn btn-outline-primary dropdown-toggle w-100" type="button" data-bs-toggle="dropdown">
                    {% if selected_category %}
                        {{ selected_category }}
                    {% else %}
                        All Categories
                    {% endif %}
                </button>
                <ul class="dropdown-menu w-100">
                    <li><a class="dropdown-item" href="{% url 'news:list' %}">All Categories</a></li>
                    {% for category in categories %}
                        <li><a class="dropdown-item" href="?category={{ category.id }}">
                            {{ category.name }}
                        </a></li>
                    {% endfor %}
                </ul>
            </div>
        </div>
    </div>
    
    <div class="row">
        {% if news %}
            {% for item in news %}
                <div class="col-md-4 mb-4">
                    <div class="card news-card shadow h-100">
                        {% if item.image %}
                            <img src="{{ item.image.url }}" class="card-img-top" alt="{{ item.title }}" style="height: 200px; object-fit: cover;">
                        {% else %}
                            <div class="card-img-top bg-secondary d-flex align-items-center justify-content-center" 
                                 style="height: 200px; color: white;">
                                <i class="fas fa-image fa-3x"></i>
                            </div>
                        {% endif %}
                        <div class="card-body">
                            <span class="badge bg-primary mb-2">{{ item.category.name }}</span>
                            <h5 class="card-title">{{ item.title|truncatechars:60 }}</h5>
                            <p class="card-text text-muted">{{ item.description|truncatechars:100 }}</p>
                            <div class="d-flex justify-content-between align-items-center mt-3">
                                <div class="text-muted small">
                                    <i class="fas fa-clock me-1"></i>{{ item.published_date|timesince }} ago
                                </div>
                                <a href="{{ item.get_absolute_url }}" class="btn btn-primary btn-sm">
                                    Read More <i class="fas fa-arrow-right ms-1"></i>
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            {% endfor %}
        {% else %}
            <div class="col-12 text-center py-5">
                <i class="fas fa-inbox fa-3x text-muted mb-3"></i>
                <p class="text-muted">No news available</p>
            </div>
        {% endif %}
    </div>
    
    {% if news.has_other_pages %}
        <nav aria-label="Page navigation" class="mt-4">
            <ul class="pagination justify-content-center">
                {% if news.has_previous %}
                    <li class="page-item"><a class="page-link" href="?page={{ news.previous_page_number }}">&laquo;</a></li>
                {% endif %}
                {% for num in news.paginator.page_range %}
                    <li class="page-item {% if num == news.number %}active{% endif %}">
                        <a class="page-link" href="?page={{ num }}">{{ num }}</a>
                    </li>
                {% endfor %}
                {% if news.has_next %}
                    <li class="page-item"><a class="page-link" href="?page={{ news.next_page_number }}">&raquo;</a></li>
                {% endif %}
            </ul>
        </nav>
    {% endif %}
</div>
{% endblock %}''')
print("✅ Created: news/templates/news/list.html")

# news/detail.html
with open('news/templates/news/detail.html', 'w', encoding='utf-8') as f:
    f.write('''{% extends 'base.html' %}

{% block title %}{{ news.title }} - News AI{% endblock %}

{% block content %}
<div class="container">
    <div class="row">
        <div class="col-lg-8 mx-auto">
            <article class="card shadow">
                {% if news.image %}
                    <img src="{{ news.image.url }}" class="card-img-top" alt="{{ news.title }}" style="max-height: 400px; object-fit: cover;">
                {% endif %}
                <div class="card-body">
                    <div class="mb-3">
                        <span class="badge bg-primary">{{ news.category.name }}</span>
                        <span class="badge bg-secondary"><i class="far fa-clock me-1"></i>{{ news.published_date|date:"F d, Y" }}</span>
                        <span class="badge bg-info"><i class="far fa-user me-1"></i>{{ news.author }}</span>
                    </div>
                    
                    <h1 class="card-title">{{ news.title }}</h1>
                    <p class="text-muted">{{ news.description }}</p>
                    
                    <div class="article-content" data-news-id="{{ news.id }}">
                        {{ news.content|linebreaks }}
                    </div>
                    
                    <hr>
                    
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <button class="btn btn-outline-danger like-btn" data-url="{% url 'news:like' news.id %}" data-news-id="{{ news.id }}">
                                <i class="fas fa-heart like-icon {% if is_liked %}text-danger{% else %}text-muted{% endif %}"></i>
                                <span class="like-count">{{ news.likes_count }}</span>
                            </button>
                            <button class="btn btn-outline-warning save-btn" data-url="{% url 'news:save' news.id %}" data-news-id="{{ news.id }}">
                                <i class="fas fa-bookmark save-icon {% if is_bookmarked %}text-warning{% else %}text-muted{% endif %}"></i>
                                <span class="save-count">{{ news.saves_count }}</span>
                            </button>
                        </div>
                        <div>
                            <span class="text-muted"><i class="far fa-eye me-1"></i>{{ news.views }} views</span>
                            <span class="text-muted ms-3"><i class="far fa-clock me-1"></i>{{ news.get_reading_time }} min read</span>
                        </div>
                    </div>
                    
                    <hr>
                    
                    <div class="text-center">
                        <a href="{% url 'news:list' %}" class="btn btn-secondary">
                            <i class="fas fa-arrow-left me-2"></i>Back to News
                        </a>
                    </div>
                </div>
            </article>
            
            {% if related_news %}
                <div class="mt-4">
                    <h4><i class="fas fa-arrow-right me-2"></i>Related News</h4>
                    <div class="row">
                        {% for related in related_news %}
                            <div class="col-md-3 mb-3">
                                <div class="card h-100">
                                    <div class="card-body">
                                        <h6 class="card-title">{{ related.title|truncatechars:40 }}</h6>
                                        <a href="{{ related.get_absolute_url }}" class="btn btn-sm btn-outline-primary">Read</a>
                                    </div>
                                </div>
                            </div>
                        {% endfor %}
                    </div>
                </div>
            {% endif %}
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
document.addEventListener('DOMContentLoaded', function() {
    // Like functionality
    document.querySelectorAll('.like-btn').forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            var url = this.dataset.url;
            var icon = this.querySelector('.like-icon');
            var countEl = this.querySelector('.like-count');
            
            fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || getCSRFToken(),
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.liked) {
                    icon.classList.add('text-danger');
                    icon.classList.remove('text-muted');
                } else {
                    icon.classList.remove('text-danger');
                    icon.classList.add('text-muted');
                }
                countEl.textContent = data.likes_count;
            });
        });
    });
    
    // Save functionality
    document.querySelectorAll('.save-btn').forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            var url = this.dataset.url;
            var icon = this.querySelector('.save-icon');
            var countEl = this.querySelector('.save-count');
            
            fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || getCSRFToken(),
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.saved) {
                    icon.classList.add('text-warning');
                    icon.classList.remove('text-muted');
                } else {
                    icon.classList.remove('text-warning');
                    icon.classList.add('text-muted');
                }
                countEl.textContent = data.saves_count;
            });
        });
    });
});

function getCSRFToken() {
    const name = 'csrftoken';
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
</script>
{% endblock %}''')
print("✅ Created: news/templates/news/detail.html")

# news/saved.html
with open('news/templates/news/saved.html', 'w', encoding='utf-8') as f:
    f.write('''{% extends 'base.html' %}

{% block title %}Saved News - News AI{% endblock %}

{% block content %}
<div class="container">
    <h2 class="mb-4"><i class="fas fa-bookmark text-warning me-2"></i>Saved Articles</h2>
    
    <div class="row">
        {% if saved_news %}
            {% for bookmark in saved_news %}
                <div class="col-md-4 mb-4">
                    <div class="card news-card shadow h-100">
                        <div class="card-body">
                            <span class="badge bg-warning mb-2"><i class="fas fa-bookmark me-1"></i>Saved</span>
                            <h5 class="card-title">{{ bookmark.news.title|truncatechars:60 }}</h5>
                            <p class="card-text text-muted">{{ bookmark.news.description|truncatechars:100 }}</p>
                            <div class="d-flex justify-content-between align-items-center mt-3">
                                <div class="text-muted small">
                                    <i class="fas fa-clock me-1"></i>{{ bookmark.created_at|timesince }} ago
                                </div>
                                <a href="{{ bookmark.news.get_absolute_url }}" class="btn btn-primary btn-sm">
                                    Read <i class="fas fa-arrow-right ms-1"></i>
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            {% endfor %}
        {% else %}
            <div class="col-12 text-center py-5">
                <i class="fas fa-bookmark fa-3x text-muted mb-3"></i>
                <p class="text-muted">No saved articles yet. Start saving news you like!</p>
                <a href="{% url 'news:list' %}" class="btn btn-primary">
                    <i class="fas fa-newspaper me-2"></i>Browse News
                </a>
            </div>
        {% endif %}
    </div>
</div>
{% endblock %}''')
print("✅ Created: news/templates/news/saved.html")

# news/categories.html
with open('news/templates/news/categories.html', 'w', encoding='utf-8') as f:
    f.write('''{% extends 'base.html' %}

{% block title %}Categories - News AI{% endblock %}

{% block content %}
<div class="container">
    <h2 class="mb-4"><i class="fas fa-tags me-2"></i>Categories</h2>
    
    <div class="row">
        {% for category in categories %}
            <div class="col-md-3 mb-4">
                <a href="{% url 'news:list' %}?category={{ category.id }}" class="text-decoration-none">
                    <div class="card text-center shadow category-card hover-card">
                        <div class="card-body py-4">
                            <i class="fas fa-{% if category.name == 'AI' %}robot{% elif category.name == 'Technology' %}laptop-code{% elif category.name == 'Sports' %}futbol{% elif category.name == 'Business' %}briefcase{% elif category.name == 'Health' %}heartbeat{% elif category.name == 'Education' %}graduation-cap{% elif category.name == 'Entertainment' %}film{% elif category.name == 'Politics' %}gavel{% else %}newspaper{% endif %} fa-3x text-primary mb-2"></i>
                            <h5 class="card-title">{{ category.name }}</h5>
                            <span class="badge bg-secondary">{{ category.news_count }} articles</span>
                        </div>
                    </div>
                </a>
            </div>
        {% empty %}
            <div class="col-12 text-center py-5">
                <p class="text-muted">No categories available</p>
            </div>
        {% endfor %}
    </div>
</div>
{% endblock %}''')
print("✅ Created: news/templates/news/categories.html")

# news/search.html
with open('news/templates/news/search.html', 'w', encoding='utf-8') as f:
    f.write('''{% extends 'base.html' %}

{% block title %}Search Results - News AI{% endblock %}

{% block content %}
<div class="container">
    <h2 class="mb-4"><i class="fas fa-search me-2"></i>Search Results</h2>
    
    {% if query %}
        <p class="text-muted">Results for: <strong>"{{ query }}"</strong> ({{ news.paginator.count }} found)</p>
    {% endif %}
    
    <div class="row">
        {% if news %}
            {% for item in news %}
                <div class="col-md-4 mb-4">
                    <div class="card news-card shadow h-100">
                        <div class="card-body">
                            <span class="badge bg-primary mb-2">{{ item.category.name }}</span>
                            <h5 class="card-title">{{ item.title|truncatechars:60 }}</h5>
                            <p class="card-text text-muted">{{ item.description|truncatechars:100 }}</p>
                            <a href="{{ item.get_absolute_url }}" class="btn btn-primary btn-sm">
                                Read More <i class="fas fa-arrow-right ms-1"></i>
                            </a>
                        </div>
                    </div>
                </div>
            {% endfor %}
        {% else %}
            <div class="col-12 text-center py-5">
                <i class="fas fa-search fa-3x text-muted mb-3"></i>
                <p class="text-muted">No results found for "{{ query }}"</p>
                <a href="{% url 'news:list' %}" class="btn btn-primary">
                    <i class="fas fa-arrow-left me-2"></i>Back to News
                </a>
            </div>
        {% endif %}
    </div>
</div>
{% endblock %}''')
print("✅ Created: news/templates/news/search.html")

# ============================================
# 4. RECOMMENDATION TEMPLATES
# ============================================

# recommendation/feed.html
with open('recommendation/templates/recommendation/feed.html', 'w', encoding='utf-8') as f:
    f.write('''{% extends 'base.html' %}

{% block title %}AI Personalized Feed - News AI{% endblock %}

{% block content %}
<div class="container">
    <div class="row mb-4">
        <div class="col-12">
            <div class="d-flex justify-content-between align-items-center">
                <h2><i class="fas fa-robot text-primary me-2"></i>AI Personalized Feed</h2>
                {% if is_personalized %}
                    <span class="badge bg-success"><i class="fas fa-check-circle me-1"></i>Personalized</span>
                {% else %}
                    <span class="badge bg-warning"><i class="fas fa-clock me-1"></i>Generating...</span>
                {% endif %}
            </div>
            <p class="text-muted">News recommendations powered by AI based on your reading history and preferences.</p>
        </div>
    </div>
    
    <div class="row">
        {% if news %}
            {% for item in news %}
                <div class="col-md-6 mb-4">
                    <div class="card news-card shadow h-100 fade-in-up" style="animation-delay: {{ forloop.counter|add:-1|stringformat:"i" }}00ms;">
                        <div class="row g-0">
                            <div class="col-md-4">
                                {% if item.image %}
                                    <img src="{{ item.image.url }}" class="img-fluid rounded-start h-100" alt="{{ item.title }}" style="object-fit: cover; min-height: 150px;">
                                {% else %}
                                    <div class="bg-secondary d-flex align-items-center justify-content-center h-100" style="min-height: 150px; color: white;">
                                        <i class="fas fa-image fa-2x"></i>
                                    </div>
                                {% endif %}
                            </div>
                            <div class="col-md-8">
                                <div class="card-body">
                                    <span class="badge bg-primary mb-2">{{ item.category.name }}</span>
                                    <h5 class="card-title">{{ item.title|truncatechars:50 }}</h5>
                                    <p class="card-text text-muted small">{{ item.description|truncatechars:80 }}</p>
                                    <div class="d-flex justify-content-between align-items-center">
                                        <small class="text-muted">{{ item.published_date|timesince }} ago</small>
                                        <a href="{{ item.get_absolute_url }}" class="btn btn-primary btn-sm">
                                            Read <i class="fas fa-arrow-right ms-1"></i>
                                        </a>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            {% endfor %}
        {% else %}
            <div class="col-12 text-center py-5">
                <i class="fas fa-robot fa-3x text-muted mb-3"></i>
                <p class="text-muted">No recommendations available. Start reading and liking articles!</p>
                <a href="{% url 'news:list' %}" class="btn btn-primary">
                    <i class="fas fa-newspaper me-2"></i>Browse News
                </a>
            </div>
        {% endif %}
    </div>
</div>
{% endblock %}''')
print("✅ Created: recommendation/templates/recommendation/feed.html")

# recommendation/trending.html
with open('recommendation/templates/recommendation/trending.html', 'w', encoding='utf-8') as f:
    f.write('''{% extends 'base.html' %}

{% block title %}Trending News - News AI{% endblock %}

{% block content %}
<div class="container">
    <h2 class="mb-4"><i class="fas fa-fire text-danger me-2"></i>Trending Now</h2>
    
    <div class="row">
        {% if news %}
            {% for item in news %}
                <div class="col-md-4 mb-4">
                    <div class="card news-card shadow h-100">
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-start">
                                <span class="badge bg-danger">#{{ forloop.counter }}</span>
                                <span class="badge bg-primary">{{ item.category.name }}</span>
                            </div>
                            <h5 class="card-title mt-2">{{ item.title|truncatechars:60 }}</h5>
                            <p class="card-text text-muted">{{ item.description|truncatechars:100 }}</p>
                            <div class="d-flex justify-content-between align-items-center mt-3">
                                <div>
                                    <span class="text-muted small"><i class="far fa-eye me-1"></i>{{ item.views }}</span>
                                    <span class="text-muted small ms-2"><i class="far fa-heart me-1"></i>{{ item.likes_count }}</span>
                                </div>
                                <a href="{{ item.get_absolute_url }}" class="btn btn-danger btn-sm">
                                    Read <i class="fas fa-arrow-right ms-1"></i>
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            {% endfor %}
        {% else %}
            <div class="col-12 text-center py-5">
                <i class="fas fa-fire fa-3x text-muted mb-3"></i>
                <p class="text-muted">No trending news available</p>
            </div>
        {% endif %}
    </div>
</div>
{% endblock %}''')
print("✅ Created: recommendation/templates/recommendation/trending.html")

# recommendation/similar.html
with open('recommendation/templates/recommendation/similar.html', 'w', encoding='utf-8') as f:
    f.write('''{% extends 'base.html' %}

{% block title %}Similar News - News AI{% endblock %}

{% block content %}
<div class="container">
    <h2 class="mb-4"><i class="fas fa-arrow-right me-2"></i>Similar Articles</h2>
    
    <div class="row">
        {% if news %}
            {% for item in news %}
                <div class="col-md-4 mb-4">
                    <div class="card news-card shadow h-100">
                        <div class="card-body">
                            <span class="badge bg-info mb-2">{{ item.category.name }}</span>
                            <h5 class="card-title">{{ item.title|truncatechars:60 }}</h5>
                            <p class="card-text text-muted">{{ item.description|truncatechars:100 }}</p>
                            <a href="{{ item.get_absolute_url }}" class="btn btn-info btn-sm">
                                Read <i class="fas fa-arrow-right ms-1"></i>
                            </a>
                        </div>
                    </div>
                </div>
            {% endfor %}
        {% else %}
            <div class="col-12 text-center py-5">
                <p class="text-muted">No similar articles found</p>
            </div>
        {% endif %}
    </div>
</div>
{% endblock %}''')
print("✅ Created: recommendation/templates/recommendation/similar.html")

# recommendation/analytics.html
with open('recommendation/templates/recommendation/analytics.html', 'w', encoding='utf-8') as f:
    f.write('''{% extends 'base.html' %}

{% block title %}Analytics - News AI{% endblock %}

{% block content %}
<div class="container">
    <h2 class="mb-4"><i class="fas fa-chart-bar text-primary me-2"></i>Your Reading Analytics</h2>
    
    <div class="row">
        <div class="col-md-3 mb-4">
            <div class="card bg-primary text-white">
                <div class="card-body text-center">
                    <h6 class="card-title">Articles Viewed</h6>
                    <h2>{{ stats.total_views }}</h2>
                </div>
            </div>
        </div>
        <div class="col-md-3 mb-4">
            <div class="card bg-success text-white">
                <div class="card-body text-center">
                    <h6 class="card-title">Articles Liked</h6>
                    <h2>{{ stats.total_likes }}</h2>
                </div>
            </div>
        </div>
        <div class="col-md-3 mb-4">
            <div class="card bg-warning text-dark">
                <div class="card-body text-center">
                    <h6 class="card-title">Articles Saved</h6>
                    <h2>{{ stats.total_saves }}</h2>
                </div>
            </div>
        </div>
        <div class="col-md-3 mb-4">
            <div class="card bg-info text-white">
                <div class="card-body text-center">
                    <h6 class="card-title">Searches</h6>
                    <h2>{{ stats.total_searches }}</h2>
                </div>
            </div>
        </div>
    </div>
    
    <div class="card">
        <div class="card-header">
            <h5 class="mb-0"><i class="fas fa-history me-2"></i>Reading History</h5>
        </div>
        <div class="card-body">
            <div class="list-group">
                {% for behavior in reading_history %}
                    <div class="list-group-item">
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <i class="fas fa-eye me-2"></i>
                                <a href="{{ behavior.news.get_absolute_url }}" class="text-decoration-none">
                                    {{ behavior.news.title|truncatechars:80 }}
                                </a>
                            </div>
                            <small class="text-muted">{{ behavior.timestamp|timesince }} ago</small>
                        </div>
                    </div>
                {% empty %}
                    <p class="text-muted">No reading history yet</p>
                {% endfor %}
            </div>
        </div>
    </div>
</div>
{% endblock %}''')
print("✅ Created: recommendation/templates/recommendation/analytics.html")

# ============================================
# 5. DASHBOARD TEMPLATES
# ============================================

# dashboard/home.html
with open('dashboard/templates/dashboard/home.html', 'w', encoding='utf-8') as f:
    f.write('''{% extends 'base.html' %}

{% block title %}Dashboard - News AI{% endblock %}

{% block content %}
<div class="container">
    <div class="row">
        <div class="col-12">
            <div class="alert alert-info fade-in-up">
                <h4><i class="fas fa-rocket me-2"></i>Welcome to AI-Powered News Recommender</h4>
                <p>Your personalized news feed powered by artificial intelligence.</p>
                <a href="{% url 'recommendation:feed' %}" class="btn btn-primary">
                    <i class="fas fa-robot me-2"></i>View AI Feed
                </a>
            </div>
        </div>
    </div>
    
    <div class="row">
        <div class="col-md-4 mb-4">
            <div class="card bg-primary text-white h-100">
                <div class="card-body text-center">
                    <i class="fas fa-user-circle fa-3x mb-3"></i>
                    <h5 class="card-title">Profile</h5>
                    <p>Welcome, {{ user.get_full_name|default:user.username }}!</p>
                    <a href="{% url 'accounts:profile' %}" class="btn btn-light btn-sm">
                        <i class="fas fa-edit me-2"></i>View Profile
                    </a>
                </div>
            </div>
        </div>
        
        <div class="col-md-4 mb-4">
            <div class="card bg-success text-white h-100">
                <div class="card-body text-center">
                    <i class="fas fa-robot fa-3x mb-3"></i>
                    <h5 class="card-title">AI Feed</h5>
                    <p>Get personalized news recommendations</p>
                    <a href="{% url 'recommendation:feed' %}" class="btn btn-light btn-sm">
                        <i class="fas fa-arrow-right me-2"></i>View Feed
                    </a>
                </div>
            </div>
        </div>
        
        <div class="col-md-4 mb-4">
            <div class="card bg-warning text-dark h-100">
                <div class="card-body text-center">
                    <i class="fas fa-newspaper fa-3x mb-3"></i>
                    <h5 class="card-title">All News</h5>
                    <p>Browse all available news articles</p>
                    <a href="{% url 'news:list' %}" class="btn btn-light btn-sm">
                        <i class="fas fa-arrow-right me-2"></i>Browse News
                    </a>
                </div>
            </div>
        </div>
    </div>
    
    <div class="row mt-4">
        <div class="col-12">
            <div class="card">
                <div class="card-header">
                    <h5 class="mb-0"><i class="fas fa-quick-actions me-2"></i>Quick Actions</h5>
                </div>
                <div class="card-body">
                    <div class="row g-3">
                        <div class="col-md-3">
                            <a href="{% url 'news:categories' %}" class="btn btn-outline-primary w-100">
                                <i class="fas fa-tags me-2"></i>Categories
                            </a>
                        </div>
                        <div class="col-md-3">
                            <a href="{% url 'news:saved' %}" class="btn btn-outline-success w-100">
                                <i class="fas fa-bookmark me-2"></i>Saved Articles
                            </a>
                        </div>
                        <div class="col-md-3">
                            <a href="{% url 'recommendation:trending' %}" class="btn btn-outline-warning w-100">
                                <i class="fas fa-fire me-2"></i>Trending
                            </a>
                        </div>
                        <div class="col-md-3">
                            <a href="{% url 'recommendation:analytics' %}" class="btn btn-outline-info w-100">
                                <i class="fas fa-chart-bar me-2"></i>Analytics
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}''')
print("✅ Created: dashboard/templates/dashboard/home.html")

# ============================================
# 6. CREATE STATIC FILES
# ============================================

# Create CSS file
with open('static/css/style.css', 'w', encoding='utf-8') as f:
    f.write('''/* Custom styles for News Recommender System */

/* General */
body {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
}

main {
    flex: 1;
}

/* News Cards */
.news-card {
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    height: 100%;
}

.news-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 20px rgba(0,0,0,0.1) !important;
}

/* Category Cards */
.hover-card {
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.hover-card:hover {
    transform: scale(1.05);
    box-shadow: 0 10px 20px rgba(0,0,0,0.1);
}

/* Animations */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.fade-in-up {
    animation: fadeInUp 0.5s ease-out;
}

/* Category Badges */
.category-badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Buttons */
.action-btn {
    transition: all 0.2s ease;
    cursor: pointer;
}

.action-btn:hover {
    transform: scale(1.1);
}

/* Responsive */
@media (max-width: 768px) {
    .profile-picture {
        width: 100px;
        height: 100px;
    }
    
    .news-card .card-img-top {
        height: 150px;
    }
}''')
print("✅ Created: static/css/style.css")

# Create JS file
with open('static/js/main.js', 'w', encoding='utf-8') as f:
    f.write('''// Main JavaScript for News Recommender System

document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss alerts
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
});

// Utility functions
function getCSRFToken() {
    const name = 'csrftoken';
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}''')
print("✅ Created: static/js/main.js")

print("\n" + "="*50)
print("✅ ALL TEMPLATES CREATED SUCCESSFULLY!")
print("="*50)
print("\n📁 Templates Created:")
print("  - templates/base.html")
print("  - accounts/templates/accounts/ (7 files)")
print("  - news/templates/news/ (4 files)")
print("  - recommendation/templates/recommendation/ (4 files)")
print("  - dashboard/templates/dashboard/ (1 file)")
print("  - static/css/style.css")
print("  - static/js/main.js")
print("\n🚀 Now run: python manage.py runserver")
print("🌐 Visit: http://localhost:8000/")