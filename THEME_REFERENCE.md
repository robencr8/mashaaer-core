# Mashaaer Feelings - Theme Reference

## Theme 1: Cosmic Experience

**Files:**
- `static/css/cosmic-theme.css` - Main theme file
- `static/css/meteor-shower.css` - Star background animations
- `static/js/meteor-shower.js` - Star background functionality

**Design Elements:**
- Deep space background with animated stars and particles
- Central purple cosmic sphere as main interaction point
- Purple color scheme with glowing elements
- Day/Night modes corresponding to English/Arabic language settings
- Responsive design for all device sizes

**Theme Features:**
- Interactive glowing sphere
- Cards with backdrop blur effect
- Custom form elements
- Animated menu items
- RTL (Right-to-Left) support for Arabic language
- Toggle switches with purple accent
- Consistent typography

**Applied to:**
- Homepage
- User Settings
- Error pages
- Basic API test pages

**Documentation:**
- Detailed theme documentation available in `docs/THEME_1_DOCUMENTATION.md`

## Theme 2: Falling Stars

**Files:**
- `static/css/falling-stars-theme.css` - Main theme file
- `static/js/falling-stars.js` - Star animation functionality

**Design Elements:**
- Serene night sky with animated falling stars
- Central purple orb as main interaction point (consistent with Theme 1)
- Gentle visual effects optimized for reduced eye strain
- Shooting stars and nebula cloud elements for visual depth
- Star trail animations on interactive elements

**Theme Features:**
- Dynamic star generation with unique movement patterns
- Subtle animations that don't distract from content
- Same UI component styling as Theme 1 for consistency
- Nebula cloud effects in the background
- Optimized performance for extended use

**Applied to:**
- Theme 2 example page
- Theme showcase page

**Documentation:**
- Comprehensive documentation available in `docs/THEME_DOCUMENTATION.md`

## How to Use Theme 1

1. Include the theme CSS files:
```html
<link rel="stylesheet" href="{{ url_for('static', filename='css/meteor-shower.css') }}">
<link rel="stylesheet" href="{{ url_for('static', filename='css/cosmic-theme.css') }}">
```

2. Add the star background elements:
```html
<div id="stars"></div>
<div id="stars2"></div>
<div id="stars3"></div>
```

3. Include the JavaScript file at the end of the body:
```html
<script src="{{ url_for('static', filename='js/meteor-shower.js') }}"></script>
```

4. Set the theme mode based on language or user preference:
```javascript
// Arabic/Night mode
document.documentElement.setAttribute('data-theme', 'night');

// English/Day mode
document.documentElement.setAttribute('data-theme', 'day');
```

## How to Use Theme 2

1. Include the theme CSS file:
```html
<link rel="stylesheet" href="{{ url_for('static', filename='css/falling-stars-theme.css') }}">
```

2. Add the stars container element:
```html
<div class="stars-container"></div>
```

3. Include the JavaScript file at the end of the body:
```html
<script src="{{ url_for('static', filename='js/falling-stars.js') }}"></script>
```

## Theme Selection System

Users can select their preferred theme from the themes showcase page (`/themes`). The selection is stored in the database and applied across all pages of the application.

### Backend Implementation

The selected theme is stored as a user setting named `theme` in the database. The value is either `cosmic` for Theme 1 or `falling-stars` for Theme 2.

```python
# Store theme preference
db_manager.set_setting('theme', 'cosmic')  # or 'falling-stars'

# Retrieve theme preference
current_theme = db_manager.get_setting('theme', 'cosmic')  # Default to cosmic
```

### Frontend Implementation

Templates check the current theme setting and include the appropriate CSS/JS files:

```html
{% if current_theme == 'cosmic' %}
    <link rel="stylesheet" href="{{ url_for('static', filename='css/meteor-shower.css') }}">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/cosmic-theme.css') }}">
    <!-- Later in the body -->
    <script src="{{ url_for('static', filename='js/meteor-shower.js') }}"></script>
{% elif current_theme == 'falling-stars' %}
    <link rel="stylesheet" href="{{ url_for('static', filename='css/falling-stars-theme.css') }}">
    <!-- Later in the body -->
    <script src="{{ url_for('static', filename='js/falling-stars.js') }}"></script>
{% endif %}
```

See the full documentation files for complete details on using these themes.