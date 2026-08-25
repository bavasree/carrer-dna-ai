import logging
import re
from datetime import datetime
from sqlalchemy import or_
from ..models import Opportunity, SavedOpportunity
from .gemini_service import gemini_service

logger = logging.getLogger('career_dna_ai.recommendation')

class RecommendationEngine:
    """
    Hybrid recommendation engine combining rule-based skill overlap pre-filtering
    with Gemini AI semantic scoring, intelligent tokenized query search,
    and automatic real-time deadline filtering.
    """

    def __init__(self):
        pass

    def get_recommendations(self, profile, filters=None, limit=50):
        """
        Main recommendation pipeline:
        1. Fetch active, non-expired opportunities from DB.
        2. Apply optional database/query filters (type, remote, search query, category).
        3. Pre-filter & compute rule-based match scores.
        4. Calculate personalized match metrics for top candidates.
        5. Sort and return ranked list.
        """
        filters = filters or {}
        opp_type = filters.get('type')
        category_id = filters.get('category_id')
        is_remote = filters.get('is_remote')
        search_query = filters.get('query')
        min_match = filters.get('min_match', 0)
        sort_by = filters.get('sort_by', 'match_desc')

        now = datetime.utcnow()

        # Base DB Query: Only active opportunities with future deadlines (or no deadline)
        query = Opportunity.query.filter(
            Opportunity.status == 'active',
            or_(Opportunity.deadline.is_(None), Opportunity.deadline >= now)
        )

        if opp_type and opp_type.lower() != 'all':
            query = query.filter(Opportunity.opportunity_type == opp_type.lower())

        if category_id:
            query = query.filter(Opportunity.category_id == category_id)

        if is_remote is not None and is_remote != '':
            remote_val = str(is_remote).lower() in ['true', '1', 'yes']
            query = query.filter(Opportunity.is_remote == remote_val)

        # Smart Search Query Filter
        if search_query and search_query.strip():
            raw_term = search_query.strip()
            # Clean punctuation and brackets e.g. "(SDE-1)" -> "SDE 1"
            clean_term = re.sub(r'[^\w\s]', ' ', raw_term)
            words = [w.strip() for w in clean_term.split() if len(w.strip()) >= 2]
            
            # Common stop words to deprioritize
            noise_words = {'junior', 'senior', 'trainee', 'intern', 'internship', 'role', 'job', 'level', 'entry', 'the', 'and', 'for', 'in'}
            core_words = [w for w in words if w.lower() not in noise_words]
            if not core_words:
                core_words = words

            # Search with OR conditions across title, company, description, and required skills
            clauses = []
            # 1. Exact phrase match attempt
            clauses.append(Opportunity.title.ilike(f"%{raw_term}%"))
            clauses.append(Opportunity.company_name.ilike(f"%{raw_term}%"))
            clauses.append(Opportunity.description.ilike(f"%{raw_term}%"))
            clauses.append(Opportunity.required_skills_json.ilike(f"%{raw_term}%"))

            # 2. Significant keywords match
            for word in core_words:
                pattern = f"%{word}%"
                clauses.append(Opportunity.title.ilike(pattern))
                clauses.append(Opportunity.company_name.ilike(pattern))
                clauses.append(Opportunity.description.ilike(pattern))
                clauses.append(Opportunity.required_skills_json.ilike(pattern))

            query = query.filter(or_(*clauses))

        opportunities = query.all()

        if not profile:
            # If no student profile, return raw opportunities with baseline score
            results = []
            for opp in opportunities[:limit]:
                data = opp.to_dict()
                data['match_score'] = 50
                data['matched_skills'] = []
                data['missing_skills'] = opp.required_skills
                data['reasons'] = ["Standard recommendation based on active listings."]
                results.append(data)
            return results

        profile_data = profile.to_dict()

        # Score opportunities
        scored_opportunities = []
        for opp in opportunities:
            opp_dict = opp.to_dict(student_id=profile.id)
            score_data = gemini_service.calculate_match_score(profile_data, opp_dict)
            
            opp_dict['match_score'] = score_data.get('match_score', 50)
            opp_dict['matched_skills'] = score_data.get('matched_skills', [])
            opp_dict['missing_skills'] = score_data.get('missing_skills', [])
            opp_dict['reasons'] = score_data.get('reasons', [])
            
            if opp_dict['match_score'] >= int(min_match or 0):
                scored_opportunities.append(opp_dict)

        # Sorting
        if sort_by == 'match_desc':
            scored_opportunities.sort(key=lambda x: x['match_score'], reverse=True)
        elif sort_by == 'match_asc':
            scored_opportunities.sort(key=lambda x: x['match_score'])
        elif sort_by == 'deadline_asc':
            scored_opportunities.sort(key=lambda x: (x['deadline'] is None, x['deadline']))
        elif sort_by == 'newest':
            scored_opportunities.sort(key=lambda x: x['created_at'] or '', reverse=True)

        return scored_opportunities[:limit]


# Singleton instance
recommendation_engine = RecommendationEngine()
