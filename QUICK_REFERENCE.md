# Quick Reference Guide - UI Design System

## 🎨 Colors

```css
/* Primary */
--primary-color: #667eea
--primary-dark: #5a67d8

/* Secondary */
--secondary-color: #764ba2

/* Status Colors */
--success-color: #10b981
--danger-color: #ef4444
--warning-color: #f59e0b
--info-color: #0ea5e9

/* Text */
--text-primary: #1a1a2e
--text-secondary: #6c757d
--text-muted: #9ca3af

/* Backgrounds */
--light-secondary: #f3f4f6
--gray-200: #e5e7eb
--gray-300: #d1d5db
--gray-400: #9ca3af
--gray-500: #6b7280
--dark: #1a1a1a
```

## 📏 Spacing Scale

| Size | Value | Use Case |
|------|-------|----------|
| xs | 0.5rem (8px) | Small gaps, icon spacing |
| sm | 1rem (16px) | Standard spacing |
| md | 1.5rem (24px) | Component padding |
| lg | 2rem (32px) | Section spacing |
| xl | 3rem (48px) | Large section gaps |

## 🔘 Border Radius

| Size | Value | Use Case |
|------|-------|----------|
| sm | 6px | Small elements |
| md | 12px | Buttons, inputs |
| lg | 16px | Cards, modals |
| xl | 24px | Large cards |
| full | 9999px | Pills, circles |

## 🎬 Buttons

### Basic Button HTML
```html
<!-- Primary -->
<button class="btn btn-primary">Click Me</button>

<!-- Secondary -->
<button class="btn btn-secondary">Click Me</button>

<!-- Success -->
<button class="btn btn-success">Click Me</button>

<!-- Danger -->
<button class="btn btn-danger">Delete</button>

<!-- Warning -->
<button class="btn btn-warning">Warning</button>

<!-- Outline -->
<button class="btn btn-outline-primary">Outline</button>

<!-- Size Variants -->
<button class="btn btn-primary btn-sm">Small</button>
<button class="btn btn-primary">Default</button>
<button class="btn btn-primary btn-lg">Large</button>

<!-- With Icon -->
<button class="btn btn-primary">
  <i class="fas fa-save me-2"></i>Save
</button>

<!-- Icon Only -->
<button class="btn btn-icon btn-primary">
  <i class="fas fa-heart"></i>
</button>

<!-- Disabled -->
<button class="btn btn-primary" disabled>Disabled</button>
```

## 📝 Forms

### Input Examples
```html
<!-- Text Input -->
<div class="form-group">
  <label class="form-label">Full Name</label>
  <input type="text" class="form-control" placeholder="John Doe">
</div>

<!-- Email Input -->
<div class="form-group">
  <label class="form-label">Email</label>
  <input type="email" class="form-control" placeholder="john@example.com">
</div>

<!-- Password Input -->
<div class="form-group">
  <label class="form-label">Password</label>
  <input type="password" class="form-control" placeholder="••••••••">
</div>

<!-- Select Dropdown -->
<div class="form-group">
  <label class="form-label">Category</label>
  <select class="form-select">
    <option selected>Choose category...</option>
    <option>Technology</option>
    <option>Sports</option>
    <option>Business</option>
  </select>
</div>

<!-- Textarea -->
<div class="form-group">
  <label class="form-label">Comments</label>
  <textarea class="form-control" rows="4"></textarea>
</div>

<!-- File Input -->
<div class="form-group">
  <label class="form-label">Upload Image</label>
  <input type="file" class="form-control" accept="image/*">
</div>

<!-- With Icon -->
<div class="form-group">
  <div class="input-group">
    <span class="input-group-text">
      <i class="fas fa-user"></i>
    </span>
    <input type="text" class="form-control" placeholder="Username">
  </div>
</div>

<!-- Error State -->
<div class="form-group">
  <label class="form-label">Email</label>
  <input type="email" class="form-control is-invalid" value="invalid">
  <div class="invalid-feedback">Please provide a valid email.</div>
</div>
```

## 🃏 Cards

