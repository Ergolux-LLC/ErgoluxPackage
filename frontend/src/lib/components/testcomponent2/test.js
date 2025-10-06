// export const message = "hello from $lib/message (component2)";

export const message = `
  <div class="card w-100">
    <div class="card-body">
      <h5 class="card-title mb-2">Patient Information</h5>
      <p class="card-text text-muted mb-3">General demographics and encounter data</p>

      <ul class="list-group list-group-flush">
        <li class="list-group-item d-flex justify-content-between align-items-start">
          <div class="ms-2 me-auto">
            <div class="fw-bold"><i class="bi bi-person-circle me-2" aria-hidden="true"></i>Name</div>
            Jane Doe
          </div>
          <small class="text-muted">DOB: 1986-07-12</small>
        </li>

        <li class="list-group-item d-flex justify-content-between align-items-start">
          <div class="ms-2 me-auto">
            <div class="fw-bold"><i class="bi bi-card-list me-2" aria-hidden="true"></i>MRN</div>
            00001234
          </div>
          <small class="text-muted">Room: 402B</small>
        </li>

        <li class="list-group-item d-flex justify-content-between align-items-start">
          <div class="ms-2 me-auto">
            <div class="fw-bold"><i class="bi bi-people me-2" aria-hidden="true"></i>Demographics</div>
            Female · 39 years
          </div>
          <small class="text-muted">Admitted: 2025-10-04</small>
        </li>

        <li class="list-group-item d-flex justify-content-between align-items-start">
          <div class="ms-2 me-auto">
            <div class="fw-bold"><i class="bi bi-hospital me-2" aria-hidden="true"></i>Encounter</div>
            Admitted for observation — primary diagnosis: chest pain
          </div>
          <small class="text-muted">Attending: Dr. Smith</small>
        </li>
      </ul>
    </div>
  </div>
`;
