import pymysql
import sys

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def view_db():
    conn = pymysql.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        password='root',
        database='career_dna_ai',
        cursorclass=pymysql.cursors.DictCursor
    )
    cursor = conn.cursor()

    print("=" * 80)
    print(" [*] CAREER DNA AI - MYSQL DATABASE VIEWER")
    print("=" * 80)

    # 1. Tables List
    cursor.execute("SHOW TABLES;")
    tables = [list(row.values())[0] for row in cursor.fetchall()]
    print(f"\n[+] Total Tables ({len(tables)}): {', '.join(tables)}\n")

    # 2. Users Table
    print("-" * 80)
    print("TABLE: users")
    print("-" * 80)
    cursor.execute("SELECT id, email, role, is_active, created_at FROM users;")
    for u in cursor.fetchall():
        print(f"ID: {u['id']:<3} | Email: {u['email']:<25} | Role: {u['role']:<8} | Active: {u['is_active']} | Created: {u['created_at']}")

    # 3. Student Profiles Table
    print("\n" + "-" * 80)
    print("TABLE: student_profiles")
    print("-" * 80)
    cursor.execute("SELECT id, user_id, full_name, college_name, degree, branch, cgpa, profile_completion_pct, target_role FROM student_profiles;")
    for p in cursor.fetchall():
        print(f"Profile ID: {p['id']} (User #{p['user_id']}) | Name: {p['full_name']}")
        print(f"  College: {p['college_name']} | Degree: {p['degree']} in {p['branch']} | CGPA: {p['cgpa']}")
        print(f"  Target Role: {p['target_role']} | Profile Completeness: {p['profile_completion_pct']}%")

    # 4. Student Skills
    print("\n" + "-" * 80)
    print("TABLE: student_skills")
    print("-" * 80)
    cursor.execute("SELECT student_id, skill_name, proficiency_level, years_of_experience FROM student_skills LIMIT 10;")
    skills = cursor.fetchall()
    for s in skills:
        print(f"  - {s['skill_name']:<20} | Proficiency: {s['proficiency_level']:<12} | Experience: {s['years_of_experience']} yrs")
    if len(skills) >= 10:
        print("    ... (and more)")

    # 5. Opportunities Table
    print("\n" + "-" * 80)
    print("TABLE: opportunities (Sample 6 of 18+)")
    print("-" * 80)
    cursor.execute("SELECT id, title, company_name, opportunity_type, location, stipend_salary, status FROM opportunities LIMIT 6;")
    for o in cursor.fetchall():
        print(f"[{o['opportunity_type'].upper():<12}] ID #{o['id']:<2} | {o['title']:<40} | Company: {o['company_name']}")
        print(f"              Location: {o['location']:<25} | Comp: {o['stipend_salary']:<20} | Status: {o['status']}")

    # 6. Applications Table
    print("\n" + "-" * 80)
    print("TABLE: applications (Kanban Tracker)")
    print("-" * 80)
    cursor.execute("SELECT id, student_id, company_name, position_title, opportunity_type, status, applied_date, salary_offered FROM applications;")
    apps = cursor.fetchall()
    if not apps:
        print("  No applications recorded yet.")
    for a in apps:
        print(f"App #{a['id']:<2} | {a['position_title']} at {a['company_name']} ({a['opportunity_type']})")
        print(f"        Stage: {a['status'].upper():<20} | Applied: {a['applied_date']} | Salary/Stipend: {a['salary_offered']}")

    # 7. AI Career Analysis & Readiness Score
    print("\n" + "-" * 80)
    print("TABLE: career_analyses")
    print("-" * 80)
    cursor.execute("SELECT id, student_id, readiness_score, ai_summary, created_at FROM career_analyses ORDER BY id DESC LIMIT 1;")
    analysis = cursor.fetchone()
    if analysis:
        print(f"Analysis #{analysis['id']} for Student #{analysis['student_id']} | Readiness Score: {analysis['readiness_score']}/100")
        print(f"AI Summary: {analysis['ai_summary']}")
    else:
        print("  No AI analysis run yet.")

    print("\n" + "=" * 80)
    conn.close()

if __name__ == '__main__':
    view_db()
