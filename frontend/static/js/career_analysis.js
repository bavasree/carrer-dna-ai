/**
 * AI Career Analysis & Skill Gap Visualizer Module
 */

document.addEventListener('DOMContentLoaded', async () => {
    if (!window.api.isAuthenticated()) {
        window.location.href = '/login?redirect=/career-analysis';
        return;
    }

    let radarChart = null;
    let gaugeChart = null;

    const runAnalysisBtn = document.getElementById('runAnalysisBtn');
    const roleGapBtn = document.getElementById('roleGapBtn');

    async function loadAnalysis() {
        try {
            const res = await window.api.get('/career-analysis');
            if (res.data) {
                renderAnalysisData(res.data);
            } else {
                showEmptyAnalysisState();
            }
        } catch (err) {
            showEmptyAnalysisState();
        }
    }

    function showEmptyAnalysisState() {
        const contentArea = document.getElementById('analysisContentArea');
        if (contentArea) {
            contentArea.innerHTML = `
                <div class="empty-state p-5 text-center my-4">
                    <div class="empty-state-icon text-primary"><i class="bi bi-cpu"></i></div>
                    <h4 class="text-light fw-bold">No AI Career Analysis Generated Yet</h4>
                    <p class="text-secondary max-w-lg mx-auto mb-4">
                        Let Google Gemini analyze your complete academic history, verified skills, and technical projects to discover your Career Readiness Score, detect skill gaps, and get personalized recommendations.
                    </p>
                    <button class="btn btn-gradient-primary px-4 py-2" id="emptyTriggerAnalysisBtn">
                        <i class="bi bi-stars me-2"></i>Run AI Career Analysis
                    </button>
                </div>
            `;
            const btn = document.getElementById('emptyTriggerAnalysisBtn');
            if (btn) btn.addEventListener('click', triggerAnalysis);
        }
    }

    async function triggerAnalysis() {
        if (runAnalysisBtn) {
            runAnalysisBtn.disabled = true;
            runAnalysisBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Gemini AI Analyzing...';
        }
        window.api.showAILoader('Gemini AI is diagnosing your skill profile, evaluating industry benchmarks, and computing your readiness score...');
        try {
            const res = await window.api.post('/career-analysis/analyze', {});
            window.api.hideAILoader();
            window.api.showToast('AI Career Analysis generated successfully!', 'success');
            renderAnalysisData(res.data);
        } catch (err) {
            window.api.hideAILoader();
            window.api.showToast(err.message || 'AI Analysis could not complete. Please retry.', 'danger');
        } finally {
            if (runAnalysisBtn) {
                runAnalysisBtn.disabled = false;
                runAnalysisBtn.innerHTML = '<i class="bi bi-stars me-2"></i>Run New AI Analysis';
            }
        }
    }

    if (runAnalysisBtn) {
        runAnalysisBtn.addEventListener('click', triggerAnalysis);
    }

    function renderAnalysisData(data) {
        const contentArea = document.getElementById('analysisContentArea');
        if (!contentArea) return;

        // Restore layout container if in empty state
        contentArea.innerHTML = `
            <!-- Top Metrics Row -->
            <div class="row g-4 mb-4">
                <div class="col-lg-4">
                    <div class="card bg-surface-card p-4 text-center h-100 d-flex flex-column justify-content-center">
                        <h6 class="text-secondary text-uppercase fw-bold mb-3" style="font-size: 0.8rem; letter-spacing: 0.05em;">Career Readiness Index</h6>
                        <div class="position-relative mx-auto" style="width: 180px; height: 140px;">
                            <canvas id="caReadinessGauge"></canvas>
                            <div class="position-absolute top-50 start-50 translate-middle mt-2 text-center">
                                <span class="display-6 fw-bold text-light" id="caScoreNum">${data.readiness_score}</span>
                                <small class="d-block text-muted" style="font-size: 0.75rem;">out of 100</small>
                            </div>
                        </div>
                        <div class="mt-2">
                            <span class="badge ${data.readiness_score >= 75 ? 'badge-emerald-subtle' : data.readiness_score >= 50 ? 'badge-primary-subtle' : 'badge-amber-subtle'} py-1 px-3">
                                ${data.readiness_score >= 75 ? 'Industry Ready (High)' : data.readiness_score >= 50 ? 'Competitive Profile' : 'Development Required'}
                            </span>
                        </div>
                    </div>
                </div>

                <div class="col-lg-8">
                    <div class="card bg-surface-card p-4 h-100">
                        <div class="d-flex align-items-center mb-3">
                            <div class="brand-icon me-3"><i class="bi bi-robot"></i></div>
                            <div>
                                <h5 class="text-light fw-bold mb-0">AI Diagnostic Summary</h5>
                                <small class="text-muted">Generated by Gemini AI &bull; ${data.created_at || 'Recent'}</small>
                            </div>
                        </div>
                        <p class="text-secondary mb-4 leading-relaxed">${data.ai_summary || 'Your profile shows strong foundational momentum.'}</p>
                        
                        <div class="row g-3">
                            <div class="col-sm-6">
                                <div class="p-3 rounded-3 bg-surface-elevated border border-subtle">
                                    <h6 class="text-emerald fw-bold mb-2 small"><i class="bi bi-shield-check me-2"></i>Core Strengths</h6>
                                    <ul class="list-unstyled mb-0 small text-secondary">
                                        ${(data.strengths || []).map(s => `<li class="mb-1"><i class="bi bi-check2 text-success me-2"></i>${s}</li>`).join('')}
                                    </ul>
                                </div>
                            </div>
                            <div class="col-sm-6">
                                <div class="p-3 rounded-3 bg-surface-elevated border border-subtle">
                                    <h6 class="text-amber fw-bold mb-2 small"><i class="bi bi-exclamation-circle me-2"></i>Growth Opportunities</h6>
                                    <ul class="list-unstyled mb-0 small text-secondary">
                                        ${(data.weaknesses || []).map(w => `<li class="mb-1"><i class="bi bi-arrow-right text-warning me-2"></i>${w}</li>`).join('')}
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Skill Gaps & Radar Row -->
            <div class="row g-4 mb-4">
                <div class="col-lg-6">
                    <div class="card bg-surface-card p-4 h-100">
                        <h5 class="text-light fw-bold mb-3"><i class="bi bi-radar me-2 text-primary"></i>Competency Benchmark Radar</h5>
                        <div style="height: 280px; position: relative;">
                            <canvas id="caRadarChart"></canvas>
                        </div>
                    </div>
                </div>

                <div class="col-lg-6">
                    <div class="card bg-surface-card p-4 h-100">
                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <h5 class="text-light fw-bold mb-0"><i class="bi bi-bullseye me-2 text-danger"></i>Detected Skill Gaps</h5>
                            <button class="btn btn-sm btn-glass" id="deepRoleGapBtn"><i class="bi bi-search me-1"></i>Role Deep Dive</button>
                        </div>
                        <p class="text-secondary small mb-3">High-priority competencies required to maximize recruitment response rates for your target role:</p>
                        
                        <div class="d-flex flex-wrap gap-2 mb-4">
                            ${(data.skill_gaps || []).map(gap => `
                                <span class="badge bg-danger-subtle border border-danger text-light p-2 small">
                                    <i class="bi bi-plus-circle me-1 text-danger"></i>${gap}
                                </span>
                            `).join('')}
                        </div>

                        <h6 class="text-secondary text-uppercase fw-bold mb-2 small" style="letter-spacing: 0.05em;">Recommended Next Technologies to Learn</h6>
                        <div class="d-flex flex-wrap gap-2">
                            ${(data.recommended_technologies || []).map(tech => `
                                <span class="badge badge-cyan-subtle p-2 small">
                                    <i class="bi bi-code-slash me-1"></i>${tech}
                                </span>
                            `).join('')}
                        </div>
                    </div>
                </div>
            </div>

            <!-- Recommended Roles & Certifications -->
            <div class="row g-4">
                <div class="col-lg-6">
                    <div class="card bg-surface-card p-4">
                        <h5 class="text-light fw-bold mb-3"><i class="bi bi-briefcase me-2 text-secondary"></i>Recommended Career Matches</h5>
                        <div class="list-group list-group-flush bg-transparent">
                            ${(data.recommended_roles || []).map(role => `
                                <div class="list-group-item bg-transparent border-subtle px-0 py-2 d-flex justify-content-between align-items-center">
                                    <span class="text-light fw-semibold"><i class="bi bi-chevron-right text-primary me-2"></i>${role}</span>
                                    <a href="/recommendations?query=${encodeURIComponent(role)}" class="btn btn-sm btn-glass py-0 px-2 small">Find Openings</a>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>

                <div class="col-lg-6">
                    <div class="card bg-surface-card p-4">
                        <h5 class="text-light fw-bold mb-3"><i class="bi bi-patch-check me-2 text-emerald"></i>Target Certifications</h5>
                        <div class="list-group list-group-flush bg-transparent">
                            ${(data.recommended_certifications || []).map(cert => `
                                <div class="list-group-item bg-transparent border-subtle px-0 py-2 d-flex justify-content-between align-items-center">
                                    <span class="text-light"><i class="bi bi-award text-emerald me-2"></i>${cert}</span>
                                    <span class="badge badge-emerald-subtle">High Value</span>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
            </div>
        `;

        renderGaugeChart(data.readiness_score);
        renderRadar();

        const deepRoleBtn = document.getElementById('deepRoleGapBtn');
        if (deepRoleBtn) {
            deepRoleBtn.addEventListener('click', () => {
                const modal = new bootstrap.Modal(document.getElementById('skillGapModal'));
                modal.show();
            });
        }
    }

    function renderGaugeChart(score) {
        const ctx = document.getElementById('caReadinessGauge');
        if (!ctx) return;

        if (gaugeChart) gaugeChart.destroy();
        gaugeChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [score, 100 - score],
                    backgroundColor: [
                        score >= 75 ? '#10B981' : score >= 50 ? '#6366F1' : '#F59E0B',
                        'rgba(255, 255, 255, 0.08)'
                    ],
                    borderWidth: 0,
                    circumference: 260,
                    rotation: 230
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '78%',
                plugins: { legend: { display: false }, tooltip: { enabled: false } }
            }
        });
    }

    function renderRadar() {
        const ctx = document.getElementById('caRadarChart');
        if (!ctx) return;

        if (radarChart) radarChart.destroy();
        radarChart = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: ['Programming Core', 'System Design', 'Cloud & DevOps', 'Databases / SQL', 'DSA & Problem Solving', 'Modern Frameworks'],
                datasets: [
                    {
                        label: 'Your Current Profile',
                        data: [85, 45, 40, 75, 70, 80],
                        backgroundColor: 'rgba(99, 102, 241, 0.25)',
                        borderColor: '#6366F1',
                        borderWidth: 2,
                        pointBackgroundColor: '#6366F1'
                    },
                    {
                        label: 'Target Industry Benchmark',
                        data: [90, 80, 75, 85, 85, 85],
                        backgroundColor: 'rgba(6, 182, 212, 0.15)',
                        borderColor: '#06B6D4',
                        borderWidth: 2,
                        borderDash: [4, 4],
                        pointBackgroundColor: '#06B6D4'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    r: {
                        angleLines: { color: 'rgba(255, 255, 255, 0.1)' },
                        grid: { color: 'rgba(255, 255, 255, 0.08)' },
                        pointLabels: { color: '#9CA3AF', font: { size: 11, family: 'Plus Jakarta Sans' } },
                        ticks: { display: false, min: 0, max: 100 }
                    }
                },
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: '#D1D5DB', boxWidth: 12, padding: 15 }
                    }
                }
            }
        });
    }

    // Role-specific Skill Gap Form submission
    const roleGapForm = document.getElementById('roleGapForm');
    if (roleGapForm) {
        roleGapForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const role = document.getElementById('targetRoleInput').value.trim();
            if (!role) return;

            window.api.showAILoader(`Analyzing specific requirements and skill gaps for ${role}...`);
            try {
                const res = await window.api.post('/career-analysis/skill-gap', { target_role: role });
                window.api.hideAILoader();

                const resultsDiv = document.getElementById('roleGapResults');
                if (resultsDiv) {
                    const d = res.data;
                    resultsDiv.classList.remove('d-none');
                    resultsDiv.innerHTML = `
                        <div class="card bg-surface-elevated p-3 border border-subtle mt-3">
                            <h6 class="text-light fw-bold mb-2">Learning Roadmap for: <span class="text-primary">${d.target_role}</span></h6>
                            <p class="small text-muted mb-2"><i class="bi bi-clock me-1"></i>Estimated time to bridge gap: <b>${d.estimated_time_to_close_gap}</b></p>
                            
                            <div class="mb-3">
                                <small class="text-secondary fw-semibold d-block mb-1">Missing Critical Competencies:</small>
                                ${(d.missing_critical_skills || []).map(s => `<span class="badge bg-danger-subtle border border-danger text-light me-1 mb-1">${s}</span>`).join('')}
                            </div>

                            <div class="mb-2">
                                <small class="text-secondary fw-semibold d-block mb-1">Actionable Learning Steps:</small>
                                <ol class="small text-secondary ps-3 mb-0">
                                    ${(d.recommended_learning_path || []).map(st => `<li class="mb-1">${st}</li>`).join('')}
                                </ol>
                            </div>
                        </div>
                    `;
                }
            } catch (err) {
                window.api.hideAILoader();
            }
        });
    }

    loadAnalysis();
});
