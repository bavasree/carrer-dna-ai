/**
 * Onboarding Wizard (Multi-step Profile Builder)
 */

document.addEventListener('DOMContentLoaded', async () => {
    if (!window.api.isAuthenticated()) {
        window.location.href = '/login?redirect=/onboarding';
        return;
    }

    let currentStep = 1;
    const totalSteps = 4;
    const selectedSkills = new Set();

    const progressBar = document.getElementById('onboardingProgress');
    const stepIndicators = document.querySelectorAll('.step-indicator');
    const stepPanes = document.querySelectorAll('.onboarding-step-pane');
    const prevBtn = document.getElementById('prevStepBtn');
    const nextBtn = document.getElementById('nextStepBtn');
    const finishBtn = document.getElementById('finishOnboardingBtn');

    // Popular skills chips
    const popularSkills = [
        "Python", "JavaScript", "TypeScript", "React", "Node.js", "Java", "C++",
        "SQL", "Docker", "AWS", "Git", "Machine Learning", "FastAPI", "TailwindCSS", "PostgreSQL"
    ];

    const skillChipsContainer = document.getElementById('popularSkillChips');
    if (skillChipsContainer) {
        popularSkills.forEach(skill => {
            const chip = document.createElement('button');
            chip.type = 'button';
            chip.className = 'btn btn-sm btn-glass me-2 mb-2 skill-chip';
            chip.innerHTML = `<i class="bi bi-plus-lg me-1"></i>${skill}`;
            chip.addEventListener('click', () => {
                if (selectedSkills.has(skill)) {
                    selectedSkills.delete(skill);
                    chip.classList.remove('btn-gradient-primary');
                    chip.classList.add('btn-glass');
                    chip.innerHTML = `<i class="bi bi-plus-lg me-1"></i>${skill}`;
                } else {
                    selectedSkills.add(skill);
                    chip.classList.remove('btn-glass');
                    chip.classList.add('btn-gradient-primary');
                    chip.innerHTML = `<i class="bi bi-check-lg me-1"></i>${skill}`;
                }
                renderSelectedSkillsList();
            });
            skillChipsContainer.appendChild(chip);
        });
    }

    // Custom Skill Input
    const addCustomSkillBtn = document.getElementById('addCustomSkillBtn');
    const customSkillInput = document.getElementById('customSkillInput');
    if (addCustomSkillBtn && customSkillInput) {
        addCustomSkillBtn.addEventListener('click', () => {
            const val = customSkillInput.value.trim();
            if (val && !selectedSkills.has(val)) {
                selectedSkills.add(val);
                customSkillInput.value = '';
                renderSelectedSkillsList();
            }
        });
        customSkillInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                addCustomSkillBtn.click();
            }
        });
    }

    function renderSelectedSkillsList() {
        const container = document.getElementById('selectedSkillsContainer');
        if (!container) return;
        container.innerHTML = '';
        selectedSkills.forEach(skill => {
            const badge = document.createElement('span');
            badge.className = 'badge bg-primary-subtle border border-primary text-light p-2 me-2 mb-2 d-inline-flex align-items-center';
            badge.innerHTML = `
                <span>${skill}</span>
                <button type="button" class="btn-close btn-close-white ms-2" style="font-size: 0.65rem;" aria-label="Remove"></button>
            `;
            badge.querySelector('.btn-close').addEventListener('click', () => {
                selectedSkills.delete(skill);
                // Update chip if exists
                document.querySelectorAll('.skill-chip').forEach(c => {
                    if (c.textContent.trim() === skill) {
                        c.classList.remove('btn-gradient-primary');
                        c.classList.add('btn-glass');
                        c.innerHTML = `<i class="bi bi-plus-lg me-1"></i>${skill}`;
                    }
                });
                renderSelectedSkillsList();
            });
            container.appendChild(badge);
        });
    }

    // Prepopulate profile if exists
    try {
        const profileRes = await window.api.get('/profile');
        if (profileRes.data) {
            const p = profileRes.data;
            if (p.full_name) document.getElementById('obFullName').value = p.full_name;
            if (p.headline) document.getElementById('obHeadline').value = p.headline;
            if (p.phone) document.getElementById('obPhone').value = p.phone;
            if (p.bio) document.getElementById('obBio').value = p.bio;

            if (p.college_name) document.getElementById('obCollege').value = p.college_name;
            if (p.degree) document.getElementById('obDegree').value = p.degree;
            if (p.branch) document.getElementById('obBranch').value = p.branch;
            if (p.graduation_year) document.getElementById('obGradYear').value = p.graduation_year;
            if (p.cgpa) document.getElementById('obCgpa').value = p.cgpa;

            if (p.target_role) document.getElementById('obTargetRole').value = p.target_role;
            if (p.career_goal) document.getElementById('obCareerGoal').value = p.career_goal;
            if (p.github_url) document.getElementById('obGithub').value = p.github_url;
            if (p.linkedin_url) document.getElementById('obLinkedin').value = p.linkedin_url;

            if (p.skills && p.skills.length > 0) {
                p.skills.forEach(s => selectedSkills.add(s.skill_name));
                renderSelectedSkillsList();
            }
        }
    } catch (err) {}

    function updateStepView() {
        stepPanes.forEach((pane, idx) => {
            if (idx + 1 === currentStep) {
                pane.classList.remove('d-none');
            } else {
                pane.classList.add('d-none');
            }
        });

        stepIndicators.forEach((ind, idx) => {
            if (idx + 1 === currentStep) {
                ind.classList.add('active');
                ind.classList.remove('completed');
            } else if (idx + 1 < currentStep) {
                ind.classList.add('completed');
                ind.classList.remove('active');
            } else {
                ind.classList.remove('active', 'completed');
            }
        });

        if (progressBar) {
            const pct = ((currentStep - 1) / (totalSteps - 1)) * 100;
            progressBar.style.width = `${pct}%`;
        }

        if (currentStep === 1) {
            prevBtn.classList.add('d-none');
        } else {
            prevBtn.classList.remove('d-none');
        }

        if (currentStep === totalSteps) {
            nextBtn.classList.add('d-none');
            finishBtn.classList.remove('d-none');
        } else {
            nextBtn.classList.remove('d-none');
            finishBtn.classList.add('d-none');
        }
    }

    if (nextBtn) {
        nextBtn.addEventListener('click', () => {
            if (currentStep < totalSteps) {
                currentStep++;
                updateStepView();
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }
        });
    }

    if (prevBtn) {
        prevBtn.addEventListener('click', () => {
            if (currentStep > 1) {
                currentStep--;
                updateStepView();
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }
        });
    }

    if (finishBtn) {
        finishBtn.addEventListener('click', async () => {
            finishBtn.disabled = true;
            finishBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Saving & Launching AI Analysis...';
            window.api.showAILoader('Creating your Career DNA & running initial AI Career Readiness analysis...');

            const profilePayload = {
                full_name: document.getElementById('obFullName').value.trim(),
                headline: document.getElementById('obHeadline').value.trim(),
                phone: document.getElementById('obPhone').value.trim(),
                bio: document.getElementById('obBio').value.trim(),
                college_name: document.getElementById('obCollege').value.trim(),
                degree: document.getElementById('obDegree').value.trim(),
                branch: document.getElementById('obBranch').value.trim(),
                graduation_year: document.getElementById('obGradYear').value ? parseInt(document.getElementById('obGradYear').value) : null,
                cgpa: document.getElementById('obCgpa').value ? parseFloat(document.getElementById('obCgpa').value) : null,
                target_role: document.getElementById('obTargetRole').value.trim(),
                career_goal: document.getElementById('obCareerGoal').value.trim(),
                github_url: document.getElementById('obGithub').value.trim(),
                linkedin_url: document.getElementById('obLinkedin').value.trim()
            };

            try {
                // 1. Update Profile
                await window.api.put('/profile', profilePayload);

                // 2. Add Selected Skills
                for (const skill of selectedSkills) {
                    try {
                        await window.api.post('/profile/skills', { skill_name: skill, proficiency_level: 'intermediate' }, { silent: true });
                    } catch (e) {}
                }

                // 3. Trigger Initial AI Career Analysis
                try {
                    await window.api.post('/career-analysis/analyze', {}, { silent: true });
                } catch (e) {}

                window.api.hideAILoader();
                window.api.showToast('Profile configured successfully!', 'success');

                setTimeout(() => {
                    window.location.href = '/dashboard';
                }, 1000);
            } catch (err) {
                window.api.hideAILoader();
                finishBtn.disabled = false;
                finishBtn.innerHTML = 'Complete Setup & Go to Dashboard <i class="bi bi-arrow-right ms-1"></i>';
            }
        });
    }

    updateStepView();
});
