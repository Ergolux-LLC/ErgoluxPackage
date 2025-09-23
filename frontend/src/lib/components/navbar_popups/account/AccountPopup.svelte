<script lang="ts">
  import { onMount } from "svelte";
  import PopupContainer from "../shared/PopupContainer.svelte";
  import { popupState, setAccountTab } from "../shared/popup.store";
  import { accountData, loadAccountData } from "./account.store";
  import { memoryManager } from "$lib/memorymanager";

  onMount(() => {
    loadAccountData();
  });

  function handleTabClick(
    tab: "profile" | "settings" | "billing" | "security",
  ) {
    setAccountTab(tab);
  }

  // Get instant user data for display
  $: userEmail = memoryManager.getUserEmail() || "Loading...";
  $: userFullName = memoryManager.getUserFullName() || "Loading...";
  $: userId = memoryManager.getUserId() || "";
</script>

<PopupContainer title="Account Management" width="500px">
  <!-- Tab Navigation -->
  <div class="nav nav-pills nav-justified mb-3" role="tablist">
    <button
      class="nav-link {$popupState.account.activeTab === 'profile'
        ? 'active'
        : ''}"
      on:click={() => handleTabClick("profile")}
      type="button"
    >
      <i class="bi bi-person me-2"></i>Profile
    </button>
    <button
      class="nav-link {$popupState.account.activeTab === 'settings'
        ? 'active'
        : ''}"
      on:click={() => handleTabClick("settings")}
      type="button"
    >
      <i class="bi bi-gear me-2"></i>Settings
    </button>
    <button
      class="nav-link {$popupState.account.activeTab === 'billing'
        ? 'active'
        : ''}"
      on:click={() => handleTabClick("billing")}
      type="button"
    >
      <i class="bi bi-credit-card me-2"></i>Billing
    </button>
    <button
      class="nav-link {$popupState.account.activeTab === 'security'
        ? 'active'
        : ''}"
      on:click={() => handleTabClick("security")}
      type="button"
    >
      <i class="bi bi-shield-lock me-2"></i>Security
    </button>
  </div>

  <!-- Tab Content -->
  <div class="tab-content">
    {#if $popupState.account.activeTab === "profile"}
      <div class="tab-pane active">
        <!-- User Profile Info -->
        <div class="user-info-card mb-4">
          <div class="row align-items-center">
            <div class="col-auto">
              <div class="user-avatar">
                <i class="bi bi-person-circle"></i>
              </div>
            </div>
            <div class="col">
              <h6 class="mb-1 text-light">{userFullName}</h6>
              <p class="mb-1 text-muted small">{userEmail}</p>
              <p class="mb-0 text-muted small">
                <i class="bi bi-clock me-1"></i>
                Last sync: {new Date(
                  $accountData.lastSync || Date.now(),
                ).toLocaleString()}
              </p>
            </div>
          </div>
        </div>

        <!-- Profile Details -->
        <div class="profile-details">
          <div class="row mb-3">
            <div class="col-sm-4">
              <strong class="text-light">User ID:</strong>
            </div>
            <div class="col-sm-8">
              <code class="text-warning small">{userId}</code>
            </div>
          </div>

          <div class="row mb-3">
            <div class="col-sm-4">
              <strong class="text-light">First Name:</strong>
            </div>
            <div class="col-sm-8">
              <span class="text-light"
                >{$accountData.firstName || "Not set"}</span
              >
            </div>
          </div>

          <div class="row mb-3">
            <div class="col-sm-4">
              <strong class="text-light">Last Name:</strong>
            </div>
            <div class="col-sm-8">
              <span class="text-light"
                >{$accountData.lastName || "Not set"}</span
              >
            </div>
          </div>

          <div class="row mb-3">
            <div class="col-sm-4">
              <strong class="text-light">Email:</strong>
            </div>
            <div class="col-sm-8">
              <span class="text-light">{$accountData.email}</span>
            </div>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="action-buttons mt-4">
          <button class="btn btn-outline-warning btn-sm me-2">
            <i class="bi bi-pencil me-1"></i>Edit Profile
          </button>
          <button class="btn btn-outline-info btn-sm">
            <i class="bi bi-camera me-1"></i>Change Avatar
          </button>
        </div>
      </div>
    {:else if $popupState.account.activeTab === "settings"}
      <div class="tab-pane active">
        <h6 class="text-light mb-3">Account Settings</h6>

        <div class="setting-item">
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <strong class="text-light">Email Notifications</strong>
              <p class="text-muted small mb-0">
                Receive updates about your account
              </p>
            </div>
            <div class="form-check form-switch">
              <input class="form-check-input" type="checkbox" checked />
            </div>
          </div>
        </div>

        <div class="setting-item">
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <strong class="text-light">Dark Mode</strong>
              <p class="text-muted small mb-0">Use dark theme</p>
            </div>
            <div class="form-check form-switch">
              <input class="form-check-input" type="checkbox" checked />
            </div>
          </div>
        </div>

        <div class="setting-item">
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <strong class="text-light">Auto-save</strong>
              <p class="text-muted small mb-0">Automatically save changes</p>
            </div>
            <div class="form-check form-switch">
              <input class="form-check-input" type="checkbox" checked />
            </div>
          </div>
        </div>
      </div>
    {:else if $popupState.account.activeTab === "billing"}
      <div class="tab-pane active">
        <h6 class="text-light mb-3">Billing Information</h6>

        <div class="billing-card mb-3">
          <div class="d-flex align-items-center">
            <i class="bi bi-credit-card text-warning me-3 fs-4"></i>
            <div>
              <strong class="text-light">Premium Plan</strong>
              <p class="text-muted small mb-0">
                $29/month • Next billing: Oct 22, 2025
              </p>
            </div>
          </div>
        </div>

        <div class="billing-actions">
          <button class="btn btn-outline-warning btn-sm me-2">
            <i class="bi bi-pencil me-1"></i>Update Payment
          </button>
          <button class="btn btn-outline-info btn-sm">
            <i class="bi bi-download me-1"></i>Download Invoice
          </button>
        </div>
      </div>
    {:else if $popupState.account.activeTab === "security"}
      <div class="tab-pane active">
        <h6 class="text-light mb-3">Security Settings</h6>

        <div class="security-item">
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <strong class="text-light">Two-Factor Authentication</strong>
              <p class="text-muted small mb-0">
                Add an extra layer of security
              </p>
            </div>
            <button class="btn btn-outline-success btn-sm">Enable</button>
          </div>
        </div>

        <div class="security-item">
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <strong class="text-light">Password</strong>
              <p class="text-muted small mb-0">Last changed 30 days ago</p>
            </div>
            <button class="btn btn-outline-warning btn-sm">Change</button>
          </div>
        </div>

        <div class="security-item">
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <strong class="text-light">Active Sessions</strong>
              <p class="text-muted small mb-0">Manage your active sessions</p>
            </div>
            <button class="btn btn-outline-info btn-sm">View</button>
          </div>
        </div>
      </div>
    {/if}
  </div>
</PopupContainer>

<style>
  .nav-pills .nav-link {
    background: rgba(255, 255, 255, 0.1);
    color: #ccc;
    border: none;
    margin: 0 2px;
    transition: all 0.3s ease;
  }

  .nav-pills .nav-link:hover {
    background: rgba(255, 255, 255, 0.2);
    color: #fff;
  }

  .nav-pills .nav-link.active {
    background: linear-gradient(145deg, #f39c12, #e67e22);
    color: #fff;
  }

  .user-info-card {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    padding: 1rem;
  }

  .user-avatar {
    width: 50px;
    height: 50px;
    background: linear-gradient(145deg, #f39c12, #e67e22);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    color: white;
  }

  .setting-item,
  .security-item,
  .billing-card {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 6px;
    padding: 1rem;
    margin-bottom: 0.75rem;
  }

  .form-check-input:checked {
    background-color: #f39c12;
    border-color: #f39c12;
  }

  .action-buttons,
  .billing-actions {
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    padding-top: 1rem;
  }
</style>
