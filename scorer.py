def calculate_score(found_skills, resume_text):
    
    score = 0

    score += min(len(found_skills) * 5, 40)

    if "project" in resume_text.lower():
        score += 20

    if "internship" in resume_text.lower():
        score += 15

    if "certification" in resume_text.lower():
        score += 10

    if "education" in resume_text.lower():
        score += 10

    if "@" in resume_text:
        score += 5

    return min(score, 100)