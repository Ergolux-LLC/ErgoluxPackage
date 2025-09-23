# Context Switcher Component

A sophisticated collapsible navigation component for switching between sub-applications in the Ergolux portal. Features hover-expand functionality, compact design, and engaging animations.

## Features

- **🎯 Collapsible Design**: Shows only the active sub-app icon when at rest
- **🔄 Hover Expansion**: Smoothly expands to reveal all sub-app options on hover
- **📏 Compact Size**: 50% smaller buttons (2rem vs 4rem) for efficient space usage
- **🎨 Enhanced Icons**: Larger, more prominent icons with better fill and visibility
- **🌈 Distinct Colors**: Each sub-app has unique, dark-mode compatible colors
- **💫 Loveable Animations**: Bounce effects, ripple animations, and smooth transitions
- **📱 Responsive Design**: Adapts proportionally across all device sizes
- **♿ Accessible**: Proper ARIA labels, keyboard navigation, and semantic markup

## Quick Start

```svelte
<script>
  import { ContextSwitcher } from '$lib/components/context_switcher';

  let currentSubApp = 'discover';

  function handleSubAppChange(event) {
    const subApp = event.detail;
    currentSubApp = subApp.id;
    // Your navigation logic here
  }
</script>

<ContextSwitcher
  activeSubApp={currentSubApp}
  on:subAppChange={handleSubAppChange}
/>
```

## Behavior

### Collapsible States

- **Collapsed**: Only the active sub-app icon is visible (2.5rem size)
- **Expanded**: All sub-app icons are visible on hover (2rem base size)
- **Smooth Transitions**: Elegant expand/collapse animations with cubic-bezier easing

### Size Specifications

- **Base Size**: 2rem (50% smaller than original 4rem)
- **Tablet Size**: 1.75rem (≤768px)
- **Mobile Size**: 1.5rem (≤576px)
- **Collapsed Active**: 2.5rem (slightly larger when alone)
- **Icon Size**: 1rem (enhanced from 1.25rem for better fill)

## Sub-Applications

| Icon | Sub-App  | Color             | Description                       |
| ---- | -------- | ----------------- | --------------------------------- |
| 🔍   | Discover | Blue (#3b82f6)    | Find new opportunities and leads  |
| ✅   | Qualify  | Emerald (#10b981) | Assess and validate prospects     |
| 🤝   | Nurture  | Amber (#f59e0b)   | Build relationships with clients  |
| 📝   | Commit   | Red (#ef4444)     | Finalize agreements and contracts |
| 🚀   | Onboard  | Violet (#8b5cf6)  | Welcome and setup new clients     |
| 🛠️   | Support  | Cyan (#06b6d4)    | Provide ongoing assistance        |
| 📈   | Expand   | Lime (#84cc16)    | Grow existing relationships       |
| 🔄   | Renew    | Orange (#f97316)  | Extend and refresh contracts      |
| 🗣️   | Advocate | Pink (#ec4899)    | Promote and represent clients     |

## Animation System

### Click Animations

- **loveableBounce**: 0.6s duration with scale and rotation effects
- **celebration**: 0.8s enhanced animation for new sub-app activation
- **Ripple Effect**: Expanding circle animation (40px/60px for compact size)

### Transitions

- **Hover**: 0.2s smooth color transitions with glow effects
- **Expand**: 0.3s cubic-bezier easing for show/hide
- **Color**: Grayscale to vibrant with enhanced brightness

## Technical Details

### State Management

```svelte
let isExpanded = false;

function handleContainerMouseEnter() {
  isExpanded = true;
}

function handleContainerMouseLeave() {
  isExpanded = false;
}
```

### Responsive Breakpoints

```css
/* Tablet (≤768px) */
@media (max-width: 768px) {
  --button-size: 1.75rem;
  --icon-size: 0.875rem;
}

/* Mobile (≤576px) */
@media (max-width: 576px) {
  --button-size: 1.5rem;
  --icon-size: 0.75rem;
}
```

### Color System

Uses CSS custom properties for consistent theming:

```css
--context-switcher-discover: #3b82f6;
--context-switcher-qualify: #10b981;
/* ... etc */
```

## Events

### `subAppChange`

Dispatched when a user clicks on a sub-app icon.

**Detail Object:**

```typescript
{
  id: string; // e.g., 'discover'
  label: string; // e.g., 'Discover'
  icon: string; // Bootstrap icon class
  description: string;
}
```

## Integration

### In Layout Components

```svelte
<!-- src/routes/(protected)/+layout.svelte -->
<header class="main-header">
  <ContextSwitcher
    activeSubApp={$page.params.subApp || 'discover'}
    on:subAppChange={handleNavigation}
  />
</header>
```

### With SvelteKit Routing

```svelte
<script>
  import { goto } from '$app/navigation';

  function handleSubAppChange(event) {
    const { id } = event.detail;
    goto(`/${id}`);
  }
</script>
```

## Accessibility

- **Semantic HTML**: Uses `<nav>` with proper `role="tablist"`
- **ARIA Labels**: Descriptive labels for each sub-app
- **Keyboard Navigation**: Full keyboard support with `tabindex="0"`
- **Color Contrast**: Dark-mode compatible colors meeting WCAG guidelines
- **Focus Management**: Visible focus indicators with proper outlines

## Customization

### Override Colors

```css
:root {
  --context-switcher-discover: #custom-blue;
  --context-switcher-qualify: #custom-green;
}
```

### Adjust Sizing

```css
.context-switcher {
  --button-size: 2.5rem; /* Custom size */
  --icon-size: 1.25rem; /* Custom icon size */
}
```

### Animation Timing

```css
.context-switcher-button {
  --transition-duration: 0.3s; /* Custom transition speed */
}
```

## Demo

Run the demo component to see the context switcher in action:

```bash
npm run dev
# Navigate to the context switcher demo page
```

The demo showcases:

- Collapsible hover-expand behavior
- All color variations and animations
- Responsive design across device sizes
- Interactive click and hover effects
