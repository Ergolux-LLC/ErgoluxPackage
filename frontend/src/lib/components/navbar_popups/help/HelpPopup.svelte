<script lang="ts">
  import PopupContainer from "../shared/PopupContainer.svelte";
  import { popupState } from "../shared/popup.store";

  let searchTerm = "";
  let selectedCategory: any = null;

  const helpCategories = [
    {
      id: "getting-started",
      title: "Getting Started",
      icon: "bi-play-circle",
      articles: [
        { title: "Welcome to Ergolux CRM", content: "Learn the basics..." },
        {
          title: "Setting up your workspace",
          content: "Configure your environment...",
        },
        { title: "Inviting team members", content: "Add collaborators..." },
      ],
    },
    {
      id: "account-management",
      title: "Account Management",
      icon: "bi-person-gear",
      articles: [
        {
          title: "Managing your profile",
          content: "Update your information...",
        },
        { title: "Billing and subscriptions", content: "Handle payments..." },
        { title: "Security settings", content: "Protect your account..." },
      ],
    },
    {
      id: "features",
      title: "Features & Tools",
      icon: "bi-tools",
      articles: [
        { title: "Dashboard overview", content: "Navigate the dashboard..." },
        { title: "Contact management", content: "Organize your contacts..." },
        { title: "Task automation", content: "Automate workflows..." },
      ],
    },
    {
      id: "troubleshooting",
      title: "Troubleshooting",
      icon: "bi-bug",
      articles: [
        { title: "Common issues", content: "Solve frequent problems..." },
        { title: "Performance tips", content: "Optimize your experience..." },
        { title: "Browser compatibility", content: "Supported browsers..." },
      ],
    },
  ];

  function selectCategory(category: any) {
    selectedCategory = category;
    popupState.update((state) => {
      state.help.activeCategory = category.id;
      return state;
    });
  }

  function goBack() {
    selectedCategory = null;
    popupState.update((state) => {
      state.help.activeCategory = null;
      return state;
    });
  }

  function handleCategoryKeydown(event: KeyboardEvent, category: any) {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      selectCategory(category);
    }
  }

  $: filteredCategories = helpCategories.filter(
    (category) =>
      category.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      category.articles.some((article) =>
        article.title.toLowerCase().includes(searchTerm.toLowerCase()),
      ),
  );
</script>

<PopupContainer title="Help & Support" width="500px">
  <!-- Search Bar -->
  <div class="help-search mb-4">
    <div class="input-group">
      <span class="input-group-text help-search-icon">
        <i class="bi bi-search"></i>
      </span>
      <input
        type="text"
        class="form-control help-search-input"
        placeholder="Search for help topics..."
        bind:value={searchTerm}
      />
    </div>
  </div>

  {#if !selectedCategory}
    <!-- Help Categories -->
    <div class="help-categories">
      <h6 class="text-light mb-3">Browse Help Topics</h6>

      {#each filteredCategories as category}
        <div
          class="help-category-card"
          role="button"
          tabindex="0"
          on:click={() => selectCategory(category)}
          on:keydown={(e) => handleCategoryKeydown(e, category)}
        >
          <div class="d-flex align-items-center">
            <div class="category-icon me-3">
              <i class={category.icon}></i>
            </div>
            <div class="flex-grow-1">
              <h6 class="text-light mb-1">{category.title}</h6>
              <p class="text-muted small mb-0">
                {category.articles.length} articles
              </p>
            </div>
            <div class="category-arrow">
              <i class="bi bi-chevron-right"></i>
            </div>
          </div>
        </div>
      {/each}

      <!-- Quick Actions -->
      <div class="help-actions mt-4 pt-4 border-top border-secondary">
        <h6 class="text-light mb-3">Need More Help?</h6>

        <div class="row">
          <div class="col-6">
            <button class="btn btn-outline-info w-100">
              <i class="bi bi-chat-dots me-2"></i>
              Live Chat
            </button>
          </div>
          <div class="col-6">
            <button class="btn btn-outline-warning w-100">
              <i class="bi bi-envelope me-2"></i>
              Contact Support
            </button>
          </div>
        </div>
      </div>
    </div>
  {:else}
    <!-- Category Articles -->
    <div class="help-articles">
      <!-- Back Button -->
      <button class="btn btn-link text-warning p-0 mb-3" on:click={goBack}>
        <i class="bi bi-arrow-left me-2"></i>Back to Categories
      </button>

      <h6 class="text-light mb-3">
        <i class="{selectedCategory.icon} me-2"></i>
        {selectedCategory.title}
      </h6>

      {#each selectedCategory.articles as article}
        <div class="help-article-card">
          <h6 class="text-light mb-2">{article.title}</h6>
          <p class="text-muted small mb-2">{article.content}</p>
          <button class="btn btn-outline-warning btn-sm">
            <i class="bi bi-arrow-right me-1"></i>Read More
          </button>
        </div>
      {/each}
    </div>
  {/if}

  <!-- Footer -->
  <div class="help-footer mt-4 pt-3 border-top border-secondary text-center">
    <small class="text-muted">
      <i class="bi bi-info-circle me-1"></i>
      Can't find what you're looking for?
      <button
        type="button"
        class="btn btn-link text-warning p-0 text-decoration-none"
        >Contact our support team</button
      >
    </small>
  </div>
</PopupContainer>

<style>
  .help-search-input {
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
    color: #fff;
  }

  .help-search-input:focus {
    background: rgba(255, 255, 255, 0.15);
    border-color: #f39c12;
    color: #fff;
    box-shadow: 0 0 0 0.2rem rgba(243, 156, 18, 0.25);
  }

  .help-search-input::placeholder {
    color: rgba(255, 255, 255, 0.5);
  }

  .help-search-icon {
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
    color: #ccc;
  }

  .help-category-card,
  .help-article-card {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 0.75rem;
    transition: all 0.3s ease;
    cursor: pointer;
  }

  .help-category-card:hover {
    background: rgba(255, 255, 255, 0.1);
    border-color: rgba(243, 156, 18, 0.3);
  }

  .help-article-card {
    cursor: default;
  }

  .category-icon {
    width: 40px;
    height: 40px;
    background: linear-gradient(145deg, #f39c12, #e67e22);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 18px;
  }

  .category-arrow {
    color: #ccc;
    transition: transform 0.3s ease;
  }

  .help-category-card:hover .category-arrow {
    transform: translateX(3px);
    color: #f39c12;
  }

  .border-secondary {
    border-color: rgba(255, 255, 255, 0.2) !important;
  }

  .btn-link {
    text-decoration: none !important;
  }

  .btn-link:hover {
    color: #f39c12 !important;
  }
</style>
