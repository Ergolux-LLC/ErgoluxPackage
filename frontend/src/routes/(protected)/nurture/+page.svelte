<script lang="ts">
  import { page } from "$app/stores";
  import { derived } from "svelte/store";

  // derive the last non-empty segment from the current pathname and convert to Title Case
  const routeName = derived(page, ($page) => {
    const parts = $page.url.pathname.split("/").filter(Boolean);
    const last = parts.length ? parts[parts.length - 1] : "home";
    return last
      .replace(/[-_]+/g, " ")
      .split(" ")
      .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
      .join(" ");
  });
</script>

<svelte:head>
  <title>{$routeName}</title>
</svelte:head>

<h1>{$routeName}</h1>
