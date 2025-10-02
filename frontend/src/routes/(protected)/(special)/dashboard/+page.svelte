<script>
  import { onMount } from "svelte";
  import { browser } from "$app/environment";

  // Import navbar popup components
  import { AccountPopup } from "$lib/components/navbar_popups/account";
  import { ProfilePopup } from "$lib/components/navbar_popups/profile";
  import { HelpPopup } from "$lib/components/navbar_popups/help";
  import { popupState, openPopup } from "$lib/components/navbar_popups/shared";

  let authStatus = null;
  let userInfo = null;
  let tokenInfo = null;
  let loadingAuth = true;
  let authError = null;
  let accessToken = null;

  // Dashboard data
  let dashboardData = {
    stats: {
      totalListings: 47,
      activeListings: 23,
      pendingOffers: 8,
      closingsThisMonth: 12,
      totalCommission: 185750,
      avgDaysOnMarket: 22,
    },
    recentListings: [
      {
        id: 1,
        address: "1234 Oak Street",
        city: "Beverly Hills",
        price: 1250000,
        beds: 4,
        baths: 3,
        sqft: 2400,
        status: "Active",
        daysOnMarket: 5,
        image: "/images/house1.jpg",
      },
      {
        id: 2,
        address: "5678 Pine Avenue",
        city: "Malibu",
        price: 2850000,
        beds: 5,
        baths: 4,
        sqft: 3200,
        status: "Pending",
        daysOnMarket: 12,
        image: "/images/house2.jpg",
      },
      {
        id: 3,
        address: "9012 Cedar Lane",
        city: "Santa Monica",
        price: 975000,
        beds: 3,
        baths: 2,
        sqft: 1850,
        status: "Active",
        daysOnMarket: 18,
        image: "/images/house3.jpg",
      },
    ],
    recentActivity: [
      {
        type: "showing",
        property: "1234 Oak Street",
        time: "2 hours ago",
        icon: "house-door",
      },
      {
        type: "offer",
        property: "5678 Pine Avenue",
        time: "4 hours ago",
        icon: "currency-dollar",
      },
      {
        type: "listing",
        property: "9012 Cedar Lane",
        time: "1 day ago",
        icon: "plus-circle",
      },
      {
        type: "closing",
        property: "4567 Maple Drive",
        time: "2 days ago",
        icon: "check-circle",
      },
    ],
    upcomingTasks: [
      {
        task: "Property showing at 1234 Oak Street",
        time: "Today 2:00 PM",
        priority: "high",
      },
      {
        task: "Follow up with buyer for 5678 Pine Avenue",
        time: "Today 4:30 PM",
        priority: "medium",
      },
      {
        task: "Market analysis for new listing",
        time: "Tomorrow 10:00 AM",
        priority: "low",
      },
      {
        task: "Closing preparation documents",
        time: "Friday 9:00 AM",
        priority: "high",
      },
    ],
  };

  // Load stored access token
  function loadAccessToken() {
    if (browser) {
      const stored = localStorage.getItem("access_token");
      if (stored) {
        accessToken = stored;
        console.log("✅ Access token loaded for dashboard");
        return stored;
      }
    }
    return null;
  }

  onMount(async () => {
    // Load access token from localStorage
    const token = loadAccessToken();

    // Get current authentication status using direct fetch (same pattern as workspace)
    try {
      if (token) {
        // Test the token with a validation request
        const validateResponse = await fetch("/api/auth/validate", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          credentials: "include",
        });

        if (validateResponse.ok) {
          const validationData = await validateResponse.json();
          authStatus = validationData;
          userInfo = validationData?.user;

          // Set token information
          tokenInfo = {
            hasToken: !!token,
            tokenPreview: token.substring(0, 12) + "...",
            isAuthenticated: true,
            tokenLength: token.length,
          };

          console.log("Dashboard - Auth Status:", authStatus);
          console.log("Dashboard - Token Info:", tokenInfo);
        } else {
          // Token validation failed
          console.warn("Token validation failed");
          authError = "Token validation failed";
          tokenInfo = {
            hasToken: false,
            isAuthenticated: false,
          };
        }
      } else {
        // No token available
        console.warn("No access token available");
        authError = "No access token available";
        tokenInfo = {
          hasToken: false,
          isAuthenticated: false,
        };
      }
    } catch (error) {
      console.error("Dashboard auth check error:", error);
      authError = error.message || "Authentication check failed";
      tokenInfo = {
        hasToken: !!token,
        isAuthenticated: false,
        error: authError,
      };
    } finally {
      loadingAuth = false;
    }
  });

  function refreshAuthStatus() {
    loadingAuth = true;
    authError = null;
    // Re-run the onMount logic
    onMount();
  }

  async function logout() {
    try {
      // Use direct fetch for logout (same pattern as workspace/logintest)
      await fetch("/api/auth/logout", {
        method: "POST",
        credentials: "include", // Include refresh token cookie
      });
    } catch (e) {
      console.warn("Logout request failed:", e);
      // ignore errors, just redirect
    }

    // Clear stored tokens
    if (browser) {
      localStorage.removeItem("access_token");
    }
    sessionStorage.clear();
    window.location.href = "/login";
  }

  // Format currency
  function formatCurrency(amount) {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  }

  // Format number with commas
  function formatNumber(num) {
    return new Intl.NumberFormat("en-US").format(num);
  }
