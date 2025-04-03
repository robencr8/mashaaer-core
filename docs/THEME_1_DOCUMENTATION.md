# Cosmic Theme 1 Documentation - Mashaaer Feelings

This document provides guidance on using the Cosmic Theme 1 across the Mashaaer Feelings application. The theme creates a unified cosmic experience with purple gradients, star-like animations, and interactive elements.

## Theme Overview

The Cosmic Theme 1 is characterized by:
- Deep space background with stars and animations
- Purple color scheme with glowing elements
- Interactive cosmic sphere as the primary UI element
- Responsive design for all device sizes
- RTL (Right-to-Left) support for Arabic language

## How to Use the Theme

### 1. Include the Theme CSS

To use the Cosmic Theme in any template, include these stylesheets:

```html
<link rel="stylesheet" href="{{ url_for('static', filename='css/meteor-shower.css') }}">
<link rel="stylesheet" href="{{ url_for('static', filename='css/cosmic-theme.css') }}">
```

### 2. Basic HTML Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="theme-color" content="#0c0c1d">
  <title>Page Title - Mashaaer Feelings</title>
  <link rel="stylesheet" href="{{ url_for('static', filename='css/meteor-shower.css') }}">
  <link rel="stylesheet" href="{{ url_for('static', filename='css/cosmic-theme.css') }}">
</head>
<body>
  <!-- Star background divs -->
  <div id="stars"></div>
  <div id="stars2"></div>
  <div id="stars3"></div>
  
  <!-- Page content -->
  <div class="container">
    <h1>Page Title</h1>
    
    <!-- Content goes here -->
    
    <!-- Interactive Cosmic Sphere -->
    <div class="cosmic-sphere" onclick="yourFunction()"></div>
  </div>
  
  <script src="{{ url_for('static', filename='js/meteor-shower.js') }}"></script>
</body>
</html>
```

### 3. Theme Modes

The theme supports light and dark modes through HTML data attributes:

```javascript
// Set dark theme (Arabic)
document.documentElement.setAttribute('data-theme', 'night');

// Set light theme (English)
document.documentElement.setAttribute('data-theme', 'day');
```

### 4. Common Components

#### Cards

```html
<div class="cosmic-card">
  <h2 class="card-title">Card Title</h2>
  <p>Card content goes here.</p>
</div>
```

#### Buttons

```html
<!-- Primary Button -->
<button class="btn btn-primary">Primary Action</button>

<!-- Outline Button -->
<button class="btn btn-outline">Secondary Action</button>

<!-- Button Group -->
<div class="btn-group">
  <button class="btn btn-outline">Cancel</button>
  <button class="btn btn-primary">Confirm</button>
</div>
```

#### Forms

```html
<form>
  <div class="form-group">
    <label for="inputField">Label Text</label>
    <input type="text" id="inputField" class="form-control">
  </div>
  
  <div class="form-group toggle-group">
    <label for="toggleOption">Toggle Option</label>
    <label class="toggle-switch">
      <input type="checkbox" id="toggleOption">
      <span class="slider"></span>
    </label>
  </div>
</form>
```

#### Navigation Menu

```html
<div class="menu">
  <a href="/page1" class="menu-item">Menu Item 1</a>
  <a href="/page2" class="menu-item">Menu Item 2</a>
  <a href="/page3" class="menu-item">Menu Item 3</a>
</div>
```

#### Cosmic Sphere

```html
<!-- Standard Sphere -->
<div class="cosmic-sphere"></div>

<!-- Small Sphere -->
<div class="cosmic-sphere-small"></div>
```

#### Back Button

```html
<button class="back-btn" onclick="window.location.href='/previous-page'">&#8592;</button>
```

### 5. RTL Support

For Arabic language pages, add RTL direction:

```html
<html lang="ar" dir="rtl">
```

The theme automatically adjusts form layouts and alignments for RTL.

## CSS Variables

You can override these variables for custom styling:

```css
:root {
  --primary-purple: #9c27b0;
  --primary-purple-light: #d0a0ff;
  --primary-purple-dark: #6a0080;
  --primary-glow: rgba(156, 39, 176, 0.6);
  --dark-bg: #0f0f23;
  --dark-bg-gradient: radial-gradient(circle at center, #151529 0%, #0c0c1d 100%);
  --text-color: #ffffff;
  --text-secondary: #e0d0ff;
  --card-bg: rgba(18, 18, 18, 0.8);
  --card-border: rgba(156, 39, 176, 0.3);
}
```

## Responsiveness

The theme is built to be responsive across devices. The main breakpoint is at 768px:

```css
@media (max-width: 768px) {
  /* Mobile styles */
}
```

## Animation Effects

The theme includes several animations:
- Cosmic sphere pulse effect
- Star twinkling
- Hover effects for menu items and buttons

## Integration with Meteor Shower Background

The theme works with the meteor-shower.css and meteor-shower.js files to create the animated star background. Make sure to include both files for the full effect.

## Example Templates

For reference implementations, see:
- homepage.html
- user_settings.html
- error.html

These templates demonstrate the proper use of the Cosmic Theme components and structure.