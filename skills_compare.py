def compare_skills(resume_skills, jd_skills):
    """
    Compares resume skills with JD skills.
    Returns a dictionary with matched, missing, and extra skills, plus a score.
    """
    # Normalize skills to lowercase for comparison
    r_skills_set = set(s.lower().strip() for s in resume_skills)
    j_skills_set = set(s.lower().strip() for s in jd_skills)
    
    matched = r_skills_set.intersection(j_skills_set)
    missing = j_skills_set.difference(r_skills_set)
    extra = r_skills_set.difference(j_skills_set)
    
    score = 0
    if len(j_skills_set) > 0:
        score = (len(matched) / len(j_skills_set)) * 100
        
    return {
        "matched": list(matched),
        "missing": list(missing),
        "extra": list(extra),
        "score": round(score, 2)
    }
