<script lang="ts">
  let loginUrl = "/";
  if (typeof window !== "undefined") {
    loginUrl = `${window.location.protocol}//${window.location.host}/`;
  }
</script>

<main>
  <h1>Logged Out</h1>
  <p>You have been successfully logged out.</p>
  <a href={loginUrl} class="login-link">Return to Login</a>
</main>

<style>
  :global(body) {
    background: #181a1b;
    color: #f3f3f3;
    font-family: system-ui, sans-serif;
    margin: 0;
    padding: 0;
  }
  main {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
  }
  h1 {
    margin-bottom: 0.5em;
  }
  p {
    margin-bottom: 1.5em;
    opacity: 0.85;
  }
  .login-link {
    color: #4f8cff;
    text-decoration: none;
    font-weight: bold;
    border: 1px solid #4f8cff;
    padding: 0.5em 1.2em;
    border-radius: 6px;
    transition:
      background 0.2s,
      color 0.2s;
  }
  .login-link:hover {
    background: #4f8cff;
    color: #fff;
  }
</style>
