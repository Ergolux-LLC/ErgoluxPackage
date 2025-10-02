<script lang="ts">
  import { onMount } from "svelte";
  import ComponentA from "$lib/components/search.svelte";
  import ComponentB from "$lib/components/display.svelte";

  export let data;

  // --- JSON variable requirements ---
  // searchUiDefinition should be an object with:
  // {
  //   title: string,                // (optional) Title for the search UI
  //   submitText: string,           // (optional) Text for the submit button
  //   sections: [                   // Array of sections (required)
  //     {
  //       name: string,             // Section name (required)
  //       fields: [                 // Array of field definitions (required)
  //         {
  //           name: string,         // Field name (required, unique in section)
  //           label: string,        // Friendly label text (required)
  //           type: string,         // Field type: "text", "number", "select", etc. (required)
  //           tooltip: string,      // Tooltip/help text (optional)
  //           placeholder: string,  // Placeholder text (optional)
  //           validation: object,   // Validation rules (optional, e.g. { required: true, min: 0 })
  //           options: [            // For select fields: array of { value, label } (optional)
  //             { value: string, label: string }
  //           ]
  //         }
  //       ]
  //     }
  //   ]
  // }
  // If searchUiDefinition is null or missing required fields, a friendly error is shown.

  let searchUiDefinition: any = null;
  let formError = "";
  let lastSearchInput: Record<string, any> | null = null;
  let searchResults: Array<Record<string, any>> = [];
  let definitionError = "";

  // Placeholder for future API call to fetch the search UI definition
  async function fetchSearchUiDefinition() {
    // TODO: Replace with real API call
    // Example:
    // const res = await fetch('/api/search-ui-definition');
    // if (res.ok) {
    //   searchUiDefinition = await res.json();
    //   definitionError = "";
    // } else {
    //   definitionError = "Failed to load search interface definition.";
    // }
    searchUiDefinition = null;
    definitionError =
      "No search interface definition available. Please check back later.";
  }

  // Placeholder for future API call to fetch search results
  async function fetchSearchResults(input: Record<string, any>) {
    // TODO: Replace with real API call
    // Example:
    // const res = await fetch('/api/search', { method: 'POST', body: JSON.stringify(input) });
    // if (res.ok) {
    //   searchResults = await res.json();
    // } else {
    //   formError = "Failed to fetch search results.";
    // }
    searchResults = [];
  }

  function handleAFormSubmit(input: Record<string, any>) {
    lastSearchInput = input;
    formError = "";
    fetchSearchResults(input);
  }

  onMount(() => {
    fetchSearchUiDefinition();
  });
</script>

<div class="directory-layout">
  <header>
    <h1>
      Workspace: <span class="workspace"
        >{data?.workspace ?? "unknown"}</span
      >
    </h1>
    <a href="/logout" class="logout-link">Logout</a>
  </header>
  <section class="components-vertical">
    <div>
      {#if searchUiDefinition}
        <ComponentA
          onSubmit={handleAFormSubmit}
          definition={searchUiDefinition}
          error={formError}
        />
        {#if lastSearchInput && Object.values(lastSearchInput).some((v) => v)}
          <p class="msg">
            Last search input: {JSON.stringify(lastSearchInput)}
          </p>
        {/if}
      {:else}
        <div class="error-msg">{definitionError}</div>
      {/if}
    </div>
    <div>
      <ComponentB results={searchResults} />
    </div>
  </section>
  <main>
    <slot />
  </main>
</div>

<style>
  .directory-layout {
    min-height: 100vh;
    background: #23272b;
    color: #f3f3f3;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 2em 1em;
  }
  header {
    width: 100%;
    max-width: 900px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2em;
  }
  h1 {
    margin: 0;
    font-size: 2em;
    color: #4f8cff;
    font-weight: 600;
  }
  .workspace {
    color: #fff;
    background: #4f8cff33;
    padding: 0.2em 0.7em;
    border-radius: 6px;
    margin-left: 0.5em;
    font-size: 0.8em;
    font-weight: 500;
  }
  .logout-link {
    color: #ff6b6b;
    text-decoration: none;
    font-weight: bold;
    border: 1px solid #ff6b6b;
    padding: 0.5em 1.2em;
    border-radius: 6px;
    background: #23272b;
    transition:
      background 0.2s,
      color 0.2s,
      border 0.2s;
  }
  .logout-link:hover {
    background: #ff6b6b;
    color: #fff;
    border-color: #ff6b6b;
  }
  .components-vertical {
    display: flex;
    flex-direction: column;
    gap: 2em;
    margin-bottom: 2em;
    width: 100%;
    max-width: 900px;
    justify-content: center;
    align-items: stretch;
  }
  .msg {
    margin-top: 0.5em;
    font-size: 1em;
    color: #b3e5fc;
    text-align: center;
  }
  .error-msg {
    color: #ff6b6b;
    background: #181a1b;
    border: 1px solid #ff6b6b;
    border-radius: 6px;
    padding: 1em;
    text-align: center;
    margin: 2em 0;
  }
  main {
    width: 100%;
    max-width: 900px;
    background: #181a1b;
    border-radius: 10px;
    box-shadow: 0 4px 24px #0008;
    padding: 2em;
    margin-top: 1em;
  }
</style>
