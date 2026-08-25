-- Career DNA AI Database Schema
-- Run in MySQL: SOURCE schema.sql; or mysql -u root -p < schema.sql

CREATE DATABASE IF NOT EXISTS career_dna_ai CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE career_dna_ai;

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'student',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_email (email),
    INDEX idx_user_role (role)
) ENGINE=InnoDB;

-- 2. Student Profiles Table
CREATE TABLE IF NOT EXISTS student_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    full_name VARCHAR(150) NOT NULL,
    headline VARCHAR(255) NULL,
    phone VARCHAR(30) NULL,
    college_name VARCHAR(200) NULL,
    degree VARCHAR(100) NULL,
    branch VARCHAR(100) NULL,
    graduation_year INT NULL,
    cgpa FLOAT NULL,
    bio TEXT NULL,
    career_goal VARCHAR(255) NULL,
    target_role VARCHAR(150) NULL,
    interests TEXT NULL,
    profile_completion_pct INT DEFAULT 0,
    github_url VARCHAR(255) NULL,
    linkedin_url VARCHAR(255) NULL,
    portfolio_url VARCHAR(255) NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_profile_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 3. Skills Master Table
CREATE TABLE IF NOT EXISTS skills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    category VARCHAR(50) NOT NULL DEFAULT 'general',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_skill_name (name)
) ENGINE=InnoDB;

-- 4. Student Skills Junction Table
CREATE TABLE IF NOT EXISTS student_skills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    skill_id INT NULL,
    skill_name VARCHAR(100) NOT NULL,
    proficiency_level VARCHAR(20) NOT NULL DEFAULT 'intermediate',
    years_of_experience FLOAT DEFAULT 1.0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_student_skills_profile FOREIGN KEY (student_id) REFERENCES student_profiles (id) ON DELETE CASCADE,
    CONSTRAINT fk_student_skills_master FOREIGN KEY (skill_id) REFERENCES skills (id) ON DELETE SET NULL,
    INDEX idx_student_skill_name (skill_name)
) ENGINE=InnoDB;

-- 5. Student Projects Table
CREATE TABLE IF NOT EXISTS student_projects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    tech_stack VARCHAR(255) NULL,
    github_url VARCHAR(255) NULL,
    live_url VARCHAR(255) NULL,
    role VARCHAR(100) NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_project_profile FOREIGN KEY (student_id) REFERENCES student_profiles (id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 6. Student Certifications Table
CREATE TABLE IF NOT EXISTS student_certifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    issuing_organization VARCHAR(150) NOT NULL,
    issue_date VARCHAR(50) NULL,
    credential_id VARCHAR(150) NULL,
    credential_url VARCHAR(255) NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_cert_profile FOREIGN KEY (student_id) REFERENCES student_profiles (id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 7. Opportunity Categories Table
CREATE TABLE IF NOT EXISTS opportunity_categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    slug VARCHAR(100) NOT NULL UNIQUE,
    icon VARCHAR(50) DEFAULT 'briefcase',
    description TEXT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 8. Opportunities Table
CREATE TABLE IF NOT EXISTS opportunities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category_id INT NULL,
    title VARCHAR(255) NOT NULL,
    company_name VARCHAR(200) NOT NULL,
    opportunity_type VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    location VARCHAR(150) DEFAULT 'Remote',
    is_remote BOOLEAN DEFAULT TRUE,
    stipend_salary VARCHAR(100) NULL,
    deadline DATETIME NULL,
    apply_url VARCHAR(500) NOT NULL,
    required_skills_json TEXT NULL,
    eligibility_criteria TEXT NULL,
    status VARCHAR(20) DEFAULT 'active',
    experience_level VARCHAR(50) DEFAULT 'Any',
    posted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_opportunity_category FOREIGN KEY (category_id) REFERENCES opportunity_categories (id) ON DELETE SET NULL,
    INDEX idx_opp_type (opportunity_type),
    INDEX idx_opp_status (status),
    INDEX idx_opp_title (title)
) ENGINE=InnoDB;

-- 9. Saved Opportunities Table
CREATE TABLE IF NOT EXISTS saved_opportunities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    opportunity_id INT NOT NULL,
    saved_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_saved_student FOREIGN KEY (student_id) REFERENCES student_profiles (id) ON DELETE CASCADE,
    CONSTRAINT fk_saved_opp FOREIGN KEY (opportunity_id) REFERENCES opportunities (id) ON DELETE CASCADE,
    UNIQUE KEY uq_student_saved_opp (student_id, opportunity_id)
) ENGINE=InnoDB;

-- 10. AI Career Analyses Table
CREATE TABLE IF NOT EXISTS career_analyses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    readiness_score INT NOT NULL DEFAULT 50,
    strengths_json TEXT NULL,
    weaknesses_json TEXT NULL,
    skill_gaps_json TEXT NULL,
    recommended_roles_json TEXT NULL,
    recommended_certifications_json TEXT NULL,
    recommended_technologies_json TEXT NULL,
    ai_summary TEXT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_analysis_student FOREIGN KEY (student_id) REFERENCES student_profiles (id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 11. Career Roadmaps Table
CREATE TABLE IF NOT EXISTS career_roadmaps (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    target_role VARCHAR(150) NOT NULL,
    overall_progress INT DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_roadmap_student FOREIGN KEY (student_id) REFERENCES student_profiles (id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 12. Roadmap Milestones Table
CREATE TABLE IF NOT EXISTS roadmap_milestones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    roadmap_id INT NOT NULL,
    stage_number INT NOT NULL DEFAULT 1,
    stage_name VARCHAR(100) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NULL,
    action_items_json TEXT NULL,
    resources_json TEXT NULL,
    is_completed BOOLEAN DEFAULT FALSE,
    completed_at DATETIME NULL,
    CONSTRAINT fk_milestone_roadmap FOREIGN KEY (roadmap_id) REFERENCES career_roadmaps (id) ON DELETE CASCADE,
    INDEX idx_milestone_stage (stage_number)
) ENGINE=InnoDB;

-- 13. Resumes Table
CREATE TABLE IF NOT EXISTS resumes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    title VARCHAR(150) DEFAULT 'My Professional Resume',
    template_name VARCHAR(50) DEFAULT 'modern',
    career_objective TEXT NULL,
    skills_summary TEXT NULL,
    ats_score INT DEFAULT 70,
    ats_feedback_json TEXT NULL,
    content_data_json TEXT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_resume_student FOREIGN KEY (student_id) REFERENCES student_profiles (id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 14. Applications Table
CREATE TABLE IF NOT EXISTS applications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    opportunity_id INT NULL,
    company_name VARCHAR(150) NOT NULL,
    position_title VARCHAR(150) NOT NULL,
    opportunity_type VARCHAR(50) DEFAULT 'job',
    status VARCHAR(30) DEFAULT 'applied',
    applied_date DATE NULL,
    interview_date DATETIME NULL,
    deadline DATE NULL,
    notes TEXT NULL,
    salary_offered VARCHAR(100) NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_app_student FOREIGN KEY (student_id) REFERENCES student_profiles (id) ON DELETE CASCADE,
    CONSTRAINT fk_app_opp FOREIGN KEY (opportunity_id) REFERENCES opportunities (id) ON DELETE SET NULL,
    INDEX idx_app_status (status)
) ENGINE=InnoDB;