### Card Examples
```html
<!-- Basic Card -->
<div class="card">
  <div class="card-body">
    <h5 class="card-title">Card Title</h5>
    <p class="card-text">Card content goes here.</p>
  </div>
</div>

<!-- Card with Shadow -->
<div class="card shadow-md">
  <div class="card-body">
    <h5 class="card-title">Card Title</h5>
    <p class="card-text">Card content goes here.</p>
  </div>
</div>

<!-- Card with Hover Effect -->
<div class="card hover-lift">
  <div class="card-body">
    <h5 class="card-title">Card Title</h5>
    <p class="card-text">Card content goes here.</p>
  </div>
</div>

<!-- News Card -->
<div class="news-card">
  <div class="card-img-wrapper">
    <img src="image.jpg" alt="News Image">
  </div>
  <div class="card-body">
    <span class="badge bg-primary">Tech</span>
    <h6 class="card-title line-clamp-2">Article Title</h6>
    <p class="card-text text-muted small">Article excerpt...</p>
  </div>
</div>

<!-- Stat Card -->
<div class="card stat-card">
  <div class="card-body d-flex align-items-center justify-content-between">
    <div>
      <p class="text-muted small mb-1">Reading Time</p>
      <h4 class="mb-0">2.5h</h4>
    </div>
    <i class="fas fa-hourglass fa-3x text-primary opacity-25"></i>
  </div>
</div>
```

## 🏷️ Badges

### Badge Examples
```html
<!-- Color Variants -->
<span class="badge bg-primary">Primary</span>
<span class="badge bg-secondary">Secondary</span>
<span class="badge bg-success">Success</span>
<span class="badge bg-danger">Danger</span>
<span class="badge bg-warning">Warning</span>
<span class="badge bg-info">Info</span>

<!-- Pill Badges -->
<span class="badge bg-primary rounded-pill">Pill Badge</span>

<!-- Large Badges -->
<span class="badge badge-lg bg-primary">Large Badge</span>

<!-- With Icon -->
<span class="badge bg-primary">
  <i class="fas fa-star me-1"></i>Featured
</span>

<!-- Status Badges -->
<span class="badge-status active">Active</span>
<span class="badge-status inactive">Inactive</span>
<span class="badge-status pending">Pending</span>
```

## ⚠️ Alerts

### Alert Examples
```html
<!-- Success Alert -->
<div class="alert alert-success" role="alert">
  <i class="fas fa-check-circle me-2"></i>
  Successfully saved!
</div>

<!-- Danger Alert -->
<div class="alert alert-danger" role="alert">
  <i class="fas fa-times-circle me-2"></i>
  An error occurred!
</div>

<!-- Warning Alert -->
<div class="alert alert-warning" role="alert">
  <i class="fas fa-exclamation-triangle me-2"></i>
  Please be careful!
</div>

<!-- Info Alert -->
<div class="alert alert-info" role="alert">
  <i class="fas fa-info-circle me-2"></i>
  Here's some information.
</div>

<!-- Dismissible Alert -->
<div class="alert alert-success alert-dismissible fade show" role="alert">
  <i class="fas fa-check-circle me-2"></i>
  Great job!
  <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
</div>
```

## 🧩 Utility Classes

### Text Utilities
```html
<!-- Text Ellipsis -->
<p class="text-ellipsis">Long text that gets truncated...</p>

<!-- Line Clamp -->
<p class="line-clamp-2">Text limited to 2 lines...</p>
<p class="line-clamp-3">Text limited to 3 lines...</p>

<!-- Text Colors -->
<p class="text-primary">Primary text</p>
<p class="text-secondary">Secondary text</p>
<p class="text-success">Success text</p>
<p class="text-danger">Danger text</p>
<p class="text-warning">Warning text</p>
<p class="text-info">Info text</p>
<p class="text-muted">Muted text</p>
```

### Flexbox Utilities
```html
<!-- Flex Between -->
<div class="flex-between">
  <span>Left</span>
  <span>Right</span>
</div>

<!-- Flex Center -->
<div class="flex-center" style="height: 100px;">
  Centered content
</div>

<!-- Gap Utilities -->
<div class="d-flex gap-1">Items with small gap</div>
<div class="d-flex gap-2">Items with medium gap</div>
<div class="d-flex gap-3">Items with large gap</div>
```

### Spacing Utilities
```html
<!-- Padding -->
<div class="p-2">Padding 1rem</div>
<div class="p-3">Padding 1.5rem</div>
<div class="p-4">Padding 2rem</div>

<!-- Margin -->
<div class="m-2">Margin 1rem</div>
<div class="m-3">Margin 1.5rem</div>
<div class="m-4">Margin 2rem</div>

<!-- Padding X (horizontal) -->
<div class="px-3">Horizontal padding</div>

<!-- Padding Y (vertical) -->
<div class="py-3">Vertical padding</div>

<!-- Margin bottom -->
<div class="mb-3">Margin bottom</div>
```

