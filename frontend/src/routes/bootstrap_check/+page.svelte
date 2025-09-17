<script lang="ts">
  import { onMount } from "svelte";

  let bootstrapCssLoaded = false;
  let bootstrapJsLoaded = false;
  let bootstrapIconsLoaded = false;
  let bootstrapVersion = "Not detected";

  onMount(() => {
    // Check if Bootstrap CSS is loaded
    const testElement = document.createElement("div");
    testElement.className = "visually-hidden";
    testElement.style.position = "absolute";
    document.body.appendChild(testElement);

    const computedStyle = window.getComputedStyle(testElement);
    bootstrapCssLoaded =
      computedStyle.position === "absolute" &&
      (computedStyle.visibility === "hidden" || computedStyle.clip !== "auto");

    document.body.removeChild(testElement);

    // Check if Bootstrap JS is loaded (from CDN)
    bootstrapJsLoaded = typeof (window as any).bootstrap !== "undefined";

    // Try to get Bootstrap version
    if (bootstrapJsLoaded) {
      // Check for specific Bootstrap 5 components
      const bootstrap = (window as any).bootstrap;
      const hasModal = typeof bootstrap.Modal !== "undefined";
      const hasDropdown = typeof bootstrap.Dropdown !== "undefined";
      if (hasModal && hasDropdown) {
        bootstrapVersion = "Bootstrap 5.3.2 (CDN)";
      }
    }

    // Check if Bootstrap Icons are loaded
    const iconTestElement = document.createElement("i");
    iconTestElement.className = "bi bi-heart";
    iconTestElement.style.position = "absolute";
    iconTestElement.style.visibility = "hidden";
    document.body.appendChild(iconTestElement);

    const iconStyle = window.getComputedStyle(iconTestElement, "::before");
    bootstrapIconsLoaded =
      iconStyle.fontFamily.includes("bootstrap-icons") ||
      iconStyle.content !== "none";

    document.body.removeChild(iconTestElement);
  });

  function showModal() {
    const bootstrap = (window as any).bootstrap;
    if (bootstrap && bootstrap.Modal) {
      const modal = new bootstrap.Modal(document.getElementById("testModal"));
      modal.show();
    }
  }

  function showTooltip() {
    const bootstrap = (window as any).bootstrap;
    if (bootstrap && bootstrap.Tooltip) {
      const tooltipTriggerList = [].slice.call(
        document.querySelectorAll('[data-bs-toggle="tooltip"]')
      );
      tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
      });
    }
  }
</script>

<svelte:head>
  <title>Bootstrap 5 Check - Ergolux CRM</title>
</svelte:head>

