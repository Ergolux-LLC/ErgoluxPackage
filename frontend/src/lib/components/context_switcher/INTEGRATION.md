# Integration Example

To integrate the Context Switcher into your existing dashboard, follow these steps:

## 1. Add to Dashboard Layout

```svelte
<!-- In your dashboard +page.svelte or +layout.svelte -->
<script>
  import { ContextSwitcher } from '$lib/components/context_switcher';

  let currentSubApp = 'discover';

  function handleSubAppChange(event) {
    const subApp = event.detail;
    currentSubApp = subApp.id;

    // TODO: Implement actual navigation logic
    // Examples:
    // - goto(`/dashboard/${subApp.id}`)
    // - dispatch('navigate', subApp)
    // - Update application state

    console.log(`Switched to ${subApp.label} sub-app`);
  }
</script>

<!-- Context Switcher at the top -->
<ContextSwitcher
  activeSubApp={currentSubApp}
  on:subAppChange={handleSubAppChange}
/>

<!-- Rest of your dashboard content -->
<div class="dashboard-content">
  <!-- Your existing dashboard components -->
</div>
```

## 2. Alternative: Add to Main Layout

For global access across all protected routes:

```svelte
<!-- src/routes/(protected)/+layout.svelte -->
<script>
  import { ContextSwitcher } from '$lib/components/context_switcher';
  import { page } from '$app/stores';

  // Determine current sub-app from URL
  $: currentSubApp = $page.url.pathname.split('/')[2] || 'discover';

  function handleSubAppChange(event) {
    const subApp = event.detail;
    goto(`/dashboard/${subApp.id}`);
  }
</script>

<ContextSwitcher
  activeSubApp={currentSubApp}
  on:subAppChange={handleSubAppChange}
/>

<main class="main-content">
  <slot />
</main>

<style>
  .main-content {
    padding-top: 0; /* Context switcher is sticky */
  }
</style>
```

## 3. Quick Test Integration

Add this to your dashboard to test the component:

```svelte
<!-- Add this import to the top of your dashboard script -->
import { ContextSwitcher } from '$lib/components/context_switcher';

<!-- Add this right after the opening body/main tag -->
<ContextSwitcher activeSubApp="discover" />
```

The context switcher will automatically appear at the top with all 9 sub-app icons.
