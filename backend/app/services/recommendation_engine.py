import logging
import re
from datetime import datetime, timedelta
from sqlalchemy import or_
from ..models import Opportunity, SavedOpportunity
from .gemini_service import gemini_service

logger = logging.getLogger('career_dna_ai.recommendation')

class RecommendationEngine:
    """
    Production-grade hybrid recommendation engine combining rule-based multi-facet
    filtering with AI-driven DNA match scoring, deadline tracking, and deep explainability.
    """

    def __init__(self):
        pass

    def get_recommendations(self, profile, filters=None, limit=60):
        """
        Main recommendation pipeline:
        1. Fetch active, non-expired opportunities from DB.
        2. Apply multi-facet database & keyword filters (type, mode, fee, stipend, location, search query, category).
        3. Score opportunities against student's Career DNA (skills, goal, degree, CGPA, projects).
        4. Apply post-scoring filters (min_match, skills chip filter, deadline urgency).
        5. Sort by selected criteria (match %, deadline, compensation/prizes, newest).
        """
        filters = filters or {}
        opp_type = filters.get('type')
        category_id = filters.get('category_id')
        is_remote = filters.get('is_remote')
        mode = filters.get('mode')
        fee = filters.get('fee')
        stipend = filters.get('stipend')
        location = filters.get('location')
        skills_filter = filters.get('skills')
        deadline_status = filters.get('deadline_status')
        search_query = filters.get('query')
        min_match = filters.get('min_match', 0)
        sort_by = filters.get('sort_by', 'match_desc')

        now = datetime.utcnow()

        # Base DB Query: Only active opportunities with future deadlines (or open/no deadline)
        query = Opportunity.query.filter(
            Opportunity.status == 'active',
            or_(Opportunity.deadline.is_(None), Opportunity.deadline >= now)
        )

        # 1. Opportunity Type Filter
        if opp_type and opp_type.lower() != 'all':
            query = query.filter(Opportunity.opportunity_type == opp_type.lower())

        # 2. Category Filter
        if category_id:
            query = query.filter(Opportunity.category_id == category_id)

        # 3. Mode Filter (Online, Offline, Hybrid, Remote)
        if mode and mode.lower() != 'all':
            m_lower = mode.lower()
            if m_lower == 'remote' or m_lower == 'online':
                query = query.filter(or_(Opportunity.is_remote == True, Opportunity.event_mode.ilike('%online%'), Opportunity.event_mode.ilike('%remote%')))
            elif m_lower == 'offline':
                query = query.filter(Opportunity.event_mode.ilike('%offline%'))
            elif m_lower == 'hybrid':
                query = query.filter(Opportunity.event_mode.ilike('%hybrid%'))

        # 4. Is Remote Boolean Fallback
        if is_remote is not None and is_remote != '':
            remote_val = str(is_remote).lower() in ['true', '1', 'yes']
            query = query.filter(Opportunity.is_remote == remote_val)

        # 5. Registration Fee Filter (Free vs Paid)
        if fee and fee.lower() != 'all':
            if fee.lower() == 'free':
                query = query.filter(or_(
                    Opportunity.registration_fee.ilike('%free%'),
                    Opportunity.registration_fee.is_(None),
                    Opportunity.registration_fee == '0'
                ))
            elif fee.lower() == 'paid':
                query = query.filter(
                    ~Opportunity.registration_fee.ilike('%free%'),
                    Opportunity.registration_fee.isnot(None),
                    Opportunity.registration_fee != ''
                )

        # 6. Location Filter
        if location and location.strip():
            loc_term = location.strip()
            query = query.filter(or_(
                Opportunity.location.ilike(f"%{loc_term}%"),
                Opportunity.venue_address.ilike(f"%{loc_term}%")
            ))

        # 7. Smart Multi-Field Keyword Search
        if search_query and search_query.strip():
            raw_term = search_query.strip()
            clean_term = re.sub(r'[^\w\s]', ' ', raw_term)
            words = [w.strip() for w in clean_term.split() if len(w.strip()) >= 2]
            
            noise_words = {'junior', 'senior', 'trainee', 'intern', 'internship', 'role', 'job', 'level', 'entry', 'the', 'and', 'for', 'in'}
            core_words = [w for w in words if w.lower() not in noise_words]
            if not core_words:
                core_words = words

            clauses = []
            # Exact phrase match
            clauses.append(Opportunity.title.ilike(f"%{raw_term}%"))
            clauses.append(Opportunity.company_name.ilike(f"%{raw_term}%"))
            clauses.append(Opportunity.description.ilike(f"%{raw_term}%"))
            clauses.append(Opportunity.required_skills_json.ilike(f"%{raw_term}%"))
            clauses.append(Opportunity.location.ilike(f"%{raw_term}%"))
            clauses.append(Opportunity.venue_address.ilike(f"%{raw_term}%"))

            # Significant word match
            for word in core_words:
                pattern = f"%{word}%"
                clauses.append(Opportunity.title.ilike(pattern))
                clauses.append(Opportunity.company_name.ilike(pattern))
                clauses.append(Opportunity.description.ilike(pattern))
                clauses.append(Opportunity.required_skills_json.ilike(pattern))

            query = query.filter(or_(*clauses))

        opportunities = query.all()

        profile_data = profile.to_dict() if profile else {}
        student_id = profile.id if profile else None

        # Score opportunities & extract complete metadata
        scored_opportunities = []
        for opp in opportunities:
            opp_dict = opp.to_dict(student_id=student_id)
            
            if profile:
                score_data = gemini_service.calculate_match_score(profile_data, opp_dict)
                opp_dict['match_score'] = score_data.get('match_score', 50)
                opp_dict['matched_skills'] = score_data.get('matched_skills', [])
                opp_dict['missing_skills'] = score_data.get('missing_skills', [])
                opp_dict['reasons'] = score_data.get('reasons', [])
                opp_dict['preparation_tips'] = score_data.get('preparation_tips', [])
                opp_dict['dna_breakdown'] = score_data.get('dna_breakdown', {})
            else:
                opp_dict['match_score'] = 50
                opp_dict['matched_skills'] = []
                opp_dict['missing_skills'] = opp.required_skills
                opp_dict['reasons'] = ["Standard recommendation based on active listings."]
                opp_dict['preparation_tips'] = ["Review required skills and register before the deadline."]
                opp_dict['dna_breakdown'] = {"skill_match": 50, "goal_alignment": 50, "eligibility_fit": 50, "experience_fit": 50}

            # Filter: min_match
            if min_match and int(min_match) > 0 and opp_dict['match_score'] < int(min_match):
                continue

            # Filter: skills chip filter
            if skills_filter:
                filter_skill_list = [s.strip().lower() for s in skills_filter.split(',') if s.strip()]
                opp_skills = [s.lower() for s in (opp_dict.get('required_skills') or [])]
                if not any(fs in ' '.join(opp_skills) for fs in filter_skill_list):
                    continue

            # Filter: urgent deadlines (< 7 days)
            if deadline_status == 'urgent':
                if not opp.deadline:
                    continue
                diff_days = (opp.deadline - now).total_seconds() / (24 * 3600)
                if diff_days > 7 or diff_days < 0:
                    continue

            scored_opportunities.append(opp_dict)

        # Sorting
        if sort_by == 'match_desc':
            scored_opportunities.sort(key=lambda x: x['match_score'], reverse=True)
        elif sort_by == 'match_asc':
            scored_opportunities.sort(key=lambda x: x['match_score'])
        elif sort_by == 'deadline_asc':
            scored_opportunities.sort(key=lambda x: (x['deadline'] is None, x['deadline'] or '9999'))
        elif sort_by == 'newest':
            scored_opportunities.sort(key=lambda x: x['created_at'] or '', reverse=True)
        elif sort_by == 'title_asc':
            scored_opportunities.sort(key=lambda x: x['title'].lower())

        return scored_opportunities[:limit]

    def get_opportunity_detail(self, opp_id, profile=None):
        """Retrieve full details for a single opportunity including Career DNA match diagnostics."""
        opp = Opportunity.query.get(opp_id)
        if not opp:
            return None

        student_id = profile.id if (profile and hasattr(profile, 'id')) else (profile.get('id') if isinstance(profile, dict) else None)
        profile_dict = profile.to_dict() if (profile and hasattr(profile, 'to_dict')) else (profile or {})

        opp_data = opp.to_dict(student_id=student_id)
        if profile_dict:
            match_info = gemini_service.calculate_match_score(profile_dict, opp_data)
            opp_data.update(match_info)
        return opp_data


# Singleton instance
recommendation_engine = RecommendationEngine()


