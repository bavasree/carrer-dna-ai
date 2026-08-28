/**
 * Student Central Dashboard Module
 */

document.addEventListener('DOMContentLoaded', async () => {
    if (!window.api.isAuthenticated()) {
        window.location.href = '/login?redirect=/dashboard';
        return;
    }

    const userNameEl = document.getElementById('dashUserName');
    const userHeadlineEl = document.getElementById('dashUserHeadline');
    const profileCompletenessBar = document.getElementById('profileCompletenessBar');
    const profileCompletenessText = document.getElementById('profileCompletenessText');

    let readinessChart = null;

    try {
        // 1. Fetch Profile
        const profileRes = await window.api.get('/profile');
        const profile = profileRes.data;

        if (userNameEl) userNameEl.textContent = profile.full_name || 'Student';
        if (userHeadlineEl) userHeadlineEl.textContent = profile.headline || profile.career_goal || 'Aspiring Software Professional';

        const compPct = profile.profile_completion_pct || 0;
        if (profileCompletenessBar) profileCompletenessBar.style.width = `${compPct}%`;
        if (profileCompletenessText) profileCompletenessText.textContent = `${compPct}%`;

        // 2. Fetch Latest Career Analysis
        const analysisRes = await window.api.get('/career-analysis');
        const analysis = analysisRes.data;
        const readinessScore = analysis ? analysis.readiness_score : 55;

        renderReadinessGauge(readinessScore);

        const aiSummaryText = document.getElementById('dashAISummary');
        if (aiSummaryText) {
            aiSummaryText.textContent = analysis ? analysis.ai_summary : 'Run your first AI Career Analysis to get personalized diagnostics and readiness feedback.';
        }

        // 3. Fetch Active Hackathons
        loadUpcomingHackathons();

        // 4. Fetch Top Recommendations
        loadTopRecommendations();

        // 5. Fetch Roadmap Progress
        loadRoadmapProgress();

        // 6. Fetch Application Stats
        loadApplicationStats();

    } catch (err) {
        console.error('Error loading dashboard:', err);
    }

    function renderReadinessGauge(score) {
        const ctx = document.getElementById('readinessGaugeChart');
        if (!ctx) return;

        const scoreEl = document.getElementById('dashReadinessScore');
        if (scoreEl) scoreEl.textContent = score;

        if (readinessChart) readinessChart.destroy();

        readinessChart = new Chart(ctx, {
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
                cutout: '80%',
                plugins: {
                    legend: { display: false },
                    tooltip: { enabled: false }
                }
            }
        });
    }

    async function loadUpcomingHackathons() {
        const container = document.getElementById('dashHackathonsContainer');
        if (!container) return;

        try {
            const res = await window.api.get('/recommendations?type=hackathon&limit=3');
            const hackathons = res.data.opportunities || [];

            // Filter out any client-side expired items defensively
            const now = new Date();
            const activeHackathons = hackathons.filter(h => !h.deadline || new Date(h.deadline) >= now);

            if (activeHackathons.length === 0) {
                container.innerHTML = `
                    <div class="col-12 py-4 text-center text-muted small">
                        <i class="bi bi-info-circle me-1.5"></i>No upcoming hackathons found right now. Check back soon!
                    </div>
                `;
                return;
            }

            container.innerHTML = activeHackathons.map(h => {
                let daysLeft = 'Open';
                let closingBadge = '';
                if (h.deadline) {
                    const diffDays = Math.ceil((new Date(h.deadline) - now) / (1000 * 60 * 60 * 24));
                    if (diffDays > 0) {
                        daysLeft = `${diffDays} days left`;
                        if (diffDays <= 7) closingBadge = '<span class="badge bg-danger-subtle border border-danger text-light py-0.5 px-2 ms-1">Closing Soon</span>';
                    } else if (diffDays === 0) {
                        daysLeft = 'Ends Today';
                        closingBadge = '<span class="badge bg-danger-subtle border border-danger text-light py-0.5 px-2 ms-1">Ends Today</span>';
                    }
                }

                return `
                    <div class="col-md-4">
                        <div class="p-3.5 bg-surface-elevated rounded-3 border border-subtle h-100 d-flex flex-column justify-content-between">
                            <div>
                                <div class="d-flex justify-content-between align-items-start mb-2">
                                    <span class="badge badge-amber-subtle text-uppercase fw-bold" style="font-size: 0.72rem;">HACKATHON</span>
                                    <span class="match-score-badge ${h.match_score >= 80 ? 'match-high' : h.match_score >= 60 ? 'match-mid' : ''}" style="font-size: 0.82rem; padding: 0.25rem 0.6rem;">
                                        <i class="bi bi-stars"></i> ${h.match_score}%
                                    </span>
                                </div>
                                <h5 class="text-white fw-bold mb-1 fs-6 text-truncate">${h.title}</h5>
                                <small class="text-secondary d-block mb-2"><i class="bi bi-building me-1"></i>${h.company_name}</small>
                                <p class="text-secondary small mb-2" style="display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; font-size: 0.88rem; line-height: 1.5;">
                                    ${h.description}
                                </p>
                            </div>
                            <div class="pt-2.5 border-top border-subtle d-flex justify-content-between align-items-center mt-2">
                                <small class="text-warning fw-semibold" style="font-size: 0.82rem;"><i class="bi bi-clock me-1"></i>${daysLeft} ${closingBadge}</small>
                                <a href="${h.apply_url}" target="_blank" rel="noopener noreferrer" class="btn btn-sm btn-glass py-1 px-2.5 fw-semibold" style="font-size: 0.82rem;">
                                    Register <i class="bi bi-box-arrow-up-right ms-1"></i>
                                </a>
                            </div>
                        </div>
                    </div>
                `;
            }).join('');
        } catch (err) {
            container.innerHTML = `<div class="col-12 text-muted small text-center">Unable to load hackathons.</div>`;
        }
    }

    async function loadTopRecommendations() {
        const container = document.getElementById('dashRecommendationsContainer');
        if (!container) return;

        try {
            const res = await window.api.get('/recommendations?limit=4');
            const opps = res.data.opportunities || [];

            if (opps.length === 0) {
                container.innerHTML = `
                    <div class="empty-state p-4 text-center">
                        <i class="bi bi-briefcase empty-state-icon"></i>
                        <p class="text-muted mb-0">No matching opportunities found. Update your profile skills to boost match rates!</p>
                    </div>
                `;
                return;
            }

            const now = new Date();

            container.innerHTML = opps.map(opp => {
                let deadlineStr = 'Open Enrollment';
                if (opp.deadline) {
                    const diffDays = Math.ceil((new Date(opp.deadline) - now) / (1000 * 60 * 60 * 24));
                    if (diffDays > 0) deadlineStr = `${diffDays} days remaining`;
                    else if (diffDays === 0) deadlineStr = 'Closing Today';
                }

                return `
                    <div class="card bg-surface-card mb-3 p-3.5 shadow-sm border border-subtle">
                        <div class="d-flex flex-column flex-sm-row justify-content-between align-items-start gap-2 mb-2">
                            <div>
                                <span class="badge badge-primary-subtle text-uppercase mb-1 fw-bold" style="font-size: 0.74rem;">${opp.opportunity_type}</span>
                                <h5 class="mb-1 fw-bold text-white fs-6">${opp.title}</h5>
                                <small class="text-secondary"><i class="bi bi-building me-1"></i>${opp.company_name} &bull; <i class="bi bi-geo-alt me-1"></i>${opp.location}</small>
                            </div>
                            <div class="match-score-badge ${opp.match_score >= 80 ? 'match-high' : opp.match_score >= 60 ? 'match-mid' : ''}">
                                <i class="bi bi-stars"></i> ${opp.match_score}% Match
                            </div>
                        </div>
                        <div class="d-flex justify-content-between align-items-center mt-2.5 pt-2.5 border-top border-subtle">
                            <small class="text-secondary"><i class="bi bi-clock me-1 text-info"></i>Deadline: ${deadlineStr}</small>
                            <a href="/recommendations" class="btn btn-sm btn-glass py-1.5 px-3 fw-semibold">View Details</a>
                        </div>
                    </div>
                `;
            }).join('');

        } catch (err) {
            container.innerHTML = `<div class="alert alert-danger py-2">Failed to load recommendations.</div>`;
        }
    }

    async function loadRoadmapProgress() {
        const progressBar = document.getElementById('dashRoadmapProgressBar');
        const progressText = document.getElementById('dashRoadmapProgressText');
        const milestoneList = document.getElementById('dashRoadmapMilestones');

        try {
            const res = await window.api.get('/roadmap');
            const roadmap = res.data;
            if (!roadmap) return;

            const progress = roadmap.overall_progress || 0;
            if (progressBar) progressBar.style.width = `${progress}%`;
            if (progressText) progressText.textContent = `${progress}% Complete`;

            if (milestoneList && roadmap.milestones) {
                const nextMilestones = roadmap.milestones.slice(0, 3);
                milestoneList.innerHTML = nextMilestones.map(m => `
                    <li class="list-group-item bg-transparent border-0 px-0 py-2.5 d-flex align-items-center">
                        <i class="bi ${m.is_completed ? 'bi-check-circle-fill text-success' : 'bi-circle text-muted'} me-2.5 fs-5"></i>
                        <div class="flex-grow-1">
                            <div class="fw-semibold text-white" style="font-size: 0.95rem;">${m.title}</div>
                            <small class="text-secondary fw-medium">STAGE ${m.stage_number}: ${m.stage_name}</small>
                        </div>
                    </li>
                `).join('');
            }
        } catch (err) {}
    }

    async function loadApplicationStats() {
        try {
            const res = await window.api.get('/applications/stats');
            const stats = res.data;
            if (!stats) return;

            const totalEl = document.getElementById('dashStatTotal');
            const interviewEl = document.getElementById('dashStatInterview');
            const offerEl = document.getElementById('dashStatOffer');

            if (totalEl) totalEl.textContent = stats.total_applications || 0;
            if (interviewEl) interviewEl.textContent = `${stats.interview_rate || 0}%`;
            if (offerEl) offerEl.textContent = `${stats.offer_rate || 0}%`;
        } catch (err) {}
    }
});
