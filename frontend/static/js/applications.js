/**
 * Application & Opportunity Tracker Module
 * Dynamic Type-Aware Workflows (Jobs, Internships, Hackathons, Competitions, Certifications)
 * Automatic Status Synchronization & Drag-and-Drop Kanban Engine
 */

document.addEventListener('DOMContentLoaded', async () => {
    if (!window.api.isAuthenticated()) {
        window.location.href = '/login?redirect=/applications';
        return;
    }

    let allApplications = [];
    let workflows = {};
    let activeWorkflowType = 'all'; // 'all', 'job', 'internship', 'hackathon', 'competition', 'certification'
    let draggedAppId = null;

    const dynamicBoard = document.getElementById('dynamicKanbanBoard');
    const syncStatusBtn = document.getElementById('syncStatusBtn');
    const workflowHintText = document.getElementById('workflowHintText');
    const addAppForm = document.getElementById('addApplicationForm');
    const editAppForm = document.getElementById('editApplicationForm');
    const addAppType = document.getElementById('addAppType');
    const addAppStatus = document.getElementById('addAppStatus');
    const editAppType = document.getElementById('editAppType');
    const editAppStatus = document.getElementById('editAppStatus');
    const workflowTabBtns = document.querySelectorAll('.workflow-tab-btn');

    // Read URL query parameter if present (e.g. /applications?type=hackathon)
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('type')) {
        const reqType = urlParams.get('type').toLowerCase();
        if (['job', 'internship', 'hackathon', 'competition', 'certification', 'course'].includes(reqType)) {
            activeWorkflowType = (reqType === 'course') ? 'certification' : (reqType === 'internship' ? 'job' : reqType);
            workflowTabBtns.forEach(btn => {
                if (btn.getAttribute('data-type') === activeWorkflowType) {
                    btn.classList.add('active', 'btn-gradient-primary');
                    btn.classList.remove('btn-glass');
                } else {
                    btn.classList.remove('active', 'btn-gradient-primary');
                    btn.classList.add('btn-glass');
                }
            });
        }
    }

    // Default Fallback Workflows
    const defaultWorkflows = {
        job: {
            label: 'Jobs & Internships',
            default_status: 'applied',
            stages: [
                { key: 'applied', label: 'Applied', icon: 'bi-send', color: 'primary' },
                { key: 'screening', label: 'Screening', icon: 'bi-funnel', color: 'info' },
                { key: 'interview', label: 'Interview', icon: 'bi-calendar2-check', color: 'warning' },
                { key: 'offer', label: 'Offer', icon: 'bi-trophy', color: 'success' },
                { key: 'rejected', label: 'Rejected', icon: 'bi-x-circle', color: 'danger' }
            ]
        },
        internship: {
            label: 'Internships',
            default_status: 'applied',
            stages: [
                { key: 'applied', label: 'Applied', icon: 'bi-send', color: 'primary' },
                { key: 'screening', label: 'Screening', icon: 'bi-funnel', color: 'info' },
                { key: 'interview', label: 'Interview', icon: 'bi-calendar2-check', color: 'warning' },
                { key: 'offer', label: 'Offer', icon: 'bi-trophy', color: 'success' },
                { key: 'rejected', label: 'Rejected', icon: 'bi-x-circle', color: 'danger' }
            ]
        },
        hackathon: {
            label: 'Hackathons',
            default_status: 'registered',
            stages: [
                { key: 'registered', label: 'Registered', icon: 'bi-clipboard-check', color: 'primary' },
                { key: 'shortlisted', label: 'Shortlisted', icon: 'bi-funnel', color: 'info' },
                { key: 'round_1', label: 'Round 1', icon: 'bi-flag', color: 'warning' },
                { key: 'round_2', label: 'Round 2', icon: 'bi-lightning', color: 'secondary' },
                { key: 'finalist', label: 'Finalist', icon: 'bi-stars', color: 'accent-purple' },
                { key: 'winner', label: 'Winner', icon: 'bi-trophy', color: 'success' },
                { key: 'not_selected', label: 'Not Selected', icon: 'bi-x-circle', color: 'danger' }
            ]
        },
        competition: {
            label: 'Competitions',
            default_status: 'registered',
            stages: [
                { key: 'registered', label: 'Registered', icon: 'bi-clipboard-check', color: 'primary' },
                { key: 'participating', label: 'Participating', icon: 'bi-play-circle', color: 'info' },
                { key: 'qualified', label: 'Qualified', icon: 'bi-patch-check', color: 'warning' },
                { key: 'final_round', label: 'Final Round', icon: 'bi-stars', color: 'accent-purple' },
                { key: 'winner', label: 'Winner', icon: 'bi-trophy', color: 'success' },
                { key: 'not_selected', label: 'Not Selected', icon: 'bi-x-circle', color: 'danger' }
            ]
        },
        certification: {
            label: 'Certifications',
            default_status: 'enrolled',
            stages: [
                { key: 'enrolled', label: 'Enrolled', icon: 'bi-journal-check', color: 'primary' },
                { key: 'in_progress', label: 'In Progress', icon: 'bi-hourglass-split', color: 'info' },
                { key: 'completed', label: 'Certified', icon: 'bi-award', color: 'success' },
                { key: 'expired', label: 'Incomplete / Expired', icon: 'bi-x-circle', color: 'danger' }
            ]
        },
        course: {
            label: 'Courses',
            default_status: 'enrolled',
            stages: [
                { key: 'enrolled', label: 'Enrolled', icon: 'bi-journal-check', color: 'primary' },
                { key: 'in_progress', label: 'In Progress', icon: 'bi-hourglass-split', color: 'info' },
                { key: 'completed', label: 'Completed', icon: 'bi-award', color: 'success' },
                { key: 'expired', label: 'Dropped / Expired', icon: 'bi-x-circle', color: 'danger' }
            ]
        }
    };

    // 1. Fetch & Initialize
    async function loadApplications() {
        if (dynamicBoard) {
            dynamicBoard.innerHTML = `
                <div class="col-12 py-5 text-center w-100">
                    <div class="spinner-border text-primary" role="status"></div>
                    <p class="text-secondary small mt-2">Loading application pipeline...</p>
                </div>
            `;
        }

        try {
            const res = await window.api.get('/applications');
            allApplications = res.data.applications || [];
            workflows = res.data.workflows || defaultWorkflows;
            renderDynamicKanban();
            loadStats();
        } catch (err) {
            console.error('Error loading applications:', err);
            if (dynamicBoard) {
                dynamicBoard.innerHTML = `
                    <div class="col-12 py-5 text-center w-100">
                        <div class="alert alert-danger d-inline-block px-4">
                            <i class="bi bi-exclamation-triangle me-2"></i>Failed to load applications. Please try again.
                        </div>
                        <div class="mt-2">
                            <button class="btn btn-sm btn-gradient-primary" onclick="window.location.reload()">
                                <i class="bi bi-arrow-clockwise me-1"></i>Retry
                            </button>
                        </div>
                    </div>
                `;
            }
        }
    }

    async function loadStats() {
        try {
            const res = await window.api.get('/applications/stats');
            const stats = res.data;
            if (!stats) return;

            const totalEl = document.getElementById('statTotalApps');
            const activeEl = document.getElementById('statActivePipeline');
            const interviewRateEl = document.getElementById('statInterviewRate');
            const offerRateEl = document.getElementById('statOfferRate');

            if (totalEl) totalEl.textContent = stats.total_applications || 0;
            if (activeEl) activeEl.textContent = stats.active_pipeline || 0;
            if (interviewRateEl) interviewRateEl.textContent = `${stats.interview_rate || 0}%`;
            if (offerRateEl) offerRateEl.textContent = `${stats.offer_rate || 0}%`;
        } catch (err) {}
    }

    // 2. Render Dynamic Kanban Board based on selected workflow tab
    function renderDynamicKanban() {
        if (!dynamicBoard) return;

        // Check if student has no applications at all
        if (allApplications.length === 0) {
            dynamicBoard.innerHTML = `
                <div class="col-12 py-5 text-center w-100">
                    <div class="p-5 bg-surface-card rounded-4 border border-subtle text-center shadow-lg" style="max-width: 600px; margin: 0 auto;">
                        <div class="rounded-circle bg-primary bg-opacity-10 d-inline-flex p-3 text-primary mb-3" style="font-size: 2.5rem;">
                            <i class="bi bi-kanban"></i>
                        </div>
                        <h4 class="text-light fw-bold mb-2">No applications or registrations yet.</h4>
                        <p class="text-secondary small mb-4">
                            Track your recruitment pipelines, hackathon progression, competition rounds, and certification milestones in one place. Explore matching opportunities to get started!
                        </p>
                        <div class="d-flex flex-wrap gap-2 justify-content-center">
                            <a href="/recommendations" class="btn btn-gradient-primary">
                                <i class="bi bi-compass me-1"></i>Explore Opportunities
                            </a>
                            <button class="btn btn-glass" data-bs-toggle="modal" data-bs-target="#addApplicationModal">
                                <i class="bi bi-plus-lg me-1"></i>Track Manually
                            </button>
                        </div>
                    </div>
                </div>
            `;
            if (workflowHintText) workflowHintText.textContent = 'No active applications in pipeline';
            return;
        }

        let activeStages = [];
        let filteredApps = [];
        let tabLabel = 'Opportunities';

        if (activeWorkflowType === 'all') {
            activeStages = [
                { key: 'applied', label: 'Applied / Registered', icon: 'bi-send', color: 'primary' },
                { key: 'screening', label: 'Screening / Progress / Rounds', icon: 'bi-funnel', color: 'info' },
                { key: 'interview', label: 'Interview / Finalist / Qualified', icon: 'bi-calendar2-check', color: 'warning' },
                { key: 'offer', label: 'Offer / Winner / Certified', icon: 'bi-trophy', color: 'success' },
                { key: 'rejected', label: 'Rejected / Not Selected', icon: 'bi-x-circle', color: 'danger' }
            ];
            filteredApps = allApplications;
            tabLabel = 'All Opportunities';
            if (workflowHintText) workflowHintText.textContent = `Showing all ${allApplications.length} opportunities mapped into unified pipeline stages`;
        } else if (activeWorkflowType === 'job') {
            activeStages = (workflows.job || defaultWorkflows.job).stages;
            filteredApps = allApplications.filter(a => a.opportunity_type === 'job' || a.opportunity_type === 'internship');
            tabLabel = 'Jobs & Internships';
            if (workflowHintText) workflowHintText.textContent = 'Jobs & Internships Workflow: Applied → Screening → Interview → Offer → Rejected';
        } else if (activeWorkflowType === 'hackathon') {
            activeStages = (workflows.hackathon || defaultWorkflows.hackathon).stages;
            filteredApps = allApplications.filter(a => a.opportunity_type === 'hackathon');
            tabLabel = 'Hackathons';
            if (workflowHintText) workflowHintText.textContent = 'Hackathon Workflow: Registered → Shortlisted → Round 1 → Round 2 → Finalist → Winner';
        } else if (activeWorkflowType === 'competition') {
            activeStages = (workflows.competition || defaultWorkflows.competition).stages;
            filteredApps = allApplications.filter(a => a.opportunity_type === 'competition');
            tabLabel = 'Competitions';
            if (workflowHintText) workflowHintText.textContent = 'Competition Workflow: Registered → Participating → Qualified → Final Round → Winner';
        } else if (activeWorkflowType === 'certification') {
            activeStages = (workflows.certification || defaultWorkflows.certification).stages;
            filteredApps = allApplications.filter(a => a.opportunity_type === 'certification' || a.opportunity_type === 'course');
            tabLabel = 'Certifications & Courses';
            if (workflowHintText) workflowHintText.textContent = 'Certifications Workflow: Enrolled → In Progress → Certified / Completed';
        }

        // Group applications by stage
        const columnMap = {};
        activeStages.forEach(stg => { columnMap[stg.key] = []; });

        filteredApps.forEach(app => {
            const mappedKey = mapAppToStageKey(app, activeWorkflowType, activeStages);
            if (columnMap[mappedKey]) {
                columnMap[mappedKey].push(app);
            } else {
                columnMap[activeStages[0].key].push(app);
            }
        });

        // If specific tab has 0 filtered items but user has other applications
        if (filteredApps.length === 0 && activeWorkflowType !== 'all') {
            dynamicBoard.innerHTML = `
                <div class="col-12 py-4 text-center w-100">
                    <div class="p-4 bg-surface-card rounded-4 border border-subtle text-center shadow-md" style="max-width: 540px; margin: 0 auto;">
                        <i class="bi bi-info-circle text-primary fs-3 d-block mb-2"></i>
                        <h5 class="text-light fw-bold mb-1">No ${tabLabel} Tracked Yet</h5>
                        <p class="text-secondary small mb-3">You have not registered for any ${tabLabel.toLowerCase()} yet. Discover upcoming opportunities to participate!</p>
                        <div class="d-flex gap-2 justify-content-center">
                            <a href="/recommendations?type=${activeWorkflowType}" class="btn btn-sm btn-gradient-primary">
                                <i class="bi bi-search me-1"></i>Explore ${tabLabel}
                            </a>
                            <button class="btn btn-sm btn-glass" onclick="document.querySelector('[data-type=all]').click()">
                                View All Applications
                            </button>
                        </div>
                    </div>
                </div>
            `;
            return;
        }

        // Generate HTML for each stage column
        dynamicBoard.innerHTML = activeStages.map(stg => {
            const appsInStage = columnMap[stg.key] || [];
            return `
                <div class="kanban-column" data-stage="${stg.key}">
                    <div class="kanban-header">
                        <span class="fw-bold text-light small d-flex align-items-center">
                            <i class="bi ${stg.icon} text-${stg.color} me-2 fs-6"></i>
                            <span>${stg.label}</span>
                        </span>
                        <span class="badge bg-surface-elevated text-light rounded-pill px-2" id="count-${stg.key}">${appsInStage.length}</span>
                    </div>
                    <div class="kanban-body" id="col-body-${stg.key}" data-stage="${stg.key}">
                        ${appsInStage.length === 0 ? `
                            <div class="p-3 text-center text-muted small border border-dashed rounded border-subtle">
                                No items in this stage
                            </div>
                        ` : appsInStage.map(app => renderKanbanCard(app)).join('')}
                    </div>
                </div>
            `;
        }).join('');

        attachKanbanEventListeners();
    }

    function mapAppToStageKey(app, workflowType, activeStages) {
        const st = (app.status || '').toLowerCase();
        const validKeys = activeStages.map(s => s.key);

        if (validKeys.includes(st)) return st;

        if (workflowType === 'all') {
            if (['registered', 'enrolled', 'applied'].includes(st)) return 'applied';
            if (['screening', 'participating', 'shortlisted', 'round_1', 'round_2', 'in_progress'].includes(st)) return 'screening';
            if (['interview', 'interview_scheduled', 'qualified', 'final_round', 'finalist'].includes(st)) return 'interview';
            if (['offer', 'winner', 'completed'].includes(st)) return 'offer';
            if (['rejected', 'not_selected', 'expired'].includes(st)) return 'rejected';
            return 'applied';
        }

        // Type specific fallbacks
        if (st === 'interview_scheduled' && validKeys.includes('interview')) return 'interview';
        if (st === 'in_progress' && validKeys.includes('screening')) return 'screening';
        if (st === 'in_progress' && validKeys.includes('participating')) return 'participating';
        if (st === 'applied' && validKeys.includes('registered')) return 'registered';
        if (st === 'applied' && validKeys.includes('enrolled')) return 'enrolled';
        if (st === 'rejected' && validKeys.includes('not_selected')) return 'not_selected';
        if (st === 'offer' && validKeys.includes('winner')) return 'winner';
        if (st === 'offer' && validKeys.includes('completed')) return 'completed';

        return activeStages[0].key;
    }

    function renderKanbanCard(app) {
        const typeBadge = {
            internship: 'badge-primary-subtle',
            job: 'badge-cyan-subtle',
            hackathon: 'badge-amber-subtle',
            competition: 'badge-rose-subtle',
            certification: 'badge-emerald-subtle',
            course: 'badge-primary-subtle'
        }[app.opportunity_type] || 'badge-primary-subtle';

        const stagesForThisType = (workflows[app.opportunity_type] || defaultWorkflows[app.opportunity_type] || defaultWorkflows.job).stages;

        return `
            <div class="kanban-card shadow-sm" draggable="true" data-id="${app.id}">
                <div class="d-flex justify-content-between align-items-start mb-2">
                    <span class="badge ${typeBadge} text-uppercase" style="font-size: 0.68rem; font-weight: 700;">
                        ${app.opportunity_type}
                    </span>
                    <div class="dropdown">
                        <button class="btn btn-link text-muted p-0" data-bs-toggle="dropdown" aria-label="Options">
                            <i class="bi bi-three-dots-vertical"></i>
                        </button>
                        <ul class="dropdown-menu dropdown-menu-dark dropdown-menu-end shadow border-subtle">
                            <li><a class="dropdown-item view-app-btn" href="#" data-id="${app.id}"><i class="bi bi-file-earmark-text me-2"></i>View Submission Details</a></li>
                            <li><a class="dropdown-item edit-app-btn" href="#" data-id="${app.id}"><i class="bi bi-pencil me-2"></i>Edit Tracking</a></li>
                            <li><hr class="dropdown-divider border-subtle"></li>
                            <li><a class="dropdown-item text-danger delete-app-btn" href="#" data-id="${app.id}"><i class="bi bi-trash me-2"></i>Delete</a></li>
                        </ul>
                    </div>
                </div>

                <h6 class="text-light fw-bold mb-1" style="font-size: 0.925rem; line-height: 1.35;">${app.position_title}</h6>
                <div class="small text-secondary mb-2"><i class="bi bi-building me-1"></i>${app.company_name}</div>

                ${app.interview_date ? `
                    <div class="p-1 px-2 rounded bg-primary-light border border-primary text-light small mb-2 d-flex align-items-center gap-1" style="font-size: 0.75rem;">
                        <i class="bi bi-calendar-event text-primary"></i>
                        <span class="fw-semibold">Event: ${app.interview_date}</span>
                    </div>
                ` : ''}

                ${app.deadline ? `
                    <div class="small text-muted mb-2" style="font-size: 0.75rem;">
                        <i class="bi bi-clock-history me-1"></i>Deadline: <span class="text-secondary">${app.deadline}</span>
                    </div>
                ` : ''}

                ${app.salary_offered ? `
                    <div class="small text-emerald mb-2 fw-semibold" style="font-size: 0.78rem;">
                        <i class="bi bi-cash-stack me-1"></i>${app.salary_offered}
                    </div>
                ` : ''}

                <div class="d-flex justify-content-between align-items-center pt-2 border-top border-subtle small text-muted" style="font-size: 0.75rem;">
                    <span><i class="bi bi-calendar-check me-1"></i>${app.applied_date || 'Tracked'}</span>
                    <select class="form-select form-select-sm py-0 px-2 quick-status-select bg-surface-elevated text-light border-subtle" data-id="${app.id}" style="font-size: 0.72rem; width: auto; font-weight: 500;">
                        ${stagesForThisType.map(stg => `
                            <option value="${stg.key}" ${app.status === stg.key ? 'selected' : ''}>${stg.label}</option>
                        `).join('')}
                    </select>
                </div>
            </div>
        `;
    }

    function attachKanbanEventListeners() {
        // Drag events
        document.querySelectorAll('.kanban-card').forEach(card => {
            card.addEventListener('dragstart', (e) => {
                draggedAppId = card.getAttribute('data-id');
                card.classList.add('dragging');
                e.dataTransfer.setData('text/plain', draggedAppId);
            });

            card.addEventListener('dragend', () => {
                card.classList.remove('dragging');
                draggedAppId = null;
            });
        });

        // Drop zones
        document.querySelectorAll('.kanban-body').forEach(col => {
            col.addEventListener('dragover', (e) => {
                e.preventDefault();
                col.classList.add('bg-surface-elevated');
            });

            col.addEventListener('dragleave', () => {
                col.classList.remove('bg-surface-elevated');
            });

            col.addEventListener('drop', async (e) => {
                e.preventDefault();
                col.classList.remove('bg-surface-elevated');
                const targetStage = col.getAttribute('data-stage');
                const appId = e.dataTransfer.getData('text/plain') || draggedAppId;

                if (appId && targetStage) {
                    await updateStatus(appId, targetStage);
                }
            });
        });

        // Quick status select
        document.querySelectorAll('.quick-status-select').forEach(sel => {
            sel.addEventListener('change', async (e) => {
                const id = sel.getAttribute('data-id');
                const status = sel.value;
                await updateStatus(id, status);
            });
        });

        // View submission details button
        document.querySelectorAll('.view-app-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const id = btn.getAttribute('data-id');
                const app = allApplications.find(a => a.id == id);
                if (app) openViewModal(app);
            });
        });

        // Edit button
        document.querySelectorAll('.edit-app-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const id = btn.getAttribute('data-id');
                const app = allApplications.find(a => a.id == id);
                if (app) openEditModal(app);
            });
        });

        // Delete button
        document.querySelectorAll('.delete-app-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                e.preventDefault();
                const id = btn.getAttribute('data-id');
                if (confirm('Delete this opportunity from your tracker?')) {
                    try {
                        await window.api.delete(`/applications/${id}`);
                        window.api.showToast('Opportunity removed from pipeline.', 'info');
                        loadApplications();
                    } catch (err) {}
                }
            });
        });
    }

    async function updateStatus(appId, status) {
        try {
            await window.api.put(`/applications/${appId}`, { status });
            window.api.showToast(`Stage updated to ${status.replace('_', ' ').toUpperCase()}!`, 'success');
            loadApplications();
        } catch (err) {
            console.error('Error updating status:', err);
        }
    }

    // 3. Workflow Tab Buttons Filter
    document.querySelectorAll('.workflow-tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.workflow-tab-btn').forEach(b => {
                b.classList.remove('active', 'btn-gradient-primary');
                b.classList.add('btn-glass');
            });
            btn.classList.add('active', 'btn-gradient-primary');
            btn.classList.remove('btn-glass');
            activeWorkflowType = btn.getAttribute('data-type');
            renderDynamicKanban();
        });
    });

    // 4. Auto Sync Button
    if (syncStatusBtn) {
        syncStatusBtn.addEventListener('click', async () => {
            syncStatusBtn.disabled = true;
            syncStatusBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-1"></span>Syncing...`;
            await loadApplications();
            setTimeout(() => {
                syncStatusBtn.disabled = false;
                syncStatusBtn.innerHTML = `<i class="bi bi-check2-circle text-success me-1"></i>Synced!`;
                setTimeout(() => {
                    syncStatusBtn.innerHTML = `<i class="bi bi-arrow-repeat me-1"></i>Auto Sync`;
                }, 1500);
            }, 500);
        });
    }

    // 5. Populate Status Dropdown in Add / Edit Modals dynamically based on selected Type
    function populateStatusDropdown(selectEl, oppType, selectedVal = null) {
        if (!selectEl) return;
        const config = workflows[oppType] || defaultWorkflows[oppType] || defaultWorkflows.job;
        selectEl.innerHTML = config.stages.map(stg => `
            <option value="${stg.key}" ${selectedVal === stg.key ? 'selected' : ''}>${stg.label}</option>
        `).join('');
    }

    if (addAppType && addAppStatus) {
        populateStatusDropdown(addAppStatus, addAppType.value);
        addAppType.addEventListener('change', () => {
            populateStatusDropdown(addAppStatus, addAppType.value);
        });
    }

    if (editAppType && editAppStatus) {
        editAppType.addEventListener('change', () => {
            populateStatusDropdown(editAppStatus, editAppType.value);
        });
    }

    // 6. Add Application Form Submission
    if (addAppForm) {
        addAppForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const payload = {
                company_name: document.getElementById('addAppCompany').value.trim(),
                position_title: document.getElementById('addAppTitle').value.trim(),
                opportunity_type: addAppType.value,
                status: addAppStatus.value,
                applied_date: document.getElementById('addAppAppliedDate').value,
                deadline: document.getElementById('addAppDeadline').value,
                interview_date: document.getElementById('addAppInterviewDate').value,
                salary_offered: document.getElementById('addAppSalary').value.trim(),
                notes: document.getElementById('addAppNotes').value.trim()
            };

            try {
                await window.api.post('/applications', payload);
                window.api.showToast('Opportunity added to tracker!', 'success');
                addAppForm.reset();
                populateStatusDropdown(addAppStatus, addAppType.value);
                const modal = bootstrap.Modal.getInstance(document.getElementById('addApplicationModal'));
                if (modal) modal.hide();
                loadApplications();
            } catch (err) {}
        });
    }

    // 7. Edit Application Modal & Form Submission
    function openEditModal(app) {
        document.getElementById('editAppId').value = app.id;
        document.getElementById('editAppCompany').value = app.company_name;
        document.getElementById('editAppTitle').value = app.position_title;
        editAppType.value = app.opportunity_type;

        populateStatusDropdown(editAppStatus, app.opportunity_type, app.status);

        document.getElementById('editAppDeadline').value = app.deadline || '';
        document.getElementById('editAppInterviewDate').value = app.interview_date ? app.interview_date.replace(' ', 'T') : '';
        document.getElementById('editAppSalary').value = app.salary_offered || '';
        document.getElementById('editAppNotes').value = app.notes || '';

        const modal = new bootstrap.Modal(document.getElementById('editApplicationModal'));
        modal.show();
    }

    if (editAppForm) {
        editAppForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const appId = document.getElementById('editAppId').value;
            const payload = {
                company_name: document.getElementById('editAppCompany').value.trim(),
                position_title: document.getElementById('editAppTitle').value.trim(),
                opportunity_type: editAppType.value,
                status: editAppStatus.value,
                deadline: document.getElementById('editAppDeadline').value,
                interview_date: document.getElementById('editAppInterviewDate').value,
                salary_offered: document.getElementById('editAppSalary').value.trim(),
                notes: document.getElementById('editAppNotes').value.trim()
            };

            try {
                await window.api.put(`/applications/${appId}`, payload);
                window.api.showToast('Application updated!', 'success');
                const modal = bootstrap.Modal.getInstance(document.getElementById('editApplicationModal'));
                if (modal) modal.hide();
                loadApplications();
            } catch (err) {}
        });
    }

    // 8. View Application / Submission Details Modal
    function openViewModal(app) {
        const modalEl = document.getElementById('viewApplicationModal');
        if (!modalEl) return;

        const typeBadge = document.getElementById('viewModalTypeBadge');
        const titleEl = document.getElementById('viewModalTitle');
        const companyEl = document.getElementById('viewModalCompany');
        const bodyEl = document.getElementById('viewModalBody');
        const editBtn = document.getElementById('viewModalEditBtn');

        if (typeBadge) typeBadge.textContent = (app.opportunity_type || 'Opportunity').toUpperCase();
        if (titleEl) titleEl.textContent = app.position_title;
        if (companyEl) companyEl.textContent = `${app.company_name} • Current Stage: ${(app.status || 'Applied').replace('_', ' ').toUpperCase()}`;

        const dt = app.submitted_details || {};
        const cand = dt.candidate || {};

        let specificHtml = '';
        if (dt.hackathon_details) {
            const h = dt.hackathon_details;
            specificHtml = `
                <div class="card bg-surface-elevated p-3 border border-subtle mb-3">
                    <h6 class="text-light fw-bold mb-2 small"><i class="bi bi-laptop text-warning me-2"></i>Hackathon Registration Details</h6>
                    <div class="row g-2 small">
                        <div class="col-sm-6"><b>Team Name:</b> <span class="text-light">${h.team_name || 'Solo'}</span> (${h.team_size || 'Individual'})</div>
                        <div class="col-sm-6"><b>Track:</b> <span class="text-info">${h.track || 'General Track'}</span></div>
                        ${h.team_members ? `<div class="col-12"><b>Team Members:</b> <span class="text-secondary">${h.team_members}</span></div>` : ''}
                        ${h.experience ? `<div class="col-sm-6"><b>Experience:</b> <span class="text-secondary">${h.experience}</span></div>` : ''}
                        ${h.tshirt_size ? `<div class="col-sm-6"><b>T-Shirt / Dietary:</b> <span class="text-secondary">${h.tshirt_size} / ${h.dietary_requirements || 'None'}</span></div>` : ''}
                        ${h.project_idea ? `<div class="col-12 mt-2"><b>Project Concept / Pitch:</b><p class="text-light bg-surface-card p-2 rounded mt-1 border border-subtle mb-0">${h.project_idea}</p></div>` : ''}
                    </div>
                </div>
            `;
        } else if (dt.internship_details) {
            const intern = dt.internship_details;
            specificHtml = `
                <div class="card bg-surface-elevated p-3 border border-subtle mb-3">
                    <h6 class="text-light fw-bold mb-2 small"><i class="bi bi-send-check text-primary me-2"></i>Internship Application Details</h6>
                    <div class="row g-2 small">
                        <div class="col-sm-6"><b>Availability:</b> <span class="text-light">${intern.availability || 'Immediate'}</span></div>
                        <div class="col-sm-6"><b>Work Mode:</b> <span class="text-light">${intern.preferred_work_mode || 'Flexible'} (${intern.preferred_location || 'Remote'})</span></div>
                        ${intern.relevant_projects ? `<div class="col-12"><b>Relevant Projects:</b> <span class="text-secondary">${intern.relevant_projects}</span></div>` : ''}
                        ${intern.cover_note ? `<div class="col-12 mt-2"><b>Cover Note / Motivation:</b><p class="text-light bg-surface-card p-2 rounded mt-1 border border-subtle mb-0">${intern.cover_note}</p></div>` : ''}
                    </div>
                </div>
            `;
        } else if (dt.job_details) {
            const j = dt.job_details;
            specificHtml = `
                <div class="card bg-surface-elevated p-3 border border-subtle mb-3">
                    <h6 class="text-light fw-bold mb-2 small"><i class="bi bi-briefcase text-info me-2"></i>Job Application Details</h6>
                    <div class="row g-2 small">
                        <div class="col-sm-6"><b>Experience:</b> <span class="text-light">${j.experience_years || 'Entry Level'}</span></div>
                        <div class="col-sm-6"><b>Notice Period:</b> <span class="text-light">${j.notice_period || 'Immediate'}</span></div>
                        <div class="col-sm-6"><b>Location Preference:</b> <span class="text-light">${j.preferred_location || 'Flexible'}</span></div>
                        ${j.expected_salary ? `<div class="col-sm-6"><b>Expected Comp:</b> <span class="text-emerald">${j.expected_salary}</span></div>` : ''}
                        ${j.previous_roles ? `<div class="col-12"><b>Previous Experience:</b> <span class="text-secondary">${j.previous_roles}</span></div>` : ''}
                        ${j.cover_letter ? `<div class="col-12 mt-2"><b>Cover Letter:</b><p class="text-light bg-surface-card p-2 rounded mt-1 border border-subtle mb-0">${j.cover_letter}</p></div>` : ''}
                    </div>
                </div>
            `;
        } else if (dt.competition_details) {
            const comp = dt.competition_details;
            specificHtml = `
                <div class="card bg-surface-elevated p-3 border border-subtle mb-3">
                    <h6 class="text-light fw-bold mb-2 small"><i class="bi bi-trophy text-warning me-2"></i>Competition Entry Details</h6>
                    <div class="row g-2 small">
                        <div class="col-sm-6"><b>Team / Handle:</b> <span class="text-light">${comp.team_name || 'Solo'}</span></div>
                        <div class="col-sm-6"><b>Track / Division:</b> <span class="text-info">${comp.track || 'Open'}</span></div>
                        ${comp.experience ? `<div class="col-12"><b>Contest Rankings:</b> <span class="text-secondary">${comp.experience}</span></div>` : ''}
                        ${comp.strategy_pitch ? `<div class="col-12 mt-2"><b>Strategy Overview:</b><p class="text-light bg-surface-card p-2 rounded mt-1 border border-subtle mb-0">${comp.strategy_pitch}</p></div>` : ''}
                    </div>
                </div>
            `;
        }

        // Resume button if available
        let resumeHtml = '';
        if (app.resume_url) {
            resumeHtml = `
                <div class="p-3 bg-surface-elevated rounded border border-subtle d-flex justify-content-between align-items-center mb-3">
                    <div>
                        <small class="text-muted d-block" style="font-size: 0.72rem;">ATTACHED RESUME</small>
                        <span class="text-light small fw-medium"><i class="bi bi-file-earmark-pdf text-danger me-1"></i>${app.resume_filename === 'ai_generated' ? 'Career DNA AI Verified Resume' : (app.resume_filename || 'Uploaded Resume')}</span>
                    </div>
                    <a href="${app.resume_url}" target="_blank" class="btn btn-sm btn-gradient-primary">
                        <i class="bi bi-file-earmark-arrow-down me-1"></i>View / Download Resume
                    </a>
                </div>
            `;
        }

        bodyEl.innerHTML = `
            <!-- Top Status Bar -->
            <div class="row g-2 mb-3">
                <div class="col-sm-4">
                    <div class="p-2 bg-surface-elevated rounded border border-subtle">
                        <small class="text-muted d-block" style="font-size: 0.7rem;">STATUS / STAGE</small>
                        <span class="badge badge-emerald-subtle text-uppercase">${(app.status || 'Applied').replace('_', ' ')}</span>
                    </div>
                </div>
                <div class="col-sm-4">
                    <div class="p-2 bg-surface-elevated rounded border border-subtle">
                        <small class="text-muted d-block" style="font-size: 0.7rem;">APPLIED DATE</small>
                        <span class="text-light small">${app.applied_date || 'N/A'}</span>
                    </div>
                </div>
                <div class="col-sm-4">
                    <div class="p-2 bg-surface-elevated rounded border border-subtle">
                        <small class="text-muted d-block" style="font-size: 0.7rem;">DEADLINE / EVENT</small>
                        <span class="text-warning small">${app.deadline || app.interview_date || 'None'}</span>
                    </div>
                </div>
            </div>

            ${resumeHtml}

            <!-- Applicant Snapshot if registered via platform -->
            ${cand.full_name ? `
                <div class="card bg-surface-card p-3 border border-subtle mb-3">
                    <h6 class="text-light fw-bold mb-2 small"><i class="bi bi-person-badge text-primary me-2"></i>Applicant Snapshot</h6>
                    <div class="row g-2 small">
                        <div class="col-sm-6"><b>Name:</b> <span class="text-light">${cand.full_name}</span></div>
                        <div class="col-sm-6"><b>Email:</b> <span class="text-secondary">${cand.email}</span></div>
                        <div class="col-sm-6"><b>Phone:</b> <span class="text-secondary">${cand.phone || 'N/A'}</span></div>
                        <div class="col-sm-6"><b>College:</b> <span class="text-secondary">${cand.college_name || 'N/A'}</span></div>
                        ${cand.skills && cand.skills.length ? `<div class="col-12"><b>Skills:</b> <div class="d-inline-flex flex-wrap gap-1 ms-1">${cand.skills.map(s => `<span class="badge badge-primary-subtle py-0 px-2" style="font-size: 0.7rem;">${s}</span>`).join('')}</div></div>` : ''}
                    </div>
                </div>
            ` : ''}

            ${specificHtml}

            ${app.notes ? `
                <div class="card bg-surface-elevated p-3 border border-subtle mb-0">
                    <h6 class="text-light fw-bold mb-1 small"><i class="bi bi-card-text text-secondary me-2"></i>Notes & Details</h6>
                    <p class="text-secondary small mb-0">${app.notes}</p>
                </div>
            ` : ''}
        `;

        if (editBtn) {
            editBtn.onclick = () => {
                const viewModalInstance = bootstrap.Modal.getInstance(modalEl);
                if (viewModalInstance) viewModalInstance.hide();
                openEditModal(app);
            };
        }

        const modal = new bootstrap.Modal(modalEl);
        modal.show();
    }

    loadApplications();
});