</script>

<svelte:head>
  <title>Real Estate Dashboard - Ergolux CRM</title>
</svelte:head>

<!-- Main Dashboard Container -->
<div class="dashboard-container">
  <!-- Top Navigation Bar -->
  <nav class="dashboard-nav">
    <div class="nav-content">
      <div class="nav-brand">
        <div class="brand-icon">
          <i class="bi bi-house-door-fill"></i>
        </div>
        <span class="brand-text">Ergolux Real Estate</span>
      </div>

      <div class="nav-actions">
        <button class="nav-notification-btn">
          <i class="bi bi-bell"></i>
          <span class="notification-badge">3</span>
        </button>

        <div class="nav-divider"></div>

        <div class="dropdown">
          <button
            class="nav-user-btn dropdown-toggle"
            type="button"
            data-bs-toggle="dropdown"
          >
            <div class="user-avatar">
              <i class="bi bi-person-fill"></i>
            </div>
            <div class="user-info">
              <span class="user-name"
                >{userInfo?.first_name || "Agent"}
                {userInfo?.last_name || "Smith"}</span
              >
              <span class="user-role">Real Estate Agent</span>
            </div>
            <i class="bi bi-chevron-down"></i>
          </button>
          <ul class="dropdown-menu user-dropdown">
            <li>
              <button
                class="dropdown-item"
                on:click={() => openPopup("profile")}
              >
                <i class="bi bi-person me-2"></i>Profile
              </button>
            </li>
            <li>
              <button
                class="dropdown-item"
                on:click={() => openPopup("account")}
              >
                <i class="bi bi-gear me-2"></i>Account
              </button>
            </li>
            <li>
              <button class="dropdown-item" on:click={() => openPopup("help")}>
                <i class="bi bi-question-circle me-2"></i>Help
              </button>
            </li>
            <li><hr class="dropdown-divider" /></li>
            <li>
              <button class="dropdown-item" on:click={logout}>
                <i class="bi bi-box-arrow-right me-2"></i>Logout
              </button>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </nav>

  <!-- Main Content -->
  <div class="dashboard-main">
    <div class="main-content">
      <!-- Welcome Header -->
      <div class="page-header">
        <div class="header-content">
          <h1 class="page-title">
            Welcome back, {userInfo?.first_name || "Agent"}!
          </h1>
          <p class="page-subtitle">
            Here's what's happening with your real estate business today.
          </p>
        </div>
        <div class="header-actions">
          <button class="btn-primary">
            <i class="bi bi-plus-circle"></i>
            New Listing
          </button>
          <button class="btn-secondary">
            <i class="bi bi-calendar-check"></i>
            Schedule Showing
          </button>
        </div>
      </div>

      <!-- Key Metrics Cards -->
      <div class="metrics-grid">
        <div class="metric-card metric-primary">
          <div class="metric-content">
            <div class="metric-info">
              <h3 class="metric-label">Active Listings</h3>
              <div class="metric-value">
                {dashboardData.stats.activeListings}
              </div>
              <div class="metric-subtext">
                of {dashboardData.stats.totalListings} total
              </div>
            </div>
            <div class="metric-icon">
              <i class="bi bi-house-door"></i>
            </div>
          </div>
          <div class="metric-trend">
            <i class="bi bi-arrow-up"></i>
            <span>+12% from last month</span>
          </div>
        </div>

        <div class="metric-card metric-success">
          <div class="metric-content">
            <div class="metric-info">
              <h3 class="metric-label">Pending Offers</h3>
              <div class="metric-value">
                {dashboardData.stats.pendingOffers}
              </div>
              <div class="metric-subtext">awaiting response</div>
            </div>
            <div class="metric-icon">
              <i class="bi bi-currency-dollar"></i>
            </div>
          </div>
          <div class="metric-trend">
            <i class="bi bi-arrow-up"></i>
            <span>+8% from last week</span>
          </div>
        </div>

        <div class="metric-card metric-info">
          <div class="metric-content">
            <div class="metric-info">
              <h3 class="metric-label">This Month</h3>
              <div class="metric-value">
                {dashboardData.stats.closingsThisMonth}
              </div>
              <div class="metric-subtext">closings completed</div>
            </div>
            <div class="metric-icon">
              <i class="bi bi-check-circle"></i>
            </div>
          </div>
          <div class="metric-trend">
            <i class="bi bi-arrow-up"></i>
            <span>+15% from last month</span>
          </div>
        </div>

        <div class="metric-card metric-warning">
          <div class="metric-content">
            <div class="metric-info">
              <h3 class="metric-label">Commission</h3>
              <div class="metric-value">
                {formatCurrency(dashboardData.stats.totalCommission)}
              </div>
              <div class="metric-subtext">earned this year</div>
            </div>
            <div class="metric-icon">
              <i class="bi bi-graph-up"></i>
            </div>
          </div>
          <div class="metric-trend">
            <i class="bi bi-arrow-up"></i>
            <span>+22% from last year</span>
          </div>
        </div>
      </div>

      <!-- Recent Listings Table -->
      <div class="data-table-container">
        <div class="table-header">
          <div class="table-title">
            <i class="bi bi-house"></i>
            <span>Recent Listings</span>
          </div>
          <button class="btn-ghost">
            View All
            <i class="bi bi-arrow-right"></i>
          </button>
        </div>

        <div class="table-wrapper">
          <table class="data-table">
            <thead>
              <tr>
                <th>Property</th>
                <th>Price</th>
                <th>Details</th>
                <th>Status</th>
                <th>Days on Market</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {#each dashboardData.recentListings as listing}
                <tr class="table-row">
                  <td>
                    <div class="property-cell">
                      <div class="property-thumbnail">
                        <i class="bi bi-house-door"></i>
                      </div>
                      <div class="property-info">
                        <div class="property-address">{listing.address}</div>
                        <div class="property-city">{listing.city}</div>
                      </div>
                    </div>
                  </td>
                  <td>
                    <div class="price-cell">
                      {formatCurrency(listing.price)}
                    </div>
                  </td>
                  <td>
                    <div class="details-cell">
                      {listing.beds} bed • {listing.baths} bath • {formatNumber(
                        listing.sqft,
                      )} sqft
                    </div>
                  </td>
                  <td>
                    <span
                      class="status-badge status-{listing.status.toLowerCase()}"
                    >
                      {listing.status}
                    </span>
                  </td>
                  <td>
                    <div class="days-cell">{listing.daysOnMarket} days</div>
                  </td>
                  <td>
                    <div class="dropdown">
                      <button
                        class="action-btn"
                        data-bs-toggle="dropdown"
                        aria-label="Actions"
                      >
                        <i class="bi bi-three-dots"></i>
                      </button>
                      <ul class="dropdown-menu action-dropdown">
                        <li>
                          <a class="dropdown-item" href="#"
                            ><i class="bi bi-eye"></i>View</a
                          >
                        </li>
                        <li>
                          <a class="dropdown-item" href="#"
                            ><i class="bi bi-pencil"></i>Edit</a
                          >
                        </li>
                        <li>
                          <a class="dropdown-item" href="#"
                            ><i class="bi bi-share"></i>Share</a
                          >
                        </li>
                      </ul>
                    </div>
                  </td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      </div>

      <!-- Recent Activity -->
      <div class="activity-container">
        <div class="activity-header">
          <div class="activity-title">
            <i class="bi bi-activity"></i>
            <span>Recent Activity</span>
          </div>
        </div>

        <div class="activity-list">
          {#each dashboardData.recentActivity as activity}
            <div class="activity-item">
              <div class="activity-icon activity-{activity.type}">
                <i class="bi bi-{activity.icon}"></i>
              </div>
              <div class="activity-content">
                <div class="activity-type">{activity.type}</div>
                <div class="activity-property">{activity.property}</div>
                <div class="activity-time">{activity.time}</div>
              </div>
            </div>
          {/each}
        </div>
      </div>
    </div>

    <!-- Sidebar -->
    <div class="sidebar">
      <!-- Quick Stats -->
      <div class="stats-widget">
        <div class="widget-header">
          <i class="bi bi-speedometer2"></i>
          <span>Quick Stats</span>
        </div>

        <div class="stats-list">
          <div class="stat-item">
            <span class="stat-label">Avg. Days on Market</span>
            <span class="stat-value"
              >{dashboardData.stats.avgDaysOnMarket} days</span
            >
          </div>
          <div class="stat-item">
            <span class="stat-label">Success Rate</span>
            <span class="stat-value stat-success">87%</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Client Satisfaction</span>
            <span class="stat-value stat-info">4.9/5</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Market Share</span>
            <span class="stat-value stat-primary">12.3%</span>
          </div>
        </div>
      </div>

      <!-- Upcoming Tasks -->
      <div class="tasks-widget">
        <div class="widget-header">
          <i class="bi bi-calendar-check"></i>
          <span>Upcoming Tasks</span>
        </div>

        <div class="tasks-list">
          {#each dashboardData.upcomingTasks as task}
            <div class="task-item">
              <div class="task-priority priority-{task.priority}"></div>
              <div class="task-content">
                <div class="task-title">{task.task}</div>
                <div class="task-time">
                  <i class="bi bi-clock"></i>
                  {task.time}
                </div>
              </div>
            </div>
          {/each}
        </div>

        <button class="add-task-btn">
          <i class="bi bi-plus"></i>
          Add Task
        </button>
      </div>
    </div>
  </div>
</div>

<!-- Navbar Popup Components -->
{#if $popupState.account.isOpen}
  <AccountPopup />
{/if}

{#if $popupState.profile.isOpen}
  <ProfilePopup />
{/if}

{#if $popupState.help.isOpen}
  <HelpPopup />
{/if}

<style>
  /* Modern Dark Dashboard Theme */

  /* CSS Variables for consistent theming */
  :global(:root) {
    --color-bg-primary: #0d1117;
    --color-bg-secondary: #161b22;
    --color-bg-tertiary: #21262d;
    --color-bg-canvas: #010409;

    --color-border-default: #30363d;
    --color-border-muted: #21262d;
    --color-border-subtle: #373e47;

    --color-text-primary: #f0f6fc;
    --color-text-secondary: #9198a1;
    --color-text-tertiary: #6e7681;
    --color-text-disabled: #484f58;

    --color-accent-primary: #58a6ff;
    --color-accent-success: #3fb950;
    --color-accent-warning: #f1c543;
    --color-accent-danger: #f85149;
    --color-accent-info: #79c0ff;

    --shadow-small: 0 1px 3px rgba(0, 0, 0, 0.3);
    --shadow-medium: 0 4px 12px rgba(0, 0, 0, 0.4);
    --shadow-large: 0 8px 24px rgba(0, 0, 0, 0.5);

    --border-radius-small: 6px;
    --border-radius-medium: 8px;
    --border-radius-large: 12px;

    --spacing-xs: 4px;
    --spacing-sm: 8px;
    --spacing-md: 16px;
    --spacing-lg: 24px;
    --spacing-xl: 32px;
  }

  /* Global overrides */
  :global(body) {
    background-color: var(--color-bg-primary) !important;
    color: var(--color-text-primary) !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans",
      Helvetica, Arial, sans-serif;
    line-height: 1.5;
  }

  /* Dashboard Container */
  .dashboard-container {
    min-height: 100vh;
    background-color: var(--color-bg-primary);
    color: var(--color-text-primary);
  }

  /* Navigation */
  .dashboard-nav {
    background-color: var(--color-bg-secondary);
    border-bottom: 1px solid var(--color-border-default);
    padding: 0;
    position: sticky;
    top: 0;
    z-index: 100;
    box-shadow: var(--shadow-small);
  }

  .nav-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--spacing-md) var(--spacing-lg);
    max-width: 1400px;
    margin: 0 auto;
  }

  .nav-brand {
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
  }

  .brand-icon {
    width: 40px;
    height: 40px;
    background: linear-gradient(
      135deg,
      var(--color-accent-primary),
      var(--color-accent-info)
    );
    border-radius: var(--border-radius-medium);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 20px;
  }

  .brand-text {
    font-size: 20px;
    font-weight: 600;
    color: var(--color-text-primary);
  }

  .nav-actions {
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
  }

  .nav-notification-btn {
    position: relative;
    background: none;
    border: none;
    padding: var(--spacing-sm);
    border-radius: var(--border-radius-small);
    color: var(--color-text-secondary);
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .nav-notification-btn:hover {
    background-color: var(--color-bg-tertiary);
    color: var(--color-text-primary);
  }

  .notification-badge {
    position: absolute;
    top: 2px;
    right: 2px;
    background-color: var(--color-accent-danger);
    color: white;
    font-size: 10px;
    padding: 2px 5px;
    border-radius: 10px;
    min-width: 16px;
    text-align: center;
  }

  .nav-divider {
    width: 1px;
    height: 24px;
    background-color: var(--color-border-default);
  }

  .nav-user-btn {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    background: none;
    border: 1px solid var(--color-border-default);
    padding: var(--spacing-sm) var(--spacing-md);
    border-radius: var(--border-radius-medium);
    color: var(--color-text-primary);
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .nav-user-btn:hover {
    border-color: var(--color-border-subtle);
    background-color: var(--color-bg-tertiary);
  }

  .user-avatar {
    width: 32px;
    height: 32px;
    background: linear-gradient(
      135deg,
      var(--color-accent-success),
      var(--color-accent-warning)
    );
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
  }

  .user-info {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
  }

  .user-name {
    font-weight: 600;
    font-size: 14px;
    line-height: 1.2;
  }

  .user-role {
    font-size: 12px;
    color: var(--color-text-secondary);
    line-height: 1.2;
  }

  .user-dropdown {
    background-color: var(--color-bg-tertiary) !important;
    border: 1px solid var(--color-border-default) !important;
    border-radius: var(--border-radius-medium) !important;
    box-shadow: var(--shadow-medium) !important;
    padding: var(--spacing-sm) !important;
  }

  .user-dropdown .dropdown-item {
    color: var(--color-text-primary) !important;
    padding: var(--spacing-sm) var(--spacing-md) !important;
    border-radius: var(--border-radius-small) !important;
    transition: all 0.2s ease !important;
  }

  .user-dropdown .dropdown-item:hover {
    background-color: var(--color-bg-secondary) !important;
    color: var(--color-text-primary) !important;
  }

  .user-dropdown .dropdown-divider {
    border-color: var(--color-border-default) !important;
    margin: var(--spacing-sm) 0 !important;
  }

  /* Main Layout */
  .dashboard-main {
    display: grid;
    grid-template-columns: 1fr 320px;
    gap: var(--spacing-xl);
    max-width: 1400px;
    margin: 0 auto;
    padding: var(--spacing-xl) var(--spacing-lg);
  }

  .main-content {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xl);
  }

  /* Page Header */
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: var(--spacing-lg);
  }

  .header-content h1.page-title {
    font-size: 32px;
    font-weight: 700;
    margin: 0 0 var(--spacing-sm) 0;
    color: var(--color-text-primary);
  }

  .page-subtitle {
    font-size: 16px;
    color: var(--color-text-secondary);
    margin: 0;
  }

  .header-actions {
    display: flex;
    gap: var(--spacing-md);
  }

  .btn-primary {
    background: linear-gradient(
      135deg,
      var(--color-accent-primary),
      var(--color-accent-info)
    );
    border: none;
    padding: var(--spacing-md) var(--spacing-lg);
    border-radius: var(--border-radius-medium);
    color: white;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    cursor: pointer;
    transition: all 0.2s ease;
    text-decoration: none;
  }

  .btn-primary:hover {
    transform: translateY(-1px);
    box-shadow: var(--shadow-medium);
  }

  .btn-secondary {
    background: var(--color-bg-tertiary);
    border: 1px solid var(--color-border-default);
    padding: var(--spacing-md) var(--spacing-lg);
    border-radius: var(--border-radius-medium);
    color: var(--color-text-primary);
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    cursor: pointer;
    transition: all 0.2s ease;
    text-decoration: none;
  }

  .btn-secondary:hover {
    border-color: var(--color-border-subtle);
    background-color: var(--color-bg-secondary);
  }

  .btn-ghost {
    background: none;
    border: none;
    color: var(--color-text-secondary);
    padding: var(--spacing-sm) var(--spacing-md);
    border-radius: var(--border-radius-small);
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    cursor: pointer;
    transition: all 0.2s ease;
    text-decoration: none;
  }

  .btn-ghost:hover {
    color: var(--color-text-primary);
    background-color: var(--color-bg-tertiary);
  }

  /* Metrics Grid */
  .metrics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: var(--spacing-lg);
  }

  .metric-card {
    background-color: var(--color-bg-secondary);
    border: 1px solid var(--color-border-default);
    border-radius: var(--border-radius-large);
    padding: var(--spacing-lg);
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
  }

  .metric-card::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: var(--gradient);
  }

  .metric-card.metric-primary {
    --gradient: linear-gradient(
      90deg,
      var(--color-accent-primary),
      var(--color-accent-info)
    );
  }

  .metric-card.metric-success {
    --gradient: linear-gradient(90deg, var(--color-accent-success), #4cc962);
  }

  .metric-card.metric-info {
    --gradient: linear-gradient(90deg, var(--color-accent-info), #a5d6ff);
  }

  .metric-card.metric-warning {
    --gradient: linear-gradient(90deg, var(--color-accent-warning), #ffd560);
  }

  .metric-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-medium);
    border-color: var(--color-border-subtle);
  }

  .metric-content {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: var(--spacing-md);
  }

  .metric-label {
    font-size: 14px;
    font-weight: 500;
    color: var(--color-text-secondary);
    margin: 0 0 var(--spacing-sm) 0;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .metric-value {
    font-size: 36px;
    font-weight: 700;
    color: var(--color-text-primary);
    line-height: 1;
    margin-bottom: var(--spacing-xs);
  }

  .metric-subtext {
    font-size: 13px;
    color: var(--color-text-tertiary);
  }

  .metric-icon {
    font-size: 40px;
    color: var(--color-text-disabled);
    opacity: 0.3;
  }

  .metric-trend {
    display: flex;
    align-items: center;
    gap: var(--spacing-xs);
    font-size: 13px;
    color: var(--color-accent-success);
    font-weight: 500;
  }

  /* Data Table */
  .data-table-container {
    background-color: var(--color-bg-secondary);
    border: 1px solid var(--color-border-default);
    border-radius: var(--border-radius-large);
    overflow: hidden;
  }

  .table-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--spacing-lg);
    border-bottom: 1px solid var(--color-border-default);
  }

  .table-title {
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
    font-size: 18px;
    font-weight: 600;
    color: var(--color-text-primary);
  }

  .table-wrapper {
    overflow-x: auto;
  }

  .data-table {
    width: 100%;
    border-collapse: collapse;
  }

  .data-table th {
    background-color: var(--color-bg-tertiary);
    padding: var(--spacing-md) var(--spacing-lg);
    text-align: left;
    font-size: 12px;
    font-weight: 600;
    color: var(--color-text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    border-bottom: 1px solid var(--color-border-default);
  }

  .data-table td {
    padding: var(--spacing-md) var(--spacing-lg);
    border-bottom: 1px solid var(--color-border-muted);
  }

  .table-row:hover {
    background-color: var(--color-bg-tertiary);
  }

  .property-cell {
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
  }

  .property-thumbnail {
    width: 48px;
    height: 48px;
    background: linear-gradient(
      135deg,
      var(--color-accent-primary),
      var(--color-accent-info)
    );
    border-radius: var(--border-radius-medium);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 20px;
  }

  .property-address {
    font-weight: 600;
    color: var(--color-text-primary);
    margin-bottom: 2px;
  }

  .property-city {
    font-size: 13px;
    color: var(--color-text-secondary);
  }

  .price-cell {
    font-weight: 700;
    font-size: 16px;
    color: var(--color-accent-warning);
  }

  .details-cell {
    font-size: 13px;
    color: var(--color-text-secondary);
  }

  .days-cell {
    color: var(--color-text-primary);
  }

  .status-badge {
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 500;
    text-transform: uppercase;
  }

  .status-active {
    background-color: rgba(63, 185, 80, 0.1);
    color: var(--color-accent-success);
    border: 1px solid rgba(63, 185, 80, 0.2);
  }

  .status-pending {
    background-color: rgba(241, 197, 67, 0.1);
    color: var(--color-accent-warning);
    border: 1px solid rgba(241, 197, 67, 0.2);
  }

  .action-btn {
    background: none;
    border: none;
    color: var(--color-text-secondary);
    padding: var(--spacing-sm);
    border-radius: var(--border-radius-small);
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .action-btn:hover {
    background-color: var(--color-bg-tertiary);
    color: var(--color-text-primary);
  }

  .action-dropdown {
    background-color: var(--color-bg-tertiary) !important;
    border: 1px solid var(--color-border-default) !important;
    border-radius: var(--border-radius-medium) !important;
    box-shadow: var(--shadow-medium) !important;
    padding: var(--spacing-sm) !important;
  }

  .action-dropdown .dropdown-item {
    color: var(--color-text-primary) !important;
    padding: var(--spacing-sm) var(--spacing-md) !important;
    border-radius: var(--border-radius-small) !important;
    display: flex !important;
    align-items: center !important;
    gap: var(--spacing-sm) !important;
    transition: all 0.2s ease !important;
  }

  .action-dropdown .dropdown-item:hover {
    background-color: var(--color-bg-secondary) !important;
  }

  /* Activity */
  .activity-container {
    background-color: var(--color-bg-secondary);
    border: 1px solid var(--color-border-default);
    border-radius: var(--border-radius-large);
    overflow: hidden;
  }

  .activity-header {
    padding: var(--spacing-lg);
    border-bottom: 1px solid var(--color-border-default);
  }

  .activity-title {
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
    font-size: 18px;
    font-weight: 600;
    color: var(--color-text-primary);
  }

  .activity-list {
    padding: var(--spacing-lg);
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: var(--spacing-md);
  }

  .activity-item {
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
    padding: var(--spacing-md);
    background-color: var(--color-bg-tertiary);
    border: 1px solid var(--color-border-muted);
    border-radius: var(--border-radius-medium);
    transition: all 0.2s ease;
  }

  .activity-item:hover {
    border-color: var(--color-border-default);
    background-color: var(--color-bg-secondary);
  }

  .activity-icon {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 16px;
  }

  .activity-showing {
    background: linear-gradient(
      135deg,
      var(--color-accent-primary),
      var(--color-accent-info)
    );
  }

  .activity-offer {
    background: linear-gradient(135deg, var(--color-accent-success), #4cc962);
  }

  .activity-listing {
    background: linear-gradient(135deg, var(--color-accent-warning), #ffd560);
  }

  .activity-closing {
    background: linear-gradient(135deg, var(--color-accent-info), #a5d6ff);
  }

  .activity-type {
    font-weight: 600;
    color: var(--color-text-primary);
    text-transform: capitalize;
    margin-bottom: 2px;
  }

  .activity-property {
    font-size: 13px;
    color: var(--color-text-secondary);
    margin-bottom: 2px;
  }

  .activity-time {
    font-size: 12px;
    color: var(--color-accent-warning);
  }

  /* Sidebar */
  .sidebar {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-lg);
  }

  .stats-widget,
  .tasks-widget {
    background-color: var(--color-bg-secondary);
    border: 1px solid var(--color-border-default);
    border-radius: var(--border-radius-large);
    overflow: hidden;
  }

  .widget-header {
    padding: var(--spacing-lg);
    border-bottom: 1px solid var(--color-border-default);
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
    font-size: 16px;
    font-weight: 600;
    color: var(--color-text-primary);
  }

  .stats-list {
    padding: var(--spacing-lg);
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
  }

  .stat-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .stat-label {
    color: var(--color-text-secondary);
    font-size: 14px;
  }

  .stat-value {
    font-weight: 600;
    color: var(--color-text-primary);
  }

  .stat-success {
    color: var(--color-accent-success);
  }

  .stat-info {
    color: var(--color-accent-info);
  }

  .stat-primary {
    color: var(--color-accent-primary);
  }

  .tasks-list {
    padding: var(--spacing-lg);
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
  }

  .task-item {
    display: flex;
    gap: var(--spacing-md);
    align-items: flex-start;
  }

  .task-priority {
    width: 4px;
    height: 40px;
    border-radius: 2px;
    flex-shrink: 0;
    margin-top: 2px;
  }

  .priority-high {
    background-color: var(--color-accent-danger);
  }

  .priority-medium {
    background-color: var(--color-accent-warning);
  }

  .priority-low {
    background-color: var(--color-text-disabled);
  }

  .task-title {
    font-weight: 500;
    color: var(--color-text-primary);
    font-size: 14px;
    margin-bottom: 4px;
    line-height: 1.3;
  }

  .task-time {
    display: flex;
    align-items: center;
    gap: var(--spacing-xs);
    font-size: 12px;
    color: var(--color-text-secondary);
  }

  .add-task-btn {
    margin: 0 var(--spacing-lg) var(--spacing-lg) var(--spacing-lg);
    background: var(--color-bg-tertiary);
    border: 1px dashed var(--color-border-default);
    padding: var(--spacing-md);
    border-radius: var(--border-radius-medium);
    color: var(--color-text-secondary);
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: var(--spacing-sm);
    font-weight: 500;
  }

  .add-task-btn:hover {
    border-color: var(--color-border-subtle);
    color: var(--color-text-primary);
    background-color: var(--color-bg-secondary);
  }

  /* Responsive Design */
  @media (max-width: 1024px) {
    .dashboard-main {
      grid-template-columns: 1fr;
      gap: var(--spacing-lg);
    }

    .metrics-grid {
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    }
  }

  @media (max-width: 768px) {
    .nav-content {
      padding: var(--spacing-md);
    }

    .dashboard-main {
      padding: var(--spacing-lg) var(--spacing-md);
    }

    .page-header {
      flex-direction: column;
      align-items: stretch;
      gap: var(--spacing-md);
    }

    .header-actions {
      order: -1;
    }

    .metrics-grid {
      grid-template-columns: 1fr;
    }

    .activity-list {
      grid-template-columns: 1fr;
    }

    .user-info {
      display: none;
    }
  }

  /* Bootstrap overrides */
  :global(.dropdown-toggle::after) {
    display: none !important;
  }
</style>
