/**
 * Admin Portal Management Module — Career DNA AI
 * Robust, High-Contrast, Error-Free Architecture for Dashboard, Students, Opportunities, Applications, and Resume Documents.
 */

document.addEventListener('DOMContentLoaded', async () => {
    // 1. Verify Admin Authentication
    if (!window.api.isAuthenticated()) {
        window.location.href = '/login?redirect=' + encodeURIComponent(window.location.pathname);
        return;
    }

    const user = window.api.getUser();
    if (!user || user.role !== 'admin') {
        window.api.showToast('Access restricted to platform administrators.', 'danger');
        setTimeout(() => { window.location.href = '/dashboard'; }, 1000);
        return;
    }

    const path = window.location.pathname;

    // 2. Dispatch to Page Initializer
    if (path.includes('/admin/students')) {
        initStudentsDirectory();
    } else if (path.includes('/admin/opportunities')) {
        initOpportunitiesCatalog();
    } else if (path.includes('/admin/applications')) {
        initApplicationsMonitor();
    } else {
        initAdminDashboard();
    }
});

// =============================================================================
// Helper: High-Contrast Opportunity Type Badge Class
// =============================================================================
function getTypeBadgeClass(oppType) {
    const map = {
        hackathon: 'badge badge-amber-subtle text-uppercase',
        internship: 'badge badge-primary-subtle text-uppercase',
        job: 'badge badge-cyan-subtle text-uppercase',
        competition: 'badge badge-rose-subtle text-uppercase',
        certification: 'badge badge-emerald-subtle text-uppercase',
        course: 'badge badge-primary-subtle text-uppercase',
        other: 'badge badge-purple-subtle text-uppercase'
    };
    return map[(oppType || '').toLowerCase()] || 'badge badge-primary-subtle text-uppercase';
}

// =============================================================================
// 1. Admin Dashboard Overview
// =============================================================================
async function initAdminDashboard() {
    const statStudents = document.getElementById('adminStatStudents');
    const statTotalOpps = document.getElementById('adminStatTotalOpps');
    const statActiveOpps = document.getElementById('adminStatActiveOpps');
    const statApps = document.getElementById('adminStatApps');
    const studentsTableBody = document.getElementById('adminRecentStudentsBody');
    const appsTableBody = document.getElementById('adminRecentAppsBody');

    try {
        const [statsRes, appsRes] = await Promise.all([
            window.api.get('/admin/stats'),
            window.api.get('/admin/applications')
        ]);

        const stats = statsRes.data || {};
        const allApps = appsRes.data?.applications || [];

        // 4 Core Metrics
        if (statStudents) statStudents.textContent = stats.total_students || 0;
        if (statTotalOpps) statTotalOpps.textContent = stats.total_opportunities || 0;
        if (statActiveOpps) statActiveOpps.textContent = stats.active_opportunities || 0;
        if (statApps) statApps.textContent = stats.total_applications || allApps.length || 0;

        // Recent Students Table Preview
        const recentStudents = stats.recent_students || [];
        if (studentsTableBody) {
            if (recentStudents.length === 0) {
                studentsTableBody.innerHTML = `<tr><td colspan="4" class="text-center py-4 text-secondary">No students registered yet.</td></tr>`;
            } else {
                studentsTableBody.innerHTML = recentStudents.map(s => `
                    <tr>
                        <td>
                            <div class="fw-bold text-light">${s.full_name}</div>
                            <small class="text-secondary">${s.email}</small>
                        </td>
                        <td>
                            <div class="text-light small">${s.degree || 'B.Tech / B.E.'}</div>
                            <small class="text-secondary">${s.branch || 'Engineering'}</small>
                        </td>
                        <td>
                            <span class="text-light small">${s.career_goal || 'Software Engineer'}</span>
                        </td>
                        <td class="text-end">
                            <button class="btn btn-sm btn-glass text-light view-student-btn" data-user-id="${s.user_id}">
                                <i class="bi bi-eye me-1 text-primary"></i>Profile
                            </button>
                        </td>
                    </tr>
                `).join('');

                attachStudentViewListeners(studentsTableBody);
            }
        }

        // Recent Applications Table Preview
        if (appsTableBody) {
            const recentApps = allApps.slice(0, 5);
            if (recentApps.length === 0) {
                appsTableBody.innerHTML = `<tr><td colspan="4" class="text-center py-4 text-secondary">No applications or registrations yet.</td></tr>`;
            } else {
                appsTableBody.innerHTML = recentApps.map(a => `
                    <tr>
                        <td>
                            <div class="fw-bold text-light">${a.student_name}</div>
                            <small class="text-secondary">${a.student_email}</small>
                        </td>
                        <td>
                            <div class="text-light small fw-medium">${a.opportunity_title}</div>
                            <small class="text-secondary">${a.company_name}</small>
                        </td>
                        <td>
                            <span class="${getTypeBadgeClass(a.opportunity_type)}" style="font-size: 0.68rem;">
                                ${a.opportunity_type}
                            </span>
                        </td>
                        <td>
                            <span class="badge badge-cyan-subtle text-uppercase" style="font-size: 0.68rem;">
                                ${(a.status || 'Applied').replace('_', ' ')}
                            </span>
                        </td>
                    </tr>
                `).join('');
            }
        }

    } catch (err) {
        console.error('Error loading admin dashboard stats:', err);
    }
}

