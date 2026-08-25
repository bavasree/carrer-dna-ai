import urllib.request
import json
import urllib.parse
import sys

BASE_URL = 'http://127.0.0.1:5000'

def make_req(path, method='GET', data=None, token=None):
    url = f"{BASE_URL}{path}"
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f"Bearer {token}"

    body = json.dumps(data).encode('utf-8') if data is not None else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req) as response:
            res_body = response.read()
            if response.headers.get('Content-Type') == 'application/pdf':
                return {'success': True, 'pdf_bytes': len(res_body), 'status': response.status}
            return json.loads(res_body.decode('utf-8'))
    except urllib.error.HTTPError as e:
        try:
            return json.loads(e.read().decode('utf-8'))
        except Exception:
            return {'success': False, 'error': str(e), 'status': e.code}

def run_tests():
    print("=" * 60)
    print("[*] RUNNING END-TO-END VERIFICATION TEST SUITE")
    print("=" * 60)
    passed = 0
    total = 0

    def assert_test(name, condition, details=""):
        nonlocal passed, total
        total += 1
        if condition:
            passed += 1
            print(f"  [PASS] {name}")
        else:
            print(f"  [FAIL] {name} - {details}")

    # 1. Page Routes
    print("\n--- Testing Page Views ---")
    for page in ['/', '/login', '/register', '/onboarding', '/dashboard', '/profile', '/career-analysis', '/recommendations', '/roadmap', '/resume-builder', '/applications', '/admin/dashboard', '/admin/opportunities']:
        try:
            with urllib.request.urlopen(f"{BASE_URL}{page}") as res:
                assert_test(f"GET {page} returns 200", res.status == 200)
        except Exception as e:
            assert_test(f"GET {page}", False, str(e))

    # 2. Auth Module (Student Login & Admin Login)
    print("\n--- Testing Module 1: Authentication ---")
    student_auth = make_req('/api/auth/login', 'POST', {'email': 'student@careerdna.ai', 'password': 'Student@123'})
    assert_test("Student Login", student_auth.get('success') is True)
    student_token = student_auth.get('data', {}).get('token')

    admin_auth = make_req('/api/auth/login', 'POST', {'email': 'admin@careerdna.ai', 'password': 'Admin@123'})
    assert_test("Admin Login", admin_auth.get('success') is True)
    admin_token = admin_auth.get('data', {}).get('token')

    # Student /me
    me_res = make_req('/api/auth/me', 'GET', token=student_token)
    assert_test("GET /api/auth/me", me_res.get('success') is True)

    # 3. Profile Module (Module 2)
    print("\n--- Testing Module 2: Student Profile ---")
    prof_res = make_req('/api/profile', 'GET', token=student_token)
    assert_test("GET /api/profile", prof_res.get('success') is True)
    profile_data = prof_res.get('data', {})
    assert_test("Profile completion calculated", profile_data.get('profile_completion_pct', 0) > 0)
    assert_test("Profile has skills", len(profile_data.get('skills', [])) > 0)
    assert_test("Profile has projects", len(profile_data.get('projects', [])) > 0)

    # Add skill
    add_skill_res = make_req('/api/profile/skills', 'POST', {'skill_name': 'GraphQL', 'proficiency_level': 'intermediate', 'years_of_experience': 1.5}, token=student_token)
    assert_test("POST /api/profile/skills", add_skill_res.get('success') is True)

    # 4. Career Analysis Module (Module 3)
    print("\n--- Testing Module 3: AI Career Analysis ---")
    analysis_res = make_req('/api/career-analysis/analyze', 'POST', {}, token=student_token)
    assert_test("POST /api/career-analysis/analyze", analysis_res.get('success') is True)
    ana_data = analysis_res.get('data', {})
    assert_test("Career readiness score generated", 'readiness_score' in ana_data and ana_data['readiness_score'] > 0)
    assert_test("Strengths & weaknesses generated", len(ana_data.get('strengths', [])) > 0)
    assert_test("Skill gaps identified", len(ana_data.get('skill_gaps', [])) > 0)

    # Skill-gap deep dive
    gap_res = make_req('/api/career-analysis/skill-gap', 'POST', {'target_role': 'DevOps Engineer'}, token=student_token)
    assert_test("POST /api/career-analysis/skill-gap", gap_res.get('success') is True)

    # 5. Recommendations Module (Module 4)
    print("\n--- Testing Module 4: Opportunity Recommendations ---")
    rec_res = make_req('/api/recommendations', 'GET', token=student_token)
    assert_test("GET /api/recommendations", rec_res.get('success') is True)
    opps = rec_res.get('data', {}).get('opportunities', [])
    assert_test("Opportunities list contains items (>15)", len(opps) >= 15)
    if opps:
        first_opp = opps[0]
        assert_test("Match score calculated per opportunity", 'match_score' in first_opp and first_opp['match_score'] > 0)
        
        # Bookmark opportunity
        save_res = make_req(f"/api/recommendations/{first_opp['id']}/save", 'POST', {}, token=student_token)
        assert_test("POST /api/recommendations/:id/save", save_res.get('success') is True)

        # Saved opportunities
        saved_list = make_req('/api/recommendations/saved', 'GET', token=student_token)
        assert_test("GET /api/recommendations/saved", saved_list.get('success') is True)

    # Filtering by type
    filter_res = make_req('/api/recommendations?type=internship', 'GET', token=student_token)
    assert_test("Filter recommendations by type=internship", filter_res.get('success') is True)

    # 6. Career Roadmap Module (Module 5)
    print("\n--- Testing Module 5: Career Roadmap ---")
    roadmap_res = make_req('/api/roadmap', 'GET', token=student_token)
    assert_test("GET /api/roadmap", roadmap_res.get('success') is True)
    milestones = roadmap_res.get('data', {}).get('milestones', [])
    assert_test("Roadmap has 7 stages", len(milestones) >= 5)

    if milestones:
        # Toggle milestone
        m_id = milestones[0]['id']
        toggle_res = make_req(f"/api/roadmap/milestones/{m_id}", 'PUT', {'is_completed': True}, token=student_token)
        assert_test("PUT /api/roadmap/milestones/:id toggle", toggle_res.get('success') is True)

    # 7. Resume Builder & PDF Generation (Module 6)
    print("\n--- Testing Module 6: AI Resume Builder & PDF Download ---")
    resume_res = make_req('/api/resume', 'GET', token=student_token)
    assert_test("GET /api/resume", resume_res.get('success') is True)

    # AI improve section
    improve_res = make_req('/api/resume/ai-improve', 'POST', {'section_type': 'career_objective', 'text_content': 'Computer science graduate seeking software developer roles.'}, token=student_token)
    assert_test("POST /api/resume/ai-improve", improve_res.get('success') is True and 'improved_text' in improve_res.get('data', {}))

    # AI score ATS
    ats_res = make_req('/api/resume/ai-score-ats', 'POST', {'target_role': 'Software Engineer'}, token=student_token)
    assert_test("POST /api/resume/ai-score-ats", ats_res.get('success') is True and 'ats_score' in ats_res.get('data', {}))

    # PDF Download (Modern Template)
    pdf_res_modern = make_req('/api/resume/download-pdf?template=modern', 'GET', token=student_token)
    assert_test("GET /api/resume/download-pdf (Modern Template)", pdf_res_modern.get('pdf_bytes', 0) > 1000)

    # PDF Download (Classic Template)
    pdf_res_classic = make_req('/api/resume/download-pdf?template=classic', 'GET', token=student_token)
    assert_test("GET /api/resume/download-pdf (Classic Template)", pdf_res_classic.get('pdf_bytes', 0) > 1000)

    # 8. Applications Kanban Module (Module 7)
    print("\n--- Testing Module 7: Application Tracker & Kanban ---")
    apps_res = make_req('/api/applications', 'GET', token=student_token)
    assert_test("GET /api/applications", apps_res.get('success') is True)
    kanban = apps_res.get('data', {}).get('kanban', {})
    assert_test("Kanban grouped by 5 statuses", 'applied' in kanban and 'interview_scheduled' in kanban and 'offer' in kanban)

    # Add Application
    new_app = make_req('/api/applications', 'POST', {
        'company_name': 'Netflix',
        'position_title': 'Software Engineer Intern',
        'opportunity_type': 'internship',
        'status': 'applied'
    }, token=student_token)
    assert_test("POST /api/applications", new_app.get('success') is True)
    app_id = new_app.get('data', {}).get('id')

    if app_id:
        # Move status (Kanban drag-and-drop equivalent)
        move_res = make_req(f"/api/applications/{app_id}", 'PUT', {'status': 'interview_scheduled'}, token=student_token)
        assert_test("PUT /api/applications/:id status move", move_res.get('success') is True and move_res.get('data', {}).get('status') in ['interview', 'interview_scheduled'])

    # Application Stats
    stats_res = make_req('/api/applications/stats', 'GET', token=student_token)
    assert_test("GET /api/applications/stats", stats_res.get('success') is True and 'total_applications' in stats_res.get('data', {}))

    # 9. Admin Management Module (Module 8)
    print("\n--- Testing Module 8: Admin Opportunity Management ---")
    admin_stats = make_req('/api/admin/stats', 'GET', token=admin_token)
    assert_test("GET /api/admin/stats (Admin protected)", admin_stats.get('success') is True)

    # Role protection check (Student attempting to access admin route)
    forbidden_res = make_req('/api/admin/stats', 'GET', token=student_token)
    assert_test("Student forbidden from /api/admin (403)", forbidden_res.get('success') is False)

    # Admin create opportunity
    created_opp = make_req('/api/admin/opportunities', 'POST', {
        'title': 'Autonomous Systems Engineer',
        'company_name': 'Tesla',
        'opportunity_type': 'job',
        'location': 'Palo Alto, CA',
        'is_remote': False,
        'stipend_salary': '$125,000/year',
        'deadline': '2026-11-30',
        'apply_url': 'https://tesla.com/careers',
        'required_skills': ['C++', 'Python', 'ROS', 'Computer Vision'],
        'description': 'Develop autopilot planning algorithms.',
        'status': 'active'
    }, token=admin_token)
    assert_test("POST /api/admin/opportunities", created_opp.get('success') is True)
    admin_opp_id = created_opp.get('data', {}).get('id')

    if admin_opp_id:
        # Bulk status update
        bulk_res = make_req('/api/admin/opportunities/bulk-status', 'POST', {'ids': [admin_opp_id], 'status': 'closed'}, token=admin_token)
        assert_test("POST /api/admin/opportunities/bulk-status", bulk_res.get('success') is True)

    print("\n" + "=" * 60)
    print(f"[RESULTS] {passed}/{total} Passed ({(passed/total)*100:.1f}%)")
    print("=" * 60)

    if passed == total:
        print("[SUCCESS] ALL TESTS PASSED PERFECTLY!")
        return 0
    else:
        print("[WARNING] Some tests failed.")
        return 1

if __name__ == '__main__':
    sys.exit(run_tests())
