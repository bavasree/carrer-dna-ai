import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable

class PDFService:
    """
    Generates high quality, ATS-compliant PDF resumes using ReportLab.
    Features structured two-column aligned tables, balanced margins,
    crisp section dividers, and robust formatting for internships & placements.
    """

    def generate_resume_pdf(self, resume_obj, profile_obj, template='modern'):
        """
        Generates PDF stream from Resume and StudentProfile models.
        Returns a BytesIO buffer.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        elements = []
        styles = getSampleStyleSheet()

        # Extract content data
        content_data = resume_obj.content_data if resume_obj and resume_obj.content_data else {}
        full_name = content_data.get('full_name') or (profile_obj.full_name if profile_obj else 'Student Name')
        email = content_data.get('email') or (profile_obj.user.email if profile_obj and profile_obj.user else '')
        phone = content_data.get('phone') or (profile_obj.phone if profile_obj else '')
        headline = content_data.get('headline') or (profile_obj.headline if profile_obj else 'Software Engineer')
        github_url = content_data.get('github_url') or (profile_obj.github_url if profile_obj else '')
        linkedin_url = content_data.get('linkedin_url') or (profile_obj.linkedin_url if profile_obj else '')
        career_obj = resume_obj.career_objective if resume_obj and resume_obj.career_objective else (profile_obj.bio if profile_obj else '')

        # Education
        degree = profile_obj.degree if profile_obj else 'B.Tech'
        branch = profile_obj.branch if profile_obj else 'Computer Science'
        college = profile_obj.college_name if profile_obj else 'University'
        grad_year = str(profile_obj.graduation_year) if profile_obj and profile_obj.graduation_year else '2026'
        cgpa = str(profile_obj.cgpa) if profile_obj and profile_obj.cgpa else ''

        # Skills
        skills_list = []
        if profile_obj:
            skills_list = [s.skill_name for s in profile_obj.skills.all()]
        if not skills_list and resume_obj and resume_obj.skills_summary:
            skills_list = [s.strip() for s in resume_obj.skills_summary.split(',') if s.strip()]

        # Projects
        projects = []
        if profile_obj:
            projects = profile_obj.projects.all()

        # Certifications
        certifications = []
        if profile_obj:
            certifications = profile_obj.certifications.all()

        if template == 'classic':
            self._build_classic_resume(
                elements, styles, full_name, email, phone, headline, github_url, linkedin_url,
                career_obj, degree, branch, college, grad_year, cgpa, skills_list, projects, certifications
            )
        else:
            self._build_modern_resume(
                elements, styles, full_name, email, phone, headline, github_url, linkedin_url,
                career_obj, degree, branch, college, grad_year, cgpa, skills_list, projects, certifications
            )

        doc.build(elements)
        buffer.seek(0)
        return buffer

    def _build_modern_resume(self, elements, styles, name, email, phone, headline, github, linkedin,
                             career_obj, degree, branch, college, grad_year, cgpa, skills, projects, certs):
        """Modern sleek resume with deep navy accents and aligned two-column table elements."""
        PRIMARY_COLOR = colors.HexColor('#1E3A8A')  # Deep navy
        SECONDARY_COLOR = colors.HexColor('#2563EB')# Vibrant royal blue
        TEXT_DARK = colors.HexColor('#0F172A')
        TEXT_MUTED = colors.HexColor('#475569')

        usable_width = 540  # 612 - 72

        title_style = ParagraphStyle(
            'ModernTitle',
            fontName='Helvetica-Bold',
            fontSize=20,
            leading=24,
            textColor=PRIMARY_COLOR
        )
        headline_style = ParagraphStyle(
            'ModernHeadline',
            fontName='Helvetica-Bold',
            fontSize=10.5,
            leading=13,
            textColor=SECONDARY_COLOR
        )
        contact_style = ParagraphStyle(
            'ModernContact',
            fontName='Helvetica',
            fontSize=8.5,
            leading=11,
            textColor=TEXT_MUTED
        )
        section_heading = ParagraphStyle(
            'ModernSection',
            fontName='Helvetica-Bold',
            fontSize=11,
            leading=14,
            textColor=PRIMARY_COLOR,
            spaceBefore=8,
            spaceAfter=3,
            keepWithNext=True
        )
        body_style = ParagraphStyle(
            'ModernBody',
            fontName='Helvetica',
            fontSize=9,
            leading=12.5,
            textColor=TEXT_DARK
        )
        bold_left = ParagraphStyle(
            'ModernBoldLeft',
            fontName='Helvetica-Bold',
            fontSize=9.5,
            leading=12.5,
            textColor=TEXT_DARK
        )
        muted_right = ParagraphStyle(
            'ModernMutedRight',
            fontName='Helvetica',
            fontSize=8.5,
            leading=12.5,
            alignment=2,  # Right align
            textColor=TEXT_MUTED
        )
        bullet_style = ParagraphStyle(
            'ModernBullet',
            fontName='Helvetica',
            fontSize=8.5,
            leading=11.5,
            leftIndent=12,
            firstLineIndent=-8,
            textColor=TEXT_DARK
        )

        # Header
        elements.append(Paragraph(name.upper(), title_style))
        if headline:
            elements.append(Paragraph(headline, headline_style))
        elements.append(Spacer(1, 2))

        # Contact info line
        contact_parts = []
        if email: contact_parts.append(f"Email: {email}")
        if phone: contact_parts.append(f"Phone: {phone}")
        if github: contact_parts.append(f"GitHub: {github}")
        if linkedin: contact_parts.append(f"LinkedIn: {linkedin}")
        elements.append(Paragraph(" • ".join(contact_parts), contact_style))
        elements.append(Spacer(1, 4))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY_COLOR, spaceAfter=6, spaceBefore=2))

        # Career Objective / Summary
        if career_obj:
            elements.append(Paragraph("PROFESSIONAL SUMMARY", section_heading))
            elements.append(Paragraph(career_obj, body_style))
            elements.append(Spacer(1, 4))

        # Education (Two-Column Table)
        elements.append(Paragraph("EDUCATION", section_heading))
        left_edu = Paragraph(f"<b>{degree} in {branch}</b><br/><font color='#475569'>{college}</font>", bold_left)
        cgpa_str = f" | CGPA: {cgpa}/10.0" if cgpa else ""
        right_edu = Paragraph(f"<b>Graduation: {grad_year}</b><br/>{cgpa_str}", muted_right)
        
        edu_table = Table([[left_edu, right_edu]], colWidths=[usable_width * 0.68, usable_width * 0.32])
        edu_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 1),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ]))
        elements.append(edu_table)
        elements.append(Spacer(1, 4))

        # Technical Skills
        if skills:
            elements.append(Paragraph("TECHNICAL COMPETENCIES", section_heading))
            skills_str = " • ".join(skills)
            elements.append(Paragraph(f"<b>Core Technologies:</b> {skills_str}", body_style))
            elements.append(Spacer(1, 4))

        # Projects
        if projects:
            elements.append(Paragraph("TECHNICAL & CAPSTONE PROJECTS", section_heading))
            for proj in projects:
                left_proj = Paragraph(f"<b>{proj.title}</b>", bold_left)
                right_proj_text = f"<i>{proj.tech_stack}</i>" if proj.tech_stack else ""
                right_proj = Paragraph(right_proj_text, muted_right)

                proj_table = Table([[left_proj, right_proj]], colWidths=[usable_width * 0.55, usable_width * 0.45])
                proj_table.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('TOPPADDING', (0, 0), (-1, -1), 1),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
                ]))
                elements.append(proj_table)

                # Process bullets
                desc = proj.description or ""
                lines = [l.strip() for l in desc.split('\n') if l.strip()]
                for line in lines:
                    bullet_text = line if line.startswith('•') else f"• {line}"
                    elements.append(Paragraph(bullet_text, bullet_style))

                # Links
                links = []
                if proj.github_url: links.append(f"Repository: {proj.github_url}")
                if proj.live_url: links.append(f"Live Demo: {proj.live_url}")
                if links:
                    elements.append(Paragraph(" | ".join(links), contact_style))
                elements.append(Spacer(1, 3))

        # Certifications
        if certs:
            elements.append(Paragraph("CERTIFICATIONS & ACCREDITATIONS", section_heading))
            for cert in certs:
                issue = f" — Issued by {cert.issuing_organization}" if cert.issuing_organization else ""
                elements.append(Paragraph(f"• <b>{cert.title}</b>{issue}", body_style))
            elements.append(Spacer(1, 4))

    def _build_classic_resume(self, elements, styles, name, email, phone, headline, github, linkedin,
                             career_obj, degree, branch, college, grad_year, cgpa, skills, projects, certs):
        """Classic ATS-optimized single-column traditional layout."""
        usable_width = 540

        name_style = ParagraphStyle(
            'ClassicName',
            fontName='Times-Bold',
            fontSize=17,
            leading=20,
            alignment=1,  # Centered
            textColor=colors.black
        )
        contact_style = ParagraphStyle(
            'ClassicContact',
            fontName='Times-Roman',
            fontSize=9,
            leading=12,
            alignment=1,
            textColor=colors.black
        )
        section_style = ParagraphStyle(
            'ClassicSection',
            fontName='Times-Bold',
            fontSize=10.5,
            leading=14,
            spaceBefore=7,
            spaceAfter=2,
            textColor=colors.black,
            keepWithNext=True
        )
        body_style = ParagraphStyle(
            'ClassicBody',
            fontName='Times-Roman',
            fontSize=9.5,
            leading=13,
            textColor=colors.black
        )
        bold_left = ParagraphStyle(
            'ClassicBoldLeft',
            fontName='Times-Bold',
            fontSize=9.5,
            leading=13,
            textColor=colors.black
        )
        muted_right = ParagraphStyle(
            'ClassicRight',
            fontName='Times-Italic',
            fontSize=9,
            leading=13,
            alignment=2,
            textColor=colors.black
        )
        bullet_style = ParagraphStyle(
            'ClassicBullet',
            fontName='Times-Roman',
            fontSize=9,
            leading=12,
            leftIndent=12,
            firstLineIndent=-8,
            textColor=colors.black
        )

        # Header
        elements.append(Paragraph(name.upper(), name_style))
        contact_parts = []
        if email: contact_parts.append(email)
        if phone: contact_parts.append(phone)
        if linkedin: contact_parts.append(linkedin)
        if github: contact_parts.append(github)
        elements.append(Paragraph(" • ".join(contact_parts), contact_style))
        elements.append(Spacer(1, 3))
        elements.append(HRFlowable(width="100%", thickness=0.75, color=colors.black, spaceAfter=5, spaceBefore=2))

        if career_obj:
            elements.append(Paragraph("OBJECTIVE", section_style))
            elements.append(Paragraph(career_obj, body_style))
            elements.append(Spacer(1, 3))

        # Education
        elements.append(Paragraph("EDUCATION", section_style))
        left_edu = Paragraph(f"<b>{college}</b> — {degree} in {branch}", bold_left)
        cgpa_str = f"CGPA: {cgpa}/10.0" if cgpa else f"Class of {grad_year}"
        right_edu = Paragraph(f"{grad_year} | {cgpa_str}", muted_right)
        
        edu_table = Table([[left_edu, right_edu]], colWidths=[usable_width * 0.65, usable_width * 0.35])
        edu_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 1),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ]))
        elements.append(edu_table)
        elements.append(Spacer(1, 3))

        if skills:
            elements.append(Paragraph("TECHNICAL SKILLS", section_style))
            elements.append(Paragraph(", ".join(skills), body_style))
            elements.append(Spacer(1, 3))

        if projects:
            elements.append(Paragraph("PROJECTS", section_style))
            for proj in projects:
                left_proj = Paragraph(f"<b>{proj.title}</b>", bold_left)
                right_proj = Paragraph(f"<i>{proj.tech_stack or ''}</i>", muted_right)

                proj_table = Table([[left_proj, right_proj]], colWidths=[usable_width * 0.55, usable_width * 0.45])
                proj_table.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('TOPPADDING', (0, 0), (-1, -1), 1),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
                ]))
                elements.append(proj_table)

                desc = proj.description or ""
                lines = [l.strip() for l in desc.split('\n') if l.strip()]
                for line in lines:
                    bullet_text = line if line.startswith('•') else f"• {line}"
                    elements.append(Paragraph(bullet_text, bullet_style))
                elements.append(Spacer(1, 2))

        if certs:
            elements.append(Paragraph("CERTIFICATIONS", section_style))
            for cert in certs:
                elements.append(Paragraph(f"• {cert.title} ({cert.issuing_organization or 'Accredited'})", body_style))


# Singleton instance
pdf_service = PDFService()