// =============================================================================
// 2. Registered Students Directory & Complete Profile Inspector
// =============================================================================
async function initStudentsDirectory() {
    const tableBody = document.getElementById('registeredStudentsTableBody');
    const searchInput = document.getElementById('studentSearchInput');
    const branchFilter = document.getElementById('studentBranchFilter');
    const yearFilter = document.getElementById('studentYearFilter');
    const countBadge = document.getElementById('studentCountBadge');
    const refreshBtn = document.getElementById('refreshStudentsBtn');

    let allStudents = [];

    async function loadStudents() {
        if (tableBody) {
            tableBody.innerHTML = `<tr><td colspan="7" class="text-center py-5"><div class="spinner-border text-primary"></div><p class="text-secondary small mt-2">Loading students directory...</p></td></tr>`;
        }

        try {
            const params = new URLSearchParams();
            if (searchInput && searchInput.value.trim()) params.append('search', searchInput.value.trim());
            if (branchFilter && branchFilter.value !== 'all') params.append('branch', branchFilter.value);
            if (yearFilter && yearFilter.value !== 'all') params.append('year', yearFilter.value);

            const res = await window.api.get(`/admin/students?${params.toString()}`);
            allStudents = res.data?.students || [];

            if (countBadge) countBadge.textContent = allStudents.length;

            if (allStudents.length === 0) {
                tableBody.innerHTML = `
                    <tr>
                        <td colspan="7" class="text-center py-5 text-secondary">
                            <i class="bi bi-person-x fs-3 d-block mb-2 text-secondary"></i>
                            No students match the current filters.
                        </td>
                    </tr>
                `;
                return;
            }

            tableBody.innerHTML = allStudents.map(s => `
                <tr>
                    <td>
                        <div class="fw-bold text-white">${s.full_name}</div>
                        <small class="text-secondary">${s.email}</small>
                        ${s.phone ? `<small class="text-secondary d-block mt-0.5" style="font-size: 0.76rem;"><i class="bi bi-telephone me-1 text-primary"></i>${s.phone}</small>` : ''}
                        ${s.has_uploaded_resume ? `<div class="mt-1"><span class="badge badge-emerald-subtle py-0.5 px-2" style="font-size: 0.70rem;"><i class="bi bi-file-earmark-pdf me-1"></i>Resume Attached</span></div>` : ''}
                    </td>
                    <td>
                        <div class="text-white small fw-medium">${s.college_name || 'University Student'}</div>
                        <small class="text-secondary">${s.degree} &bull; ${s.branch}</small>
                    </td>
                    <td>
                        <span class="badge bg-surface-elevated text-white border border-subtle fw-semibold px-2 py-1">${s.graduation_year || 'N/A'}</span>
                        ${s.cgpa ? `<small class="text-secondary d-block mt-1 fw-medium">CGPA: <b class="text-white">${s.cgpa}</b></small>` : ''}
                    </td>
                    <td>
                        <div class="d-flex flex-wrap gap-1" style="max-width: 200px;">
                            ${(s.skills || []).slice(0, 3).map(sk => `<span class="badge badge-primary-subtle py-0.5 px-2" style="font-size: 0.72rem;">${sk}</span>`).join('')}
                            ${(s.skills || []).length > 3 ? `<span class="badge bg-surface-elevated text-white py-0.5 px-1.5" style="font-size: 0.70rem;">+${s.skills.length - 3}</span>` : ''}
                        </div>
                    </td>
                    <td>
                        <span class="text-white small fw-medium">${s.career_goal || 'Software Engineer'}</span>
                    </td>
                    <td>
                        <span class="badge badge-cyan-subtle px-2 py-1 fw-bold">${s.applications_count || 0} submissions</span>
                    </td>
                    <td class="text-end">
                        <div class="btn-group btn-group-sm">
                            <button class="btn btn-sm btn-gradient-primary text-white fw-bold view-student-btn" data-user-id="${s.user_id}">
                                <i class="bi bi-person-badge me-1"></i>Full Profile
                            </button>
                            <a href="${s.resume_url || `/api/resume/student/${s.id}/pdf`}" target="_blank" class="btn btn-sm btn-glass text-light fw-bold" title="Open Attached Resume">
                                <i class="bi bi-file-earmark-pdf text-danger"></i>
                            </a>
                        </div>
                    </td>
                </tr>
            `).join('');

            attachStudentViewListeners(tableBody);

        } catch (err) {
            if (tableBody) tableBody.innerHTML = `<tr><td colspan="7" class="text-center py-4 text-danger">Error loading students directory.</td></tr>`;
        }
    }

    if (searchInput) {
        let timeout;
        searchInput.addEventListener('input', () => {
            clearTimeout(timeout);
            timeout = setTimeout(loadStudents, 250);
        });
    }

    if (branchFilter) branchFilter.addEventListener('change', loadStudents);
    if (yearFilter) yearFilter.addEventListener('change', loadStudents);
    if (refreshBtn) refreshBtn.addEventListener('click', loadStudents);

    loadStudents();
}

function attachStudentViewListeners(container) {
    container.querySelectorAll('.view-student-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const userId = btn.getAttribute('data-user-id');
            openStudentDetailModal(userId);
        });
    });
}

