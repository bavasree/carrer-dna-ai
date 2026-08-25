/**
 * Personalized Career Roadmap Module (7-Stage Career Engine)
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
    const generateBtn = document.getElementById('generateNewRoadmapBtn');

    let currentRoadmap = null;

    async function loadRoadmap() {
        if (!container) return;
        try {
            const res = await window.api.get('/roadmap');
            currentRoadmap = res.data;
            renderRoadmap(currentRoadmap);
        } catch (err) {
            container.innerHTML = `<div class="alert alert-danger">Failed to load roadmap. Please try again.</div>`;
        }
    }

    function renderRoadmap(roadmap) {
        if (!roadmap || !roadmap.milestones || roadmap.milestones.length === 0) {
            container.innerHTML = `
                <div class="empty-state p-5 text-center">
                    <div class="empty-state-icon"><i class="bi bi-map"></i></div>
                    <h5 class="text-light fw-bold">No Career Roadmap Generated Yet</h5>
                    <p class="text-secondary small mb-3">Generate a personalized step-by-step career path from skill baseline to job placement.</p>
                    <button class="btn btn-gradient-primary" id="firstGenBtn"><i class="bi bi-stars me-2"></i>Generate AI Roadmap</button>
                </div>
            `;
            const btn = document.getElementById('firstGenBtn');
            if (btn) btn.addEventListener('click', () => triggerRoadmapGeneration(null));
            return;
        }

        if (targetRoleBadge) targetRoleBadge.textContent = roadmap.target_role;
        const progress = roadmap.overall_progress || 0;
        if (progressBar) progressBar.style.width = `${progress}%`;
        if (progressText) progressText.textContent = `${progress}% Completed`;

        container.innerHTML = `
            <div class="roadmap-timeline">
                ${roadmap.milestones.map((m) => `
                    <div class="roadmap-node ${m.is_completed ? 'completed' : ''}" data-id="${m.id}">
                        <div class="roadmap-marker">
                            <i class="bi ${m.is_completed ? 'bi-check-lg' : 'bi-circle'}"></i>
                        </div>
                        <div class="card bg-surface-card p-4">
                            <div class="d-flex justify-content-between align-items-start mb-2">
                                <div>
                                    <span class="badge ${m.is_completed ? 'badge-emerald-subtle' : 'badge-primary-subtle'} mb-1" style="font-size: 0.72rem;">
                                        STAGE ${m.stage_number}: ${m.stage_name}
                                    </span>
                                    <h5 class="text-light fw-bold mb-1">${m.title}</h5>
                                </div>
                                <div class="form-check form-switch">
                                    <input class="form-check-input milestone-complete-toggle" type="checkbox" role="switch" data-id="${m.id}" id="toggle_stage_${m.id}" ${m.is_completed ? 'checked' : ''}>
                                    <label class="form-check-label small text-muted" for="toggle_stage_${m.id}">${m.is_completed ? 'Completed' : 'Mark Stage Done'}</label>
                                </div>
                            </div>

                            <p class="text-secondary small mb-3">${m.description || ''}</p>

                            <!-- Action Items Checklist -->
                            <div class="mb-3">
                                <h6 class="text-light fw-semibold small mb-2"><i class="bi bi-list-check me-2 text-primary"></i>Action Milestones</h6>
                                <div class="action-items-list">
                                    ${(m.action_items || []).map((item, itemIdx) => `
                                        <div class="form-check mb-2 bg-surface-elevated p-2 ps-4 rounded border border-subtle">
                                            <input class="form-check-input action-item-check" type="checkbox" id="chk_${m.id}_${itemIdx}" data-milestone-id="${m.id}" data-item-idx="${itemIdx}" ${item.completed ? 'checked' : ''}>
                                            <label class="form-check-label small ${item.completed ? 'text-decoration-line-through text-muted' : 'text-light'}" for="chk_${m.id}_${itemIdx}">
                                                ${item.text}
                                            </label>
                                        </div>
                                    `).join('')}
                                </div>
                            </div>

                            <!-- Resources & Study Links -->
                            ${(m.resources || []).length > 0 ? `
                                <div class="pt-2 border-top border-subtle">
                                    <small class="text-muted fw-semibold d-block mb-2"><i class="bi bi-journal-bookmark me-1 text-secondary"></i>Recommended Resources</small>
                                    <div class="d-flex flex-wrap gap-2">
                                        ${(m.resources || []).map(r => `
                                            <a href="${r.url}" target="_blank" class="btn btn-sm btn-glass py-1 px-2" style="font-size: 0.75rem;">
                                                <i class="bi bi-box-arrow-up-right me-1 text-primary"></i>${r.title}
                                            </a>
                                        `).join('')}
                                    </div>
                                </div>
                            ` : ''}
                        </div>
                    </div>
                `).join('')}
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
                    window.api.showToast(`Stage ${isCompleted ? 'completed!' : 'reset.'}`, 'success');
                    
                    const progress = res.data.overall_progress ?? 0;
                    if (progressBar) progressBar.style.width = `${progress}%`;
                    if (progressText) progressText.textContent = `${progress}% Completed`;

                    // Update label and node state
                    const label = toggle.nextElementSibling;
                    if (label) label.textContent = isCompleted ? 'Completed' : 'Mark Stage Done';

                    const node = document.querySelector(`.roadmap-node[data-id="${id}"]`);
                    if (node) {
                        if (isCompleted) {
                            node.classList.add('completed');
                            node.querySelector('.roadmap-marker').innerHTML = '<i class="bi bi-check-lg"></i>';
                        } else {
                            node.classList.remove('completed');
                            node.querySelector('.roadmap-marker').innerHTML = '<i class="bi bi-circle"></i>';
                        }
                        
                        // Sync checkboxes inside this stage
                        node.querySelectorAll('.action-item-check').forEach(chk => {
                            chk.checked = isCompleted;
                            const chkLabel = chk.nextElementSibling;
                            if (chkLabel) {
                                if (isCompleted) {
                                    chkLabel.classList.add('text-decoration-line-through', 'text-muted');
                                    chkLabel.classList.remove('text-light');
                                } else {
                                    chkLabel.classList.remove('text-decoration-line-through', 'text-muted');
                                    chkLabel.classList.add('text-light');
                                }
                            }
                        });
                    }

                    // Update local milestone state
                    const m = (currentRoadmap.milestones || []).find(it => it.id == id);
                    if (m) {
                        m.is_completed = isCompleted;
                        (m.action_items || []).forEach(it => it.completed = isCompleted);
                    }
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
                        label.classList.remove('text-light');
                    } else {
                        label.classList.remove('text-decoration-line-through', 'text-muted');
                        label.classList.add('text-light');
                    }

                    const progress = res.data.overall_progress ?? 0;
                    if (progressBar) progressBar.style.width = `${progress}%`;
                    if (progressText) progressText.textContent = `${progress}% Completed`;

                    // Check if milestone became completed or uncompleted
                    const updatedMilestone = res.data.milestone;
                    const isAllDone = updatedMilestone ? updatedMilestone.is_completed : items.every(it => it.completed);
                    
                    const toggle = document.querySelector(`.milestone-complete-toggle[data-id="${mId}"]`);
                    if (toggle) {
                        toggle.checked = isAllDone;
                        const toggleLabel = toggle.nextElementSibling;
                        if (toggleLabel) toggleLabel.textContent = isAllDone ? 'Completed' : 'Mark Stage Done';
                    }

                    const node = document.querySelector(`.roadmap-node[data-id="${mId}"]`);
                    if (node) {
                        if (isAllDone) {
                            node.classList.add('completed');
                            node.querySelector('.roadmap-marker').innerHTML = '<i class="bi bi-check-lg"></i>';
                        } else {
                            node.classList.remove('completed');
                            node.querySelector('.roadmap-marker').innerHTML = '<i class="bi bi-circle"></i>';
                        }
                    }
                } catch (err) {
                    chk.checked = !chk.checked;
                }
            });
        });
    }

    async function triggerRoadmapGeneration(targetRole) {
        const role = targetRole || (currentRoadmap ? currentRoadmap.target_role : 'Full-Stack Software Engineer');
        if (generateBtn) {
            generateBtn.disabled = true;
            generateBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Constructing Roadmap...';
        }
        window.api.showAILoader(`Gemini AI is constructing your personalized 7-Stage Career Roadmap for ${role}...`);

        try {
            const res = await window.api.post('/roadmap/generate', { target_role: role });
            window.api.hideAILoader();
            window.api.showToast('Personalized Career Roadmap generated!', 'success');
            currentRoadmap = res.data;
            renderRoadmap(currentRoadmap);
        } catch (err) {
            window.api.hideAILoader();
            window.api.showToast(err.message || 'Failed to generate roadmap. Please retry.', 'danger');
        } finally {
            if (generateBtn) {
                generateBtn.disabled = false;
                generateBtn.innerHTML = '<i class="bi bi-magic me-2"></i>Customize Target Role Roadmap';
            }
        }
    }

    if (generateBtn) {
        generateBtn.addEventListener('click', () => {
            const defaultRole = currentRoadmap ? currentRoadmap.target_role : 'Full-Stack Software Engineer';
            const role = prompt('Enter your target career role for this roadmap:', defaultRole);
            if (role && role.trim()) {
                triggerRoadmapGeneration(role.trim());
            }
        });
    }

    loadRoadmap();
});
