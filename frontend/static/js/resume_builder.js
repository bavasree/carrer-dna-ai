/**
 * AI Resume Builder & PDF Live Preview Module
 * Professional ATS-compliant Resume Layout & Real-Time Sync
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
        const name = content.full_name || 'Student Name';
        const headline = content.headline || 'Software Engineer';
        const email = content.email || 'student@careerdna.ai';
        const phone = content.phone || '';
        const github = content.github_url || '';
        const linkedin = content.linkedin_url || '';

        const objective = objInput ? objInput.value : (currentResume.career_objective || '');
        const skillsStr = skillsInput ? skillsInput.value : (currentResume.skills_summary || '');
        const skills = skillsStr ? skillsStr.split(',').map(s => s.trim()).filter(Boolean) : (content.skills || []);

        const projects = content.projects || [];
        const certs = content.certifications || [];

        if (selectedTemplate === 'classic') {
            // Classic ATS Single Column Template (Traditional Serif)
            paperPreview.className = 'resume-paper font-serif';
            paperPreview.innerHTML = `
                <!-- Header -->
                <div class="text-center pb-2 mb-3 border-bottom border-dark">
                    <h2 class="fw-bold mb-1" style="font-size: 1.55rem; letter-spacing: 0.05em; color: #000000; margin: 0; padding: 0;">${name.toUpperCase()}</h2>
                    <div class="small mt-1" style="color: #1F2937; font-size: 0.88rem;">
                        ${[
                            email ? `<span>${email}</span>` : '',
                            phone ? `<span>${phone}</span>` : '',
                            linkedin ? `<a href="${linkedin}" target="_blank" style="color: #000000; text-decoration: underline;">LinkedIn</a>` : '',
                            github ? `<a href="${github}" target="_blank" style="color: #000000; text-decoration: underline;">GitHub</a>` : ''
                        ].filter(Boolean).join(' &bull; ')}
                    </div>
                </div>

                <!-- Objective -->
                ${objective ? `
                    <div class="mb-3">
                        <div class="resume-section-title" style="font-size: 0.88rem; font-weight: 700; text-transform: uppercase; border-bottom: 1.5px solid #000000; padding-bottom: 2px; margin-bottom: 6px; color: #000000;">OBJECTIVE</div>
                        <p class="small mb-0" style="color: #111827; font-size: 0.88rem; line-height: 1.5;">${objective}</p>
                    </div>
                ` : ''}

                <!-- Education -->
                <div class="mb-3">
                    <div class="resume-section-title" style="font-size: 0.88rem; font-weight: 700; text-transform: uppercase; border-bottom: 1.5px solid #000000; padding-bottom: 2px; margin-bottom: 6px; color: #000000;">EDUCATION</div>
                    <div class="d-flex justify-content-between align-items-start small" style="font-size: 0.88rem;">
                        <div>
                            <span class="fw-bold" style="color: #000000;">${content.college_name || 'University'}</span> — <span>${content.degree || 'B.Tech'} in ${content.branch || 'Computer Science'}</span>
                        </div>
                        <div class="text-end fst-italic" style="color: #374151; white-space: nowrap;">
                            ${content.graduation_year || '2026'}${content.cgpa ? ` | CGPA: ${content.cgpa}/10.0` : ''}
                        </div>
                    </div>
                </div>

                <!-- Technical Skills -->
                ${skills.length > 0 ? `
                    <div class="mb-3">
                        <div class="resume-section-title" style="font-size: 0.88rem; font-weight: 700; text-transform: uppercase; border-bottom: 1.5px solid #000000; padding-bottom: 2px; margin-bottom: 6px; color: #000000;">TECHNICAL SKILLS</div>
                        <p class="small mb-0" style="color: #111827; font-size: 0.88rem; line-height: 1.5;">${skills.join(' • ')}</p>
                    </div>
                ` : ''}

                <!-- Projects -->
                ${projects.length > 0 ? `
                    <div class="mb-3">
                        <div class="resume-section-title" style="font-size: 0.88rem; font-weight: 700; text-transform: uppercase; border-bottom: 1.5px solid #000000; padding-bottom: 2px; margin-bottom: 6px; color: #000000;">PROJECTS</div>
                        ${projects.map(p => {
                            const descLines = (p.description || '').split('\n').map(l => l.trim()).filter(Boolean);
                            return `
                                <div class="mb-2.5">
                                    <div class="d-flex justify-content-between align-items-baseline small" style="font-size: 0.88rem;">
                                        <span class="fw-bold" style="color: #000000;">${p.title}</span>
                                        <span class="fst-italic" style="color: #4B5563; font-size: 0.82rem;">${p.tech_stack || ''}</span>
                                    </div>
                                    <div class="ps-2 mt-0.5">
                                        ${descLines.map(l => `<p class="small mb-0" style="color: #1F2937; font-size: 0.85rem; line-height: 1.45;">${l.startsWith('•') ? l : '• ' + l}</p>`).join('')}
                                    </div>
                                    ${(p.github_url || p.live_url) ? `
                                        <div class="small mt-1 ps-2" style="font-size: 0.80rem; color: #4B5563;">
                                            ${p.github_url ? `<a href="${p.github_url}" target="_blank" style="color: #000000; text-decoration: underline; margin-right: 12px;">Repository: ${p.github_url}</a>` : ''}
                                            ${p.live_url ? `<a href="${p.live_url}" target="_blank" style="color: #000000; text-decoration: underline;">Live Demo: ${p.live_url}</a>` : ''}
                                        </div>
                                    ` : ''}
                                </div>
                            `;
                        }).join('')}
                    </div>
                ` : ''}

                <!-- Certifications -->
                ${certs.length > 0 ? `
                    <div>
                        <div class="resume-section-title" style="font-size: 0.88rem; font-weight: 700; text-transform: uppercase; border-bottom: 1.5px solid #000000; padding-bottom: 2px; margin-bottom: 6px; color: #000000;">CERTIFICATIONS</div>
                        <ul class="small ps-3 mb-0" style="color: #111827; font-size: 0.88rem; line-height: 1.5;">
                            ${certs.map(c => `<li><b>${c.title}</b>${c.issuing_organization ? ` — ${c.issuing_organization}` : ''}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
            `;
        } else {
            // Modern Tech Template (Deep Navy & Clean Blue Accents)
            paperPreview.className = 'resume-paper';
            paperPreview.innerHTML = `
                <!-- Header -->
                <div class="resume-header mb-3 pb-2.5" style="border-bottom: 2px solid #1E3A8A;">
                    <h2 class="fw-bold mb-0" style="font-size: 1.65rem; color: #1E3A8A; letter-spacing: -0.01em; margin: 0; padding: 0;">${name.toUpperCase()}</h2>
                    <div class="fw-semibold small mt-0.5 mb-1" style="color: #2563EB; font-size: 0.94rem;">${headline}</div>
                    <div class="small" style="color: #475569; font-size: 0.86rem;">
                        ${[
                            email ? `<span><i class="bi bi-envelope me-1"></i>${email}</span>` : '',
                            phone ? `<span><i class="bi bi-telephone me-1"></i>${phone}</span>` : '',
                            github ? `<a href="${github}" target="_blank" style="color: #1E3A8A; font-weight: 600;"><i class="bi bi-github me-1"></i>GitHub</a>` : '',
                            linkedin ? `<a href="${linkedin}" target="_blank" style="color: #1E3A8A; font-weight: 600;"><i class="bi bi-linkedin me-1"></i>LinkedIn</a>` : ''
                        ].filter(Boolean).join(' &bull; ')}
                    </div>
                </div>

                <!-- Professional Summary -->
                ${objective ? `
                    <div class="mb-3">
                        <div class="resume-section-title" style="font-size: 0.90rem; font-weight: 750; text-transform: uppercase; color: #1E3A8A; border-bottom: 1.5px solid #E2E8F0; padding-bottom: 3px; margin-bottom: 6px; letter-spacing: 0.04em;">PROFESSIONAL SUMMARY</div>
                        <p class="small mb-0" style="color: #334155; font-size: 0.88rem; line-height: 1.55;">${objective}</p>
                    </div>
                ` : ''}

                <!-- Education -->
                <div class="mb-3">
                    <div class="resume-section-title" style="font-size: 0.90rem; font-weight: 750; text-transform: uppercase; color: #1E3A8A; border-bottom: 1.5px solid #E2E8F0; padding-bottom: 3px; margin-bottom: 6px; letter-spacing: 0.04em;">EDUCATION</div>
                    <div class="d-flex justify-content-between align-items-start small" style="font-size: 0.88rem;">
                        <div>
                            <div class="fw-bold" style="color: #0F172A;">${content.degree || 'B.Tech'} in ${content.branch || 'Computer Science'}</div>
                            <div style="color: #475569;">${content.college_name || 'University'}</div>
                        </div>
                        <div class="text-end" style="color: #475569;">
                            <div class="fw-bold" style="color: #0F172A;">Graduation: ${content.graduation_year || '2026'}</div>
                            <div>${content.cgpa ? `Cumulative CGPA: ${content.cgpa}/10.0` : ''}</div>
                        </div>
                    </div>
                </div>

                <!-- Technical Competencies -->
                ${skills.length > 0 ? `
                    <div class="mb-3">
                        <div class="resume-section-title" style="font-size: 0.90rem; font-weight: 750; text-transform: uppercase; color: #1E3A8A; border-bottom: 1.5px solid #E2E8F0; padding-bottom: 3px; margin-bottom: 6px; letter-spacing: 0.04em;">TECHNICAL COMPETENCIES</div>
                        <p class="small mb-0" style="color: #1E293B; font-size: 0.88rem; line-height: 1.55;">
                            <b>Core Technologies:</b> ${skills.join(' • ')}
                        </p>
                    </div>
                ` : ''}

                <!-- Projects -->
                ${projects.length > 0 ? `
                    <div class="mb-3">
                        <div class="resume-section-title" style="font-size: 0.90rem; font-weight: 750; text-transform: uppercase; color: #1E3A8A; border-bottom: 1.5px solid #E2E8F0; padding-bottom: 3px; margin-bottom: 6px; letter-spacing: 0.04em;">TECHNICAL & CAPSTONE PROJECTS</div>
                        ${projects.map(p => {
                            const descLines = (p.description || '').split('\n').map(l => l.trim()).filter(Boolean);
                            return `
                                <div class="mb-2.5">
                                    <div class="d-flex justify-content-between align-items-baseline small" style="font-size: 0.88rem;">
                                        <span class="fw-bold" style="color: #0F172A;">${p.title}</span>
                                        <span class="fst-italic" style="color: #64748B; font-size: 0.82rem;">${p.tech_stack || ''}</span>
                                    </div>
                                    <div class="ps-2 mt-0.5">
                                        ${descLines.map(l => `<p class="small mb-0" style="color: #334155; font-size: 0.86rem; line-height: 1.45;">${l.startsWith('•') ? l : '• ' + l}</p>`).join('')}
                                    </div>
                                    ${(p.github_url || p.live_url) ? `
                                        <div class="small mt-1 ps-2" style="font-size: 0.80rem;">
                                            ${p.github_url ? `<a href="${p.github_url}" target="_blank" style="color: #2563EB; font-weight: 500; margin-right: 12px;"><i class="bi bi-github me-1"></i>Repository</a>` : ''}
                                            ${p.live_url ? `<a href="${p.live_url}" target="_blank" style="color: #2563EB; font-weight: 500;"><i class="bi bi-box-arrow-up-right me-1"></i>Live Demo</a>` : ''}
                                        </div>
                                    ` : ''}
                                </div>
                            `;
                        }).join('')}
                    </div>
                ` : ''}

                <!-- Certifications -->
                ${certs.length > 0 ? `
                    <div>
                        <div class="resume-section-title" style="font-size: 0.90rem; font-weight: 750; text-transform: uppercase; color: #1E3A8A; border-bottom: 1.5px solid #E2E8F0; padding-bottom: 3px; margin-bottom: 6px; letter-spacing: 0.04em;">CERTIFICATIONS & ACCREDITATIONS</div>
                        <ul class="small ps-3 mb-0" style="color: #1E293B; font-size: 0.88rem; line-height: 1.5;">
                            ${certs.map(c => `<li><b>${c.title}</b>${c.issuing_organization ? ` — ${c.issuing_organization}` : ''}</li>`).join('')}
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
                const blob = await window.api.get(`/resume/download-pdf?template=${selectedTemplate}&force_generate=true`, { responseType: 'blob' });
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
