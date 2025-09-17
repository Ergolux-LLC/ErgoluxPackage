<script lang="ts">
  import { createEventDispatcher } from "svelte";

  const dispatch = createEventDispatcher<{
    ready: { ready: boolean; password: string };
  }>();

  // Support prop for external binding (needed for DialogEngine integration)
  export let value = "";
  export let defaultValue = "DevPassword!234"; // Strong default for development

  let password = defaultValue || "DevPassword!234";
  let show = false;

  // Password requirements
  const requirements = [
    { label: "At least 12 characters", test: (pw: string) => pw.length >= 12 },
    { label: "A lowercase letter", test: (pw: string) => /[a-z]/.test(pw) },
    { label: "An uppercase letter", test: (pw: string) => /[A-Z]/.test(pw) },
    { label: "A number", test: (pw: string) => /\d/.test(pw) },
    { label: "A symbol", test: (pw: string) => /[^A-Za-z0-9]/.test(pw) },
  ];

  // Evaluate password
  $: checks = requirements.map((r) => r.test(password));
  $: passed = checks.filter(Boolean).length;
  $: ready = passed === requirements.length;

  // Traffic light color
  $: color =
    passed === requirements.length ? "green" : passed >= 3 ? "yellow" : "red";

  // Update external value when password changes and is valid
  $: {
    if (ready) {
      value = password;
    } else {
      value = "";
    }
  }

  // Notify parent when ready
  $: dispatch("ready", { ready, password });

  function recommendBitwarden() {
    window.open("https://bitwarden.com/", "_blank");
  }
</script>

<div class="password-entry">
  <label for="password"
    >Password <span class="pw-req">(min. 12 characters)</span></label
  >
  <div class="input-row">
    <input
      id="password"
      type={show ? "text" : "password"}
      bind:value={password}
      autocomplete="new-password"
      placeholder="At least 12 characters, strong password"
      aria-describedby="password-guidance"
    />
    <button
      type="button"
      class="show-btn"
      on:click={() => (show = !show)}
      aria-label={show ? "Hide password" : "Show password"}
    >
      {show ? "Hide" : "Show"}
    </button>
  </div>

  <div class="compact-strength">
    <div class="strength-meter">
      <span class="strength-label">
        {color === "green"
          ? "Strong"
          : color === "yellow"
            ? "Moderate"
            : "Weak"}
      </span>
      <span class="meter-lights">
        <span class="light" class:red={color === "red"}></span>
        <span class="light" class:yellow={color === "yellow"}></span>
        <span class="light" class:green={color === "green"}></span>
      </span>
    </div>

    <div class="compact-requirements">
      {#each requirements as req, i}
        <span class="req-pill" class:met={checks[i]} title={req.label}>
          {req.label.replace(/^A |An |At least /g, "").split(" ")[0]}
        </span>
      {/each}
    </div>
  </div>

  {#if !ready}
    <div class="missing-requirements">
      <span class="missing-label">Missing: </span>
      {#each requirements.filter((_, i) => !checks[i]) as req, i}
        <span class="req-missing"
          >{i > 0 ? ", " : ""}{req.label
            .replace(/^A |An |At least /g, "")
            .split(" ")[0]}</span
        >
      {/each}
    </div>
  {/if}
</div>

<style>
  .password-entry {
    display: flex;
    flex-direction: column;
    gap: 0.5em;
    margin-bottom: 0.8em;
  }
  label {
    font-weight: 500;
    color: #f3f3f3;
    margin-bottom: 0.2em;
  }
  .input-row {
    display: flex;
    align-items: center;
    gap: 0.5em;
    margin-bottom: 0.3em;
  }
  input[type="password"],
  input[type="text"] {
    flex: 1;
    padding: 0.7em;
    border-radius: 7px;
    border: 1px solid #444;
    background: #23272b;
    color: #f3f3f3;
    font-size: 1em;
  }
  .show-btn {
    background: #23272b;
    color: #4f8cff;
    border: 1px solid #4f8cff;
    border-radius: 5px;
    padding: 0.4em 0.8em;
    cursor: pointer;
    font-size: 0.95em;
    transition:
      background 0.2s,
      color 0.2s;
  }
  .show-btn:hover {
    background: #4f8cff;
    color: #fff;
  }

  /* Compact strength meter */
  .compact-strength {
    display: flex;
    flex-direction: column;
    gap: 0.5em;
    background: #23272b;
    border-radius: 6px;
    padding: 0.4em 0.5em;
    font-size: 0.9em;
  }

  .strength-meter {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .strength-label {
    font-weight: 600;
    font-size: 0.9em;
  }

  .meter-lights {
    display: flex;
    gap: 0.3em;
  }

  .light {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: #2c2c2c;
    display: inline-block;
  }

  .light.red {
    background: #ff6b6b;
  }
  .light.yellow {
    background: #ffe082;
  }
  .light.green {
    background: #4caf50;
  }

  /* Requirements pills */
  .compact-requirements {
    display: flex;
    flex-wrap: wrap;
    gap: 0.3em;
  }

  .req-pill {
    font-size: 0.75em;
    background: #2c2c2c;
    color: #ff6b6b;
    padding: 0.2em 0.5em;
    border-radius: 3px;
    white-space: nowrap;
  }

  .req-pill.met {
    color: #4caf50;
    text-decoration: line-through;
  }

  /* Missing requirements */
  .missing-requirements {
    font-size: 0.8em;
    color: #ff6b6b;
    margin-top: 0.2em;
  }

  .missing-label {
    font-weight: 600;
  }
</style>
