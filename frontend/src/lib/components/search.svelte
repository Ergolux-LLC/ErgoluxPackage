<script lang="ts">
  export let definition: any = null; // The searchUiDefinition JSON
  export let error: string = "";
  export let onSubmit: (data: Record<string, any>) => void = () => {};

  // Store form values by field name
  let formValues: Record<string, any> = {};

  // Initialize form values when definition changes
  $: if (definition) {
    for (const section of definition.sections ?? []) {
      for (const field of section.fields ?? []) {
        if (!(field.name in formValues)) {
          formValues[field.name] = field.type === "select" ? "" : "";
        }
      }
    }
  }

  function handleSubmit(event: Event) {
    event.preventDefault();
    onSubmit({ ...formValues });
  }
</script>

<form on:submit={handleSubmit} class="component-a-form">
  <h2>{definition?.title ?? "Search"}</h2>
  {#each definition?.sections ?? [] as section}
    <fieldset>
      <legend>{section.name}</legend>
      {#each section.fields as field}
        <div class="field">
          <label title={field.tooltip ?? ""} for={field.name}>
            {field.label}
          </label>
          {#if field.type === "select"}
            <select
              id={field.name}
              bind:value={formValues[field.name]}
              name={field.name}
            >
              {#each field.options ?? [] as opt}
                <option value={opt.value}>{opt.label}</option>
              {/each}
            </select>
          {:else if field.type === "number"}
            <input
              id={field.name}
              type="number"
              bind:value={formValues[field.name]}
              name={field.name}
              placeholder={field.placeholder ?? ""}
              min={field.validation?.min}
              max={field.validation?.max}
              autocomplete="off"
            />
          {:else}
            <input
              id={field.name}
              type="text"
              bind:value={formValues[field.name]}
              name={field.name}
              placeholder={field.placeholder ?? ""}
              minlength={field.validation?.minLength}
              autocomplete="off"
            />
          {/if}
        </div>
      {/each}
    </fieldset>
  {/each}
  <button type="submit">{definition?.submitText ?? "Submit"}</button>
  {#if error}
    <div class="error">{error}</div>
  {/if}
</form>

<style>
  .component-a-form {
    display: flex;
    flex-direction: column;
    gap: 1.2em;
    background: #23272b;
    padding: 1em;
    border-radius: 8px;
    box-shadow: 0 2px 8px #0004;
    color: #f3f3f3;
    max-width: 500px;
    margin: 0 auto;
  }
  h2 {
    margin: 0 0 0.5em 0;
    color: #4f8cff;
    font-size: 1.3em;
    text-align: center;
  }
  fieldset {
    border: 1px solid #444;
    border-radius: 6px;
    padding: 1em;
    margin-bottom: 0.5em;
  }
  legend {
    color: #b3e5fc;
    font-size: 1.1em;
    padding: 0 0.5em;
  }
  .field {
    display: flex;
    flex-direction: column;
    margin-bottom: 1em;
  }
  label {
    font-size: 1em;
    margin-bottom: 0.2em;
    cursor: help;
  }
  input,
  select {
    padding: 0.5em;
    border-radius: 5px;
    border: 1px solid #444;
    background: #181a1b;
    color: #f3f3f3;
    font-size: 1em;
  }
  button {
    padding: 0.5em 1em;
    border-radius: 5px;
    border: none;
    background: #4f8cff;
    color: #fff;
    font-weight: bold;
    cursor: pointer;
    transition: background 0.2s;
    margin-top: 0.5em;
  }
  button:hover {
    background: #357ae8;
  }
  .error {
    color: #ff6b6b;
    font-size: 0.95em;
    margin-top: 0.3em;
    text-align: center;
  }
</style>
