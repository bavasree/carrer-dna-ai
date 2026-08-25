/**
 * Opportunity Recommendations & Explorer Module
 * Real-World Opportunity-Specific Registration and Application Engine
 */

document.addEventListener('DOMContentLoaded', () => {
    let currentFilters = {
        type: 'all',
        is_remote: '',
        query: '',
        sort_by: 'match_desc'
    };

    let loadedOpportunities = [];
    let cachedStudentProfile = null;

    const container = document.getElementById('opportunitiesGrid');
    const searchInput = document.getElementById('searchQueryInput');
    const typeFilterPills = document.querySelectorAll('.type-filter-pill');
    const remoteCheckbox = document.getElementById('remoteOnlyCheckbox');
    const sortSelect = document.getElementById('sortSelect');
    const resultCountEl = document.getElementById('oppResultCount');

    // Read query params from URL if any
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('type')) {
        currentFilters.type = urlParams.get('type');
        typeFilterPills.forEach(p => {
            if (p.getAttribute('data-type') === currentFilters.type) {
                p.classList.add('active', 'btn-gradient-primary');
                p.classList.remove('btn-glass');
            } else {
                p.classList.remove('active', 'btn-gradient-primary');
                p.classList.add('btn-glass');
            }
        });
    }

    if (urlParams.get('query')) {
        currentFilters.query = urlParams.get('query').trim();
        if (searchInput) searchInput.value = currentFilters.query;
    }

    async function loadOpportunities() {
        if (!container) return;
        container.innerHTML = `
            <div class="col-12 py-5 text-center">
                <div class="spinner-border text-primary" role="status"></div>
                <p class="text-secondary mt-2 small">Finding matching opportunities tailored to your skills...</p>
            </div>
        `;

        try {
            const params = new URLSearchParams();
            if (currentFilters.type && currentFilters.type !== 'all') params.append('type', currentFilters.type);
            if (currentFilters.is_remote !== '') params.append('is_remote', currentFilters.is_remote);
            if (currentFilters.query) params.append('query', currentFilters.query);
            if (currentFilters.sort_by) params.append('sort_by', currentFilters.sort_by);

            const res = await window.api.get(`/recommendations?${params.toString()}`);
            loadedOpportunities = res.data.opportunities || [];

            if (resultCountEl) {
                resultCountEl.innerHTML = `<span><b>${loadedOpportunities.length}</b> Opportunities Found</span>` + 
                    (currentFilters.query ? `<span class="badge bg-primary-subtle border border-primary text-light ms-2">Keyword: "${currentFilters.query}" <button type="button" class="btn-close btn-close-white ms-1" id="removeQueryTagBtn" style="font-size: 0.6rem; vertical-align: middle;"></button></span>` : '');
                
                const removeTagBtn = document.getElementById('removeQueryTagBtn');
                if (removeTagBtn) {
                    removeTagBtn.addEventListener('click', () => {
                        currentFilters.query = '';
                        if (searchInput) searchInput.value = '';
                        const newUrl = new URL(window.location);
                        newUrl.searchParams.delete('query');
                        window.history.replaceState({}, '', newUrl);
                        loadOpportunities();
                    });
                }
            }

            if (loadedOpportunities.length === 0) {
                container.innerHTML = `
                    <div class="col-12">
                        <div class="empty-state p-5 text-center">
                            <div class="empty-state-icon"><i class="bi bi-search"></i></div>
                            <h5 class="text-light fw-bold">No Opportunities Found</h5>
                            <p class="text-muted small">No active opportunities match the selected filters or search query "${currentFilters.query || ''}".</p>
                            <button class="btn btn-gradient-primary mt-2" id="clearFiltersBtn"><i class="bi bi-arrow-counterclockwise me-1"></i>Reset All Filters</button>
                        </div>
                    </div>
                `;
                const clearBtn = document.getElementById('clearFiltersBtn');
                if (clearBtn) clearBtn.addEventListener('click', resetFilters);
                return;
            }

            container.innerHTML = loadedOpportunities.map(opp => renderOpportunityCard(opp)).join('');
            attachCardEventListeners();

        } catch (err) {
            container.innerHTML = `<div class="col-12"><div class="alert alert-danger">Error loading opportunities. Please try again.</div></div>`;
        }
    }

    function getTypeActionMeta(oppType) {
        switch ((oppType || '').toLowerCase()) {
            case 'hackathon':
                return {
                    label: 'Register for Hackathon',
                    icon: 'bi-laptop',
                    initialStage: 'Registered'
                };
            case 'competition':
                return {
                    label: 'Register for Competition',
                    icon: 'bi-trophy',
                    initialStage: 'Registered'
                };
            case 'internship':
                return {
                    label: 'Apply for Internship',
                    icon: 'bi-send-check',
                    initialStage: 'Applied'
                };
            case 'job':
                return {
                    label: 'Apply for Job',
                    icon: 'bi-briefcase',
                    initialStage: 'Applied'
                };
            case 'certification':
                return {
                    label: 'Enroll in Certification',
                    icon: 'bi-patch-check',
                    initialStage: 'Enrolled'
                };
            case 'course':
                return {
                    label: 'Enroll in Course',
                    icon: 'bi-journal-bookmark',
                    initialStage: 'Enrolled'
                };
            default:
                return {
                    label: 'Register / Apply Now',
                    icon: 'bi-arrow-right-circle',
                    initialStage: 'Registered'
                };
        }
    }

    function renderOpportunityCard(opp) {
        const typeBadgeStyles = {
            internship: 'badge-primary-subtle',
            hackathon: 'badge-amber-subtle',
            certification: 'badge-emerald-subtle',
            course: 'badge-cyan-subtle',
            competition: 'badge-rose-subtle',
            job: 'badge-primary-subtle'
        };

        const scoreClass = opp.match_score >= 80 ? 'match-high' : opp.match_score >= 60 ? 'match-mid' : '';

        // Calculate days remaining
        let deadlineLabel = 'Ongoing';
        let deadlineBadge = '';
        if (opp.deadline) {
            const deadlineDate = new Date(opp.deadline);
            const now = new Date();
            const diffTime = deadlineDate - now;
            const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
            
            if (diffDays > 0) {
                deadlineLabel = `${diffDays} days left`;
                deadlineBadge = diffDays <= 7 ? `<span class="badge bg-danger-subtle border border-danger text-light py-0 px-2 small ms-1"><i class="bi bi-fire text-danger me-1"></i>Closing Soon</span>` : '';
            } else if (diffDays === 0) {
                deadlineLabel = 'Ends Today';
                deadlineBadge = `<span class="badge bg-danger-subtle border border-danger text-light py-0 px-2 small ms-1">Ends Today</span>`;
            }
        }

        const actionMeta = getTypeActionMeta(opp.opportunity_type);

        // Action button based on application status
        let actionBtnHtml = '';
        if (opp.is_applied) {
            const stageLabel = (opp.application_status || 'Registered').replace('_', ' ').toUpperCase();
            actionBtnHtml = `
                <button class="btn btn-sm btn-glass text-emerald flex-grow-1" disabled>
                    <i class="bi bi-check2-circle me-1"></i>${stageLabel}
                </button>
                <a href="/applications" class="btn btn-sm btn-glass" title="View in Application Tracker">
                    <i class="bi bi-kanban"></i>
                </a>
            `;
        } else {
            actionBtnHtml = `
                <button class="btn btn-sm btn-gradient-primary flex-grow-1 apply-now-btn" data-id="${opp.id}">
                    <i class="bi ${actionMeta.icon} me-1"></i>${actionMeta.label}
                </button>
            `;
        }

        return `
            <div class="col-md-6 col-xl-4 mb-4">
                <div class="card bg-surface-card h-100 p-3 d-flex flex-column justify-content-between">
                    <div>
                        <!-- Header Row -->
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <span class="badge badge-pill ${typeBadgeStyles[opp.opportunity_type] || 'badge-primary-subtle'} text-uppercase" style="font-size: 0.7rem;">
                                ${opp.opportunity_type}
                            </span>
                            <div class="d-flex align-items-center gap-2">
                                <span class="match-score-badge ${scoreClass}">
                                    <i class="bi bi-stars"></i> ${opp.match_score}%
                                </span>
                                <button class="btn btn-link text-secondary p-0 bookmark-btn" data-id="${opp.id}" data-saved="${opp.is_saved}" title="${opp.is_saved ? 'Remove Bookmark' : 'Bookmark'}">
                                    <i class="bi ${opp.is_saved ? 'bi-bookmark-fill text-primary' : 'bi-bookmark'} fs-5"></i>
                                </button>
                            </div>
                        </div>

                        <!-- Title & Company -->
                        <h5 class="text-light fw-bold mb-1" style="font-size: 1.05rem;">${opp.title}</h5>
                        <div class="small text-secondary mb-3">
                            <span class="text-light fw-medium"><i class="bi bi-building me-1"></i>${opp.company_name}</span> &bull; 
                            <span><i class="bi bi-geo-alt me-1"></i>${opp.location}</span>
                        </div>

                        <!-- Description Snippet -->
                        <p class="text-secondary small mb-3" style="display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">
                            ${opp.description}
                        </p>

                        <!-- Required Skills Tags -->
                        <div class="mb-3">
                            <small class="text-muted d-block mb-1" style="font-size: 0.72rem;">REQUIRED SKILLS</small>
                            <div class="d-flex flex-wrap gap-1">
                                ${(opp.required_skills || []).slice(0, 4).map(s => {
                                    const isMatched = (opp.matched_skills || []).map(ms => ms.toLowerCase()).includes(s.toLowerCase());
                                    return `<span class="badge ${isMatched ? 'badge-emerald-subtle' : 'badge-primary-subtle'}" style="font-size: 0.7rem;">${isMatched ? '<i class="bi bi-check-lg me-1"></i>' : ''}${s}</span>`;
                                }).join('')}
                                ${(opp.required_skills || []).length > 4 ? `<span class="badge bg-surface-elevated text-muted" style="font-size: 0.7rem;">+${opp.required_skills.length - 4}</span>` : ''}
                            </div>
                        </div>
                    </div>

                    <!-- Card Footer -->
                    <div class="pt-3 border-top border-subtle">
                        <div class="d-flex justify-content-between align-items-center mb-2 small text-muted">
                            <span><i class="bi bi-cash-stack me-1"></i>${opp.stipend_salary || 'Competitive'}</span>
                            <span><i class="bi bi-clock me-1"></i>${deadlineLabel} ${deadlineBadge}</span>
                        </div>
                        <div class="d-flex gap-2">
                            <button class="btn btn-sm btn-glass details-btn" data-id="${opp.id}" title="Match Breakdown">
                                <i class="bi bi-info-circle"></i>
                            </button>
                            ${actionBtnHtml}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    function attachCardEventListeners() {
        // Bookmarks
        document.querySelectorAll('.bookmark-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                e.preventDefault();
                if (!window.api.isAuthenticated()) {
                    window.location.href = '/login';
                    return;
                }
                const id = btn.getAttribute('data-id');
                const isSaved = btn.getAttribute('data-saved') === 'true';

                try {
                    if (isSaved) {
                        await window.api.delete(`/recommendations/${id}/save`);
                        btn.setAttribute('data-saved', 'false');
                        btn.innerHTML = '<i class="bi bi-bookmark fs-5"></i>';
                        window.api.showToast('Bookmark removed', 'info');
                    } else {
                        await window.api.post(`/recommendations/${id}/save`);
                        btn.setAttribute('data-saved', 'true');
                        btn.innerHTML = '<i class="bi bi-bookmark-fill text-primary fs-5"></i>';
                        window.api.showToast('Opportunity bookmarked!', 'success');
                    }
                } catch (err) {}
            });
        });

        // Details Modal
        document.querySelectorAll('.details-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const id = btn.getAttribute('data-id');
                openDetailsModal(id);
            });
        });

        // Apply / Register Trigger
        document.querySelectorAll('.apply-now-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const id = btn.getAttribute('data-id');
                const opp = loadedOpportunities.find(o => o.id == id);
                if (opp) openOpportunityApplicationModal(opp);
            });
        });
    }

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
                college_name: 'University Student',
                degree: 'B.Tech / B.E.',
                branch: 'Computer Science & Engineering',
                graduation_year: 2026,
                skills: ['Python', 'Data Structures & Algorithms', 'Problem Solving']
            };
        }
    }

    // =========================================================================
    // Opportunity-Specific Real-World Registration Form Renderers
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

        bodyContent.innerHTML = `<div class="p-5 text-center"><div class="spinner-border text-primary"></div><p class="text-secondary small mt-2">Loading application form...</p></div>`;

        const modal = new bootstrap.Modal(modalEl);
        modal.show();

        const profile = await fetchStudentProfileSnapshot();
        const userObj = profile.user || {};
        const fullName = profile.full_name || userObj.full_name || 'Student';
        const email = userObj.email || '';
        const phone = profile.phone || '';
        const college = profile.college_name || '';
        const degree = profile.degree || '';
        const branch = profile.branch || '';
        const year = profile.graduation_year || 2026;
        const cgpa = profile.cgpa || '';
        const github = profile.github_url || '';
        const linkedin = profile.linkedin_url || '';
        const portfolio = profile.portfolio_url || '';
        const skillsList = (profile.skills || []).map(s => (typeof s === 'string' ? s : (s.skill_name || s.name || ''))).filter(Boolean);

        const oppType = (opp.opportunity_type || 'job').toLowerCase();
        const actionMeta = getTypeActionMeta(oppType);

        if (modalTitle) modalTitle.textContent = `${actionMeta.label} — ${opp.title}`;
        if (modalCompany) modalCompany.textContent = `${opp.company_name} • ${opp.location || 'Remote'}`;
        if (typeBadge) typeBadge.textContent = oppType.toUpperCase();

        // Opportunity Header Banner
        const oppSummaryBanner = `
            <div class="card bg-surface-elevated p-3 border border-subtle mb-4">
                <div class="row g-2 align-items-center">
                    <div class="col-md-4">
                        <small class="text-muted d-block" style="font-size: 0.72rem;">ORGANIZATION / HOST</small>
                        <span class="text-light fw-bold small"><i class="bi bi-building me-1 text-primary"></i>${opp.company_name}</span>
                    </div>
                    <div class="col-md-3">
                        <small class="text-muted d-block" style="font-size: 0.72rem;">COMPENSATION / PRIZE</small>
                        <span class="text-emerald fw-semibold small"><i class="bi bi-cash-stack me-1"></i>${opp.stipend_salary || 'Competitive'}</span>
                    </div>
                    <div class="col-md-3">
                        <small class="text-muted d-block" style="font-size: 0.72rem;">APPLICATION DEADLINE</small>
                        <span class="text-warning fw-semibold small"><i class="bi bi-clock me-1"></i>${opp.deadline || 'Ongoing / Open'}</span>
                    </div>
                    <div class="col-md-2 text-md-end">
                        <a href="${opp.apply_url}" target="_blank" class="btn btn-sm btn-glass text-primary" title="Visit actual opportunity website">
                            Official Site <i class="bi bi-box-arrow-up-right ms-1"></i>
                        </a>
                    </div>
                </div>
            </div>
            <div id="applyFormErrorAlert" class="alert alert-danger d-none mb-3"></div>
        `;

        // Render type-specific form HTML
        let formHtml = '';
        if (oppType === 'hackathon') {
            formHtml = renderHackathonFormHtml(opp, fullName, email, phone, college, branch, year, github, linkedin, portfolio, skillsList);
        } else if (oppType === 'internship') {
            formHtml = renderInternshipFormHtml(opp, fullName, email, phone, college, degree, branch, year, cgpa, github, linkedin, portfolio, skillsList);
        } else if (oppType === 'job') {
            formHtml = renderJobFormHtml(opp, fullName, email, phone, college, degree, branch, year, github, linkedin, portfolio, skillsList);
        } else if (oppType === 'competition') {
            formHtml = renderCompetitionFormHtml(opp, fullName, email, phone, college, branch, year, skillsList);
        } else {
            formHtml = renderCourseCertificationFormHtml(opp, fullName, email, phone, college, skillsList);
        }

        bodyContent.innerHTML = oppSummaryBanner + formHtml;
        attachFormSubmitHandler(opp, modal);
    }

    // 1. Hackathon Registration Form HTML
    function renderHackathonFormHtml(opp, fullName, email, phone, college, branch, year, github, linkedin, portfolio, skillsList) {
        return `
            <form id="realWorldApplicationForm" enctype="multipart/form-data">
                <input type="hidden" name="opportunity_id" value="${opp.id}">
                <input type="hidden" name="opportunity_type" value="hackathon">

                <!-- Section 1: Hacker / Applicant Identity -->
                <div class="mb-4">
                    <h6 class="text-light fw-bold mb-3 border-bottom border-subtle pb-2">
                        <i class="bi bi-person-fill text-primary me-2"></i>1. Participant Details
                    </h6>
                    <div class="row g-3">
                        <div class="col-md-6">
                            <label class="form-label">Full Name *</label>
                            <input type="text" name="full_name" class="form-control" value="${fullName}" required>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Email Address *</label>
                            <input type="email" name="email" class="form-control" value="${email}" required>
                        </div>
                        <div class="col-md-4">
                            <label class="form-label">Phone Number *</label>
                            <input type="tel" name="phone" class="form-control" value="${phone}" placeholder="+1 (555) 000-0000" required>
                        </div>
                        <div class="col-md-5">
                            <label class="form-label">College / University *</label>
                            <input type="text" name="college_name" class="form-control" value="${college}" placeholder="e.g. Stanford University" required>
                        </div>
                        <div class="col-md-3">
                            <label class="form-label">Graduation Year *</label>
                            <select name="year_of_study" class="form-select">
                                <option value="2025" ${year == 2025 ? 'selected' : ''}>2025</option>
                                <option value="2026" ${year == 2026 ? 'selected' : ''}>2026</option>
                                <option value="2027" ${year == 2027 ? 'selected' : ''}>2027</option>
                                <option value="2028" ${year == 2028 ? 'selected' : ''}>2028</option>
                                <option value="2029" ${year == 2029 ? 'selected' : ''}>2029+</option>
                            </select>
                        </div>
                    </div>
                </div>

                <!-- Section 2: Team Configuration -->
                <div class="mb-4">
                    <h6 class="text-light fw-bold mb-3 border-bottom border-subtle pb-2">
                        <i class="bi bi-people-fill text-warning me-2"></i>2. Team & Participation Mode
                    </h6>
                    <div class="row g-3">
                        <div class="col-md-6">
                            <label class="form-label">Team Name *</label>
                            <input type="text" name="team_name" class="form-control" placeholder="e.g. Team NeuroByte (or Solo / Individual)" required>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Team Size *</label>
                            <select name="team_size" class="form-select">
                                <option value="Individual (1 Person)">Individual (1 Person)</option>
                                <option value="2 Members" selected>2 Members</option>
                                <option value="3 Members">3 Members</option>
                                <option value="4 Members">4 Members</option>
                                <option value="5+ Members">5+ Members</option>
                            </select>
                        </div>
                        <div class="col-12">
                            <label class="form-label">Team Members Details (Names, Emails, & Roles)</label>
                            <textarea name="team_members" class="form-control" rows="2" placeholder="e.g. Alex Morgan (Frontend/AI), John Doe (Backend API), Sarah Lee (UI/UX)"></textarea>
                        </div>
                    </div>
                </div>

                <!-- Section 3: Experience, Track & Project Concept -->
                <div class="mb-4">
                    <h6 class="text-light fw-bold mb-3 border-bottom border-subtle pb-2">
                        <i class="bi bi-laptop text-info me-2"></i>3. Hackathon Track & Project Pitch
                    </h6>
                    <div class="row g-3">
                        <div class="col-md-6">
                            <label class="form-label">Previous Hackathon Experience</label>
                            <select name="hackathon_experience" class="form-select">
                                <option value="First-Time Hacker">First-Time Hacker (Excited to build!)</option>
                                <option value="1-2 Hackathons" selected>1-2 Hackathons</option>
                                <option value="3-5 Hackathons">3-5 Hackathons</option>
                                <option value="Veteran Hacker (5+ Hackathons)">Veteran Hacker (5+ Hackathons)</option>
                            </select>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Preferred Project Track / Category *</label>
                            <select name="project_track" class="form-select">
                                <option value="AI & Machine Learning" selected>AI & Intelligent Agents</option>
                                <option value="Full-Stack & Cloud Apps">Full-Stack & Cloud Applications</option>
                                <option value="Web3 & Decentralized Systems">Web3 & Decentralized Systems</option>
                                <option value="Healthcare & BioTech">HealthTech & Social Good</option>
                                <option value="Developer Tools & Productivity">Developer Tools & Productivity</option>
                                <option value="Open Innovation">Open Innovation Track</option>
                            </select>
                        </div>
                        <div class="col-12">
                            <label class="form-label">Project Concept / Problem You Plan to Solve *</label>
                            <textarea name="project_idea" class="form-control" rows="3" placeholder="Describe the problem you're tackling, the intended tech stack, and what you aim to ship during the hackathon..." required></textarea>
                        </div>
                    </div>
                </div>

                <!-- Section 4: Profiles & Preferences -->
                <div class="mb-4">
                    <h6 class="text-light fw-bold mb-3 border-bottom border-subtle pb-2">
                        <i class="bi bi-link-45deg text-success me-2"></i>4. Links & Logistics
                    </h6>
                    <div class="row g-3">
                        <div class="col-md-4">
                            <label class="form-label">GitHub Profile</label>
                            <input type="url" name="github_url" class="form-control" value="${github}" placeholder="https://github.com/...">
                        </div>
                        <div class="col-md-4">
                            <label class="form-label">LinkedIn Profile</label>
                            <input type="url" name="linkedin_url" class="form-control" value="${linkedin}" placeholder="https://linkedin.com/in/...">
                        </div>
                        <div class="col-md-4">
                            <label class="form-label">Portfolio / Devpost URL</label>
                            <input type="url" name="portfolio_url" class="form-control" value="${portfolio}" placeholder="https://myportfolio.dev">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">T-Shirt Size</label>
                            <select name="tshirt_size" class="form-select">
                                <option value="M" selected>Unisex M</option>
                                <option value="S">Unisex S</option>
                                <option value="L">Unisex L</option>
                                <option value="XL">Unisex XL</option>
                            </select>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Dietary / Special Requirements</label>
                            <input type="text" name="dietary_requirements" class="form-control" placeholder="e.g. Vegetarian, Halal, None">
                        </div>
                    </div>
                </div>

                <!-- Footer Actions -->
                <div class="modal-footer border-subtle px-0 pb-0 pt-3">
                    <button type="button" class="btn btn-glass" data-bs-dismiss="modal">Cancel</button>
                    <button type="submit" class="btn btn-gradient-primary" id="formSubmitBtn">
                        <i class="bi bi-laptop me-1"></i>Confirm & Submit Hackathon Registration
                    </button>
                </div>
            </form>
        `;
    }

    // 2. Internship Application Form HTML
    function renderInternshipFormHtml(opp, fullName, email, phone, college, degree, branch, year, cgpa, github, linkedin, portfolio, skillsList) {
        return `
            <form id="realWorldApplicationForm" enctype="multipart/form-data">
                <input type="hidden" name="opportunity_id" value="${opp.id}">
                <input type="hidden" name="opportunity_type" value="internship">

                <!-- Section 1: Candidate Background -->
                <div class="mb-4">
                    <h6 class="text-light fw-bold mb-3 border-bottom border-subtle pb-2">
                        <i class="bi bi-person-fill text-primary me-2"></i>1. Personal & Academic Information
                    </h6>
                    <div class="row g-3">
                        <div class="col-md-6">
                            <label class="form-label">Full Name *</label>
                            <input type="text" name="full_name" class="form-control" value="${fullName}" required>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Email Address *</label>
                            <input type="email" name="email" class="form-control" value="${email}" required>
                        </div>
                        <div class="col-md-4">
                            <label class="form-label">Phone Number *</label>
                            <input type="tel" name="phone" class="form-control" value="${phone}" placeholder="+1 (555) 000-0000" required>
                        </div>
                        <div class="col-md-4">
                            <label class="form-label">College / University *</label>
                            <input type="text" name="college_name" class="form-control" value="${college}" required>
                        </div>
                        <div class="col-md-4">
                            <label class="form-label">Degree & Major *</label>
                            <input type="text" name="department" class="form-control" value="${degree ? degree + ' - ' + branch : branch}" placeholder="e.g. B.S. Computer Science" required>
                        </div>
                        <div class="col-md-4">
                            <label class="form-label">Graduation Year *</label>
                            <input type="number" name="year_of_study" class="form-control" value="${year}" min="2025" max="2030" required>
                        </div>
                        <div class="col-md-4">
                            <label class="form-label">Current CGPA / GPA</label>
                            <input type="text" name="cgpa" class="form-control" value="${cgpa}" placeholder="e.g. 3.8 / 4.0 or 8.9 / 10">
                        </div>
                        <div class="col-md-4">
                            <label class="form-label">Core Skills (comma separated) *</label>
                            <input type="text" name="skills" class="form-control" value="${skillsList.join(', ')}" required>
                        </div>
                    </div>
                </div>

                <!-- Section 2: Resume & Professional Links -->
                <div class="mb-4">
                    <h6 class="text-light fw-bold mb-3 border-bottom border-subtle pb-2">
                        <i class="bi bi-file-earmark-person-fill text-info me-2"></i>2. Resume & Portfolio
                    </h6>
                    <div class="row g-3">
                        <div class="col-md-6">
                            <label class="form-label">Upload Resume (PDF or DOCX)</label>
                            <input type="file" name="resume_file" class="form-control" accept=".pdf,.docx,.doc">
                            <small class="text-muted">Upload your tailored PDF resume (max 10MB)</small>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Or Select Platform Resume</label>
                            <div class="form-check mt-2">
                                <input class="form-check-input" type="checkbox" name="resume_source" value="ai_generated" id="useAiResumeCheck" checked>
                                <label class="form-check-label text-light small" for="useAiResumeCheck">
                                    <i class="bi bi-stars text-primary me-1"></i>Attach my verified Career DNA AI Resume
                                </label>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <label class="form-label">GitHub Profile</label>
                            <input type="url" name="github_url" class="form-control" value="${github}" placeholder="https://github.com/username">
                        </div>
                        <div class="col-md-4">
                            <label class="form-label">LinkedIn Profile</label>
                            <input type="url" name="linkedin_url" class="form-control" value="${linkedin}" placeholder="https://linkedin.com/in/username">
                        </div>
                        <div class="col-md-4">
                            <label class="form-label">Portfolio / Project Demo</label>
                            <input type="url" name="portfolio_url" class="form-control" value="${portfolio}" placeholder="https://mywebsite.com">
                        </div>
                    </div>
                </div>

                <!-- Section 3: Availability & Work Preferences -->
                <div class="mb-4">
                    <h6 class="text-light fw-bold mb-3 border-bottom border-subtle pb-2">
                        <i class="bi bi-geo-alt-fill text-warning me-2"></i>3. Availability & Preferences
                    </h6>
                    <div class="row g-3">
                        <div class="col-md-4">
                            <label class="form-label">Internship Availability *</label>
                            <select name="availability" class="form-select">
                                <option value="Immediate" selected>Immediate / Right Away</option>
                                <option value="Within 15 Days">Within 15 Days</option>
                                <option value="Next Month">Next Month</option>
                                <option value="Summer 2026">Summer 2026</option>
                                <option value="6-Month Co-op">6-Month Co-op</option>
                            </select>
                        </div>
                        <div class="col-md-4">
                            <label class="form-label">Preferred Work Mode *</label>
                            <select name="preferred_work_mode" class="form-select">
                                <option value="Remote" ${opp.is_remote ? 'selected' : ''}>Remote</option>
                                <option value="Hybrid">Hybrid</option>
                                <option value="In-Office">In-Office / On-Site</option>
                                <option value="Flexible">Flexible / Open to Any</option>
                            </select>
                        </div>
                        <div class="col-md-4">
                            <label class="form-label">Preferred Location</label>
                            <input type="text" name="preferred_location" class="form-control" value="${opp.location || 'Remote'}" placeholder="e.g. Remote, New York, Bangalore">
                        </div>
                        <div class="col-12">
                            <label class="form-label">Key Relevant Projects</label>
                            <textarea name="relevant_projects" class="form-control" rows="2" placeholder="List 1-2 projects demonstrating skills matching this internship..."></textarea>
                        </div>
                        <div class="col-12">
                            <label class="form-label">Cover Note / Why are you a great fit? *</label>
                            <textarea name="cover_note" class="form-control" rows="3" placeholder="Highlight why you want to intern at ${opp.company_name} and how your background aligns with this role..." required></textarea>
                        </div>
                    </div>
                </div>

                <!-- Footer Actions -->
                <div class="modal-footer border-subtle px-0 pb-0 pt-3">
                    <button type="button" class="btn btn-glass" data-bs-dismiss="modal">Cancel</button>
                    <button type="submit" class="btn btn-gradient-primary" id="formSubmitBtn">
                        <i class="bi bi-send-check me-1"></i>Confirm & Submit Internship Application
                    </button>
                </div>
            </form>
        `;
    }

    // 3. Full-Time Job Application Form HTML
    function renderJobFormHtml(opp, fullName, email, phone, college, degree, branch, year, github, linkedin, portfolio, skillsList) {
        return `
            <form id="realWorldApplicationForm" enctype="multipart/form-data">
                <input type="hidden" name="opportunity_id" value="${opp.id}">
                <input type="hidden" name="opportunity_type" value="job">

                <!-- Section 1: Candidate Identity -->
                <div class="mb-4">
                    <h6 class="text-light fw-bold mb-3 border-bottom border-subtle pb-2">
                        <i class="bi bi-person-fill text-primary me-2"></i>1. Candidate Information
                    </h6>
                    <div class="row g-3">
                        <div class="col-md-6">
                            <label class="form-label">Full Name *</label>
                            <input type="text" name="full_name" class="form-control" value="${fullName}" required>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Email Address *</label>
                            <input type="email" name="email" class="form-control" value="${email}" required>
                        </div>
                        <div class="col-md-4">
                            <label class="form-label">Phone Number *</label>
                            <input type="tel" name="phone" class="form-control" value="${phone}" placeholder="+1 (555) 000-0000" required>
                        </div>
                        <div class="col-md-4">
                            <label class="form-label">Education / University *</label>
                            <input type="text" name="education" class="form-control" value="${college ? college + ' (' + branch + ')' : ''}" placeholder="e.g. B.Tech CS, XYZ University" required>
                        </div>
                        <div class="col-md-4">
                            <label class="form-label">Years of Experience *</label>
                            <select name="work_experience_years" class="form-select">
                                <option value="Fresh Graduate / Entry Level" selected>Fresh Graduate / Entry Level (0-1 yrs)</option>
                                <option value="1-2 Years">1-2 Years Experience</option>
                                <option value="3-5 Years">3-5 Years Experience</option>
                                <option value="5+ Years">5+ Years Senior Experience</option>
                            </select>
                        </div>
                        <div class="col-12">
                            <label class="form-label">Key Technical Skills *</label>
                            <input type="text" name="skills" class="form-control" value="${skillsList.join(', ')}" placeholder="e.g. React, Node.js, Python, PostgreSQL, AWS" required>
                        </div>
                    </div>
                </div>

                <!-- Section 2: Resume & Profiles -->
                <div class="mb-4">
                    <h6 class="text-light fw-bold mb-3 border-bottom border-subtle pb-2">
                        <i class="bi bi-file-earmark-text-fill text-info me-2"></i>2. Resume & Professional Footprint
                    </h6>
                    <div class="row g-3">
                        <div class="col-md-6">
                            <label class="form-label">Upload Resume (PDF / DOCX)</label>
                            <input type="file" name="resume_file" class="form-control" accept=".pdf,.docx,.doc">
                            <small class="text-muted">Upload standard PDF resume</small>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Or Attach Platform Resume</label>
                            <div class="form-check mt-2">
                                <input class="form-check-input" type="checkbox" name="resume_source" value="ai_generated" id="useAiResumeJob" checked>
                                <label class="form-check-label text-light small" for="useAiResumeJob">
                                    <i class="bi bi-stars text-primary me-1"></i>Attach my verified Career DNA AI Resume
                                </label>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <label class="form-label">LinkedIn Profile</label>
                            <input type="url" name="linkedin_url" class="form-control" value="${linkedin}" placeholder="https://linkedin.com/in/...">
                        </div>
                        <div class="col-md-4">
                            <label class="form-label">GitHub Profile</label>
                            <input type="url" name="github_url" class="form-control" value="${github}" placeholder="https://github.com/...">
                        </div>
                        <div class="col-md-4">
                            <label class="form-label">Portfolio / Blog URL</label>
                            <input type="url" name="portfolio_url" class="form-control" value="${portfolio}" placeholder="https://portfolio.me">
                        </div>
                    </div>
                </div>

                <!-- Section 3: Compensation & Logistics -->
                <div class="mb-4">
                    <h6 class="text-light fw-bold mb-3 border-bottom border-subtle pb-2">
                        <i class="bi bi-briefcase-fill text-warning me-2"></i>3. Role Expectations & Logistics
                    </h6>
                    <div class="row g-3">
                        <div class="col-md-4">
                            <label class="form-label">Current Location *</label>
                            <input type="text" name="current_location" class="form-control" placeholder="e.g. San Francisco / Bangalore" required>
                        </div>
                        <div class="col-md-4">
                            <label class="form-label">Notice Period / Availability *</label>
                            <select name="notice_period" class="form-select">
                                <option value="Immediate" selected>Immediate / Under 15 Days</option>
                                <option value="30 Days">30 Days Notice</option>
                                <option value="60 Days">60 Days Notice</option>
                                <option value="90 Days">90 Days Notice</option>
                            </select>
                        </div>
                        <div class="col-md-4">
                            <label class="form-label">Expected Compensation</label>
                            <input type="text" name="expected_salary" class="form-control" value="${opp.stipend_salary || ''}" placeholder="e.g. $90,000/yr or ₹18 LPA">
                        </div>
                        <div class="col-12">
                            <label class="form-label">Previous Work / Internships Experience Summary</label>
                            <textarea name="previous_company_roles" class="form-control" rows="2" placeholder="Brief summary of your most recent roles, organizations, and key accomplishments..."></textarea>
                        </div>
                        <div class="col-12">
                            <label class="form-label">Cover Letter / Message to Hiring Manager *</label>
                            <textarea name="cover_letter" class="form-control" rows="3" placeholder="Introduce yourself and explain why your technical expertise makes you the right fit for this role at ${opp.company_name}..." required></textarea>
                        </div>
                    </div>
                </div>

                <!-- Footer Actions -->
                <div class="modal-footer border-subtle px-0 pb-0 pt-3">
                    <button type="button" class="btn btn-glass" data-bs-dismiss="modal">Cancel</button>
                    <button type="submit" class="btn btn-gradient-primary" id="formSubmitBtn">
                        <i class="bi bi-briefcase me-1"></i>Confirm & Submit Job Application
                    </button>
                </div>
            </form>
        `;
    }

    // 4. Competition Registration Form HTML
    function renderCompetitionFormHtml(opp, fullName, email, phone, college, branch, year, skillsList) {
        return `
            <form id="realWorldApplicationForm" enctype="multipart/form-data">
                <input type="hidden" name="opportunity_id" value="${opp.id}">
                <input type="hidden" name="opportunity_type" value="competition">

                <div class="mb-4">
                    <h6 class="text-light fw-bold mb-3 border-bottom border-subtle pb-2">
                        <i class="bi bi-trophy-fill text-warning me-2"></i>1. Competitor & Team Registration
                    </h6>
                    <div class="row g-3">
                        <div class="col-md-6">
                            <label class="form-label">Primary Competitor Name *</label>
                            <input type="text" name="full_name" class="form-control" value="${fullName}" required>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Email Address *</label>
                            <input type="email" name="email" class="form-control" value="${email}" required>
                        </div>
                        <div class="col-md-4">
                            <label class="form-label">Phone Number *</label>
                            <input type="tel" name="phone" class="form-control" value="${phone}" placeholder="+1 (555) 000-0000" required>
                        </div>
                        <div class="col-md-5">
                            <label class="form-label">College / University *</label>
                            <input type="text" name="college_name" class="form-control" value="${college}" required>
                        </div>
                        <div class="col-md-3">
                            <label class="form-label">Year of Study</label>
                            <input type="text" name="year_of_study" class="form-control" value="${year}">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Team / Handle Name *</label>
                            <input type="text" name="team_name" class="form-control" placeholder="e.g. AlgoWarriors (or Solo)" required>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Competition Track / Division *</label>
                            <input type="text" name="competition_track" class="form-control" value="${opp.title}" required>
                        </div>
                        <div class="col-12">
                            <label class="form-label">Team Members (if applicable)</label>
                            <textarea name="team_members" class="form-control" rows="2" placeholder="List teammate names, emails, and roles if competing as a team..."></textarea>
                        </div>
                        <div class="col-12">
                            <label class="form-label">Relevant Competitive Programming / Contest Rankings</label>
                            <input type="text" name="relevant_experience" class="form-control" placeholder="e.g. LeetCode 1850 rating, Codeforces Specialist, Kaggle Expert, Prior ICPC Regionalist">
                        </div>
                        <div class="col-12">
                            <label class="form-label">Strategy / Approach Statement *</label>
                            <textarea name="strategy_pitch" class="form-control" rows="3" placeholder="Briefly outline your team's strategy and preparation for this competition..." required></textarea>
                        </div>
                    </div>
                </div>

                <div class="modal-footer border-subtle px-0 pb-0 pt-3">
                    <button type="button" class="btn btn-glass" data-bs-dismiss="modal">Cancel</button>
                    <button type="submit" class="btn btn-gradient-primary" id="formSubmitBtn">
                        <i class="bi bi-trophy me-1"></i>Confirm & Register for Competition
                    </button>
                </div>
            </form>
        `;
    }

    // 5. Certification / Course Enrollment Form HTML
    function renderCourseCertificationFormHtml(opp, fullName, email, phone, college, skillsList) {
        return `
            <form id="realWorldApplicationForm" enctype="multipart/form-data">
                <input type="hidden" name="opportunity_id" value="${opp.id}">
                <input type="hidden" name="opportunity_type" value="${opp.opportunity_type || 'certification'}">

                <div class="mb-4">
                    <h6 class="text-light fw-bold mb-3 border-bottom border-subtle pb-2">
                        <i class="bi bi-patch-check-fill text-emerald me-2"></i>1. Student Enrollment Details
                    </h6>
                    <div class="row g-3">
                        <div class="col-md-6">
                            <label class="form-label">Full Name *</label>
                            <input type="text" name="full_name" class="form-control" value="${fullName}" required>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Email Address *</label>
                            <input type="email" name="email" class="form-control" value="${email}" required>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">College / University</label>
                            <input type="text" name="college_name" class="form-control" value="${college}">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Learning Schedule / Commitment *</label>
                            <select name="learning_schedule" class="form-select">
                                <option value="Self-Paced (3-5 hrs/week)" selected>Self-Paced (3-5 hrs/week)</option>
                                <option value="Intensive (10-15 hrs/week)">Intensive (10-15 hrs/week)</option>
                                <option value="Weekend Intensive">Weekend Intensive (6 hrs/weekend)</option>
                            </select>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Target Completion Timeline</label>
                            <input type="text" name="target_completion" class="form-control" placeholder="e.g. 4 Weeks / Next Month">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Prerequisite Skills</label>
                            <input type="text" name="skills" class="form-control" value="${skillsList.slice(0, 4).join(', ')}">
                        </div>
                        <div class="col-12">
                            <label class="form-label">Learning Motivation & Career Goals *</label>
                            <textarea name="motivation" class="form-control" rows="3" placeholder="What key skills do you want to master through this certification and how will you apply them in your career?" required></textarea>
                        </div>
                    </div>
                </div>

                <div class="modal-footer border-subtle px-0 pb-0 pt-3">
                    <button type="button" class="btn btn-glass" data-bs-dismiss="modal">Cancel</button>
                    <button type="submit" class="btn btn-gradient-primary" id="formSubmitBtn">
                        <i class="bi bi-patch-check me-1"></i>Confirm & Enroll Now
                    </button>
                </div>
            </form>
        `;
    }

    // Attach Submission Handler to the rendered form
    function attachFormSubmitHandler(opp, modalInstance) {
        const form = document.getElementById('realWorldApplicationForm');
        if (!form) return;

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
                submitBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-1"></span>Submitting details...`;
            }

            const formData = new FormData(form);

            try {
                // Submit via window.api with multipart support or headers
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
                    throw new Error(resData.message || 'Application submission failed.');
                }

                // Hide apply modal
                modalInstance.hide();

                // Update local opportunity object state
                const targetOpp = loadedOpportunities.find(o => o.id == opp.id);
                if (targetOpp) {
                    targetOpp.is_applied = true;
                    targetOpp.application_status = resData.data.initial_stage || 'Registered';
                }

                // Show Success Confirmation Modal
                showSuccessModal(targetOpp || opp, resData.data.initial_stage);

                // Re-render grid to show updated "Registered" badge on card
                container.innerHTML = loadedOpportunities.map(o => renderOpportunityCard(o)).join('');
                attachCardEventListeners();

            } catch (err) {
                const errMsg = err.message || 'Failed to submit registration.';
                if (errorAlert) {
                    errorAlert.textContent = errMsg;
                    errorAlert.classList.remove('d-none');
                    errorAlert.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                } else {
                    window.api.showToast(errMsg, 'danger');
                }
            } finally {
                if (submitBtn) {
                    submitBtn.disabled = false;
                    const actionMeta = getTypeActionMeta(opp.opportunity_type);
                    submitBtn.innerHTML = `<i class="bi ${actionMeta.icon} me-1"></i>Confirm & Submit`;
                }
            }
        });
    }

    function showSuccessModal(opp, initialStage) {
        const modalEl = document.getElementById('applicationSuccessModal');
        if (!modalEl) return;

        const actionMeta = getTypeActionMeta(opp ? opp.opportunity_type : '');
        const titleEl = document.getElementById('successModalTitle');
        const subTitleEl = document.getElementById('successModalSubtitle');
        const oppNameEl = document.getElementById('successModalOppName');
        const companyEl = document.getElementById('successModalCompany');
        const stageEl = document.getElementById('successModalStage');
        const dateEl = document.getElementById('successModalDate');

        if (titleEl) titleEl.textContent = `${actionMeta.initialStage} Successfully!`;
        if (subTitleEl) subTitleEl.textContent = `Your registration has been saved in the database and linked to your Application Tracker.`;
        if (oppNameEl && opp) oppNameEl.textContent = opp.title;
        if (companyEl && opp) companyEl.textContent = opp.company_name;
        if (stageEl) stageEl.textContent = (initialStage || actionMeta.initialStage).toUpperCase();
        if (dateEl) dateEl.textContent = new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });

        const modal = new bootstrap.Modal(modalEl);
        modal.show();
    }

    async function openDetailsModal(oppId) {
        const modalEl = document.getElementById('opportunityDetailModal');
        if (!modalEl) return;

        const bodyEl = document.getElementById('oppModalBody');
        bodyEl.innerHTML = `<div class="p-4 text-center"><div class="spinner-border text-primary"></div></div>`;

        const modal = new bootstrap.Modal(modalEl);
        modal.show();

        try {
            const res = await window.api.get(`/recommendations/${oppId}`);
            const opp = res.data;
            const actionMeta = getTypeActionMeta(opp.opportunity_type);

            let modalActionBtn = '';
            if (opp.is_applied) {
                modalActionBtn = `
                    <div class="d-flex gap-2">
                        <button class="btn btn-glass text-emerald" disabled>
                            <i class="bi bi-check2-circle me-1"></i>${(opp.application_status || 'Registered').toUpperCase()}
                        </button>
                        <a href="/applications" class="btn btn-gradient-primary">
                            <i class="bi bi-kanban me-1"></i>View in Tracker
                        </a>
                    </div>
                `;
            } else {
                modalActionBtn = `
                    <button class="btn btn-gradient-primary modal-apply-btn" data-id="${opp.id}">
                        <i class="bi ${actionMeta.icon} me-1"></i>${actionMeta.label}
                    </button>
                `;
            }

            bodyEl.innerHTML = `
                <div class="d-flex justify-content-between align-items-start mb-3">
                    <div>
                        <span class="badge badge-pill badge-primary-subtle text-uppercase mb-2">${opp.opportunity_type}</span>
                        <h4 class="text-light fw-bold mb-1">${opp.title}</h4>
                        <p class="text-secondary mb-0"><i class="bi bi-building me-1"></i>${opp.company_name} &bull; <i class="bi bi-geo-alt me-1"></i>${opp.location}</p>
                    </div>
                    <div class="text-end">
                        <span class="display-6 fw-bold text-primary">${opp.match_score}%</span>
                        <small class="d-block text-muted">AI Match Score</small>
                    </div>
                </div>

                <div class="card bg-surface-elevated p-3 border border-subtle mb-3">
                    <h6 class="text-light fw-bold mb-2 small"><i class="bi bi-stars text-primary me-2"></i>Why This Opportunity Matches You</h6>
                    <ul class="small text-secondary ps-3 mb-0">
                        ${(opp.reasons || []).map(r => `<li class="mb-1">${r}</li>`).join('')}
                    </ul>
                </div>

                <div class="row g-3 mb-3">
                    <div class="col-sm-6">
                        <div class="p-3 bg-surface-elevated rounded border border-subtle">
                            <small class="text-emerald fw-bold d-block mb-1"><i class="bi bi-check-circle me-1"></i>Skills You Have (${(opp.matched_skills || []).length})</small>
                            ${(opp.matched_skills || []).length > 0 ? (opp.matched_skills || []).map(s => `<span class="badge badge-emerald-subtle me-1 mb-1">${s}</span>`).join('') : '<span class="text-muted small">None yet</span>'}
                        </div>
                    </div>
                    <div class="col-sm-6">
                        <div class="p-3 bg-surface-elevated rounded border border-subtle">
                            <small class="text-amber fw-bold d-block mb-1"><i class="bi bi-exclamation-circle me-1"></i>Skills to Develop (${(opp.missing_skills || []).length})</small>
                            ${(opp.missing_skills || []).length > 0 ? (opp.missing_skills || []).map(s => `<span class="badge badge-amber-subtle me-1 mb-1">${s}</span>`).join('') : '<span class="text-muted small">All required skills met!</span>'}
                        </div>
                    </div>
                </div>

                <h6 class="text-light fw-bold mb-2">Description & Scope</h6>
                <p class="text-secondary small leading-relaxed mb-3">${opp.description}</p>

                ${opp.eligibility_criteria ? `
                    <h6 class="text-light fw-bold mb-2">Eligibility Criteria</h6>
                    <p class="text-secondary small mb-3">${opp.eligibility_criteria}</p>
                ` : ''}

                <div class="d-flex justify-content-between align-items-center pt-3 border-top border-subtle">
                    <a href="${opp.apply_url}" target="_blank" class="btn btn-glass">
                        Official Site <i class="bi bi-box-arrow-up-right ms-1"></i>
                    </a>
                    ${modalActionBtn}
                </div>
            `;

            // Modal apply button
            const modalApplyBtn = bodyEl.querySelector('.modal-apply-btn');
            if (modalApplyBtn) {
                modalApplyBtn.addEventListener('click', () => {
                    modal.hide();
                    openOpportunityApplicationModal(opp);
                });
            }

        } catch (err) {
            bodyEl.innerHTML = `<div class="alert alert-danger">Failed to load opportunity details.</div>`;
        }
    }

    // Filter Listeners
    typeFilterPills.forEach(pill => {
        pill.addEventListener('click', () => {
            typeFilterPills.forEach(p => {
                p.classList.remove('active', 'btn-gradient-primary');
                p.classList.add('btn-glass');
            });
            pill.classList.add('active', 'btn-gradient-primary');
            pill.classList.remove('btn-glass');
            currentFilters.type = pill.getAttribute('data-type');
            loadOpportunities();
        });
    });

    if (remoteCheckbox) {
        remoteCheckbox.addEventListener('change', () => {
            currentFilters.is_remote = remoteCheckbox.checked ? 'true' : '';
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
            timeout = setTimeout(() => {
                currentFilters.query = searchInput.value.trim();
                loadOpportunities();
            }, 300);
        });
    }

    function resetFilters() {
        currentFilters = { type: 'all', is_remote: '', query: '', sort_by: 'match_desc' };
        if (searchInput) searchInput.value = '';
        if (remoteCheckbox) remoteCheckbox.checked = false;
        if (sortSelect) sortSelect.value = 'match_desc';
        
        typeFilterPills.forEach(p => {
            if (p.getAttribute('data-type') === 'all') {
                p.classList.add('active', 'btn-gradient-primary');
                p.classList.remove('btn-glass');
            } else {
                p.classList.remove('active', 'btn-gradient-primary');
                p.classList.add('btn-glass');
            }
        });

        const newUrl = new URL(window.location);
        newUrl.search = '';
        window.history.replaceState({}, '', newUrl);

        loadOpportunities();
    }

    loadOpportunities();
});