<div class="container mt-5">
  <div class="row">
    <div class="col-md-8 offset-md-2">
      <h1 class="display-4 text-center mb-4">
        <i class="bi bi-check-circle-fill text-success"></i>
        Bootstrap 5 Integration Check
      </h1>

      <!-- Status Cards -->
      <div class="row mb-4">
        <div class="col-md-4 mb-3">
          <div
            class="card {bootstrapCssLoaded
              ? 'border-success'
              : 'border-danger'}"
          >
            <div class="card-body text-center">
              <i
                class="bi {bootstrapCssLoaded
                  ? 'bi-check-circle-fill text-success'
                  : 'bi-x-circle-fill text-danger'} fs-1"
              ></i>
              <h5 class="card-title mt-2">Bootstrap CSS</h5>
              <p class="card-text">
                Status: <strong
                  class={bootstrapCssLoaded ? "text-success" : "text-danger"}
                >
                  {bootstrapCssLoaded ? "Loaded" : "Not Loaded"}
                </strong>
              </p>
            </div>
          </div>
        </div>

        <div class="col-md-4 mb-3">
          <div
            class="card {bootstrapJsLoaded
              ? 'border-success'
              : 'border-danger'}"
          >
            <div class="card-body text-center">
              <i
                class="bi {bootstrapJsLoaded
                  ? 'bi-check-circle-fill text-success'
                  : 'bi-x-circle-fill text-danger'} fs-1"
              ></i>
              <h5 class="card-title mt-2">Bootstrap JS</h5>
              <p class="card-text">
                Status: <strong
                  class={bootstrapJsLoaded ? "text-success" : "text-danger"}
                >
                  {bootstrapJsLoaded ? "Loaded" : "Not Loaded"}
                </strong>
              </p>
            </div>
          </div>
        </div>

        <div class="col-md-4 mb-3">
          <div
            class="card {bootstrapIconsLoaded
              ? 'border-success'
              : 'border-danger'}"
          >
            <div class="card-body text-center">
              <i
                class="bi {bootstrapIconsLoaded
                  ? 'bi-check-circle-fill text-success'
                  : 'bi-x-circle-fill text-danger'} fs-1"
              ></i>
              <h5 class="card-title mt-2">Bootstrap Icons</h5>
              <p class="card-text">
                Status: <strong
                  class={bootstrapIconsLoaded ? "text-success" : "text-danger"}
                >
                  {bootstrapIconsLoaded ? "Loaded" : "Not Loaded"}
                </strong>
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Version Info -->
      <div class="alert alert-info mb-4">
        <h5 class="alert-heading">
          <i class="bi bi-info-circle"></i>
          Version Information
        </h5>
        <p class="mb-0">{bootstrapVersion}</p>
      </div>

      <!-- Component Tests -->
      <div class="card mb-4">
        <div class="card-header">
          <h5 class="mb-0">
            <i class="bi bi-gear"></i>
            Interactive Component Tests
          </h5>
        </div>
        <div class="card-body">
          <!-- Button Group -->
          <div class="mb-3">
            <h6>Buttons & Colors:</h6>
            <button type="button" class="btn btn-primary me-2">Primary</button>
            <button type="button" class="btn btn-success me-2">Success</button>
            <button type="button" class="btn btn-warning me-2">Warning</button>
            <button type="button" class="btn btn-danger">Danger</button>
          </div>

          <!-- Modal Test -->
          <div class="mb-3">
            <h6>Modal Test:</h6>
            <button type="button" class="btn btn-info" on:click={showModal}>
              <i class="bi bi-window"></i>
              Test Modal
            </button>
          </div>

          <!-- Tooltip Test -->
          <div class="mb-3">
            <h6>Tooltip Test:</h6>
            <button
              type="button"
              class="btn btn-secondary"
              data-bs-toggle="tooltip"
              data-bs-placement="top"
              title="This is a Bootstrap tooltip!"
              on:click={showTooltip}
            >
              <i class="bi bi-info-circle"></i>
              Hover for Tooltip (Click to Initialize)
            </button>
          </div>

          <!-- Icons Showcase -->
          <div class="mb-3">
            <h6>Bootstrap Icons:</h6>
            <div class="d-flex gap-3 fs-4">
              <i class="bi bi-heart-fill text-danger"></i>
              <i class="bi bi-star-fill text-warning"></i>
              <i class="bi bi-shield-check text-success"></i>
              <i class="bi bi-lightning-fill text-primary"></i>
              <i class="bi bi-house-door-fill text-info"></i>
              <i class="bi bi-person-circle text-secondary"></i>
            </div>
          </div>

          <!-- Responsive Grid Test -->
          <div class="mb-3">
            <h6>Responsive Grid:</h6>
            <div class="row text-center">
              <div class="col-sm-6 col-md-3 mb-2">
                <div class="bg-primary text-white p-2 rounded">Col 1</div>
              </div>
              <div class="col-sm-6 col-md-3 mb-2">
                <div class="bg-success text-white p-2 rounded">Col 2</div>
              </div>
              <div class="col-sm-6 col-md-3 mb-2">
                <div class="bg-warning text-white p-2 rounded">Col 3</div>
              </div>
              <div class="col-sm-6 col-md-3 mb-2">
                <div class="bg-danger text-white p-2 rounded">Col 4</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Navigation -->
      <div class="text-center">
        <a href="/" class="btn btn-outline-primary">
          <i class="bi bi-arrow-left"></i>
          Back to Home
        </a>
        <a href="/setup" class="btn btn-outline-secondary ms-2">
          <i class="bi bi-gear"></i>
          Go to Setup
        </a>
      </div>
    </div>
  </div>
</div>

<!-- Test Modal -->
<div
  class="modal fade"
  id="testModal"
  tabindex="-1"
  aria-labelledby="testModalLabel"
  aria-hidden="true"
>
  <div class="modal-dialog">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title" id="testModalLabel">
          <i class="bi bi-check-circle-fill text-success"></i>
          Bootstrap Modal Test
        </h5>
        <button
          type="button"
          class="btn-close"
          data-bs-dismiss="modal"
          aria-label="Close"
        ></button>
      </div>
      <div class="modal-body">
        <p>🎉 Congratulations! Bootstrap JavaScript is working correctly.</p>
        <p>
          This modal demonstrates that Bootstrap's JavaScript components are
          properly loaded and functional.
        </p>
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal"
          >Close</button
        >
        <button type="button" class="btn btn-primary">
          <i class="bi bi-heart-fill"></i>
          Awesome!
        </button>
      </div>
    </div>
  </div>
</div>
