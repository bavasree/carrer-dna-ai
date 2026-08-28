/**
 * Career DNA AI — Opportunities & Hackathons Explorer
 * Clean, Simple, and Focused on Essential Opportunity Information
 */

document.addEventListener('DOMContentLoaded', () => {
    // Current filter state
    let currentFilters = {
        type: 'all',
        query: '',
        location: '',
        sort_by: 'deadline_asc'
    };

    let loadedOpportunities = [];
    let cachedStudentProfile = null;

    // DOM Elements
    const container = document.getElementById('opportunitiesGrid');
    const searchInput = document.getElementById('searchQueryInput');
    const clearSearchBtn = document.getElementById('clearSearchBtn');
    const typeFilterPills = document.querySelectorAll('.type-filter-pill');
    const locationSelect = document.getElementById('locationSelect');
    const sortSelect = document.getElementById('sortSelect');
    const resultCountEl = document.getElementById('oppResultCount');
    const totalOppCounterEl = document.getElementById('totalOppCounter');

    // Read URL query params on initial load
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('type')) {
        currentFilters.type = urlParams.get('type');
        updateActiveTypePill(currentFilters.type);
    }
    if (urlParams.get('query')) {
        currentFilters.query = urlParams.get('query').trim();
        if (searchInput) {
            searchInput.value = currentFilters.query;
            if (clearSearchBtn) clearSearchBtn.style.display = 'block';
        }
    }
    if (urlParams.get('location')) {
        currentFilters.location = urlParams.get('location');
        if (locationSelect) locationSelect.value = currentFilters.location;
    }

    // Helper: Category metadata & labels
    function getTypeMeta(oppType) {
        const t = (oppType || 'job').toLowerCase();
        switch (t) {
            case 'hackathon':
                return {
                    label: 'Hackathon',
                    orgLabel: 'Conducting College / Host',
                    badgeClass: 'badge-amber-subtle',
                    icon: 'bi-laptop',
                    actionLabel: 'Register',
                    initialStage: 'Registered'
                };
            case 'internship':
                return {
                    label: 'Internship',
                    orgLabel: 'Offering Company',
                    badgeClass: 'badge-primary-subtle',
                    icon: 'bi-briefcase',
                    actionLabel: 'Apply',
                    initialStage: 'Applied'
                };
            case 'job':
                return {
                    label: 'Job',
                    orgLabel: 'Offering Company',
                    badgeClass: 'badge-cyan-subtle',
                    icon: 'bi-building',
                    actionLabel: 'Apply',
                    initialStage: 'Applied'
                };
            case 'competition':
                return {
                    label: 'Competition',
                    orgLabel: 'Organized by',
                    badgeClass: 'badge-rose-subtle',
                    icon: 'bi-trophy',
                    actionLabel: 'Register',
                    initialStage: 'Registered'
                };
            default:
                return {
                    label: 'Opportunity',
                    orgLabel: 'Organization',
                    badgeClass: 'badge-primary-subtle',
                    icon: 'bi-stars',
                    actionLabel: 'Apply',
                    initialStage: 'Registered'
                };
        }
    }

    // Format deadline date cleanly
    function formatDeadline(deadlineStr) {
        if (!deadlineStr) return 'Ongoing / Open';
        try {
            const date = new Date(deadlineStr);
            if (isNaN(date.getTime())) return deadlineStr;
            return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
        } catch (e) {
            return deadlineStr;
        }
    }

    // Fetch Student Profile Snapshot
    async function fetchStudentProfileSnapshot() {
        if (cachedStudentProfile) return cachedStudentProfile;
        try {
            const res = await window.api.get('/profile');
            cachedStudentProfile = res.data;
            return cachedStudentProfile;
        } catch (err) {
            const user = window.api.getCurrentUser() || {};
            return {
                user: { full_name: user.full_name || 'Student', email: user.email || '' },
                college_name: '',
                degree: '',
                branch: '',
                graduation_year: 2026,
                cgpa: ''
            };
        }
    }

    // Main API Fetch for Opportunities
    async function loadOpportunities() {
        if (!container) return;
        container.innerHTML = `
            <div class="col-12 py-5 text-center">
                <div class="spinner-border text-primary" role="status"></div>
                <p class="text-secondary mt-2 small">Loading opportunities...</p>
            </div>
        `;

        try {
            const params = new URLSearchParams();
            if (currentFilters.type && currentFilters.type !== 'all') params.append('type', currentFilters.type);
            if (currentFilters.location) params.append('location', currentFilters.location);
            if (currentFilters.query) params.append('query', currentFilters.query);
            if (currentFilters.sort_by) params.append('sort_by', currentFilters.sort_by);

            const res = await window.api.get(`/recommendations?${params.toString()}`);
            let allOpportunities = res.data.opportunities || [];

            // Update total counter if viewing all without filters
            if (totalOppCounterEl && currentFilters.type === 'all' && !currentFilters.query && !currentFilters.location) {
                totalOppCounterEl.textContent = allOpportunities.length;
            }

            loadedOpportunities = allOpportunities;

            if (resultCountEl) {
                resultCountEl.innerHTML = `Showing <b class="text-light">${loadedOpportunities.length}</b> opportunities`;
            }

            if (loadedOpportunities.length === 0) {
                container.innerHTML = `
                    <div class="col-12">
                        <div class="card bg-surface-card p-5 text-center border border-subtle">
                            <div class="rounded-circle bg-surface-elevated d-inline-flex p-3 text-secondary mb-3 mx-auto" style="font-size: 2rem;">
                                <i class="bi bi-search"></i>
                            </div>
                            <h5 class="text-light fw-bold mb-1">No Opportunities Found</h5>
                            <p class="text-secondary small mb-3">Try adjusting your search keywords or category filter.</p>
                            <div>
                                <button class="btn btn-gradient-primary btn-sm" id="resetAllFiltersBtn">
                                    <i class="bi bi-arrow-counterclockwise me-1"></i>View All Opportunities
                                </button>
                            </div>
                        </div>
                    </div>
                `;
                const resetBtn = document.getElementById('resetAllFiltersBtn');
                if (resetBtn) resetBtn.addEventListener('click', resetAllFilters);
                return;
            }

            container.innerHTML = loadedOpportunities.map(opp => renderOpportunityCard(opp)).join('');
            attachCardEventListeners();

        } catch (err) {
            container.innerHTML = `
                <div class="col-12">
                    <div class="alert alert-danger p-4 text-center">
                        <i class="bi bi-exclamation-triangle-fill me-2"></i>Failed to load opportunities. Please refresh the page.
                    </div>
                </div>
            `;
        }
    }

    // Render Opportunity Card HTML (Clean & Focused on Essential Fields Only)
    function renderOpportunityCard(opp) {
        const typeMeta = getTypeMeta(opp.opportunity_type);
        const deadlineFormatted = formatDeadline(opp.deadline);

        // Register / Apply Action Button
        let actionBtnHtml = '';
        if (opp.is_applied) {
            actionBtnHtml = `
                <button class="btn btn-sm btn-glass text-emerald flex-grow-1" disabled>
                    <i class="bi bi-check2-circle me-1"></i>${(opp.application_status || 'Registered').toUpperCase()}
                </button>
            `;
        } else {
            actionBtnHtml = `
                <button class="btn btn-sm btn-gradient-primary flex-grow-1 apply-now-btn" data-id="${opp.id}">
                    <i class="bi ${typeMeta.icon} me-1"></i>${typeMeta.actionLabel}
                </button>
            `;
        }

        return `
            <div class="col-md-6 col-lg-4">
                <div class="card bg-surface-card h-100 p-4 border border-subtle shadow-sm d-flex flex-column justify-content-between">
                    <div>
                        <!-- Opportunity Type Badge -->
                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <span class="badge ${typeMeta.badgeClass} text-uppercase" style="font-size: 0.72rem;">
                                <i class="bi ${typeMeta.icon} me-1"></i>${typeMeta.label}
                            </span>
                        </div>

                        <!-- 1. Opportunity Name -->
                        <h5 class="text-light fw-bold mb-3" style="font-size: 1.1rem; line-height: 1.35;">${opp.title}</h5>

                        <!-- 2. Company / Conducting College / Organization -->
                        <div class="mb-2">
                            <small class="text-secondary d-block" style="font-size: 0.75rem;">${typeMeta.orgLabel}:</small>
                            <span class="text-light fw-semibold small"><i class="bi bi-building me-1 text-primary"></i>${opp.company_name}</span>
                        </div>

                        <!-- 3. Location -->
                        <div class="mb-2">
                            <small class="text-secondary d-block" style="font-size: 0.75rem;">Location:</small>
                            <span class="text-light small"><i class="bi bi-geo-alt me-1 text-danger"></i>${opp.location || 'Remote / Online'}</span>
                        </div>

                        <!-- 4. Deadline -->
                        <div class="mb-3">
                            <small class="text-secondary d-block" style="font-size: 0.75rem;">Deadline:</small>
                            <span class="text-warning fw-medium small"><i class="bi bi-calendar-event me-1"></i>${deadlineFormatted}</span>
                        </div>
                    </div>

                    <!-- Actions Row: Official Website, View Details, Register/Apply -->
                    <div class="pt-3 border-top border-subtle mt-auto">
                        <div class="d-flex flex-column gap-2">
                            <div class="d-flex gap-2">
                                <a href="${opp.apply_url || '#'}" target="_blank" class="btn btn-sm btn-glass flex-grow-1 text-center" title="Visit Official Website">
                                    <i class="bi bi-box-arrow-up-right me-1"></i>Official Website
                                </a>
                                <button class="btn btn-sm btn-glass flex-grow-1 details-btn" data-id="${opp.id}">
                                    <i class="bi bi-info-circle me-1"></i>View Details
                                </button>
                            </div>
                            ${actionBtnHtml}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    // Attach Event Listeners to Opportunity Cards
    function attachCardEventListeners() {
        // View Details Modal Button
        document.querySelectorAll('.details-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const id = btn.getAttribute('data-id');
                openDetailsModal(id);
            });
        });

        // Apply / Register Button
        document.querySelectorAll('.apply-now-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const id = btn.getAttribute('data-id');
                const opp = loadedOpportunities.find(o => o.id == id);
                if (opp) openOpportunityApplicationModal(opp);
            });
        });
    }

    // =========================================================================
    // Clean Opportunity Details Modal
    // =========================================================================
    async function openDetailsModal(oppId) {
        const modalEl = document.getElementById('opportunityDetailModal');
        if (!modalEl) return;

        const bodyEl = document.getElementById('oppModalBody');
        const modalTitle = document.getElementById('modalOppTitle');
        const typeBadge = document.getElementById('modalOppTypeBadge');

        bodyEl.innerHTML = `<div class="p-4 text-center"><div class="spinner-border text-primary"></div><p class="text-secondary small mt-2">Loading details...</p></div>`;

        const modal = new bootstrap.Modal(modalEl);
        modal.show();

        try {
            const res = await window.api.get(`/recommendations/${oppId}`);
            const opp = res.data;
            const typeMeta = getTypeMeta(opp.opportunity_type);
            const deadlineFormatted = formatDeadline(opp.deadline);

            if (modalTitle) modalTitle.textContent = opp.title;
            if (typeBadge) {
                typeBadge.textContent = typeMeta.label.toUpperCase();
                typeBadge.className = `badge ${typeMeta.badgeClass} text-uppercase`;
            }

            bodyEl.innerHTML = `
                <div class="mb-4">
                    <div class="row g-3 p-3 bg-surface-elevated rounded-3 border border-subtle mb-3">
                        <div class="col-md-6">
                            <small class="text-secondary d-block mb-1">${typeMeta.orgLabel}:</small>
                            <span class="text-light fw-bold small"><i class="bi bi-building me-1 text-primary"></i>${opp.company_name}</span>
                        </div>
                        <div class="col-md-6">
                            <small class="text-secondary d-block mb-1">Location / Venue:</small>
                            <span class="text-light fw-semibold small"><i class="bi bi-geo-alt me-1 text-danger"></i>${opp.venue_address || opp.location || 'Remote / Online'}</span>
                        </div>
                        <div class="col-md-6">
                            <small class="text-secondary d-block mb-1">Registration Deadline:</small>
                            <span class="text-warning fw-semibold small"><i class="bi bi-calendar-event me-1"></i>${deadlineFormatted}</span>
                        </div>
                        <div class="col-md-6">
                            <small class="text-secondary d-block mb-1">Official Link:</small>
                            <a href="${opp.apply_url || '#'}" target="_blank" class="text-primary small text-decoration-none">
                                Visit Official Portal <i class="bi bi-box-arrow-up-right ms-1"></i>
                            </a>
                        </div>
                    </div>

                    <!-- Description -->
                    <div class="mb-3">
                        <h6 class="text-light fw-bold mb-2">Description</h6>
                        <p class="text-secondary small leading-relaxed mb-0" style="white-space: pre-line;">${opp.description || 'No additional description provided.'}</p>
                    </div>

                    <!-- Eligibility -->
                    ${opp.eligibility_criteria ? `
                        <div class="mb-3 p-3 bg-surface-elevated rounded-3 border border-subtle">
                            <h6 class="text-light fw-bold mb-1 small"><i class="bi bi-shield-check me-1 text-emerald"></i>Eligibility Criteria</h6>
                            <p class="text-secondary small mb-0">${opp.eligibility_criteria}</p>
                        </div>
                    ` : ''}
                </div>

                <!-- Footer Actions -->
                <div class="d-flex justify-content-between align-items-center pt-3 border-top border-subtle">
                    <a href="${opp.apply_url || '#'}" target="_blank" class="btn btn-glass btn-sm">
                        <i class="bi bi-box-arrow-up-right me-1"></i>Official Website
                    </a>
                    ${opp.is_applied ? `
                        <button class="btn btn-glass btn-sm text-emerald" disabled>
                            <i class="bi bi-check2-circle me-1"></i>Already Registered
                        </button>
                    ` : `
                        <button class="btn btn-gradient-primary btn-sm modal-apply-trigger-btn" data-id="${opp.id}">
                            <i class="bi ${typeMeta.icon} me-1"></i>${typeMeta.actionLabel}
                        </button>
                    `}
                </div>
            `;

            // Trigger apply form from within detail modal
            const modalApplyBtn = bodyEl.querySelector('.modal-apply-trigger-btn');
            if (modalApplyBtn) {
                modalApplyBtn.addEventListener('click', () => {
                    modal.hide();
                    openOpportunityApplicationModal(opp);
                });
            }

        } catch (err) {
            bodyEl.innerHTML = `<div class="alert alert-danger p-3 text-center">Failed to load opportunity details.</div>`;
        }
    }

    // =========================================================================
    // Clean Register / Apply Modal
    // =========================================================================
    async function openOpportunityApplicationModal(opp) {
        if (!window.api.isAuthenticated()) {
            window.location.href = '/login';
            return;
        }

        const modalEl = document.getElementById('opportunityApplyModal');
        const bodyContent = document.getElementById('applyModalBodyContent');
        const modalTitle = document.getElementById('applyModalOppTitle');
        const modalCompany = document.getElementById('applyModalOppCompany');
        const typeBadge = document.getElementById('applyModalOppTypeBadge');

        if (!modalEl || !bodyContent) return;

        bodyContent.innerHTML = `<div class="p-4 text-center"><div class="spinner-border text-primary"></div><p class="text-secondary small mt-2">Loading application form...</p></div>`;

        const modal = new bootstrap.Modal(modalEl);
        modal.show();

        const profile = await fetchStudentProfileSnapshot();
        const userObj = profile.user || {};
        const fullName = profile.full_name || userObj.full_name || 'Student';
        const email = userObj.email || '';
        const phone = profile.phone || '';
        const college = profile.college_name || '';

        const oppType = (opp.opportunity_type || 'job').toLowerCase();
        const typeMeta = getTypeMeta(oppType);

        if (modalTitle) modalTitle.textContent = `${typeMeta.actionLabel} — ${opp.title}`;
        if (modalCompany) modalCompany.textContent = `${opp.company_name} • ${opp.location || 'Remote'}`;
        if (typeBadge) typeBadge.textContent = oppType.toUpperCase();

        const isHackathon = oppType === 'hackathon';

        bodyContent.innerHTML = `
            <div id="applyFormErrorAlert" class="alert alert-danger d-none mb-3"></div>
            <form id="simpleApplicationForm">
                <input type="hidden" name="opportunity_id" value="${opp.id}">
                <input type="hidden" name="opportunity_type" value="${oppType}">

                <div class="row g-3 mb-3">
                    <div class="col-md-6">
                        <label class="form-label small">Full Name *</label>
                        <input type="text" name="full_name" class="form-control form-control-sm" value="${fullName}" required>
                    </div>
                    <div class="col-md-6">
                        <label class="form-label small">Email Address *</label>
                        <input type="email" name="email" class="form-control form-control-sm" value="${email}" required>
                    </div>
                    <div class="col-md-6">
                        <label class="form-label small">Phone Number *</label>
                        <input type="tel" name="phone" class="form-control form-control-sm" value="${phone}" placeholder="+91 98765 43210" required>
                    </div>
                    <div class="col-md-6">
                        <label class="form-label small">College / University *</label>
                        <input type="text" name="college_name" class="form-control form-control-sm" value="${college}" placeholder="e.g. SNS College of Technology" required>
                    </div>

                    ${isHackathon ? `
                        <div class="col-md-6">
                            <label class="form-label small">Team Name *</label>
                            <input type="text" name="team_name" class="form-control form-control-sm" placeholder="e.g. Nexus Hackers (or Solo)" required>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label small">Participation Mode</label>
                            <select name="team_size" class="form-select form-select-sm">
                                <option value="Individual">Individual (Solo)</option>
                                <option value="2 Members">Team of 2</option>
                                <option value="3 Members">Team of 3</option>
                                <option value="4 Members" selected>Team of 4</option>
                            </select>
                        </div>
                        <div class="col-12">
                            <label class="form-label small">Project Concept / Idea Summary</label>
                            <textarea name="project_idea" class="form-control form-control-sm" rows="2" placeholder="Brief outline of your proposed hackathon project..."></textarea>
                        </div>
                    ` : `
                        <div class="col-12">
                            <label class="form-label small">Brief Pitch / Notes</label>
                            <textarea name="cover_letter" class="form-control form-control-sm" rows="3" placeholder="Briefly introduce yourself and your relevant skills..."></textarea>
                        </div>
                    `}
                </div>

                <div class="d-flex justify-content-between align-items-center pt-3 border-top border-subtle">
                    <button type="button" class="btn btn-glass btn-sm" data-bs-dismiss="modal">Cancel</button>
                    <button type="submit" class="btn btn-gradient-primary btn-sm" id="formSubmitBtn">
                        <i class="bi bi-send me-1"></i>Confirm ${typeMeta.actionLabel}
                    </button>
                </div>
            </form>
        `;

        // Handle Submission
        const form = document.getElementById('simpleApplicationForm');
        if (form) {
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                const submitBtn = document.getElementById('formSubmitBtn');
                const errorAlert = document.getElementById('applyFormErrorAlert');

                if (errorAlert) {
                    errorAlert.classList.add('d-none');
                    errorAlert.textContent = '';
                }

                if (submitBtn) {
                    submitBtn.disabled = true;
                    submitBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-1"></span>Submitting...`;
                }

                const formData = new FormData(form);

                try {
                    const token = window.api.getToken();
                    const response = await fetch('/api/applications/apply', {
                        method: 'POST',
                        headers: {
                            'Authorization': `Bearer ${token}`
                        },
                        body: formData
                    });

                    const resData = await response.json();

                    if (!response.ok || !resData.success) {
                        throw new Error(resData.message || 'Submission failed.');
                    }

                    modal.hide();

                    const targetOpp = loadedOpportunities.find(o => o.id == opp.id);
                    if (targetOpp) {
                        targetOpp.is_applied = true;
                        targetOpp.application_status = resData.data.initial_stage || 'Registered';
                    }

                    showSuccessModal(targetOpp || opp, resData.data.initial_stage);

                    // Re-render card list to reflect applied status
                    container.innerHTML = loadedOpportunities.map(o => renderOpportunityCard(o)).join('');
                    attachCardEventListeners();

                } catch (err) {
                    const errMsg = err.message || 'Failed to submit registration.';
                    if (errorAlert) {
                        errorAlert.textContent = errMsg;
                        errorAlert.classList.remove('d-none');
                    } else {
                        window.api.showToast(errMsg, 'danger');
                    }
                } finally {
                    if (submitBtn) {
                        submitBtn.disabled = false;
                        submitBtn.innerHTML = `<i class="bi bi-send me-1"></i>Confirm ${typeMeta.actionLabel}`;
                    }
                }
            });
        }
    }

    function showSuccessModal(opp, initialStage) {
        const modalEl = document.getElementById('applicationSuccessModal');
        if (!modalEl) return;

        const titleEl = document.getElementById('successModalTitle');
        const oppNameEl = document.getElementById('successModalOppName');
        const companyEl = document.getElementById('successModalCompany');
        const stageEl = document.getElementById('successModalStage');

        if (titleEl) titleEl.textContent = `${initialStage || 'Registration'} Confirmed!`;
        if (oppNameEl && opp) oppNameEl.textContent = opp.title;
        if (companyEl && opp) companyEl.textContent = opp.company_name;
        if (stageEl) stageEl.textContent = (initialStage || 'Registered').toUpperCase();

        const modal = new bootstrap.Modal(modalEl);
        modal.show();
    }

    // Filter Listeners
    function updateActiveTypePill(selectedType) {
        typeFilterPills.forEach(p => {
            if (p.getAttribute('data-type') === selectedType) {
                p.classList.add('active', 'btn-gradient-primary');
                p.classList.remove('btn-glass');
            } else {
                p.classList.remove('active', 'btn-gradient-primary');
                p.classList.add('btn-glass');
            }
        });
    }

    typeFilterPills.forEach(pill => {
        pill.addEventListener('click', () => {
            currentFilters.type = pill.getAttribute('data-type');
            updateActiveTypePill(currentFilters.type);
            loadOpportunities();
        });
    });

    if (locationSelect) {
        locationSelect.addEventListener('change', () => {
            currentFilters.location = locationSelect.value;
            loadOpportunities();
        });
    }

    if (sortSelect) {
        sortSelect.addEventListener('change', () => {
            currentFilters.sort_by = sortSelect.value;
            loadOpportunities();
        });
    }

    if (searchInput) {
        let timeout;
        searchInput.addEventListener('input', () => {
            clearTimeout(timeout);
            if (clearSearchBtn) {
                clearSearchBtn.style.display = searchInput.value.trim() ? 'block' : 'none';
            }
            timeout = setTimeout(() => {
                currentFilters.query = searchInput.value.trim();
                loadOpportunities();
            }, 300);
        });
    }

    if (clearSearchBtn) {
        clearSearchBtn.addEventListener('click', () => {
            searchInput.value = '';
            clearSearchBtn.style.display = 'none';
            currentFilters.query = '';
            loadOpportunities();
        });
    }

    function resetAllFilters() {
        currentFilters = {
            type: 'all',
            query: '',
            location: '',
            sort_by: 'deadline_asc'
        };

        if (searchInput) searchInput.value = '';
        if (clearSearchBtn) clearSearchBtn.style.display = 'none';
        if (locationSelect) locationSelect.value = '';
        if (sortSelect) sortSelect.value = 'deadline_asc';

        updateActiveTypePill('all');

        const newUrl = new URL(window.location);
        newUrl.search = '';
        window.history.replaceState({}, '', newUrl);

        loadOpportunities();
    }

    // Initialize
    loadOpportunities();
});