async function openStudentDetailModal(userId) {
    const modalEl = document.getElementById('studentDetailsModal');
    const bodyEl = document.getElementById('studentDetailsModalBody');
    if (!modalEl || !bodyEl) return;

    const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
    bodyEl.innerHTML = `<div class="text-center py-5 text-secondary"><div class="spinner-border text-primary me-2"></div>Loading full student career profile...</div>`;
    modal.show();

    try {
        const res = await window.api.get(`/admin/students/${userId}`);
        const sData = res.data || {};
        const p = sData.profile || {};
        const apps = sData.applications || [];
        const skills = sData.skills || [];

        bodyEl.innerHTML = `
            <!-- Top Identity Row -->
            <div class="d-flex flex-column flex-md-row justify-content-between align-items-start pb-3 border-bottom border-subtle mb-3 gap-2">
                <div>
                    <h4 class="text-white fw-bold mb-1">${p.full_name || 'Student'}</h4>
                    <p class="text-secondary small mb-1"><i class="bi bi-envelope me-1 text-primary"></i>${sData.email || p.email} &bull; <i class="bi bi-telephone me-1 text-primary"></i>${p.phone || 'No phone provided'}</p>
                    <p class="text-white small mb-0"><i class="bi bi-building me-1 text-primary"></i>${p.college_name || 'College'} &bull; ${p.degree} (${p.branch})</p>
                </div>
                <div class="text-md-end d-flex flex-wrap gap-2 align-items-center">
                    <span class="badge bg-primary px-3 py-2 fs-6">Class of ${p.graduation_year || 2026}</span>
                </div>
            </div>

            <!-- Attached Official Resume Banner -->
            <div class="p-3 bg-surface-elevated rounded-3 border border-subtle mb-3">
                <div class="d-flex flex-column flex-sm-row justify-content-between align-items-sm-center gap-2">
                    <div class="d-flex align-items-center gap-3">
                        <div class="brand-icon ${p.has_uploaded_resume ? 'bg-danger bg-opacity-20 text-danger border border-danger border-opacity-30' : 'bg-primary bg-opacity-20 text-primary border border-primary border-opacity-30'} rounded-3 p-2 fs-4" style="width: 44px; height: 44px;">
                            <i class="bi ${p.has_uploaded_resume ? 'bi-file-earmark-pdf' : 'bi-file-earmark-person'}"></i>
                        </div>
                        <div>
                            <small class="text-white text-uppercase fw-bold d-block" style="font-size: 0.72rem; letter-spacing: 0.04em;">
                                ${p.has_uploaded_resume ? 'ATTACHED OFFICIAL RESUME' : 'CAREER DNA PROFILE RESUME'}
                            </small>
                            <span class="text-white fw-semibold small">
                                ${p.has_uploaded_resume ? (p.resume_original_name || p.resume_filename) : 'Live Auto-Generated AI Profile Resume'}
                            </span>
                            ${p.resume_uploaded_at ? `<small class="text-secondary d-block" style="font-size: 0.75rem;"><i class="bi bi-clock-history me-1"></i>Uploaded: ${p.resume_uploaded_at}</small>` : ''}
                        </div>
                    </div>
                    <div class="d-flex flex-wrap gap-2 align-items-center">
                        <a href="/api/resume/student/${p.id}/pdf" target="_blank" class="btn btn-sm btn-gradient-primary fw-bold shadow-sm px-3">
                            <i class="bi bi-box-arrow-up-right me-1"></i>Open ${p.has_uploaded_resume ? 'Uploaded Resume' : 'Resume'}
                        </a>
                        ${p.has_uploaded_resume ? `
                            <a href="/api/resume/student/${p.id}/pdf?force_generate=true" target="_blank" class="btn btn-sm btn-glass text-light fw-medium">
                                <i class="bi bi-robot me-1 text-primary"></i>AI Profile Resume
                            </a>
                        ` : ''}
                    </div>
                </div>
            </div>

            <!-- Career Goal & Socials -->
            <div class="row g-3 mb-3">
                <div class="col-md-6">
                    <div class="p-3 bg-surface-elevated rounded border border-subtle h-100">
                        <small class="text-white text-uppercase fw-bold d-block mb-1" style="font-size: 0.72rem; letter-spacing: 0.04em;">CAREER GOAL & ASPIRATION</small>
                        <span class="text-white fw-semibold small">${p.career_goal || p.target_role || 'Software Engineering'}</span>
                        ${p.headline ? `<p class="text-secondary small mt-1 mb-0">${p.headline}</p>` : ''}
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="p-3 bg-surface-elevated rounded border border-subtle h-100">
                        <small class="text-white text-uppercase fw-bold d-block mb-1" style="font-size: 0.72rem; letter-spacing: 0.04em;">PROFILES & PORTFOLIO</small>
                        <div class="d-flex flex-wrap gap-2">
                            ${p.github_url ? `<a href="${p.github_url}" target="_blank" class="badge bg-dark border border-subtle text-light text-decoration-none py-1.5 px-2.5"><i class="bi bi-github me-1"></i>GitHub</a>` : ''}
                            ${p.linkedin_url ? `<a href="${p.linkedin_url}" target="_blank" class="badge bg-primary bg-opacity-20 text-primary border border-primary border-opacity-30 text-decoration-none py-1.5 px-2.5"><i class="bi bi-linkedin me-1"></i>LinkedIn</a>` : ''}
                            ${p.portfolio_url ? `<a href="${p.portfolio_url}" target="_blank" class="badge bg-success bg-opacity-20 text-success border border-success border-opacity-30 text-decoration-none py-1.5 px-2.5"><i class="bi bi-globe me-1"></i>Portfolio</a>` : ''}
                        </div>
                    </div>
                </div>
            </div>

            <!-- Verified Skills -->
            <div class="mb-3">
                <small class="text-light text-uppercase fw-semibold d-block mb-2" style="font-size: 0.72rem; letter-spacing: 0.03em;">VERIFIED TECHNICAL SKILLS (${skills.length})</small>
                <div class="d-flex flex-wrap gap-1">
                    ${skills.length > 0 ? skills.map(sk => `<span class="badge badge-primary-subtle">${sk.skill_name || sk}</span>`).join('') : '<span class="text-secondary small">No skills added yet</span>'}
                </div>
            </div>

            <!-- Student's Submitted Opportunities -->
            <div class="mt-4 pt-3 border-top border-subtle">
                <h6 class="text-white fw-bold mb-3"><i class="bi bi-kanban text-primary me-2"></i>Opportunities Applied / Registered (${apps.length})</h6>
                ${apps.length === 0 ? `
                    <div class="p-3 bg-surface-elevated rounded text-center text-secondary small border border-subtle">
                        This student has not submitted any applications or registrations yet.
                    </div>
                ` : `
                    <div class="table-responsive">
                        <table class="table table-dark table-sm align-middle mb-0" style="background: transparent;">
                            <thead class="bg-surface-elevated text-light small">
                                <tr>
                                    <th>OPPORTUNITY</th>
                                    <th>TYPE</th>
                                    <th>DATE</th>
                                    <th>STAGE</th>
                                    <th>DETAILS / NOTE</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${apps.map(a => `
                                    <tr>
                                        <td>
                                            <div class="fw-bold text-light small">${a.position_title}</div>
                                            <small class="text-secondary">${a.company_name}</small>
                                        </td>
                                        <td><span class="${getTypeBadgeClass(a.opportunity_type)}" style="font-size: 0.65rem;">${a.opportunity_type}</span></td>
                                        <td><small class="text-secondary">${a.applied_date}</small></td>
                                        <td><span class="badge badge-cyan-subtle text-uppercase" style="font-size: 0.65rem;">${(a.status || 'Applied').replace('_', ' ')}</span></td>
                                        <td><small class="text-secondary">${a.notes || 'Registered'}</small></td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                `}
            </div>
        `;

    } catch (err) {
        bodyEl.innerHTML = `<div class="alert alert-danger">Failed to load student details.</div>`;
    }
}

// =============================================================================
// 3. Opportunities Catalog Management (Add, Edit, Delete, Bulk, Clean Expired)
// =============================================================================
async function initOpportunitiesCatalog() {
    let opportunities = [];
    const tableBody = document.getElementById('adminOppTableBody');
    const searchInput = document.getElementById('adminOppSearch');
    const statusFilter = document.getElementById('adminOppStatusFilter');
    const typeFilter = document.getElementById('adminOppTypeFilter');
    const selectAllCheckbox = document.getElementById('adminSelectAll');
    const bulkActivateBtn = document.getElementById('bulkActivateBtn');
    const bulkDeactivateBtn = document.getElementById('bulkDeactivateBtn');
    const cleanExpiredBtn = document.getElementById('cleanExpiredOppsBtn');
    const createForm = document.getElementById('createOppForm');
    const editForm = document.getElementById('editOppForm');

    async function loadAdminOpportunities() {
        if (!tableBody) return;
        tableBody.innerHTML = `<tr><td colspan="8" class="text-center py-5"><div class="spinner-border text-primary"></div><p class="text-secondary small mt-2">Loading opportunities catalog...</p></td></tr>`;

        try {
            const params = new URLSearchParams();
            if (statusFilter && statusFilter.value !== 'all') params.append('status', statusFilter.value);
            if (typeFilter && typeFilter.value !== 'all') params.append('type', typeFilter.value);
            if (searchInput && searchInput.value.trim()) params.append('search', searchInput.value.trim());

            const res = await window.api.get(`/admin/opportunities?${params.toString()}`);
            opportunities = res.data.opportunities || [];

            renderAdminOppTable(opportunities);
        } catch (err) {
            tableBody.innerHTML = `<tr><td colspan="8" class="text-center text-danger py-4">Error loading opportunities catalog.</td></tr>`;
        }
    }

    function renderAdminOppTable(opps) {
        if (opps.length === 0) {
            tableBody.innerHTML = `<tr><td colspan="8" class="text-center py-5 text-secondary">No opportunities found matching the selected filters.</td></tr>`;
            return;
        }

        tableBody.innerHTML = opps.map(opp => {
            const isExpired = opp.is_expired;
            const statusBadge = isExpired ?
                `<span class="badge bg-danger bg-opacity-20 text-danger border border-danger fw-semibold">Expired</span>` :
                (opp.status === 'active' ? `<span class="badge badge-emerald-subtle">Active</span>` : `<span class="badge bg-secondary text-uppercase">${opp.status}</span>`);

            return `
                <tr>
                    <td><input type="checkbox" class="form-check-input opp-checkbox" data-id="${opp.id}"></td>
                    <td>
                        <div class="fw-bold text-white">${opp.title}</div>
                        <small class="text-secondary">${opp.company_name} &bull; ${opp.location || 'Remote'}</small>
                    </td>
                    <td><span class="${getTypeBadgeClass(opp.opportunity_type)}" style="font-size: 0.72rem;">${opp.opportunity_type}</span></td>
                    <td>${statusBadge}</td>
                    <td>
                        <button class="btn btn-sm btn-glass text-white py-0.5 px-2.5 view-applicants-btn fw-bold shadow-sm" data-id="${opp.id}" style="font-size: 0.76rem;">
                            <i class="bi bi-people me-1 text-primary"></i>${opp.applicants_count || 0} Students
                        </button>
                    </td>
                    <td><span class="text-white small fw-medium">${opp.deadline || 'Ongoing'}</span></td>
                    <td>
                        <div class="d-flex flex-wrap gap-1" style="max-width: 180px;">
                            ${(opp.required_skills || []).slice(0, 2).map(s => `<span class="badge badge-primary-subtle py-0.5 px-1.5" style="font-size: 0.70rem;">${s}</span>`).join('')}
                            ${(opp.required_skills || []).length > 2 ? `<span class="badge bg-surface-elevated text-white py-0.5 px-1.5" style="font-size: 0.68rem;">+${opp.required_skills.length - 2}</span>` : ''}
                        </div>
                    </td>
                    <td class="text-end">
                        <div class="btn-group btn-group-sm">
                            <button class="btn btn-glass text-white edit-opp-btn" data-id="${opp.id}" title="Edit Opportunity"><i class="bi bi-pencil"></i></button>
                            <button class="btn btn-glass text-danger delete-opp-btn" data-id="${opp.id}" title="Delete Opportunity"><i class="bi bi-trash"></i></button>
                        </div>
                    </td>
                </tr>
            `;
        }).join('');

        attachOppTableListeners();
    }

    function attachOppTableListeners() {
        // View Applicants Modal
        document.querySelectorAll('.view-applicants-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const id = btn.getAttribute('data-id');
                openOppApplicantsModal(id);
            });
        });

        // Edit Opportunity Modal
        document.querySelectorAll('.edit-opp-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const id = btn.getAttribute('data-id');
                const opp = opportunities.find(o => o.id == id);
                if (opp) openEditOppModal(opp);
            });
        });

        // Delete Opportunity
        document.querySelectorAll('.delete-opp-btn').forEach(btn => {
            btn.addEventListener('click', async () => {
                const id = btn.getAttribute('data-id');
                if (confirm('Permanently delete this opportunity from catalog?')) {
                    try {
                        await window.api.delete(`/admin/opportunities/${id}`);
                        window.api.showToast('Opportunity deleted successfully.', 'info');
                        loadAdminOpportunities();
                    } catch (err) {}
                }
            });
        });
    }

    // Select All Checkbox
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', () => {
            document.querySelectorAll('.opp-checkbox').forEach(cb => {
                cb.checked = selectAllCheckbox.checked;
            });
        });
    }

    // Bulk Activate Action
    if (bulkActivateBtn) {
        bulkActivateBtn.addEventListener('click', async () => {
            const selectedIds = Array.from(document.querySelectorAll('.opp-checkbox:checked')).map(cb => parseInt(cb.getAttribute('data-id')));
            if (selectedIds.length === 0) {
                window.api.showToast('Please select at least one opportunity.', 'warning');
                return;
            }
            try {
                await window.api.post('/admin/opportunities/bulk-status', { ids: selectedIds, status: 'active' });
                window.api.showToast(`Activated ${selectedIds.length} opportunities!`, 'success');
                loadAdminOpportunities();
            } catch (err) {}
        });
    }

    // Bulk Deactivate Action
    if (bulkDeactivateBtn) {
        bulkDeactivateBtn.addEventListener('click', async () => {
            const selectedIds = Array.from(document.querySelectorAll('.opp-checkbox:checked')).map(cb => parseInt(cb.getAttribute('data-id')));
            if (selectedIds.length === 0) {
                window.api.showToast('Please select at least one opportunity.', 'warning');
                return;
            }
            try {
                await window.api.post('/admin/opportunities/bulk-status', { ids: selectedIds, status: 'closed' });
                window.api.showToast(`Deactivated ${selectedIds.length} opportunities.`, 'info');
                loadAdminOpportunities();
            } catch (err) {}
        });
    }

    // Clean Expired Button
    if (cleanExpiredBtn) {
        cleanExpiredBtn.addEventListener('click', async () => {
            if (confirm('Archive all opportunities whose deadline has passed?')) {
                try {
                    const res = await window.api.post('/admin/opportunities/clean-expired', { action: 'archive' });
                    window.api.showToast(res.message || 'Expired opportunities archived.', 'success');
                    loadAdminOpportunities();
                } catch (err) {}
            }
        });
    }

    // Search and Filter Listeners
    if (searchInput) {
        let timeout;
        searchInput.addEventListener('input', () => {
            clearTimeout(timeout);
            timeout = setTimeout(loadAdminOpportunities, 250);
        });
    }

    if (statusFilter) statusFilter.addEventListener('change', loadAdminOpportunities);
    if (typeFilter) typeFilter.addEventListener('change', loadAdminOpportunities);

    // Applicants Modal Loader
    async function openOppApplicantsModal(oppId) {
        const modalEl = document.getElementById('oppApplicantsModal');
        if (!modalEl) return;

        const tableBody = document.getElementById('oppApplicantsTableBody');
        const modalTitle = document.getElementById('modalOppTitle');
        const modalCompany = document.getElementById('modalOppCompany');
        const modalTypeBadge = document.getElementById('modalOppTypeBadge');
        const totalText = document.getElementById('oppApplicantsTotalText');

        if (tableBody) {
            tableBody.innerHTML = `<tr><td colspan="6" class="text-center py-4"><div class="spinner-border text-primary"></div><p class="text-secondary small mt-2">Loading registered applicants...</p></td></tr>`;
        }

        const modal = new bootstrap.Modal(modalEl);
        modal.show();

        try {
            const res = await window.api.get(`/admin/opportunities/${oppId}/applicants`);
            const data = res.data || {};
            const opp = data.opportunity || {};
            const applicants = data.applicants || [];

            if (modalTitle) modalTitle.textContent = opp.title || 'Registered Students';
            if (modalCompany) modalCompany.textContent = `${opp.company_name || ''} • Location: ${opp.location || 'Remote'}`;
            if (modalTypeBadge) modalTypeBadge.textContent = (opp.opportunity_type || 'Opportunity').toUpperCase();
            if (totalText) totalText.textContent = `${applicants.length} student${applicants.length === 1 ? '' : 's'} registered`;

            if (applicants.length === 0) {
                tableBody.innerHTML = `<tr><td colspan="6" class="text-center py-5 text-secondary">No students have registered or applied for this opportunity yet.</td></tr>`;
                return;
            }

            tableBody.innerHTML = applicants.map(a => {
                let resumeBtn = `<span class="text-secondary small">None</span>`;
                if (a.resume_url) {
                    resumeBtn = `<div class="mt-1"><a href="${a.resume_url}" target="_blank" class="badge bg-primary text-white text-decoration-none py-1.5 px-2.5 fw-semibold shadow-sm"><i class="bi bi-file-earmark-pdf me-1"></i>Resume</a></div>`;
                }

                let detailsNote = a.notes || 'Direct Registration';
                const sdt = a.submitted_details || {};
                if (sdt.hackathon_details) {
                    const h = sdt.hackathon_details;
                    detailsNote = `<b>Team:</b> ${h.team_name || 'Solo'} (${h.team_size || 'Individual'})<br><span class="text-info">${h.track || ''}</span><br>${h.project_idea ? h.project_idea.substring(0, 70) + '...' : ''}`;
                } else if (sdt.internship_details) {
                    const intern = sdt.internship_details;
                    detailsNote = `<b>Avail:</b> ${intern.availability} | <b>Mode:</b> ${intern.preferred_work_mode}<br>${intern.cover_note ? intern.cover_note.substring(0, 80) + '...' : ''}`;
                } else if (sdt.job_details) {
                    const j = sdt.job_details;
                    detailsNote = `<b>Exp:</b> ${j.experience_years} | <b>Notice:</b> ${j.notice_period}<br>${j.cover_letter ? j.cover_letter.substring(0, 80) + '...' : ''}`;
                }

                return `
                    <tr>
                        <td>
                            <div class="fw-bold text-white">${a.name}</div>
                            <small class="text-secondary">${a.email}</small>
                            ${a.phone ? `<small class="text-secondary d-block mt-0.5" style="font-size: 0.76rem;"><i class="bi bi-telephone me-1 text-primary"></i>${a.phone}</small>` : ''}
                            ${resumeBtn}
                        </td>
                        <td>
                            <div class="text-white small fw-medium">${a.college || 'University Student'}</div>
                            <small class="text-secondary">${a.degree || a.branch || ''}</small>
                        </td>
                        <td>
                            <div class="d-flex flex-wrap gap-1" style="max-width: 180px;">
                                ${(a.skills || []).slice(0, 3).map(s => `<span class="badge badge-primary-subtle py-0.5 px-2" style="font-size: 0.72rem;">${s}</span>`).join('')}
                            </div>
                        </td>
                        <td><span class="text-white small fw-medium">${a.applied_date}</span></td>
                        <td><span class="badge badge-cyan-subtle text-uppercase px-2 py-1 fw-bold">${(a.status || 'Applied').replace('_', ' ')}</span></td>
                        <td><div class="text-secondary small fw-medium" style="max-width: 220px; line-height: 1.4;">${detailsNote}</div></td>
                    </tr>
                `;
            }).join('');

        } catch (err) {
            tableBody.innerHTML = `<tr><td colspan="6" class="text-center py-4 text-danger">Failed to load applicants list.</td></tr>`;
        }
    }

    // Open Edit Opportunity Modal
    function openEditOppModal(opp) {
        document.getElementById('editOppId').value = opp.id;
        document.getElementById('editOppTitle').value = opp.title || '';
        document.getElementById('editOppCompany').value = opp.company_name || '';
        document.getElementById('editOppType').value = (opp.opportunity_type || 'hackathon').toLowerCase();
        document.getElementById('editOppLocation').value = opp.location || '';
        
        const isRemoteEl = document.getElementById('editOppIsRemote');
        if (isRemoteEl) isRemoteEl.checked = !!opp.is_remote;
        
        document.getElementById('editOppSalary').value = opp.stipend_salary || '';
        document.getElementById('editOppDeadline').value = opp.deadline ? opp.deadline.split('T')[0] : '';
        document.getElementById('editOppApplyUrl').value = opp.apply_url || '';
        document.getElementById('editOppSkills').value = (opp.required_skills || []).join(', ');
        document.getElementById('editOppStatus').value = opp.status || 'active';
        document.getElementById('editOppDesc').value = opp.description || '';
        
        const eligEl = document.getElementById('editOppEligibility');
        if (eligEl) eligEl.value = opp.eligibility_criteria || '';

        const modal = new bootstrap.Modal(document.getElementById('editOppModal'));
        modal.show();
    }

    // Create Opportunity Form Submit Handler
    if (createForm) {
        createForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const submitBtn = document.getElementById('saveCreateOppBtn');
            const originalText = submitBtn ? submitBtn.innerHTML : '';
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-1"></span>Saving...`;
            }

            const isRemoteEl = document.getElementById('createOppIsRemote');
            const payload = {
                title: document.getElementById('createOppTitle').value.trim(),
                company_name: document.getElementById('createOppCompany').value.trim(),
                opportunity_type: document.getElementById('createOppType').value,
                location: document.getElementById('createOppLocation').value.trim() || 'Remote',
                is_remote: isRemoteEl ? isRemoteEl.checked : true,
                stipend_salary: document.getElementById('createOppSalary').value.trim(),
                deadline: document.getElementById('createOppDeadline').value || null,
                apply_url: document.getElementById('createOppApplyUrl').value.trim(),
                required_skills: document.getElementById('createOppSkills').value.split(',').map(s => s.trim()).filter(Boolean),
                description: document.getElementById('createOppDesc').value.trim(),
                eligibility_criteria: document.getElementById('createOppEligibility').value.trim(),
                status: document.getElementById('createOppStatus').value
            };

            try {
                await window.api.post('/admin/opportunities', payload);
                window.api.showToast('Opportunity added to catalog successfully!', 'success');
                createForm.reset();
                const modalEl = document.getElementById('createOppModal');
                if (modalEl && typeof bootstrap !== 'undefined') {
                    const modal = bootstrap.Modal.getInstance(modalEl) || bootstrap.Modal.getOrCreateInstance(modalEl);
                    if (modal) modal.hide();
                }
                setTimeout(() => {
                    document.querySelectorAll('.modal-backdrop').forEach(el => el.remove());
                    document.body.classList.remove('modal-open');
                    document.body.style.removeProperty('overflow');
                    document.body.style.removeProperty('padding-right');
                }, 300);
                loadAdminOpportunities();
            } catch (err) {
                console.error('Error creating opportunity:', err);
            } finally {
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalText;
                }
            }
        });
    }

    // Edit Opportunity Form Submit Handler
    if (editForm) {
        editForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const submitBtn = document.getElementById('saveEditOppBtn');
            const originalText = submitBtn ? submitBtn.innerHTML : '';
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-1"></span>Saving...`;
            }

            const id = document.getElementById('editOppId').value;
            const isRemoteEl = document.getElementById('editOppIsRemote');
            const payload = {
                title: document.getElementById('editOppTitle').value.trim(),
                company_name: document.getElementById('editOppCompany').value.trim(),
                opportunity_type: document.getElementById('editOppType').value,
                location: document.getElementById('editOppLocation').value.trim(),
                is_remote: isRemoteEl ? isRemoteEl.checked : true,
                stipend_salary: document.getElementById('editOppSalary').value.trim(),
                deadline: document.getElementById('editOppDeadline').value || null,
                apply_url: document.getElementById('editOppApplyUrl').value.trim(),
                required_skills: document.getElementById('editOppSkills').value.split(',').map(s => s.trim()).filter(Boolean),
                status: document.getElementById('editOppStatus').value,
                description: document.getElementById('editOppDesc').value.trim(),
                eligibility_criteria: document.getElementById('editOppEligibility').value.trim()
            };

            try {
                await window.api.put(`/admin/opportunities/${id}`, payload);
                window.api.showToast('Opportunity updated successfully in database!', 'success');
                const modalEl = document.getElementById('editOppModal');
                if (modalEl && typeof bootstrap !== 'undefined') {
                    const modal = bootstrap.Modal.getInstance(modalEl) || bootstrap.Modal.getOrCreateInstance(modalEl);
                    if (modal) modal.hide();
                }
                setTimeout(() => {
                    document.querySelectorAll('.modal-backdrop').forEach(el => el.remove());
                    document.body.classList.remove('modal-open');
                    document.body.style.removeProperty('overflow');
                    document.body.style.removeProperty('padding-right');
                }, 300);
                loadAdminOpportunities();
            } catch (err) {
                console.error('Error editing opportunity:', err);
            } finally {
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalText;
                }
            }
        });
    }

    loadAdminOpportunities();
}