## 🎯 Common Patterns

### Navigation Item
```html
<a href="#" class="sidebar-link">
  <i class="fas fa-home me-2"></i>
  <span>Dashboard</span>
</a>
```

### Profile Avatar
```html
<div class="rounded-circle d-flex align-items-center justify-content-center" 
     style="width: 56px; height: 56px; background: linear-gradient(135deg, #667eea, #764ba2); color: white;">
  <i class="fas fa-user fa-2x"></i>
</div>
```

### Empty State
```html
<div class="empty-state">
  <div class="empty-state-icon">
    <i class="fas fa-inbox fa-3x"></i>
  </div>
  <h6 class="empty-state-title">No Items Found</h6>
  <p class="empty-state-text text-muted">Try adjusting your filters</p>
  <button class="btn btn-primary btn-sm">Clear Filters</button>
</div>
```

### Stat Card
```html
<div class="card">
  <div class="card-body d-flex align-items-center justify-content-between">
    <div>
      <p class="text-muted small mb-1">Label</p>
      <h4 class="mb-0">123</h4>
    </div>
    <i class="fas fa-icon fa-3x text-primary opacity-25"></i>
  </div>
</div>
```

## 🔤 Typography Classes

```html
<!-- Headings -->
<h1>Heading 1</h1>
<h2>Heading 2</h2>
<h3>Heading 3</h3>
<h4>Heading 4</h4>
<h5>Heading 5</h5>
<h6>Heading 6</h6>

<!-- Font Weights -->
<p class="fw-normal">Normal weight</p>
<p class="fw-semibold">Semibold weight</p>
<p class="fw-bold">Bold weight</p>

<!-- Font Sizes -->
<p class="fs-1">Extra large text</p>
<p class="fs-2">Large text</p>
<p class="fs-3">Default text</p>
<p class="fs-4">Small text</p>
<p class="fs-5">Extra small text</p>

<!-- Line Height -->
<p class="lh-1">1.0 line height</p>
<p class="lh-base">1.5 line height (default)</p>
<p class="lh-lg">1.8 line height</p>
```

## 📱 Responsive Classes

```html
<!-- Show/Hide by Breakpoint -->
<div class="d-none d-sm-block">Hidden on mobile, visible on tablet+</div>
<div class="d-sm-none">Visible on mobile, hidden on tablet+</div>

<!-- Responsive Columns -->
<div class="col-12 col-sm-6 col-lg-3">
  Full width on mobile, half on tablet, quarter on desktop
</div>

<!-- Responsive Padding -->
<div class="p-2 p-sm-3 p-md-4">
  Padding scales with screen size
</div>
```

## 🚀 Quick Copy-Paste Components

### Login Form
```html
<div class="container-auth">
  <div class="card card-blur rounded-4">
    <div class="card-body p-5">
      <h3 class="fw-bold mb-4">Sign In</h3>
      <form>
        <div class="form-group mb-3">
          <label class="form-label">Email</label>
          <input type="email" class="form-control" placeholder="your@email.com">
        </div>
        <div class="form-group mb-4">
          <label class="form-label">Password</label>
          <input type="password" class="form-control" placeholder="••••••••">
        </div>
        <button class="btn btn-primary w-100 mb-3">Sign In</button>
      </form>
    </div>
  </div>
</div>
```

### News Grid
```html
<div class="row">
  <div class="col-12 col-md-6 col-lg-4">
    <div class="news-card">
      <div class="card-img-wrapper">
        <img src="image.jpg" alt="News">
      </div>
      <div class="card-body">
        <span class="badge bg-primary mb-2">Category</span>
        <h6 class="card-title line-clamp-2">Article Title</h6>
        <p class="card-text text-muted small">Excerpt text...</p>
      </div>
    </div>
  </div>
</div>
```

---

## 📚 Reference Files

- **CSS System**: `static/css/style.css`
- **Design Documentation**: `UI_REDESIGN_SUMMARY.md`
- **Implementation Checklist**: `UI_REDESIGN_IMPLEMENTATION_CHECKLIST.md`

---

**Last Updated**: 2024
**Version**: 1.0
