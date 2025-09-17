<script lang="ts">
  export let results: Array<Record<string, any>> = [];
</script>

<div>
  <h2>Search Results</h2>
  {#if results.length > 0}
    <table>
      <thead>
        <tr>
          {#each Object.keys(results[0]) as key}
            <th>{key.charAt(0).toUpperCase() + key.slice(1)}</th>
          {/each}
        </tr>
      </thead>
      <tbody>
        {#each results as row}
          <tr>
            {#each Object.keys(row) as key}
              <td>{row[key]}</td>
            {/each}
          </tr>
        {/each}
      </tbody>
    </table>
  {:else}
    <p>No results found.</p>
  {/if}
</div>

<style>
  table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 1em;
    background: #23272b;
    color: #f3f3f3;
  }
  th,
  td {
    border: 1px solid #444;
    padding: 0.5em 1em;
    text-align: left;
  }
  th {
    background: #181a1b;
    color: #4f8cff;
  }
</style>