// =============================================================================
// 4. Applications / Registrations Monitor
// =============================================================================
async function initApplicationsMonitor() {
    const tableBody = document.getElementById('adminAllAppsTableBody');
    const searchInput = document.getElementById('adminAppSearchInput');
    const typeFilter = document.getElementById('adminAppTypeFilter');
    const statusFilter = document.getElementById('adminAppStatusFilter');
    const countBadge = document.getElementById('adminAppCountBadge');
    const refreshBtn = document.getElementById('refreshAdminAppsBtn');

    let allApps = [];

    async function loadApplications() {
        if (tableBody) {
            tableBody.innerHTML = `<tr><td colspan="7" class="text-center py-5"><div class="spinner-border text-primary"></div><p class="text-secondary small mt-2">Loading applications & registrations...</p></td></tr>`;
        }

        try {
            const params = new URLSearchParams();
            if (searchInput && searchInput.value.trim()) params.append('search', searchInput.value.trim());
            if (typeFilter && typeFilter.value !== 'all') params.append('type', typeFilter.value);
            if (statusFilter && statusFilter.value !== 'all') params.append('status', statusFilter.value);

            const res = await window.api.get(`/admin/applications?${params.toString()}`);
            allApps = res.data?.applications || [];

            if (countBadge) countBadge.textContent = allApps.length;

            if (allApps.length === 0) {
                tableBody.innerHTML = `
                    <tr>
                        <td colspan="7" class="text-center py-5 text-secondary">
                            <i class="bi bi-inbox fs-3 d-block mb-2 text-secondary"></i>
                            No applications or registrations match the selected filters.
                        </td>
                    </tr>
                `;
                return;
            }

            tableBody.innerHTML = allApps.map(a => {
                let resumeBtn = `<span class="text-secondary small">None</span>`;
                if (a.resume_url) {
                    resumeBtn = `<a href="${a.resume_url}" target="_blank" class="badge bg-primary text-white text-decoration-none py-1.5 px-2.5 fw-bold shadow-sm"><i class="bi bi-file-earmark-pdf me-1"></i>Resume</a>`;
                }

                return `
                    <tr>
                        <td>
                            <div class="fw-bold text-white">${a.student_name}</div>
                            <small class="text-secondary">${a.student_email}</small>
                            ${a.student_phone ? `<small class="text-secondary d-block mt-0.5" style="font-size: 0.76rem;"><i class="bi bi-telephone me-1 text-primary"></i>${a.student_phone}</small>` : ''}
                        </td>
                        <td>
                            <div class="fw-bold text-white small">${a.opportunity_title}</div>
                            <small class="text-secondary"><i class="bi bi-building me-1 text-primary"></i>${a.company_name}</small>
                        </td>
                        <td>
                            <span class="${getTypeBadgeClass(a.opportunity_type)}" style="font-size: 0.72rem;">
                                ${a.opportunity_type}
                            </span>
                        </td>
                        <td>
                            <span class="text-white small fw-medium">${a.applied_date}</span>
                        </td>
                        <td>
                            <span class="badge badge-cyan-subtle text-uppercase px-2 py-1 fw-bold">${(a.status || 'Applied').replace('_', ' ')}</span>
                        </td>
                        <td>
                            ${resumeBtn}
                        </td>
                        <td class="text-end">
                            <button class="btn btn-sm btn-gradient-primary text-white fw-bold inspect-app-btn" data-id="${a.id}">
                                <i class="bi bi-file-earmark-text me-1"></i>View Details
                            </button>
                        </td>
                    </tr>
                `;
            }).join('');

            attachAppInspectListeners();

        } catch (err) {
            if (tableBody) tableBody.innerHTML = `<tr><td colspan="7" class="text-center py-4 text-danger">Error loading applications.</td></tr>`;
        }
    }

    function attachAppInspectListeners() {
        document.querySelectorAll('.inspect-app-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const id = btn.getAttribute('data-id');
                const app = allApps.find(a => a.id == id);
                if (app) openAdminAppDetailModal(app, loadApplications);
            });
        });
    }

    if (searchInput) {
        let timeout;
        searchInput.addEventListener('input', () => {
            clearTimeout(timeout);
            timeout = setTimeout(loadApplications, 250);
        });
    }

    if (typeFilter) typeFilter.addEventListener('change', loadApplications);
    if (statusFilter) statusFilter.addEventListener('change', loadApplications);
    if (refreshBtn) refreshBtn.addEventListener('click', loadApplications);

    loadApplications();
}

