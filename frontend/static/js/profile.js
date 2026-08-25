/**
 * Profile Management Module
 */

document.addEventListener('DOMContentLoaded', async () => {
    if (!window.api.isAuthenticated()) {
        window.location.href = '/login?redirect=/profile';
        return;
    }

    const profileForm = document.getElementById('profileDetailsForm');
    const skillsListEl = document.getElementById('profileSkillsList');
    const projectsListEl = document.getElementById('profileProjectsList');
    const certsListEl = document.getElementById('profileCertsList');
    const compPctEl = document.getElementById('profileCompletionBadge');

    let currentProfile = null;

    async function loadProfile() {
        try {
            const res = await window.api.get('/profile');
            currentProfile = res.data;
            populateForm(currentProfile);
            renderSkills(currentProfile.skills || []);
            renderProjects(currentProfile.projects || []);
            renderCertifications(currentProfile.certifications || []);

            if (compPctEl) {
                compPctEl.textContent = `${currentProfile.profile_completion_pct || 0}% Complete`;
            }
        } catch (err) {
            console.error('Failed to load profile:', err);
        }
    }

    function populateForm(p) {
        if (!p) return;
        document.getElementById('profFullName').value = p.full_name || '';
        document.getElementById('profHeadline').value = p.headline || '';
        document.getElementById('profPhone').value = p.phone || '';
        document.getElementById('profBio').value = p.bio || '';
        document.getElementById('profCollege').value = p.college_name || '';
        document.getElementById('profDegree').value = p.degree || '';
        document.getElementById('profBranch').value = p.branch || '';
        document.getElementById('profGradYear').value = p.graduation_year || '';
        document.getElementById('profCgpa').value = p.cgpa || '';
        document.getElementById('profTargetRole').value = p.target_role || '';
        document.getElementById('profCareerGoal').value = p.career_goal || '';
        document.getElementById('profInterests').value = p.interests_raw || (p.interests ? p.interests.join(', ') : '');
        document.getElementById('profGithub').value = p.github_url || '';
        document.getElementById('profLinkedin').value = p.linkedin_url || '';
        document.getElementById('profPortfolio').value = p.portfolio_url || '';
    }

    if (profileForm) {
        profileForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const submitBtn = profileForm.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;

            const payload = {
                full_name: document.getElementById('profFullName').value.trim(),
                headline: document.getElementById('profHeadline').value.trim(),
                phone: document.getElementById('profPhone').value.trim(),
                bio: document.getElementById('profBio').value.trim(),
                college_name: document.getElementById('profCollege').value.trim(),
                degree: document.getElementById('profDegree').value.trim(),
                branch: document.getElementById('profBranch').value.trim(),
                graduation_year: document.getElementById('profGradYear').value ? parseInt(document.getElementById('profGradYear').value) : null,
                cgpa: document.getElementById('profCgpa').value ? parseFloat(document.getElementById('profCgpa').value) : null,
                target_role: document.getElementById('profTargetRole').value.trim(),
                career_goal: document.getElementById('profCareerGoal').value.trim(),
                interests: document.getElementById('profInterests').value.trim(),
                github_url: document.getElementById('profGithub').value.trim(),
                linkedin_url: document.getElementById('profLinkedin').value.trim(),
                portfolio_url: document.getElementById('profPortfolio').value.trim()
            };

            try {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Saving...';

                const res = await window.api.put('/profile', payload);
                window.api.showToast('Profile updated successfully!', 'success');
                currentProfile = res.data;
                if (compPctEl) compPctEl.textContent = `${currentProfile.profile_completion_pct || 0}% Complete`;

                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
            } catch (err) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
            }
        });
    }

    // ==========================================
    // Skills CRUD
    // ==========================================
    function renderSkills(skills) {
        if (!skillsListEl) return;
        if (skills.length === 0) {
            skillsListEl.innerHTML = `<p class="text-muted small mb-0">No technical skills added yet. Add your core programming languages & frameworks below.</p>`;
            return;
        }

        const levelColors = {
            beginner: 'badge-amber-subtle',
            intermediate: 'badge-cyan-subtle',
            advanced: 'badge-primary-subtle',
            expert: 'badge-emerald-subtle'
        };

        skillsListEl.innerHTML = skills.map(s => `
            <div class="d-inline-flex align-items-center bg-surface-elevated border border-subtle rounded-pill px-3 py-1 me-2 mb-2">
                <span class="fw-semibold text-light me-2">${s.skill_name}</span>
                <span class="badge ${levelColors[s.proficiency_level] || 'badge-primary-subtle'} me-2">${s.proficiency_level}</span>
                <button type="button" class="btn btn-link text-danger p-0 delete-skill-btn" data-id="${s.id}" title="Remove">
                    <i class="bi bi-x-circle"></i>
                </button>
            </div>
        `).join('');

        document.querySelectorAll('.delete-skill-btn').forEach(btn => {
            btn.addEventListener('click', async () => {
                const id = btn.getAttribute('data-id');
                try {
                    await window.api.delete(`/profile/skills/${id}`);
                    window.api.showToast('Skill removed.', 'info');
                    loadProfile();
                } catch (err) {}
            });
        });
    }

    const addSkillForm = document.getElementById('addSkillForm');
    if (addSkillForm) {
        addSkillForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const name = document.getElementById('newSkillName').value.trim();
            const level = document.getElementById('newSkillProficiency').value;
            const yoe = document.getElementById('newSkillYoe').value;

            if (!name) return;

            try {
                await window.api.post('/profile/skills', {
                    skill_name: name,
                    proficiency_level: level,
                    years_of_experience: yoe ? parseFloat(yoe) : 1.0
                });
                document.getElementById('newSkillName').value = '';
                window.api.showToast('Skill added!', 'success');
                loadProfile();
            } catch (err) {}
        });
    }

    // ==========================================
    // Projects CRUD
    // ==========================================
    function renderProjects(projects) {
        if (!projectsListEl) return;
        if (projects.length === 0) {
            projectsListEl.innerHTML = `
                <div class="empty-state p-3 text-center">
                    <p class="text-muted small mb-0">No projects added. Showcase your web apps, systems, or research here!</p>
                </div>
            `;
            return;
        }

        projectsListEl.innerHTML = projects.map(p => `
            <div class="card bg-surface-card p-3 mb-3">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <h6 class="text-light fw-bold mb-1">${p.title} ${p.role ? `<span class="badge badge-primary-subtle ms-2">${p.role}</span>` : ''}</h6>
                        <small class="text-secondary d-block mb-2"><i class="bi bi-tools me-1"></i>Tech: ${p.tech_stack || 'Not specified'}</small>
                    </div>
                    <button class="btn btn-sm btn-glass-danger delete-project-btn" data-id="${p.id}"><i class="bi bi-trash"></i></button>
                </div>
                <p class="small text-secondary mb-2">${p.description}</p>
                <div class="d-flex gap-3">
                    ${p.github_url ? `<a href="${p.github_url}" target="_blank" class="small text-decoration-none text-info"><i class="bi bi-github me-1"></i>Repository</a>` : ''}
                    ${p.live_url ? `<a href="${p.live_url}" target="_blank" class="small text-decoration-none text-emerald"><i class="bi bi-box-arrow-up-right me-1"></i>Live Demo</a>` : ''}
                </div>
            </div>
        `).join('');

        document.querySelectorAll('.delete-project-btn').forEach(btn => {
            btn.addEventListener('click', async () => {
                const id = btn.getAttribute('data-id');
                if (confirm('Delete this project?')) {
                    try {
                        await window.api.delete(`/profile/projects/${id}`);
                        window.api.showToast('Project deleted.', 'info');
                        loadProfile();
                    } catch (err) {}
                }
            });
        });
    }

    const addProjectForm = document.getElementById('addProjectForm');
    if (addProjectForm) {
        addProjectForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const payload = {
                title: document.getElementById('projTitle').value.trim(),
                description: document.getElementById('projDesc').value.trim(),
                tech_stack: document.getElementById('projTech').value.trim(),
                role: document.getElementById('projRole').value.trim(),
                github_url: document.getElementById('projGithub').value.trim(),
                live_url: document.getElementById('projLive').value.trim()
            };

            try {
                await window.api.post('/profile/projects', payload);
                window.api.showToast('Project added!', 'success');
                addProjectForm.reset();
                const modal = bootstrap.Modal.getInstance(document.getElementById('addProjectModal'));
                if (modal) modal.hide();
                loadProfile();
            } catch (err) {}
        });
    }

    // ==========================================
    // Certifications CRUD
    // ==========================================
    function renderCertifications(certs) {
        if (!certsListEl) return;
        if (certs.length === 0) {
            certsListEl.innerHTML = `<p class="text-muted small mb-0">No certifications added yet.</p>`;
            return;
        }

        certsListEl.innerHTML = certs.map(c => `
            <div class="card bg-surface-card p-3 mb-2 d-flex flex-row justify-content-between align-items-center">
                <div>
                    <h6 class="text-light fw-bold mb-0">${c.title}</h6>
                    <small class="text-secondary">${c.issuing_organization} &bull; ${c.issue_date || 'Accredited'}</small>
                </div>
                <button class="btn btn-sm btn-glass-danger delete-cert-btn" data-id="${c.id}"><i class="bi bi-trash"></i></button>
            </div>
        `).join('');

        document.querySelectorAll('.delete-cert-btn').forEach(btn => {
            btn.addEventListener('click', async () => {
                const id = btn.getAttribute('data-id');
                try {
                    await window.api.delete(`/profile/certifications/${id}`);
                    window.api.showToast('Certification removed.', 'info');
                    loadProfile();
                } catch (err) {}
            });
        });
    }

    const addCertForm = document.getElementById('addCertForm');
    if (addCertForm) {
        addCertForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const payload = {
                title: document.getElementById('certTitle').value.trim(),
                issuing_organization: document.getElementById('certOrg').value.trim(),
                issue_date: document.getElementById('certDate').value.trim(),
                credential_id: document.getElementById('certCredId').value.trim(),
                credential_url: document.getElementById('certUrl').value.trim()
            };

            try {
                await window.api.post('/profile/certifications', payload);
                window.api.showToast('Certification added!', 'success');
                addCertForm.reset();
                const modal = bootstrap.Modal.getInstance(document.getElementById('addCertModal'));
                if (modal) modal.hide();
                loadProfile();
            } catch (err) {}
        });
    }

    loadProfile();
});
