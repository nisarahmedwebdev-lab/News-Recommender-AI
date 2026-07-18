import os

# Create directories
os.makedirs('accounts/templates/accounts', exist_ok=True)
os.makedirs('templates', exist_ok=True)

# Create base.html
with open('templates/base.html', 'w', encoding='utf-8') as f:
    f.write('''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}News AI{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="/">
                <i class="fas fa-newspaper me-2"></i>News AI
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    {% if user.is_authenticated %}
                        <li class="nav-item">
                            <a class="nav-link" href="{% url 'accounts:profile' %}">
                                <i class="fas fa-user me-1"></i>{{ user.username }}
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{% url 'accounts:logout' %}">
                                <i class="fas fa-sign-out-alt me-1"></i>Logout
                            </a>
                        </li>
                    {% else %}
                        <li class="nav-item">
                            <a class="nav-link" href="{% url 'accounts:login' %}">Login</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{% url 'accounts:register' %}">Register</a>
                        </li>
                    {% endif %}
                </ul>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        {% if messages %}
            {% for message in messages %}
                <div class="alert alert-{{ message.tags }} alert-dismissible fade show">
                    {{ message }}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            {% endfor %}
        {% endif %}
        
        {% block content %}{% endblock %}
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>''')

# Create login.html
with open('accounts/templates/accounts/login.html', 'w', encoding='utf-8') as f:
    f.write('''{% extends 'base.html' %}

{% block title %}Login - News AI{% endblock %}

{% block content %}
<div class="container">
    <div class="row justify-content-center">
        <div class="col-md-6 col-lg-5">
            <div class="card shadow">
                <div class="card-header bg-primary text-white text-center py-3">
                    <h4 class="mb-0"><i class="fas fa-sign-in-alt me-2"></i>Login</h4>
                </div>
                <div class="card-body p-4">
                    <form method="post">
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
                        
                        <div class="d-grid">
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

# Create register.html
with open('accounts/templates/accounts/register.html', 'w', encoding='utf-8') as f:
    f.write('''{% extends 'base.html' %}

{% block title %}Register - News AI{% endblock %}

{% block content %}
<div class="container">
    <div class="row justify-content-center">
        <div class="col-md-8 col-lg-6">
            <div class="card shadow">
                <div class="card-header bg-success text-white text-center py-3">
                    <h4 class="mb-0"><i class="fas fa-user-plus me-2"></i>Create Account</h4>
                </div>
                <div class="card-body p-4">
                    <form method="post">
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
                                       placeholder="Choose a username" required>
                            </div>
                        </div>
                        
                        <div class="mb-3">
                            <label for="id_email" class="form-label">Email <span class="text-danger">*</span></label>
                            <div class="input-group">
                                <span class="input-group-text"><i class="fas fa-envelope"></i></span>
                                <input type="email" name="email" id="id_email" class="form-control" 
                                       placeholder="Enter email address" required>
                            </div>
                        </div>
                        
                        <div class="mb-3">
                            <label for="id_interests" class="form-label">Interests</label>
                            <select name="interests" id="id_interests" class="form-select">
                                <option value="">Select your primary interest</option>
                                <option value="AI">Artificial Intelligence</option>
                                <option value="TECH">Technology</option>
                                <option value="SPORTS">Sports</option>
                                <option value="BUSINESS">Business</option>
                                <option value="HEALTH">Health</option>
                                <option value="EDUCATION">Education</option>
                                <option value="ENTERTAINMENT">Entertainment</option>
                                <option value="POLITICS">Politics</option>
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
                        </div>
                        
                        <div class="mb-3">
                            <label for="id_password2" class="form-label">Confirm Password <span class="text-danger">*</span></label>
                            <div class="input-group">
                                <span class="input-group-text"><i class="fas fa-lock"></i></span>
                                <input type="password" name="password2" id="id_password2" class="form-control" 
                                       placeholder="Confirm password" required>
                            </div>
                        </div>
                        
                        <div class="d-grid">
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

# Create profile.html
with open('accounts/templates/accounts/profile.html', 'w', encoding='utf-8') as f:
    f.write('''{% extends 'base.html' %}

{% block title %}Profile - News AI{% endblock %}

{% block content %}
<div class="container">
    <div class="row justify-content-center">
        <div class="col-md-8">
            <div class="card shadow">
                <div class="card-header bg-primary text-white">
                    <h5 class="mb-0"><i class="fas fa-user me-2"></i>Profile</h5>
                </div>
                <div class="card-body">
                    <div class="text-center mb-4">
                        {% if user.profile_picture %}
                            <img src="{{ user.profile_picture.url }}" alt="Profile" class="rounded-circle" width="100" height="100">
                        {% else %}
                            <div class="bg-secondary rounded-circle d-inline-flex align-items-center justify-content-center" style="width: 100px; height: 100px;">
                                <i class="fas fa-user fa-3x text-white"></i>
                            </div>
                        {% endif %}
                        <h4 class="mt-2">{{ user.get_full_name|default:user.username }}</h4>
                        <p class="text-muted">@{{ user.username }}</p>
                        {% if user.interests %}
                            <span class="badge bg-primary">{{ user.get_interests_display }}</span>
                        {% endif %}
                    </div>
                    <hr>
                    <p><strong>Email:</strong> {{ user.email }}</p>
                    <p><strong>Joined:</strong> {{ user.date_joined|date:"F d, Y" }}</p>
                    <p><strong>Last Login:</strong> {{ user.last_login|date:"F d, Y" }}</p>
                    <div class="d-grid">
                        <a href="{% url 'accounts:logout' %}" class="btn btn-danger">
                            <i class="fas fa-sign-out-alt me-2"></i>Logout
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}''')

print("Templates created successfully!")