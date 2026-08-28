/**
 * Personalized Career Roadmap Engine (7-Stage Progression System)
 * High-Contrast Typography, Card Styling, and Matched Learning Resources
 */

document.addEventListener('DOMContentLoaded', async () => {
    if (!window.api.isAuthenticated()) {
        window.location.href = '/login?redirect=/roadmap';
        return;
    }

    const container = document.getElementById('roadmapTimelineContainer');
    const targetRoleBadge = document.getElementById('roadmapTargetRoleBadge');
    const progressBar = document.getElementById('roadmapOverallProgressBar');
    const progressText = document.getElementById('roadmapOverallProgressText');
    const stageSummaryText = document.getElementById('roadmapStageSummaryText');
    const stagePillsNav = document.getElementById('roadmapStagePillsNav');

    const customizeModalEl = document.getElementById('customizeRoadmapModal');
    const customizeForm = document.getElementById('customizeRoadmapForm');
    const customRoleInput = document.getElementById('customTargetRoleInput');
    const submitCustomBtn = document.getElementById('btnSubmitCustomRoadmap');

    let currentRoadmap = null;

    // Trusted Learning Resource Dictionary for matching topics/skills inside roadmap
    const TOPIC_RESOURCE_MAPPINGS = [
        { pattern: /\b(python)\b/i, title: 'Python Official Docs', url: 'https://www.python.org/', label: 'Learn Now' },
        { pattern: /\b(dsa|data structure|algorithms?|leetcode)\b/i, title: 'LeetCode Practice', url: 'https://leetcode.com/', label: 'Start Practice' },
        { pattern: /\b(html|css|html5|css3|flexbox|grid)\b/i, title: 'MDN Web Docs — HTML/CSS', url: 'https://developer.mozilla.org/', label: 'Learn Now' },
        { pattern: /\b(javascript|js|es6|typescript|ts)\b/i, title: 'MDN JavaScript Guide', url: 'https://developer.mozilla.org/', label: 'Learn Now' },
        { pattern: /\b(sql|database|postgres|postgresql|mysql|sqlite)\b/i, title: 'W3Schools SQL Tutorial', url: 'https://www.w3schools.com/sql/', label: 'Learn Now' },
        { pattern: /\b(git|github|version control|repository)\b/i, title: 'GitHub Skills', url: 'https://skills.github.com/', label: 'Visit Resource' },
        { pattern: /\b(aws|cloud|amazon web services|gcp|azure)\b/i, title: 'AWS Cloud Training', url: 'https://aws.amazon.com/training/', label: 'Visit Resource' },
        { pattern: /\b(react|next\.js|redux)\b/i, title: 'React Official Docs', url: 'https://react.dev/', label: 'Learn Now' },
        { pattern: /\b(docker|container|kubernetes|k8s)\b/i, title: 'Docker Official Docs', url: 'https://docs.docker.com/', label: 'Visit Resource' },
        { pattern: /\b(linux|bash|shell|unix)\b/i, title: 'Linux Journey', url: 'https://linuxjourney.com/', label: 'Learn Now' },
        { pattern: /\b(system design|microservices|distributed systems)\b/i, title: 'System Design Primer', url: 'https://github.com/donnemartin/system-design-primer', label: 'Study Guide' },
        { pattern: /\b(interview|star method|mock interview)\b/i, title: 'Tech Interview Handbook', url: 'https://www.techinterviewhandbook.org/', label: 'Visit Guide' },
        { pattern: /\b(salary|compensation|negotiat|placement|offer)\b/i, title: 'Levels.fyi Tech Salaries', url: 'https://www.levels.fyi/', label: 'Visit Resource' },
        { pattern: /\b(owasp|cyber|security|penetration)\b/i, title: 'OWASP Security Guide', url: 'https://owasp.org/www-project-top-ten/', label: 'Learn Now' },
        { pattern: /\b(pytorch|deep learning|neural)\b/i, title: 'PyTorch Tutorials', url: 'https://pytorch.org/tutorials/', label: 'Visit Resource' },
        { pattern: /\b(machine learning|scikit-learn|pandas|numpy)\b/i, title: 'Kaggle Learn ML', url: 'https://www.kaggle.com/learn', label: 'Start Learning' }
    ];

    function resolveTopicResource(text) {
        if (!text) return null;
        for (const item of TOPIC_RESOURCE_MAPPINGS) {
            if (item.pattern.test(text)) {
                return item;
            }
        }
        return null;
    }

    async function loadRoadmap() {
        if (!container) return;
        try {
            const res = await window.api.get('/roadmap');
            currentRoadmap = res.data;
            renderRoadmap(currentRoadmap);
        } catch (err) {
            container.innerHTML = `<div class="alert alert-danger">Failed to load roadmap. Please try refreshing the page.</div>`;
        }
    }

    function getStageStatus(milestone, index, allMilestones) {
        if (milestone.is_completed) {
            return { key: 'completed', label: 'COMPLETED', badgeClass: 'badge-emerald-subtle', markerClass: 'completed', icon: 'bi-check-lg' };
        }
        const items = milestone.action_items || [];
        const hasDoneItems = items.some(it => it.completed);
        
        // Find first incomplete index
        const firstIncompleteIdx = allMilestones.findIndex(m => !m.is_completed);
        if (hasDoneItems || index === firstIncompleteIdx) {
            return { key: 'in_progress', label: 'IN PROGRESS', badgeClass: 'badge-cyan-subtle', markerClass: 'in-progress', icon: 'bi-arrow-repeat' };
        }
        return { key: 'not_started', label: 'NOT STARTED', badgeClass: 'bg-surface-elevated text-secondary', markerClass: 'not-started', icon: 'bi-circle' };
    }

    function getResourceTypeBadge(type) {
        const t = (type || '').toLowerCase();
        if (t.includes('doc')) return 'badge-cyan-subtle';
        if (t.includes('practice')) return 'badge-emerald-subtle';
        if (t.includes('course') || t.includes('cert')) return 'badge-primary-subtle';
        if (t.includes('tool')) return 'badge-amber-subtle';
        if (t.includes('repo')) return 'badge-rose-subtle';
        return 'badge-primary-subtle';
    }

    function renderRoadmap(roadmap) {
        if (!roadmap || !roadmap.milestones || roadmap.milestones.length === 0) {
            container.innerHTML = `
                <div class="card bg-surface-card p-5 text-center border border-subtle">
                    <div class="brand-icon bg-primary text-white border-0 shadow-sm mx-auto mb-3" style="width: 54px; height: 54px;"><i class="bi bi-diagram-3 fs-3"></i></div>
                    <h4 class="text-white fw-bold">No Career Roadmap Generated Yet</h4>
                    <p class="text-secondary small mb-3">Generate a personalized step-by-step career path from skill baseline to job placement.</p>
                    <button class="btn btn-gradient-primary" id="firstGenBtn"><i class="bi bi-stars me-2"></i>Generate AI Roadmap</button>
                </div>
            `;
            const btn = document.getElementById('firstGenBtn');
            if (btn) btn.addEventListener('click', () => triggerRoadmapGeneration('Full-Stack Software Engineer'));
            return;
        }

        if (targetRoleBadge) targetRoleBadge.textContent = roadmap.target_role;
        if (customRoleInput) customRoleInput.value = roadmap.target_role;

        const milestones = roadmap.milestones;
        const progress = roadmap.overall_progress || 0;
        
        if (progressBar) progressBar.style.width = `${progress}%`;
        if (progressText) progressText.textContent = `${progress}% Completed`;

        const completedCount = milestones.filter(m => m.is_completed).length;
        if (stageSummaryText) {
            stageSummaryText.textContent = `${completedCount} of 7 Stages Completed &bull; Target: ${roadmap.target_role}`;
        }

        // Render Top 7-Stage Horizontal Nav Tracker
        if (stagePillsNav) {
            stagePillsNav.innerHTML = milestones.map((m, idx) => {
                const st = getStageStatus(m, idx, milestones);
                let borderStyle = 'border-subtle';
                let iconHtml = `<span class="badge ${st.badgeClass} me-1.5" style="font-size: 0.72rem;">S${m.stage_number}</span>`;
                if (st.key === 'completed') {
                    borderStyle = 'border-success';
                    iconHtml = `<i class="bi bi-check-circle-fill text-success me-1.5"></i>`;
                } else if (st.key === 'in_progress') {
                    borderStyle = 'border-info';
                    iconHtml = `<i class="bi bi-record-circle text-info me-1.5 animate-pulse"></i>`;
                }

                return `
                    <a href="#stage_card_${m.id}" class="btn btn-sm btn-glass text-light py-1.5 px-2.5 text-decoration-none d-flex align-items-center ${borderStyle}" style="font-size: 0.84rem;">
                        ${iconHtml}
                        <span class="fw-semibold text-truncate" style="max-width: 125px;">${m.stage_name}</span>
                    </a>
                `;
            }).join('');
        }

        // Render 7 Stages Timeline Cards
        container.innerHTML = `
            <div class="roadmap-timeline">
                ${milestones.map((m, idx) => {
                    const st = getStageStatus(m, idx, milestones);
                    const items = m.action_items || [];
                    const doneItemsCount = items.filter(it => it.completed).length;

                    return `
                        <div class="roadmap-node ${st.markerClass}" data-id="${m.id}" id="stage_card_${m.id}">
                            <div class="roadmap-marker">
                                ${st.key === 'completed' ? '<i class="bi bi-check-lg text-white fs-5"></i>' : `<span>${m.stage_number}</span>`}
                            </div>
                            <div class="card p-4 p-md-4 shadow-md">
                                <!-- Stage Header -->
                                <div class="d-flex flex-column flex-sm-row justify-content-between align-items-start align-items-sm-center gap-2 pb-3 mb-3 border-bottom border-subtle">
                                    <div>
                                        <div class="d-flex align-items-center gap-2 mb-1.5">
                                            <span class="badge ${st.badgeClass} py-1.5 px-3 fw-bold text-uppercase" style="font-size: 0.78rem; letter-spacing: 0.04em;">
                                                STAGE ${m.stage_number}: ${m.stage_name}
                                            </span>
                                            <span class="badge ${st.key === 'completed' ? 'badge-emerald-subtle' : (st.key === 'in_progress' ? 'badge-cyan-subtle' : 'bg-surface-elevated text-secondary')} py-1 px-2.5 fw-bold" style="font-size: 0.72rem;">
                                                ${st.label}
                                            </span>
                                        </div>
                                        <h4 class="text-white fw-bold mb-0 fs-5">${m.title}</h4>
                                    </div>
                                    <div class="form-check form-switch ps-sm-3">
                                        <input class="form-check-input milestone-complete-toggle cursor-pointer" type="checkbox" role="switch" data-id="${m.id}" id="toggle_stage_${m.id}" ${m.is_completed ? 'checked' : ''} style="width: 2.2rem; height: 1.2rem; cursor: pointer;">
                                        <label class="form-check-label fw-bold ms-1 ${m.is_completed ? 'text-emerald' : 'text-secondary'}" for="toggle_stage_${m.id}" style="font-size: 0.90rem; cursor: pointer;">
                                            ${m.is_completed ? 'Completed' : 'Mark Stage Done'}
                                        </label>
                                    </div>
                                </div>

                                ${m.description ? `<p class="text-secondary mb-3" style="font-size: 0.98rem; line-height: 1.6;">${m.description}</p>` : ''}

                                <!-- Key Tasks / Action Items Required -->
                                <div class="mt-3">
                                    <div class="d-flex justify-content-between align-items-center mb-3">
                                        <h6 class="text-white fw-bold mb-0" style="font-size: 1.02rem;">
                                            <i class="bi bi-check2-square me-2 text-primary"></i>Key Required Actions & Learning Topics
                                        </h6>
                                        <span class="text-secondary small fw-semibold" id="stage_count_${m.id}">
                                            ${doneItemsCount} of ${items.length} completed
                                        </span>
                                    </div>
                                    <div class="action-items-list d-flex flex-column gap-2.5">
                                        ${items.map((item, itemIdx) => {
                                            const matchedResource = resolveTopicResource(item.text);
                                            return `
                                                <div class="form-check bg-surface-elevated p-3 ps-3.5 rounded-3 border border-subtle d-flex flex-column flex-sm-row justify-content-between align-items-sm-center gap-2 mb-0">
                                                    <div class="d-flex align-items-center flex-grow-1">
                                                        <input class="form-check-input action-item-check me-3 flex-shrink-0" type="checkbox" id="chk_${m.id}_${itemIdx}" data-milestone-id="${m.id}" data-item-idx="${itemIdx}" ${item.completed ? 'checked' : ''} style="width: 1.25rem; height: 1.25rem; cursor: pointer;">
                                                        <label class="form-check-label fw-medium ${item.completed ? 'text-decoration-line-through text-muted' : 'text-white'}" for="chk_${m.id}_${itemIdx}" style="cursor: pointer; font-size: 0.98rem; line-height: 1.5;">
                                                            ${item.text}
                                                        </label>
                                                    </div>
                                                    ${matchedResource ? `
                                                        <a href="${matchedResource.url}" target="_blank" rel="noopener noreferrer" class="btn btn-sm btn-glass text-cyan border border-info border-opacity-40 py-1 px-2.5 flex-shrink-0 align-self-start align-self-sm-auto shadow-sm" style="font-size: 0.82rem;">
                                                            <i class="bi bi-box-arrow-up-right me-1.5"></i>${matchedResource.label || 'Learn Now'}
                                                        </a>
                                                    ` : ''}
                                                </div>
                                            `;
                                        }).join('')}
                                    </div>
                                </div>

                                <!-- Recommended Learning Resources & Trusted Official Links -->
                                ${(m.resources && m.resources.length > 0) ? `
                                    <div class="mt-4 pt-3 border-top border-subtle">
                                        <div class="d-flex justify-content-between align-items-center mb-3">
                                            <h6 class="text-white fw-bold mb-0" style="font-size: 1.02rem;">
                                                <i class="bi bi-book-half me-2 text-cyan"></i>Recommended Learning Resources & Documentation
                                            </h6>
                                            <span class="badge badge-cyan-subtle fw-semibold" style="font-size: 0.76rem;">${m.resources.length} Verified Links</span>
                                        </div>
                                        <div class="row g-3">
                                            ${m.resources.map(r => `
                                                <div class="col-12 col-md-6">
                                                    <div class="learning-resource-card p-3.5 rounded-3 border border-subtle h-100 d-flex flex-column justify-content-between">
                                                        <div>
                                                            <div class="d-flex justify-content-between align-items-start gap-2 mb-2">
                                                                <h5 class="text-white fw-bold mb-0 fs-6">${r.title}</h5>
                                                                <span class="badge ${getResourceTypeBadge(r.type)} text-uppercase fw-bold" style="font-size: 0.72rem;">${r.type || 'Resource'}</span>
                                                            </div>
                                                            <p class="text-secondary small mb-3" style="font-size: 0.90rem; line-height: 1.5;">${r.description || 'Master key concepts with official documentation and hands-on practice.'}</p>
                                                        </div>
                                                        <div class="pt-2.5 border-top border-subtle text-end">
                                                            <a href="${r.url}" target="_blank" rel="noopener noreferrer" class="btn btn-sm btn-gradient-secondary fw-bold px-3 py-1.5 shadow-sm">
                                                                <i class="bi bi-box-arrow-up-right me-1.5"></i>${r.action_label || 'Visit Resource'}
                                                            </a>
                                                        </div>
                                                    </div>
                                                </div>
                                            `).join('')}
                                        </div>
                                    </div>
                                ` : ''}
                            </div>
                        </div>
                    `;
                }).join('')}
            </div>
        `;

        attachMilestoneListeners();
    }

    function attachMilestoneListeners() {
        // Milestone toggle ("Mark Stage Done")
        document.querySelectorAll('.milestone-complete-toggle').forEach(toggle => {
            toggle.addEventListener('change', async () => {
                const id = toggle.getAttribute('data-id');
                const isCompleted = toggle.checked;

                try {
                    const res = await window.api.put(`/roadmap/milestones/${id}`, { is_completed: isCompleted });
                    window.api.showToast(`Stage ${isCompleted ? 'marked completed!' : 'reset.'}`, 'success');
                    
                    // Reload to update progression states across stages
                    await loadRoadmap();
                } catch (err) {
                    toggle.checked = !isCompleted;
                }
            });
        });

        // Action Item Checklist toggle
        document.querySelectorAll('.action-item-check').forEach(chk => {
            chk.addEventListener('change', async () => {
                const mId = chk.getAttribute('data-milestone-id');
                const itemIdx = parseInt(chk.getAttribute('data-item-idx'));
                
                const milestone = (currentRoadmap.milestones || []).find(m => m.id == mId);
                if (!milestone) return;

                const items = [...(milestone.action_items || [])];
                if (items[itemIdx]) {
                    items[itemIdx].completed = chk.checked;
                }

                try {
                    const res = await window.api.put(`/roadmap/milestones/${mId}`, { action_items: items });
                    milestone.action_items = items;
                    
                    const label = chk.nextElementSibling;
                    if (chk.checked) {
                        label.classList.add('text-decoration-line-through', 'text-muted');
                        label.classList.remove('text-white');
                    } else {
                        label.classList.remove('text-decoration-line-through', 'text-muted');
                        label.classList.add('text-white');
                    }

                    const progress = res.data.overall_progress ?? 0;
                    if (progressBar) progressBar.style.width = `${progress}%`;
                    if (progressText) progressText.textContent = `${progress}% Completed`;

                    // Update count label
                    const countEl = document.getElementById(`stage_count_${mId}`);
                    const doneCount = items.filter(it => it.completed).length;
                    if (countEl) countEl.textContent = `${doneCount} of ${items.length} completed`;

                    // If all items completed, reload roadmap to advance stage markers
                    if (doneCount === items.length || doneCount === items.length - 1) {
                        await loadRoadmap();
                    }
                } catch (err) {
                    chk.checked = !chk.checked;
                }
            });
        });
    }

    async function triggerRoadmapGeneration(targetRole) {
        const role = targetRole || (customRoleInput ? customRoleInput.value.trim() : 'Full-Stack Software Engineer');
        if (!role) {
            window.api.showToast('Please enter or select a target career role.', 'warning');
            return;
        }

        if (submitCustomBtn) {
            submitCustomBtn.disabled = true;
            submitCustomBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Constructing 7 Stages...';
        }

        // Hide modal
        if (customizeModalEl) {
            const modal = bootstrap.Modal.getInstance(customizeModalEl);
            if (modal) modal.hide();
        }

        window.api.showAILoader(`Gemini AI is constructing your personalized 7-Stage Career Development Plan for "${role}"...`);

        try {
            const res = await window.api.post('/roadmap/generate', { target_role: role });
            window.api.hideAILoader();
            window.api.showToast(`Personalized Career Roadmap for ${role} generated!`, 'success');
            currentRoadmap = res.data;
            renderRoadmap(currentRoadmap);
        } catch (err) {
            window.api.hideAILoader();
            window.api.showToast(err.message || 'Failed to generate roadmap. Please retry.', 'danger');
        } finally {
            if (submitCustomBtn) {
                submitCustomBtn.disabled = false;
                submitCustomBtn.innerHTML = '<i class="bi bi-stars me-1"></i>Generate Personalized 7-Stage Roadmap';
            }
        }
    }

    // Modal chip selection
    document.querySelectorAll('.suggested-role-chip').forEach(chip => {
        chip.addEventListener('click', () => {
            const role = chip.getAttribute('data-role');
            if (customRoleInput) customRoleInput.value = role;
            document.querySelectorAll('.suggested-role-chip').forEach(c => c.classList.remove('btn-gradient-secondary', 'active'));
            chip.classList.add('btn-gradient-secondary', 'active');
        });
    });

    if (customizeForm) {
        customizeForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const role = customRoleInput ? customRoleInput.value.trim() : '';
            triggerRoadmapGeneration(role);
        });
    }

    loadRoadmap();
});
