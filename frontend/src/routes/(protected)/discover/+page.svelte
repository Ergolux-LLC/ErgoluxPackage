<!-- Discover Page - Demo Content -->
<div class="discover-page">
  <div class="container-fluid py-4">
    <div class="row">
      <div class="col-12">
        <!-- Page Header -->
        <div class="d-flex justify-content-between align-items-center mb-4">
          <div>
            <h1 class="h2 text-light mb-1">
              <i class="bi bi-compass text-primary me-2"></i>
              Discover
            </h1>
            <p class="text-muted mb-0">Find new opportunities and insights</p>
          </div>
          <div class="d-flex gap-2">
            <button class="btn btn-outline-primary btn-sm">
              <i class="bi bi-funnel me-1"></i>
              Filter
            </button>
            <button class="btn btn-primary btn-sm">
              <i class="bi bi-plus-lg me-1"></i>
              New Search
            </button>
          </div>
        </div>

        <!-- Stats Cards -->
        <div class="row g-3 mb-4">
          <div class="col-md-3">
            <div class="card bg-dark border-secondary">
              <div class="card-body">
                <div class="d-flex align-items-center">
                  <div class="flex-shrink-0">
                    <div class="bg-primary bg-opacity-25 rounded p-2">
                      <i class="bi bi-people text-primary fs-5"></i>
                    </div>
                  </div>
                  <div class="flex-grow-1 ms-3">
                    <h6 class="card-title text-light mb-0">Total Contacts</h6>
                    <h4 class="text-primary mb-0">2,847</h4>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="card bg-dark border-secondary">
              <div class="card-body">
                <div class="d-flex align-items-center">
                  <div class="flex-shrink-0">
                    <div class="bg-success bg-opacity-25 rounded p-2">
                      <i class="bi bi-graph-up text-success fs-5"></i>
                    </div>
                  </div>
                  <div class="flex-grow-1 ms-3">
                    <h6 class="card-title text-light mb-0">Active Leads</h6>
                    <h4 class="text-success mb-0">324</h4>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="card bg-dark border-secondary">
              <div class="card-body">
                <div class="d-flex align-items-center">
                  <div class="flex-shrink-0">
                    <div class="bg-warning bg-opacity-25 rounded p-2">
                      <i class="bi bi-clock text-warning fs-5"></i>
                    </div>
                  </div>
                  <div class="flex-grow-1 ms-3">
                    <h6 class="card-title text-light mb-0">Pending Review</h6>
                    <h4 class="text-warning mb-0">89</h4>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="card bg-dark border-secondary">
              <div class="card-body">
                <div class="d-flex align-items-center">
                  <div class="flex-shrink-0">
                    <div class="bg-info bg-opacity-25 rounded p-2">
                      <i class="bi bi-star text-info fs-5"></i>
                    </div>
                  </div>
                  <div class="flex-grow-1 ms-3">
                    <h6 class="card-title text-light mb-0">Hot Prospects</h6>
                    <h4 class="text-info mb-0">47</h4>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Search and Filters -->
        <div class="card bg-dark border-secondary mb-4">
          <div class="card-header bg-dark border-secondary">
            <h5 class="card-title text-light mb-0">
              <i class="bi bi-search me-2"></i>
              Discovery Tools
            </h5>
          </div>
          <div class="card-body">
            <div class="row g-3">
              <div class="col-md-6">
                <label for="search-contacts" class="form-label text-light"
                  >Search Contacts</label
                >
                <div class="input-group">
                  <span
                    class="input-group-text bg-dark border-secondary text-muted"
                  >
                    <i class="bi bi-search"></i>
                  </span>
                  <input
                    id="search-contacts"
                    type="text"
                    class="form-control bg-dark border-secondary text-light"
                    placeholder="Search by name, company, or email..."
                  />
                </div>
              </div>
              <div class="col-md-3">
                <label for="industry-filter" class="form-label text-light"
                  >Industry</label
                >
                <select
                  id="industry-filter"
                  class="form-select bg-dark border-secondary text-light"
                >
                  <option selected>All Industries</option>
                  <option value="tech">Technology</option>
                  <option value="finance">Finance</option>
                  <option value="healthcare">Healthcare</option>
                  <option value="retail">Retail</option>
                </select>
              </div>
              <div class="col-md-3">
                <label for="status-filter" class="form-label text-light"
                  >Status</label
                >
                <select
                  id="status-filter"
                  class="form-select bg-dark border-secondary text-light"
                >
                  <option selected>All Status</option>
                  <option value="new">New</option>
                  <option value="contacted">Contacted</option>
                  <option value="qualified">Qualified</option>
                  <option value="closed">Closed</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        <!-- Results Table -->
        <div class="card bg-dark border-secondary">
          <div
            class="card-header bg-dark border-secondary d-flex justify-content-between align-items-center"
          >
            <h5 class="card-title text-light mb-0">
              <i class="bi bi-list-ul me-2"></i>
              Discovery Results
            </h5>
            <small class="text-muted">Showing 1-10 of 324 results</small>
          </div>
          <div class="card-body p-0">
            <div class="table-responsive">
              <table class="table table-dark table-hover mb-0">
                <thead>
                  <tr>
                    <th scope="col">Contact</th>
                    <th scope="col">Company</th>
                    <th scope="col">Industry</th>
                    <th scope="col">Status</th>
                    <th scope="col">Last Activity</th>
                    <th scope="col">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>
                      <div class="d-flex align-items-center">
                        <div
                          class="bg-primary bg-opacity-25 rounded-circle p-2 me-2"
                        >
                          <i class="bi bi-person text-primary"></i>
                        </div>
                        <div>
                          <div class="text-light">Sarah Johnson</div>
                          <small class="text-muted">sarah@techcorp.com</small>
                        </div>
                      </div>
                    </td>
                    <td class="text-light">TechCorp Solutions</td>
                    <td><span class="badge bg-info">Technology</span></td>
                    <td><span class="badge bg-success">Qualified</span></td>
                    <td class="text-muted">2 hours ago</td>
                    <td>
                      <div class="btn-group btn-group-sm">
                        <button
                          class="btn btn-outline-primary"
                          aria-label="View Sarah Johnson details"
                        >
                          <i class="bi bi-eye"></i>
                        </button>
                        <button
                          class="btn btn-outline-success"
                          aria-label="Contact Sarah Johnson"
                        >
                          <i class="bi bi-chat"></i>
                        </button>
                      </div>
                    </td>
                  </tr>
                  <tr>
                    <td>
                      <div class="d-flex align-items-center">
                        <div
                          class="bg-success bg-opacity-25 rounded-circle p-2 me-2"
                        >
                          <i class="bi bi-person text-success"></i>
                        </div>
                        <div>
                          <div class="text-light">Michael Chen</div>
                          <small class="text-muted"
                            >m.chen@financeplus.com</small
                          >
                        </div>
                      </div>
                    </td>
                    <td class="text-light">FinancePlus Inc</td>
                    <td><span class="badge bg-warning">Finance</span></td>
                    <td><span class="badge bg-warning">Contacted</span></td>
                    <td class="text-muted">1 day ago</td>
                    <td>
                      <div class="btn-group btn-group-sm">
                        <button
                          class="btn btn-outline-primary"
                          aria-label="View Michael Chen details"
                        >
                          <i class="bi bi-eye"></i>
                        </button>
                        <button
                          class="btn btn-outline-success"
                          aria-label="Contact Michael Chen"
                        >
                          <i class="bi bi-chat"></i>
                        </button>
                      </div>
                    </td>
                  </tr>
                  <tr>
                    <td>
                      <div class="d-flex align-items-center">
                        <div
                          class="bg-danger bg-opacity-25 rounded-circle p-2 me-2"
                        >
                          <i class="bi bi-person text-danger"></i>
                        </div>
                        <div>
                          <div class="text-light">Emma Rodriguez</div>
                          <small class="text-muted">emma@healthsys.org</small>
                        </div>
                      </div>
                    </td>
                    <td class="text-light">HealthSystems Corp</td>
                    <td><span class="badge bg-danger">Healthcare</span></td>
                    <td><span class="badge bg-secondary">New</span></td>
                    <td class="text-muted">3 days ago</td>
                    <td>
                      <div class="btn-group btn-group-sm">
                        <button
                          class="btn btn-outline-primary"
                          aria-label="View Emma Rodriguez details"
                        >
                          <i class="bi bi-eye"></i>
                        </button>
                        <button
                          class="btn btn-outline-success"
                          aria-label="Contact Emma Rodriguez"
                        >
                          <i class="bi bi-chat"></i>
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
          <div class="card-footer bg-dark border-secondary">
            <nav>
              <ul class="pagination pagination-sm mb-0 justify-content-center">
                <li class="page-item disabled">
                  <span class="page-link bg-dark border-secondary text-muted"
                    >Previous</span
                  >
                </li>
                <li class="page-item active">
                  <span class="page-link bg-primary border-primary">1</span>
                </li>
                <li class="page-item">
                  <button
                    type="button"
                    class="page-link bg-dark border-secondary text-light"
                    >2</button
                  >
                </li>
                <li class="page-item">
                  <button
                    type="button"
                    class="page-link bg-dark border-secondary text-light"
                    >3</button
                  >
                </li>
                <li class="page-item">
                  <button
                    type="button"
                    class="page-link bg-dark border-secondary text-light"
                    >Next</button
                  >
                </li>
              </ul>
            </nav>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>

<style>
  .discover-page {
    /* Layout handles sidebar margins */
    min-height: 100vh;
    background-color: var(--bs-dark, #212529);
  }

  /* Custom dark theme adjustments */
  .form-control:focus,
  .form-select:focus {
    background-color: var(--bs-dark, #212529);
    border-color: var(--bs-primary, #0d6efd);
    color: var(--bs-light, #f8f9fa);
    box-shadow: 0 0 0 0.25rem rgba(13, 110, 253, 0.25);
  }

  .table-dark th {
    border-color: #495057;
  }

  .card-header {
    border-bottom: 1px solid #495057;
  }

  .card-footer {
    border-top: 1px solid #495057;
  }
</style>
