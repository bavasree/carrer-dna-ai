import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.path.insert(0, 'backend')

from app import create_app
from app.models import db, Opportunity, Application, User

def run_tests():
    print("=" * 70)
    print("[*] RUNNING VERIFICATION FOR APPLICATION TRACKER DIRECT ACCESS & SYNC")
    print("=" * 70)

    app = create_app()
    client = app.test_client()

    def assert_test(name, condition, details=""):
        if condition:
            print(f"  [PASS] {name}")
        else:
            print(f"  [FAIL] {name} - {details}")
            raise AssertionError(f"Test failed: {name}")

    with app.app_context():
        # 1. Login Student & Admin
        print("\n--- 1. Authentication ---")
        s_login_res = client.post('/api/auth/login', json={'email': 'student@careerdna.ai', 'password': 'Student@123'})
        s_data = s_login_res.get_json() or {}
        student_token = s_data.get('data', {}).get('token')
        assert_test("Student Login", s_login_res.status_code == 200 and student_token is not None)

        s_headers = {'Authorization': f'Bearer {student_token}'}

        a_login_res = client.post('/api/auth/login', json={'email': 'admin@careerdna.ai', 'password': 'Admin@123'})
        a_data = a_login_res.get_json() or {}
        admin_token = a_data.get('data', {}).get('token')
        assert_test("Admin Login", a_login_res.status_code == 200 and admin_token is not None)

        a_headers = {'Authorization': f'Bearer {admin_token}'}

        # Clear prior test applications
        student_user = User.query.filter_by(email='student@careerdna.ai').first()
        if student_user and student_user.profile:
            Application.query.filter_by(student_id=student_user.profile.id).delete()
            db.session.commit()

        # TEST 1: Direct Access with 0 Applications
        print("\n--- TEST 1: Direct Access with 0 Applications (Empty State) ---")
        zero_res = client.get('/api/applications', headers=s_headers)
        assert_test("GET /api/applications returns 200", zero_res.status_code == 200)
        z_data = zero_res.get_json() or {}
        assert_test("Empty applications array returned", len(z_data.get('data', {}).get('applications', [])) == 0)
        assert_test("Total count is 0", z_data.get('data', {}).get('total_count') == 0)
        assert_test("Workflows configuration returned", 'hackathon' in z_data.get('data', {}).get('workflows', {}))

        zero_stats = client.get('/api/applications/stats', headers=s_headers)
        assert_test("GET /api/applications/stats returns 200", zero_stats.status_code == 200)
        zs_data = zero_stats.get_json() or {}
        assert_test("Stats total is 0", zs_data.get('data', {}).get('total_applications') == 0)

        # TEST 2: Hackathon Registration -> Direct Sync in Tracker
        print("\n--- TEST 2: Hackathon Registration -> Tracker Sync ---")
        hackathon_opp = Opportunity.query.filter_by(opportunity_type='hackathon').first()
        assert_test("Found Hackathon Opportunity in Database", hackathon_opp is not None)

        hack_payload = {
            'opportunity_id': hackathon_opp.id,
            'opportunity_type': 'hackathon',
            'full_name': 'Alex Morgan',
            'email': 'student@careerdna.ai',
            'phone': '+1 555-019-2834',
            'college_name': 'Stanford University',
            'team_name': 'Team ByteCrafters',
            'team_size': '3 Members',
            'team_members': 'Alex Morgan, John Smith, Sarah Lee',
            'hackathon_experience': '3-5 Hackathons',
            'project_track': 'AI & Machine Learning',
            'project_idea': 'Autonomous AI Career Navigation system with direct recruiter pipeline sync.',
            'github_url': 'https://github.com/alexmorgan-ai',
            'linkedin_url': 'https://linkedin.com/in/alexmorgan-ai'
        }
        hack_reg_res = client.post('/api/applications/apply', json=hack_payload, headers=s_headers)
        assert_test("Register for Hackathon returns 201", hack_reg_res.status_code == 201)

        # Open Tracker (Direct API fetch)
        tracker_res = client.get('/api/applications', headers=s_headers).get_json() or {}
        apps = tracker_res.get('data', {}).get('applications', [])
        assert_test("Registered Hackathon immediately appears in Tracker", len(apps) == 1)
        hack_app = apps[0]
        assert_test("Hackathon initial status is 'registered'", hack_app.get('status') == 'registered')
        assert_test("Hackathon opportunity_type is 'hackathon'", hack_app.get('opportunity_type') == 'hackathon')
        assert_test("Hackathon position_title matches opportunity", hack_app.get('position_title') == hackathon_opp.title)
        assert_test("Hackathon submitted details preserved", hack_app.get('submitted_details', {}).get('hackathon_details', {}).get('team_name') == 'Team ByteCrafters')

        # TEST 3: Internship Application -> Direct Sync in Tracker
        print("\n--- TEST 3: Internship Application -> Tracker Sync ---")
        intern_opp = Opportunity.query.filter_by(opportunity_type='internship').first()
        assert_test("Found Internship Opportunity in Database", intern_opp is not None)

        intern_payload = {
            'opportunity_id': intern_opp.id,
            'opportunity_type': 'internship',
            'full_name': 'Alex Morgan',
            'email': 'student@careerdna.ai',
            'phone': '+1 555-019-2834',
            'college_name': 'Stanford University',
            'degree': 'B.S. Computer Science',
            'availability': 'Immediate',
            'preferred_work_mode': 'Remote',
            'preferred_location': 'San Francisco / Remote',
            'resume_source': 'ai_generated',
            'cover_note': 'Enthusiastic full-stack and AI software engineer candidate.'
        }
        intern_res = client.post('/api/applications/apply', json=intern_payload, headers=s_headers)
        assert_test("Apply for Internship returns 201", intern_res.status_code == 201)

        # Open Tracker
        tracker_res2 = client.get('/api/applications', headers=s_headers).get_json() or {}
        apps2 = tracker_res2.get('data', {}).get('applications', [])
        assert_test("Tracker now has 2 opportunities", len(apps2) == 2)
        intern_app = next((a for a in apps2 if a.get('opportunity_type') == 'internship'), None)
        assert_test("Internship found with status = 'applied'", intern_app is not None and intern_app.get('status') == 'applied')

        # TEST 4: Job Application -> Direct Sync in Tracker
        print("\n--- TEST 4: Job Application -> Tracker Sync ---")
        job_opp = Opportunity.query.filter_by(opportunity_type='job').first()
        assert_test("Found Job Opportunity in Database", job_opp is not None)

        job_payload = {
            'opportunity_id': job_opp.id,
            'opportunity_type': 'job',
            'full_name': 'Alex Morgan',
            'email': 'student@careerdna.ai',
            'phone': '+1 555-019-2834',
            'education': 'B.S. Computer Science, Stanford',
            'work_experience_years': 'Fresh Graduate / Entry Level',
            'current_location': 'San Francisco, CA',
            'preferred_location': 'San Francisco / Remote',
            'notice_period': 'Immediate',
            'expected_salary': '$120,000/yr',
            'resume_source': 'ai_generated',
            'cover_letter': 'Experienced in building scalable distributed backends and reactive frontends.'
        }
        job_res = client.post('/api/applications/apply', json=job_payload, headers=s_headers)
        assert_test("Apply for Job returns 201", job_res.status_code == 201)

        # Open Tracker
        tracker_res3 = client.get('/api/applications', headers=s_headers).get_json() or {}
        apps3 = tracker_res3.get('data', {}).get('applications', [])
        assert_test("Tracker now has 3 opportunities", len(apps3) == 3)
        job_app = next((a for a in apps3 if a.get('opportunity_type') == 'job'), None)
        assert_test("Job found with status = 'applied'", job_app is not None and job_app.get('status') == 'applied')

        # TEST 5: Data Persistence Across Re-Login
        print("\n--- TEST 5: Persistence Across Logout & Re-Login ---")
        # Generate new JWT session
        fresh_login = client.post('/api/auth/login', json={'email': 'student@careerdna.ai', 'password': 'Student@123'})
        fresh_token = (fresh_login.get_json() or {}).get('data', {}).get('token')
        fresh_headers = {'Authorization': f'Bearer {fresh_token}'}

        persisted_res = client.get('/api/applications', headers=fresh_headers).get_json() or {}
        persisted_apps = persisted_res.get('data', {}).get('applications', [])
        assert_test("All 3 opportunities persist after fresh login", len(persisted_apps) == 3)
        
        # Verify type-specific kanban categorization
        type_kanban = persisted_res.get('data', {}).get('type_kanban', {})
        assert_test("Hackathon present in type_kanban['hackathon']['registered']",
                    len(type_kanban.get('hackathon', {}).get('registered', [])) == 1)
        assert_test("Internship present in type_kanban['internship']['applied']",
                    len(type_kanban.get('internship', {}).get('applied', [])) == 1)
        assert_test("Job present in type_kanban['job']['applied']",
                    len(type_kanban.get('job', {}).get('applied', [])) == 1)

        # TEST 6: Individual Application Details View
        print("\n--- TEST 6: Application Details Inspector (GET /api/applications/:id) ---")
        app_detail_res = client.get(f"/api/applications/{hack_app['id']}", headers=fresh_headers).get_json() or {}
        assert_test("Fetch specific application by ID", app_detail_res.get('success') is True)
        assert_test("Application detail includes team name", app_detail_res.get('data', {}).get('submitted_details', {}).get('hackathon_details', {}).get('team_name') == 'Team ByteCrafters')

        # TEST 7: Admin Inspection
        print("\n--- TEST 7: Admin Opportunity Applicants View ---")
        admin_res = client.get(f"/api/admin/opportunities/{hackathon_opp.id}/applicants", headers=a_headers).get_json() or {}
        assert_test("Admin sees applicant for Hackathon", len(admin_res.get('data', {}).get('applicants', [])) >= 1)

        print("\n" + "=" * 70)
        print("[SUCCESS] ALL APPLICATION TRACKER & SYNC TESTS PASSED (100%)!")
        print("=" * 70)

if __name__ == '__main__':
    run_tests()