function openAdminAppDetailModal(app, onUpdateCallback) {
    const modalEl = document.getElementById('adminAppDetailModal');
    if (!modalEl) return;

    const typeBadge = document.getElementById('adminModalAppType');
    const titleEl = document.getElementById('adminModalAppTitle');
    const companyEl = document.getElementById('adminModalAppCompany');
    const bodyEl = document.getElementById('adminModalAppBody');
    const quickStatusSelect = document.getElementById('adminModalQuickStatus');
    const saveStatusBtn = document.getElementById('adminModalSaveStatusBtn');

    if (typeBadge) typeBadge.textContent = (app.opportunity_type || 'Opportunity').toUpperCase();
    if (titleEl) titleEl.textContent = `${app.opportunity_title} — ${app.student_name}`;
    if (companyEl) companyEl.textContent = `${app.company_name} • Submitted on ${app.applied_date}`;

    // Populate stage options
    if (quickStatusSelect) {
        const oppType = (app.opportunity_type || 'job').toLowerCase();
        let stages = ['applied', 'screening', 'interview', 'offer', 'rejected'];
        if (oppType === 'hackathon') {
            stages = ['registered', 'shortlisted', 'round_1', 'round_2', 'finalist', 'winner', 'not_selected'];
        } else if (oppType === 'competition') {
            stages = ['registered', 'participating', 'qualified', 'final_round', 'winner', 'not_selected'];
        } else if (oppType === 'certification' || oppType === 'course') {
            stages = ['enrolled', 'in_progress', 'completed', 'expired'];
        }

        quickStatusSelect.innerHTML = stages.map(stg => `
            <option value="${stg}" ${app.status === stg ? 'selected' : ''}>${stg.replace('_', ' ').toUpperCase()}</option>
        `).join('');
    }

    const dt = app.submitted_details || {};
    const cand = dt.candidate || {};

    let specificHtml = '';
    if (dt.hackathon_details) {
        const h = dt.hackathon_details;
        specificHtml = `
            <div class="card bg-surface-elevated p-3 border border-subtle mb-3">
                <h6 class="text-white fw-bold mb-2 small"><i class="bi bi-laptop text-warning me-2"></i>Hackathon Registration Details</h6>
                <div class="row g-2 small">
                    <div class="col-sm-6"><b>Team Name:</b> <span class="text-light">${h.team_name || 'Solo'}</span> (${h.team_size || 'Individual'})</div>
                    <div class="col-sm-6"><b>Track:</b> <span class="text-info">${h.track || 'General'}</span></div>
                    ${h.team_members ? `<div class="col-12"><b>Team Members:</b> <span class="text-secondary">${h.team_members}</span></div>` : ''}
                    ${h.experience ? `<div class="col-sm-6"><b>Experience:</b> <span class="text-secondary">${h.experience}</span></div>` : ''}
                    ${h.project_idea ? `<div class="col-12 mt-2"><b>Project Concept / Pitch:</b><p class="text-light bg-surface-card p-2 rounded mt-1 border border-subtle mb-0">${h.project_idea}</p></div>` : ''}
                </div>
            </div>
        `;
    } else if (dt.internship_details) {
        const intern = dt.internship_details;
        specificHtml = `
            <div class="card bg-surface-elevated p-3 border border-subtle mb-3">
                <h6 class="text-white fw-bold mb-2 small"><i class="bi bi-send-check text-primary me-2"></i>Internship Application Details</h6>
                <div class="row g-2 small">
                    <div class="col-sm-6"><b>Availability:</b> <span class="text-light">${intern.availability || 'Immediate'}</span></div>
                    <div class="col-sm-6"><b>Work Mode:</b> <span class="text-light">${intern.preferred_work_mode || 'Flexible'} (${intern.preferred_location || 'Remote'})</span></div>
                    ${intern.relevant_projects ? `<div class="col-12"><b>Projects:</b> <span class="text-secondary">${intern.relevant_projects}</span></div>` : ''}
                    ${intern.cover_note ? `<div class="col-12 mt-2"><b>Cover Note:</b><p class="text-light bg-surface-card p-2 rounded mt-1 border border-subtle mb-0">${intern.cover_note}</p></div>` : ''}
                </div>
            </div>
        `;
    } else if (dt.job_details) {
        const j = dt.job_details;
        specificHtml = `
            <div class="card bg-surface-elevated p-3 border border-subtle mb-3">
                <h6 class="text-white fw-bold mb-2 small"><i class="bi bi-briefcase text-info me-2"></i>Job Application Details</h6>
                <div class="row g-2 small">
                    <div class="col-sm-6"><b>Experience:</b> <span class="text-light">${j.experience_years || 'Entry Level'}</span></div>
                    <div class="col-sm-6"><b>Notice Period:</b> <span class="text-light">${j.notice_period || 'Immediate'}</span></div>
                    <div class="col-sm-6"><b>Expected Salary:</b> <span class="text-emerald">${j.expected_salary || 'Competitive'}</span></div>
                    <div class="col-sm-6"><b>Location Preference:</b> <span class="text-light">${j.preferred_location || 'Flexible'}</span></div>
                    ${j.cover_letter ? `<div class="col-12 mt-2"><b>Cover Letter:</b><p class="text-light bg-surface-card p-2 rounded mt-1 border border-subtle mb-0">${j.cover_letter}</p></div>` : ''}
                </div>
            </div>
        `;
    }

    let resumeHtml = '';
    if (app.resume_url) {
        resumeHtml = `
            <div class="p-3 bg-surface-elevated rounded border border-subtle d-flex justify-content-between align-items-center mb-3">
                <div>
                    <small class="text-light text-uppercase fw-semibold d-block" style="font-size: 0.72rem; letter-spacing: 0.03em;">ATTACHED CANDIDATE RESUME</small>
                    <span class="text-white small fw-semibold"><i class="bi bi-file-earmark-pdf text-danger me-1"></i>${app.resume_filename === 'ai_generated' ? 'Career DNA AI Verified Resume' : (app.resume_filename || 'Uploaded Resume')}</span>
                </div>
                <a href="${app.resume_url}" target="_blank" class="btn btn-sm btn-gradient-primary fw-bold shadow-sm">
                    <i class="bi bi-file-earmark-arrow-down me-1"></i>Download Resume
                </a>
            </div>
        `;
    }

    bodyEl.innerHTML = `
        <div class="card bg-surface-card p-3 border border-subtle mb-3">
            <h6 class="text-white fw-bold mb-2 small"><i class="bi bi-person-badge text-primary me-2"></i>Candidate Profile Snapshot</h6>
            <div class="row g-2 small">
                <div class="col-sm-6"><b>Student Name:</b> <span class="text-light">${cand.full_name || app.student_name}</span></div>
                <div class="col-sm-6"><b>Email Address:</b> <span class="text-secondary">${cand.email || app.student_email}</span></div>
                <div class="col-sm-6"><b>Phone:</b> <span class="text-secondary">${cand.phone || app.student_phone || 'N/A'}</span></div>
                <div class="col-sm-6"><b>College / Dept:</b> <span class="text-secondary">${cand.college_name || app.college_name || 'N/A'}</span></div>
                ${cand.skills && cand.skills.length ? `<div class="col-12"><b>Skills:</b> <div class="d-inline-flex flex-wrap gap-1 ms-1">${cand.skills.map(s => `<span class="badge badge-primary-subtle py-0 px-2" style="font-size: 0.7rem;">${s}</span>`).join('')}</div></div>` : ''}
            </div>
        </div>

        ${resumeHtml}
        ${specificHtml}

        ${app.notes ? `
            <div class="card bg-surface-elevated p-3 border border-subtle mb-0">
                <h6 class="text-white fw-bold mb-1 small"><i class="bi bi-card-text text-secondary me-2"></i>Notes & Submission Record</h6>
                <p class="text-secondary small mb-0">${app.notes}</p>
            </div>
        ` : ''}
    `;

    if (saveStatusBtn) {
        saveStatusBtn.onclick = async () => {
            const newStatus = quickStatusSelect.value;
            saveStatusBtn.disabled = true;
            try {
                await window.api.put(`/admin/applications/${app.id}/status`, { status: newStatus });
                window.api.showToast(`Stage updated to ${newStatus.replace('_', ' ').toUpperCase()}!`, 'success');
                app.status = newStatus;
                if (modalEl && typeof bootstrap !== 'undefined') {
                    const modal = bootstrap.Modal.getInstance(modalEl) || bootstrap.Modal.getOrCreateInstance(modalEl);
                    if (modal) modal.hide();
                }
                setTimeout(() => {
                    document.querySelectorAll('.modal-backdrop').forEach(el => el.remove());
                    document.body.classList.remove('modal-open');
                    document.body.style.removeProperty('overflow');
                    document.body.style.removeProperty('padding-right');
                }, 300);
                if (onUpdateCallback) onUpdateCallback();
            } catch (err) {
                console.error('Error updating status:', err);
            } finally {
                saveStatusBtn.disabled = false;
            }
        };
    }

    const modal = new bootstrap.Modal(modalEl);
    modal.show();
}
