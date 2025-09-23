<script lang="ts">
  import { onMount } from "svelte";
  import PopupContainer from "../shared/PopupContainer.svelte";
  import { popupState } from "../shared/popup.store";
  import { memoryManager } from "$lib/memorymanager";

  let isEditing = false;
  let firstName = "";
  let lastName = "";
  let email = "";
  let bio = "";

  onMount(() => {
    const user = memoryManager.getCurrentUser();
    if (user) {
      firstName = user.first_name;
      lastName = user.last_name;
      email = user.email;
      bio = user.preferences?.bio || "";
    }
  });

  function toggleEdit() {
    isEditing = !isEditing;
    popupState.update((state) => {
      state.profile.isEditing = isEditing;
      return state;
    });
  }

  function saveProfile() {
    // Here you would typically call an API to save the profile
    console.log("Saving profile:", { firstName, lastName, email, bio });
    isEditing = false;
    popupState.update((state) => {
      state.profile.isEditing = false;
      return state;
    });
  }

  function cancelEdit() {
    // Reset form data
    const user = memoryManager.getCurrentUser();
    if (user) {
      firstName = user.first_name;
      lastName = user.last_name;
      email = user.email;
      bio = user.preferences?.bio || "";
    }
    isEditing = false;
    popupState.update((state) => {
      state.profile.isEditing = false;
      return state;
    });
  }
</script>

<PopupContainer title="User Profile" width="450px">
  <!-- Profile Header -->
  <div class="profile-header text-center mb-4">
    <div class="profile-avatar-large mb-3">
      <i class="bi bi-person-circle"></i>
    </div>
    <h5 class="text-light mb-1">{firstName} {lastName}</h5>
    <p class="text-muted small">{email}</p>
  </div>

  <!-- Profile Form -->
  <form on:submit|preventDefault={saveProfile}>
    <div class="row mb-3">
      <div class="col-6">
        <label for="firstName" class="form-label text-light">First Name</label>
        <input
          type="text"
          class="form-control profile-input"
          id="firstName"
          bind:value={firstName}
          disabled={!isEditing}
        />
      </div>
      <div class="col-6">
        <label for="lastName" class="form-label text-light">Last Name</label>
        <input
          type="text"
          class="form-control profile-input"
          id="lastName"
          bind:value={lastName}
          disabled={!isEditing}
        />
      </div>
    </div>

    <div class="mb-3">
      <label for="email" class="form-label text-light">Email Address</label>
      <input
        type="email"
        class="form-control profile-input"
        id="email"
        bind:value={email}
        disabled={!isEditing}
      />
    </div>

    <div class="mb-4">
      <label for="bio" class="form-label text-light">Bio</label>
      <textarea
        class="form-control profile-input"
        id="bio"
        rows="3"
        bind:value={bio}
        disabled={!isEditing}
        placeholder="Tell us about yourself..."
      ></textarea>
    </div>

    <!-- Action Buttons -->
    <div class="profile-actions">
      {#if !isEditing}
        <button
          type="button"
          class="btn btn-outline-warning"
          on:click={toggleEdit}
        >
          <i class="bi bi-pencil me-2"></i>Edit Profile
        </button>
        <button type="button" class="btn btn-outline-info ms-2">
          <i class="bi bi-camera me-2"></i>Change Photo
        </button>
      {:else}
        <button type="submit" class="btn btn-success">
          <i class="bi bi-check me-2"></i>Save Changes
        </button>
        <button
          type="button"
          class="btn btn-outline-secondary ms-2"
          on:click={cancelEdit}
        >
          <i class="bi bi-x me-2"></i>Cancel
        </button>
      {/if}
    </div>
  </form>

  <!-- Additional Profile Info -->
  <div class="profile-stats mt-4 pt-4 border-top border-secondary">
    <div class="row text-center">
      <div class="col-4">
        <div class="stat-item">
          <h6 class="text-warning mb-1">24</h6>
          <small class="text-muted">Projects</small>
        </div>
      </div>
      <div class="col-4">
        <div class="stat-item">
          <h6 class="text-warning mb-1">156</h6>
          <small class="text-muted">Tasks</small>
        </div>
      </div>
      <div class="col-4">
        <div class="stat-item">
          <h6 class="text-warning mb-1">89%</h6>
          <small class="text-muted">Complete</small>
        </div>
      </div>
    </div>
  </div>
</PopupContainer>

<style>
  .profile-avatar-large {
    width: 80px;
    height: 80px;
    background: linear-gradient(145deg, #f39c12, #e67e22);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 48px;
    color: white;
    margin: 0 auto;
  }

  .profile-input {
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
    color: #fff;
    transition: all 0.3s ease;
  }

  .profile-input:focus {
    background: rgba(255, 255, 255, 0.15);
    border-color: #f39c12;
    color: #fff;
    box-shadow: 0 0 0 0.2rem rgba(243, 156, 18, 0.25);
  }

  .profile-input:disabled {
    background: rgba(255, 255, 255, 0.05);
    border-color: rgba(255, 255, 255, 0.1);
    color: #ccc;
  }

  .profile-input::placeholder {
    color: rgba(255, 255, 255, 0.5);
  }

  .profile-actions {
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    padding-top: 1rem;
  }

  .stat-item {
    padding: 0.5rem;
  }

  .border-secondary {
    border-color: rgba(255, 255, 255, 0.2) !important;
  }
</style>
