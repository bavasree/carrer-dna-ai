/**
 * AI Resume Builder & PDF Live Preview Module
 */

document.addEventListener('DOMContentLoaded', async () => {
    if (!window.api.isAuthenticated()) {
        window.location.href = '/login?redirect=/resume-builder';
        return;
    }

    let currentResume = null;
    let selectedTemplate = 'modern';

    const objInput = document.getElementById('resumeCareerObjective');
    const skillsInput = document.getElementById('resumeSkillsSummary');
    const templateSelect = document.getElementById('resumeTemplateSelect');
    const saveBtn = document.getElementById('saveResumeBtn');
    const downloadPdfBtn = document.getElementById('downloadPdfBtn');
    const aiEnhanceObjBtn = document.getElementById('aiEnhanceObjBtn');
    const aiScoreAtsBtn = document.getElementById('aiScoreAtsBtn');

    const paperPreview = document.getElementById('resumePaperPreview');
    const atsScoreBadge = document.getElementById('resumeAtsScoreBadge');

    async function loadResume() {
        try {
            const res = await window.api.get('/resume');
            currentResume = res.data;
            selectedTemplate = currentResume.template_name || 'modern';
            if (templateSelect) templateSelect.value = selectedTemplate;

            if (objInput) objInput.value = currentResume.career_objective || '';
            if (skillsInput) skillsInput.value = currentResume.skills_summary || '';

            if (atsScoreBadge) {
                const score = currentResume.ats_score || 75;
                atsScoreBadge.textContent = `ATS Score: ${score}/100`;
                atsScoreBadge.className = `badge ${score >= 80 ? 'badge-emerald-subtle' : 'badge-primary-subtle'} py-2 px-3 fw-bold`;
            }

            renderLivePreview();
        } catch (err) {
            console.error('Failed to load resume:', err);
        }
    }

    function renderLivePreview() {
        if (!paperPreview || !currentResume) return;

        const content = currentResume.content_data || {};
        const name = content.full_name || 'Your Full Name';
        const headline = content.headline || 'Software Engineer';
        const email = content.email || 'student@careerdna.ai';
        const phone = content.phone || '+1 (555) 000-0000';
        const github = content.github_url || '';
        const linkedin = content.linkedin_url || '';

        const objective = objInput ? objInput.value : (currentResume.career_objective || '');
        const skillsStr = skillsInput ? skillsInput.value : (currentResume.skills_summary || '');
        const skills = skillsStr ? skillsStr.split(',').map(s => s.trim()).filter(Boolean) : (content.skills || []);

        const projects = content.projects || [];
        const certs = content.certifications || [];

        if (selectedTemplate === 'classic') {
            // Classic ATS Single Column Template
            paperPreview.className = 'resume-paper font-serif';
            paperPreview.innerHTML = `
                <div class="text-center pb-2 mb-3 border-bottom border-dark">
                    <h2 class="text-dark fw-bold mb-1" style="font-size: 1.5rem; letter-spacing: 0.05em; border: none; margin: 0; padding: 0;">${name.toUpperCase()}</h2>
                    <div class="small text-dark mt-1">
                        ${email} &bull; ${phone} ${github ? `&bull; <a href="${github}" target="_blank" class="text-dark">GitHub</a>` : ''} ${linkedin ? `&bull; <a href="${linkedin}" target="_blank" class="text-dark">LinkedIn</a>` : ''}
                    </div>
                </div>

                ${objective ? `
                    <div class="mb-3">
                        <h6 class="fw-bold text-dark text-uppercase border-bottom border-dark pb-1 mb-2" style="font-size: 0.85rem; letter-spacing: 0.05em;">Professional Objective</h6>
                        <p class="small text-dark mb-0 leading-relaxed">${objective}</p>
                    </div>
                ` : ''}

                <div class="mb-3">
                    <h6 class="fw-bold text-dark text-uppercase border-bottom border-dark pb-1 mb-2" style="font-size: 0.85rem; letter-spacing: 0.05em;">Education</h6>
                    <div class="d-flex justify-content-between text-dark small fw-bold">
                        <span>${content.college_name || 'University'} — ${content.degree || 'B.S.'} in ${content.branch || 'Computer Science'}</span>
                        <span>${content.graduation_year || '2026'}</span>
                    </div>
                    ${content.cgpa ? `<div class="small text-muted">Cumulative CGPA: ${content.cgpa}/10.0</div>` : ''}
                </div>

                ${skills.length > 0 ? `
                    <div class="mb-3">
                        <h6 class="fw-bold text-dark text-uppercase border-bottom border-dark pb-1 mb-2" style="font-size: 0.85rem; letter-spacing: 0.05em;">Technical Competencies</h6>
                        <p class="small text-dark mb-0">${skills.join(' • ')}</p>
                    </div>
                ` : ''}

                ${projects.length > 0 ? `
                    <div class="mb-3">
                        <h6 class="fw-bold text-dark text-uppercase border-bottom border-dark pb-1 mb-2" style="font-size: 0.85rem; letter-spacing: 0.05em;">Technical Projects</h6>
                        ${projects.map(p => {
                            const descLines = (p.description || '').split('\n').map(l => l.trim()).filter(Boolean);
                            return `
                                <div class="mb-2">
                                    <div class="d-flex justify-content-between text-dark small">
                                        <span class="fw-bold">${p.title}</span>
                                        <span class="fst-italic text-muted">${p.tech_stack || ''}</span>
                                    </div>
                                    <div class="ps-2">
                                        ${descLines.map(l => `<p class="small text-dark mb-0 leading-tight">${l.startsWith('•') ? l : '• ' + l}</p>`).join('')}
                                    </div>
                                    ${p.github_url || p.live_url ? `
                                        <div class="small text-muted mt-1">
                                            ${p.github_url ? `<a href="${p.github_url}" target="_blank" class="text-dark me-2">Code</a>` : ''}
                                            ${p.live_url ? `<a href="${p.live_url}" target="_blank" class="text-dark">Live Demo</a>` : ''}
                                        </div>
                                    ` : ''}
                                </div>
                            `;
                        }).join('')}
                    </div>
                ` : ''}

                ${certs.length > 0 ? `
                    <div>
                        <h6 class="fw-bold text-dark text-uppercase border-bottom border-dark pb-1 mb-2" style="font-size: 0.85rem; letter-spacing: 0.05em;">Certifications & Accreditations</h6>
                        <ul class="small text-dark ps-3 mb-0">
                            ${certs.map(c => `<li><b>${c.title}</b> — ${c.issuing_organization || 'Accredited'}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
            `;
        } else {
            // Modern Tech Template
            paperPreview.className = 'resume-paper';
            paperPreview.innerHTML = `
                <div class="resume-header mb-3 pb-2" style="border-bottom: 2px solid #1E3A8A;">
                    <h2 class="fw-bold mb-0" style="font-size: 1.55rem; color: #1E3A8A; letter-spacing: -0.01em; border: none; margin: 0; padding: 0;">${name.toUpperCase()}</h2>
                    <div class="fw-semibold small mb-1" style="color: #2563EB;">${headline}</div>
                    <div class="small text-muted">
                        ${email} &bull; ${phone}
                        ${github ? `&bull; <a href="${github}" target="_blank" style="color: #1E3A8A; font-weight: 500;"><i class="bi bi-github me-1"></i>GitHub</a>` : ''}
                        ${linkedin ? `&bull; <a href="${linkedin}" target="_blank" style="color: #1E3A8A; font-weight: 500;"><i class="bi bi-linkedin me-1"></i>LinkedIn</a>` : ''}
                    </div>
                </div>

                ${objective ? `
                    <div class="mb-3">
                        <h6 class="fw-bold text-uppercase pb-1 mb-2" style="color: #1E3A8A; border-bottom: 1.5px solid #E2E8F0; font-size: 0.85rem; letter-spacing: 0.05em;">Professional Summary</h6>
                        <p class="small text-dark mb-0 leading-relaxed">${objective}</p>
                    </div>
                ` : ''}

                <div class="mb-3">
                    <h6 class="fw-bold text-uppercase pb-1 mb-2" style="color: #1E3A8A; border-bottom: 1.5px solid #E2E8F0; font-size: 0.85rem; letter-spacing: 0.05em;">Education</h6>
                    <div class="d-flex justify-content-between text-dark small fw-bold">
                        <span style="color: #0F172A;">${content.degree || 'B.Tech'} in ${content.branch || 'Computer Science'}</span>
                        <span class="text-muted">Graduation: ${content.graduation_year || '2026'}</span>
                    </div>
                    <div class="d-flex justify-content-between small text-muted">
                        <span>${content.college_name || 'University'}</span>
                        <span>${content.cgpa ? `Cumulative CGPA: ${content.cgpa}/10.0` : ''}</span>
                    </div>
                </div>

                ${skills.length > 0 ? `
                    <div class="mb-3">
                        <h6 class="fw-bold text-uppercase pb-1 mb-2" style="color: #1E3A8A; border-bottom: 1.5px solid #E2E8F0; font-size: 0.85rem; letter-spacing: 0.05em;">Technical Competencies</h6>
                        <div class="d-flex flex-wrap gap-1 mt-1">
                            ${skills.map(s => `<span class="badge bg-light text-dark border p-1" style="font-size: 0.72rem; font-weight: 500;">${s}</span>`).join('')}
                        </div>
                    </div>
                ` : ''}

                ${projects.length > 0 ? `
                    <div class="mb-3">
                        <h6 class="fw-bold text-uppercase pb-1 mb-2" style="color: #1E3A8A; border-bottom: 1.5px solid #E2E8F0; font-size: 0.85rem; letter-spacing: 0.05em;">Technical & Capstone Projects</h6>
                        ${projects.map(p => {
                            const descLines = (p.description || '').split('\n').map(l => l.trim()).filter(Boolean);
                            return `
                                <div class="mb-2">
                                    <div class="d-flex justify-content-between text-dark small">
                                        <span class="fw-bold" style="color: #0F172A;">${p.title}</span>
                                        <span class="text-muted fst-italic" style="font-size: 0.78rem;">${p.tech_stack || ''}</span>
                                    </div>
                                    <div class="ps-2">
                                        ${descLines.map(l => `<p class="small text-dark mb-0 leading-tight" style="color: #334155;">${l.startsWith('•') ? l : '• ' + l}</p>`).join('')}
                                    </div>
                                    ${p.github_url || p.live_url ? `
                                        <div class="small text-muted mt-1">
                                            ${p.github_url ? `<a href="${p.github_url}" target="_blank" class="me-2" style="color: #2563EB;">Code Repository</a>` : ''}
                                            ${p.live_url ? `<a href="${p.live_url}" target="_blank" style="color: #2563EB;">Live Demo</a>` : ''}
                                        </div>
                                    ` : ''}
                                </div>
                            `;
                        }).join('')}
                    </div>
                ` : ''}

                ${certs.length > 0 ? `
                    <div>
                        <h6 class="fw-bold text-uppercase pb-1 mb-2" style="color: #1E3A8A; border-bottom: 1.5px solid #E2E8F0; font-size: 0.85rem; letter-spacing: 0.05em;">Certifications & Awards</h6>
                        <ul class="small text-dark ps-3 mb-0">
                            ${certs.map(c => `<li><b>${c.title}</b> — ${c.issuing_organization || 'Accredited'}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
            `;
        }
    }

    // Live sync on typing
    if (objInput) objInput.addEventListener('input', renderLivePreview);
    if (skillsInput) skillsInput.addEventListener('input', renderLivePreview);

    if (templateSelect) {
        templateSelect.addEventListener('change', () => {
            selectedTemplate = templateSelect.value;
            renderLivePreview();
        });
    }

    // Save Resume
    if (saveBtn) {
        saveBtn.addEventListener('click', async () => {
            saveBtn.disabled = true;
            saveBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Saving...';

            const payload = {
                template_name: selectedTemplate,
                career_objective: objInput ? objInput.value : '',
                skills_summary: skillsInput ? skillsInput.value : ''
            };

            try {
                const res = await window.api.put('/resume', payload);
                currentResume = res.data;
                window.api.showToast('Resume draft saved successfully!', 'success');
            } catch (err) {
                window.api.showToast('Failed to save resume draft.', 'danger');
            } finally {
                saveBtn.disabled = false;
                saveBtn.innerHTML = '<i class="bi bi-save me-1"></i>Save Draft';
            }
        });
    }

    // AI Enhance Objective
    if (aiEnhanceObjBtn) {
        aiEnhanceObjBtn.addEventListener('click', async () => {
            const currentText = objInput ? objInput.value.trim() : '';
            aiEnhanceObjBtn.disabled = true;
            window.api.showAILoader('Gemini AI is crafting a high-impact, ATS-optimized professional objective with strong action verbs...');

            try {
                const res = await window.api.post('/resume/ai-improve', {
                    section_type: 'career_objective',
                    text_content: currentText || 'Software developer passionate about building scalable applications.'
                });
                window.api.hideAILoader();
                if (res.data && res.data.improved_text) {
                    if (objInput) objInput.value = res.data.improved_text;
                    renderLivePreview();
                    window.api.showToast('Professional objective enhanced with AI!', 'success');
                }
            } catch (err) {
                window.api.hideAILoader();
                window.api.showToast('Failed to enhance text with AI. Please retry.', 'danger');
            } finally {
                aiEnhanceObjBtn.disabled = false;
            }
        });
    }

    // AI Score ATS Analyzer
    if (aiScoreAtsBtn) {
        aiScoreAtsBtn.addEventListener('click', async () => {
            aiScoreAtsBtn.disabled = true;
            aiScoreAtsBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Analyzing...';
            window.api.showAILoader('Scanning resume content with Gemini ATS Analyzer for keyword saturation and recruiter formatting compliance...');

            try {
                const res = await window.api.post('/resume/ai-score-ats', {
                    target_role: currentResume?.content_data?.target_role || 'Software Engineer',
                    career_objective: objInput ? objInput.value : '',
                    skills_summary: skillsInput ? skillsInput.value : ''
                });
                window.api.hideAILoader();

                const atsData = res.data;
                const score = atsData.ats_score || 75;
                if (atsScoreBadge) {
                    atsScoreBadge.textContent = `ATS Score: ${score}/100`;
                    atsScoreBadge.className = `badge ${score >= 80 ? 'badge-emerald-subtle' : 'badge-primary-subtle'} py-2 px-3 fw-bold`;
                }

                // Show ATS Modal
                const modalBody = document.getElementById('atsModalBody');
                if (modalBody) {
                    modalBody.innerHTML = `
                        <div class="text-center mb-4">
                            <span class="display-4 fw-bold ${score >= 80 ? 'text-success' : 'text-primary'}">${score}</span>
                            <span class="fs-4 text-muted">/100</span>
                            <div class="small text-secondary mt-1">Overall ATS Compatibility Grade for <b>${atsData.target_role || 'Software Engineer'}</b></div>
                        </div>

                        <div class="row g-3 mb-3">
                            <div class="col-6 text-center p-2 bg-surface-elevated rounded border border-subtle">
                                <small class="text-muted d-block">Formatting Score</small>
                                <span class="fw-bold text-light fs-5">${atsData.formatting_score || 88}%</span>
                            </div>
                            <div class="col-6 text-center p-2 bg-surface-elevated rounded border border-subtle">
                                <small class="text-muted d-block">Keyword Density</small>
                                <span class="fw-bold text-light fs-5">${atsData.keyword_density_score || 75}%</span>
                            </div>
                        </div>

                        ${(atsData.identified_relevant_skills || []).length > 0 ? `
                            <div class="mb-3">
                                <h6 class="text-success fw-bold small mb-1"><i class="bi bi-check-circle me-1"></i>Skills Detected Relevant to Role</h6>
                                <div class="d-flex flex-wrap gap-1">
                                    ${(atsData.identified_relevant_skills || []).map(sk => `<span class="badge badge-emerald-subtle border border-success text-light">${sk}</span>`).join('')}
                                </div>
                            </div>
                        ` : ''}

                        <div class="mb-3">
                            <h6 class="text-danger fw-bold small mb-1"><i class="bi bi-exclamation-triangle me-1"></i>Crucial Missing Keywords for ${atsData.target_role || 'Target Role'}</h6>
                            <div class="d-flex flex-wrap gap-1">
                                ${(atsData.missing_keywords || []).map(kw => `<span class="badge bg-danger-subtle border border-danger text-light">${kw}</span>`).join('')}
                            </div>
                        </div>

                        <div>
                            <h6 class="text-light fw-bold small mb-2"><i class="bi bi-lightbulb me-1 text-warning"></i>Actionable ATS Improvement Suggestions</h6>
                            <ul class="small text-secondary ps-3 mb-0">
                                ${(atsData.actionable_suggestions || []).map(sug => `<li class="mb-1">${sug}</li>`).join('')}
                            </ul>
                        </div>
                    `;
                    const modal = new bootstrap.Modal(document.getElementById('atsFeedbackModal'));
                    modal.show();
                }
            } catch (err) {
                window.api.hideAILoader();
                window.api.showToast('ATS Scoring could not complete. Please retry.', 'danger');
            } finally {
                aiScoreAtsBtn.disabled = false;
                aiScoreAtsBtn.innerHTML = '<i class="bi bi-search me-1"></i>Score ATS';
            }
        });
    }

    // Download PDF
    if (downloadPdfBtn) {
        downloadPdfBtn.addEventListener('click', async () => {
            downloadPdfBtn.disabled = true;
            downloadPdfBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Generating PDF...';

            try {
                const blob = await window.api.get(`/resume/download-pdf?template=${selectedTemplate}`, { responseType: 'blob' });
                const downloadUrl = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = downloadUrl;
                const safeName = (currentResume?.content_data?.full_name || 'Student').replace(/\s+/g, '_');
                a.download = `${safeName}_Resume_${selectedTemplate.toUpperCase()}.pdf`;
                document.body.appendChild(a);
                a.click();
                a.remove();
                window.URL.revokeObjectURL(downloadUrl);
                window.api.showToast('PDF Resume downloaded successfully!', 'success');
            } catch (err) {
                window.api.showToast('Failed to download PDF resume.', 'danger');
            } finally {
                downloadPdfBtn.disabled = false;
                downloadPdfBtn.innerHTML = '<i class="bi bi-file-earmark-pdf me-1"></i>Download PDF';
            }
        });
    }

    loadResume();
});
