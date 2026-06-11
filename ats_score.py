def calculate_ats_score(resume_text):
    
    score = 0

    text = resume_text.lower()

    if "@" in resume_text:
        score += 15

    if "skills" in text:
        score += 20

    if "project" in text:
        score += 20

    if "internship" in text:
        score += 15

    if "certification" in text:
        score += 15

    if "education" in text:
        score += 15

    return min(score, 100)