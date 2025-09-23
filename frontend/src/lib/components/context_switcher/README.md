# Context Switcher Component

A SvelteKit component for navigating between different sub-applications in the Ergolux platform.

## Features

- **Dark mode compatible** - Designed for dark themes with proper contrast
- **Distinct color system** - Each sub-app has its unique color for visual recognition
- **Grayscale-to-color transitions** - Icons start muted and become vibrant on hover
- **Enhanced active states** - Current sub-app gets boosted brightness and glow effects
- **Loveable click animations** - Delightful bounce effects with icon pulse and ripple animations
- **Celebration feedback** - Special animation when switching to a new sub-app
- **Responsive design** - Adapts to different screen sizes
- **Accessibility compliant** - Proper ARIA labels and keyboard navigation
- **Smooth animations** - Sophisticated hover effects and transitions
- **Bootstrap Icons** - Uses Bootstrap Icons for consistent iconography
- **Sticky positioning** - Stays at the top of the page with backdrop blur

## Sub-Applications

The context switcher includes 9 sub-applications with distinct colors:

| Icon | Sub-App      | Color                                        | Purpose                           |
| ---- | ------------ | -------------------------------------------- | --------------------------------- |
| 🧭   | **Discover** | <span style="color:#3b82f6">■</span> Blue    | Find new opportunities and leads  |
| 📋   | **Qualify**  | <span style="color:#10b981">■</span> Emerald | Assess and validate prospects     |
| 💬   | **Nurture**  | <span style="color:#f59e0b">■</span> Amber   | Build relationships with clients  |
| 📝   | **Commit**   | <span style="color:#ef4444">■</span> Red     | Finalize agreements and contracts |
| 🚀   | **Onboard**  | <span style="color:#8b5cf6">■</span> Violet  | Welcome and setup new clients     |
| 🛟    | **Support**  | <span style="color:#06b6d4">■</span> Cyan    | Provide ongoing assistance        |
| ⛶    | **Expand**   | <span style="color:#84cc16">■</span> Lime    | Grow existing relationships       |
| 🔄   | **Renew**    | <span style="color:#f97316">■</span> Orange  | Extend and refresh contracts      |
| 📢   | **Advocate** | <span style="color:#ec4899">■</span> Pink    | Promote and represent clients     |

### Color Interaction States

- **Default State**: Icons appear grayscale and muted (`filter: grayscale(1) brightness(0.7)`)
- **Hover State**: Icons transition to full color with glow effects and lift animation
- **Active State**: Current sub-app remains colored with enhanced brightness (120% → 130% on hover)
- **Click Animation**: Loveable bounce effect with icon pulse, ripple, and enhanced glow (0.6s duration)
- **Celebration Animation**: Special bounce sequence when becoming the new active sub-app (0.8s duration)
- **Transitions**: Smooth 0.3s transitions between all states with cubic-bezier easing

## Usage

### Basic Implementation

```svelte
<script>
  import { ContextSwitcher } from '$lib/components/context_switcher';

  let activeSubApp = 'discover';

  function handleSubAppChange(event) {
    const subApp = event.detail;
    activeSubApp = subApp.id;
    // Implement your navigation logic here
    console.log(`Switching to ${subApp.label}`);
  }
</script>

<ContextSwitcher
  {activeSubApp}
  on:subAppChange={handleSubAppChange}
/>
```

### Integration with SvelteKit Router

```svelte
<script>
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { ContextSwitcher } from '$lib/components/context_switcher';

  // Determine active sub-app from current route
  $: activeSubApp = $page.route.id?.split('/')[1] || 'discover';

  function handleSubAppChange(event) {
    const subApp = event.detail;
    goto(`/${subApp.id}`);
  }
</script>

<ContextSwitcher
  {activeSubApp}
  on:subAppChange={handleSubAppChange}
/>
```

### Adding to Layout

Place the context switcher in your main layout to appear on all pages:

```svelte
<!-- src/routes/+layout.svelte -->
<script>
  import { ContextSwitcher } from '$lib/components/context_switcher';
  // ... other imports
</script>

<ContextSwitcher {activeSubApp} on:subAppChange={handleNavigation} />

<main>
  <slot />
</main>
```

## Props

| Prop           | Type     | Default      | Description                             |
| -------------- | -------- | ------------ | --------------------------------------- |
| `activeSubApp` | `string` | `'discover'` | The currently active sub-application ID |

## Events

| Event          | Detail Type | Description                                  |
| -------------- | ----------- | -------------------------------------------- |
| `subAppChange` | `SubApp`    | Fired when a user clicks on a sub-app button |

## Styling

The component uses CSS custom properties that match your existing dark theme:

```css
--color-bg-secondary: #161b22
--color-bg-tertiary: #21262d
--color-bg-canvas: #010409
--color-border-default: #30363d
--color-border-muted: #21262d
--color-border-subtle: #373e47
--color-text-primary: #f0f6fc
--color-text-secondary: #9198a1
--bs-primary: #0d6efd
```

## Customization

### Custom Icons

To use different icons, modify the `subApps` array in `ContextSwitcher.svelte`:

```javascript
const subApps = [
  { id: "discover", label: "Discover", icon: "your-custom-icon" },
  // ... other apps
];
```

### Custom Styling

Override the CSS custom properties or add additional styles:

```css
.context-switcher {
  /* Your custom styles */
}
```

## Dependencies

- **Bootstrap Icons** - Ensure Bootstrap Icons are included in your project
- **SvelteKit** - Compatible with SvelteKit applications
- **CSS Custom Properties** - Uses modern CSS variables for theming

## Browser Support

- Modern browsers with CSS Grid and Custom Properties support
- Mobile responsive (tested on iOS/Android)
- Supports both light and dark mode preferences
