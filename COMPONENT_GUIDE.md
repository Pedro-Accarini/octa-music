# UI Component Style Guide

This guide explains how to use the design system in Octa Music.

## Design Tokens

All design tokens are defined in `/src/static/css/design-tokens.css`. Import this file first in your HTML templates.

### Color System

```css
/* Primary Colors (Spotify Green) */
--color-primary-500: #1db954;  /* Main brand color */
--color-primary-700: #159c41;  /* Darker for hover states */

/* Semantic Colors */
--color-success: #10b981;
--color-error: #ef4444;
--color-warning: #f59e0b;
--color-info: #3b82f6;
```

**WCAG AA Compliance:**
- Primary green (#1db954) on white: 3.46:1 (AA for large text 18px+)
- Text primary (#222) on white: 16.79:1 (AAA)
- Text secondary (#555) on white: 7.48:1 (AAA)

### Spacing Scale

Uses a 4px base grid system:
```css
--spacing-1: 0.25rem;  /* 4px */
--spacing-2: 0.5rem;   /* 8px */
--spacing-3: 0.75rem;  /* 12px */
--spacing-4: 1rem;     /* 16px */
--spacing-6: 1.5rem;   /* 24px */
--spacing-8: 2rem;     /* 32px */
--spacing-12: 3rem;    /* 48px */
```

### Typography Scale

```css
--font-size-sm: 0.875rem;   /* 14px */
--font-size-base: 1rem;     /* 16px */
--font-size-lg: 1.125rem;   /* 18px */
--font-size-xl: 1.25rem;    /* 20px */
--font-size-2xl: 1.5rem;    /* 24px */
--font-size-3xl: 1.875rem;  /* 30px */
```

### Responsive Breakpoints

```css
320px  - Mobile Small
375px  - Mobile Standard  
412px  - Mobile Large
480px  - Phablet
768px  - Tablet
1024px - Desktop
1280px - Desktop Large
1440px - Desktop XL
```

## Components

### Buttons

**Usage:**
```html
<!-- Primary Button (44px minimum touch target) -->
<button class="btn btn-primary">Search</button>

<!-- Secondary Button -->
<button class="btn btn-secondary">Cancel</button>

<!-- Large Button -->
<button class="btn btn-primary btn-lg">Large Button</button>

<!-- Full Width Button -->
<button class="btn btn-primary btn-block">Full Width</button>
```

**Accessibility:**
- Minimum height: 44px (WCAG touch target)
- Clear focus indicators with outline ring
- High contrast hover states

### Input Fields

**Usage:**
```html
<!-- Text Input (44px minimum height) -->
<input type="text" class="input" placeholder="Enter text">

<!-- With Form Group -->
<div class="form-group">
  <label class="form-label" for="email">Email</label>
  <input type="email" id="email" class="input" placeholder="you@example.com">
  <span class="form-help">We'll never share your email.</span>
</div>
```

**Accessibility:**
- Minimum height: 44px (WCAG touch target)
- 3px focus ring for keyboard navigation
- High contrast borders and placeholders

### Cards

**Usage:**
```html
<!-- Standard Card -->
<div class="card">
  <div class="card-header">
    <h3 class="card-title">Card Title</h3>
    <p class="card-subtitle">Subtitle text</p>
  </div>
  <div class="card-body">
    Card content goes here
  </div>
</div>

<!-- Compact Card -->
<div class="card card-compact">
  Content with less padding
</div>
```

### Forms

**Usage:**
```html
<!-- Inline Form (horizontal) -->
<form class="form-inline">
  <input type="text" class="input" placeholder="Search">
  <button type="submit" class="btn btn-primary">Search</button>
</form>

<!-- Standard Form -->
<form>
  <div class="form-group">
    <label class="form-label" for="name">Name</label>
    <input type="text" id="name" class="input">
  </div>
  <button type="submit" class="btn btn-primary">Submit</button>
</form>
```

## Layout Utilities

### Flexbox

```html
<!-- Flex Container -->
<div class="flex items-center justify-between gap-4">
  <div>Item 1</div>
  <div>Item 2</div>
</div>

<!-- Column Layout -->
<div class="flex flex-col gap-6">
  <div>Row 1</div>
  <div>Row 2</div>
</div>
```

### Spacing

```html
<!-- Margin Top -->
<div class="mt-4">Content with 16px top margin</div>

<!-- Margin Bottom -->
<div class="mb-6">Content with 24px bottom margin</div>

<!-- Padding -->
<div class="p-4">Content with 16px padding</div>
```

### Text Utilities

```html
<!-- Text Alignment -->
<p class="text-center">Centered text</p>
<p class="text-left">Left-aligned text</p>

<!-- Font Sizes -->
<p class="text-sm">Small text (14px)</p>
<p class="text-base">Base text (16px)</p>
<p class="text-lg">Large text (18px)</p>

<!-- Font Weights -->
<span class="font-normal">Normal weight (400)</span>
<span class="font-semibold">Semibold (600)</span>
<span class="font-bold">Bold (700)</span>
```

## Dark Mode

Dark mode is automatically applied via the `.dark-mode` class on `<body>`. The design tokens automatically adjust:

```javascript
// Toggle dark mode
document.body.classList.toggle('dark-mode');
localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));
```

## Creating New Components

When adding new components:

1. **Use design tokens** - Never use hard-coded values
2. **Ensure accessibility:**
   - Minimum 44px touch targets for interactive elements
   - 3px focus rings with proper contrast
   - WCAG AA color contrast (4.5:1 for normal text, 3:1 for large text)
3. **Make it responsive** - Test at all breakpoints
4. **Support dark mode** - Use theme tokens (--text-primary, --bg-primary, etc.)

### Example New Component

```css
.my-component {
  /* Use design tokens */
  padding: var(--spacing-4);
  background: var(--surface-base);
  border-radius: var(--radius-base);
  box-shadow: var(--shadow-md);
  
  /* Transitions */
  transition: all var(--transition-fast);
}

.my-component:hover {
  box-shadow: var(--shadow-lg);
  transform: translateY(-2px);
}

.my-component:focus-visible {
  outline: var(--focus-ring-width) solid var(--focus-ring-color);
  outline-offset: var(--focus-ring-offset);
}
```

## File Structure

```
src/static/css/
├── design-tokens.css  # All design tokens (import first)
├── base.css          # Base styles, reusable components
├── main.css          # Layout and page-specific styles
├── spotify.css       # Spotify search component
├── youtube.css       # YouTube search component
└── login.css         # Login page styles
```

## Import Order

Always import CSS files in this order in your HTML templates:

```html
<link rel="stylesheet" href="{{ url_for('static', filename='css/design-tokens.css') }}">
<link rel="stylesheet" href="{{ url_for('static', filename='css/base.css') }}">
<link rel="stylesheet" href="{{ url_for('static', filename='css/main.css') }}">
<!-- Then component-specific CSS -->
```

## Migration Notes

### From Old to New System

**Old way:**
```html
<button style="padding: 0.5rem 1rem; background: #1db954;">Click</button>
```

**New way:**
```html
<button class="btn btn-primary">Click</button>
```

### Key Changes

1. **No inline styles** - Use utility classes or component classes
2. **Use design tokens** - Replace hard-coded values with CSS variables
3. **Consistent spacing** - Use the 4px grid system
4. **Proper focus states** - All interactive elements have focus rings
5. **Minimum touch targets** - All buttons/inputs are 44px minimum

## Testing Checklist

When adding/modifying components:

- [ ] Test at all breakpoints (320, 375, 412, 480, 768, 1024, 1280, 1440px)
- [ ] Verify no horizontal scroll on mobile
- [ ] Check keyboard navigation (Tab key)
- [ ] Verify focus indicators are visible
- [ ] Test in light and dark mode
- [ ] Verify touch targets are 44-48px minimum
- [ ] Check color contrast with WCAG tools
- [ ] Test with screen reader if possible
