<script lang="ts">
  import { config } from "$lib/config/environment";
</script>

<svelte:head>
  <title>{config.app.name} - Not Found</title>
</svelte:head>

<div class="container py-5">
  <div class="row justify-content-center">
    <div class="col-md-8 text-center">
      <h1 class="display-4">404 — Page Not Found</h1>
      <p class="lead">We couldn't find the page you're looking for.</p>
      <a class="btn btn-primary" href="/">Go home</a>
    </div>
  </div>
</div>
