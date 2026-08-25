import sys
import os
from datetime import datetime, timedelta
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.path.insert(0, 'backend')

from app import create_app
from app.models import db, User, Opportunity, Application, StudentProfile

def run_admin_comprehensive_tests():
    print("=" * 75)
    print("[*] RUNNING COMPLETE ADMIN PANEL VERIFICATION & DATABASE SYNC SUITE")
    print("=" * 75)

    app = create_app()
    client = app.test_client()

    def assert_test(name, condition, details=""):
        if condition:
            print(f"  [PASS] {name}")
        else:
            print(f"  [FAIL] {name} - {details}")
            raise AssertionError(f"Test failed: {name} | {details}")

    with app.app_context():
        # 1. Authentication & Security
        print("\n--- 1. Authentication & Role-Guards ---")
        s_res = client.post('/api/auth/login', json={'email': 'student@careerdna.ai', 'password': 'Student@123'})
        s_tok = (s_res.get_json() or {}).get('data', {}).get('token')
        s_headers = {'Authorization': f'Bearer {s_tok}'}

        a_res = client.post('/api/auth/login', json={'email': 'admin@careerdna.ai', 'password': 'Admin@123'})
        a_tok = (a_res.get_json() or {}).get('data', {}).get('token')
        a_headers = {'Authorization': f'Bearer {a_tok}'}

        assert_test("Student Login", s_res.status_code == 200)
        assert_test("Admin Login", a_res.status_code == 200)

        # Security check: Non-admin student blocked from all admin endpoints
        assert_test("Student blocked from /api/admin/stats (403)", client.get('/api/admin/stats', headers=s_headers).status_code == 403)
        assert_test("Student blocked from /api/admin/students (403)", client.get('/api/admin/students', headers=s_headers).status_code == 403)
        assert_test("Student blocked from /api/admin/opportunities (403)", client.get('/api/admin/opportunities', headers=s_headers).status_code == 403)
        assert_test("Student blocked from /api/admin/applications (403)", client.get('/api/admin/applications', headers=s_headers).status_code == 403)
        assert_test("Unauthenticated blocked from admin (401)", client.get('/api/admin/stats').status_code == 401)

        # 2. View Routes
        print("\n--- 2. Admin Page View Routes ---")
        routes = ['/admin', '/admin/dashboard', '/admin/students', '/admin/opportunities', '/admin/applications']
        for r in routes:
            res = client.get(r)
            assert_test(f"GET {r} returns 200 OK", res.status_code == 200)

        # 3. Section 1: Dashboard Metrics & Activity Previews
        print("\n--- 3. Dashboard Metrics & Synchronization ---")
        stats_res = client.get('/api/admin/stats', headers=a_headers)
        assert_test("GET /api/admin/stats returns 200", stats_res.status_code == 200)
        stats = (stats_res.get_json() or {}).get('data', {})
        assert_test("Metric: Total Registered Students present", 'total_students' in stats and stats['total_students'] >= 1)
        assert_test("Metric: Total Opportunities present", 'total_opportunities' in stats and stats['total_opportunities'] >= 1)
        assert_test("Metric: Active Opportunities present", 'active_opportunities' in stats)
        assert_test("Metric: Total Applications present", 'total_applications' in stats)
        assert_test("Recent Students array returned", isinstance(stats.get('recent_students'), list))

        # 4. Section 2: Students Directory, Search & Profile Inspector
        print("\n--- 4. Students Directory & Profile Inspector ---")
        students_res = client.get('/api/admin/students', headers=a_headers)
        assert_test("GET /api/admin/students returns 200", students_res.status_code == 200)
        students = (students_res.get_json() or {}).get('data', {}).get('students', [])
        assert_test("Students list is non-empty", len(students) > 0)
        
        target_student = students[0]
        # Search by student email
        search_res = client.get(f"/api/admin/students?search={target_student['email']}", headers=a_headers)
        assert_test("Search students by email works", len((search_res.get_json() or {}).get('data', {}).get('students', [])) >= 1)
        
        # Profile Inspector
        prof_res = client.get(f"/api/admin/students/{target_student['user_id']}", headers=a_headers)
        assert_test("GET /api/admin/students/<id> returns 200", prof_res.status_code == 200)
        prof_data = (prof_res.get_json() or {}).get('data', {})
        assert_test("Profile includes full details", prof_data.get('profile') is not None)
        assert_test("Profile includes verified skills", isinstance(prof_data.get('skills'), list))
        assert_test("Profile includes student applications", isinstance(prof_data.get('applications'), list))

        # Toggle student active status
        toggle_res = client.put(f"/api/admin/students/{target_student['user_id']}/status", json={'is_active': False}, headers=a_headers)
        assert_test("Deactivate student account returns 200", toggle_res.status_code == 200)
        # Restore active
        client.put(f"/api/admin/students/{target_student['user_id']}/status", json={'is_active': True}, headers=a_headers)

        # 5. Section 3: Opportunities Full CRUD & Database Sync
        print("\n--- 5. Opportunities CRUD & Database Sync ---")
        # Step A: Admin adds Hackathon
        hack_payload = {
            'title': 'Global AI Agentic Hackathon 2026',
            'company_name': 'Google DeepMind & OpenAI',
            'opportunity_type': 'hackathon',
            'location': 'San Francisco / Global Online',
            'is_remote': True,
            'stipend_salary': '$50,000 Prize Pool',
            'deadline': '2026-11-20',
            'apply_url': 'https://example.com/ai-hackathon',
            'required_skills': ['Python', 'Gemini API', 'PyTorch', 'FastAPI'],
            'description': 'Build revolutionary autonomous agentic coding systems.',
            'eligibility_criteria': 'All students worldwide.',
            'status': 'active'
        }
        create_res = client.post('/api/admin/opportunities', json=hack_payload, headers=a_headers)
        assert_test("Admin adds Hackathon (POST returns 201)", create_res.status_code == 201)
        created_opp = (create_res.get_json() or {}).get('data', {})
        opp_id = created_opp.get('id')
        assert_test("Hackathon created with valid ID", opp_id is not None)

        # Step B: Verify MySQL/Database has persisted the record
        db_opp = Opportunity.query.get(opp_id)
        assert_test("Database sync: Hackathon exists in DB", db_opp is not None and db_opp.title == 'Global AI Agentic Hackathon 2026')

        # Step C: Admin fetches single opportunity
        get_single = client.get(f"/api/admin/opportunities/{opp_id}", headers=a_headers)
        assert_test("Admin fetches single opportunity (GET returns 200)", get_single.status_code == 200)

        # Step D: Admin edits deadline & details
        new_deadline_str = '2026-12-31'
        edit_payload = {
            'title': 'Global AI Agentic Hackathon 2026 (Extended)',
            'company_name': 'Google DeepMind & OpenAI',
            'opportunity_type': 'hackathon',
            'stipend_salary': '$75,000 Prize Pool',
            'deadline': new_deadline_str,
            'status': 'active',
            'required_skills': ['Python', 'Gemini API', 'PyTorch', 'FastAPI', 'Docker']
        }
        edit_res = client.put(f"/api/admin/opportunities/{opp_id}", json=edit_payload, headers=a_headers)
        assert_test("Admin edits deadline (PUT returns 200)", edit_res.status_code == 200)

        # Step E: Verify updated deadline in DB
        db.session.refresh(db_opp)
        assert_test("Database sync: Updated deadline reflected in DB", db_opp.deadline.strftime('%Y-%m-%d') == new_deadline_str)
        assert_test("Database sync: Updated title reflected in DB", db_opp.title == 'Global AI Agentic Hackathon 2026 (Extended)')

        # Step F: Bulk Status Update (Deactivate then Activate)
        bulk_res = client.post('/api/admin/opportunities/bulk-status', json={'ids': [opp_id], 'status': 'closed'}, headers=a_headers)
        assert_test("Bulk status update (Deactivate) returns 200", bulk_res.status_code == 200)
        db.session.refresh(db_opp)
        assert_test("Database sync: Status updated to 'closed'", db_opp.status == 'closed')

        bulk_res2 = client.post('/api/admin/opportunities/bulk-status', json={'ids': [opp_id], 'status': 'active'}, headers=a_headers)
        assert_test("Bulk status update (Activate) returns 200", bulk_res2.status_code == 200)
        db.session.refresh(db_opp)
        assert_test("Database sync: Status updated to 'active'", db_opp.status == 'active')

        # Step G: Applicants inspection endpoint
        app_list_res = client.get(f"/api/admin/opportunities/{opp_id}/applicants", headers=a_headers)
        assert_test("GET /api/admin/opportunities/<id>/applicants returns 200", app_list_res.status_code == 200)

        # Step H: Clean Expired Opportunities
        clean_res = client.post('/api/admin/opportunities/clean-expired', json={'action': 'archive'}, headers=a_headers)
        assert_test("POST /api/admin/opportunities/clean-expired returns 200", clean_res.status_code == 200)

        # Step I: Admin deletes opportunity
        del_res = client.delete(f"/api/admin/opportunities/{opp_id}", headers=a_headers)
        assert_test("Admin deletes opportunity (DELETE returns 200)", del_res.status_code == 200)
        assert_test("Database sync: Opportunity removed from DB", Opportunity.query.get(opp_id) is None)

        # 6. Section 4: Applications & Registrations Monitoring
        print("\n--- 6. Applications & Registrations Monitoring ---")
        all_apps_res = client.get('/api/admin/applications', headers=a_headers)
        assert_test("GET /api/admin/applications returns 200", all_apps_res.status_code == 200)
        apps_list = (all_apps_res.get_json() or {}).get('data', {}).get('applications', [])
        assert_test("Applications list returned", isinstance(apps_list, list))

        if len(apps_list) > 0:
            sample_app = apps_list[0]
            assert_test("Application item contains student name", 'student_name' in sample_app)
            assert_test("Application item contains opportunity title", 'opportunity_title' in sample_app)
            assert_test("Application item contains opportunity type", 'opportunity_type' in sample_app)
            assert_test("Application item contains current status", 'status' in sample_app)
            assert_test("Application item contains applied date", 'applied_date' in sample_app)

            # Update stage from Admin Panel
            app_id = sample_app['id']
            new_stage = 'screening'
            update_stg = client.put(f"/api/admin/applications/{app_id}/status", json={'status': new_stage}, headers=a_headers)
            assert_test("Admin updates application stage (PUT returns 200)", update_stg.status_code == 200)

            # Database check
            app_in_db = Application.query.get(app_id)
            assert_test("Database sync: Application stage updated in DB", app_in_db.status == new_stage)

            # Test direct resume document access
            resume_res = client.get(f"/api/applications/{app_id}/resume")
            assert_test("Direct application resume view (/api/applications/<id>/resume) returns 200", resume_res.status_code == 200)
            assert_test("Resume response is application/pdf", resume_res.mimetype == 'application/pdf')

        # 7. Section 5: Resume & Documents PDF Direct Endpoints (No Missing Token Blockers)
        print("\n--- 7. Resume & Documents PDF Direct Access ---")
        student_prof = StudentProfile.query.first()
        if student_prof:
            student_pdf_res = client.get(f"/api/resume/student/{student_prof.id}/pdf")
            assert_test("GET /api/resume/student/<id>/pdf returns 200 PDF", student_pdf_res.status_code == 200 and student_pdf_res.mimetype == 'application/pdf')

        pdf_download_res = client.get("/api/resume/download-pdf?template=modern")
        assert_test("GET /api/resume/download-pdf returns 200 PDF without auth header crash", pdf_download_res.status_code == 200 and pdf_download_res.mimetype == 'application/pdf')

        print("\n" + "=" * 75)
        print("[SUCCESS] ALL ADMIN PANEL WORKFLOWS & DB SYNCS VERIFIED (100%)!")
        print("=" * 75)

if __name__ == '__main__':
    run_admin_comprehensive_tests()
