import pandas as pd

def company_match(company_file, detected_skills):

    company_skills = pd.read_csv(
        company_file,
        header=None
    )[0].tolist()

    matched_skills = []
    missing_skills = []

    for skill in company_skills:

        if skill in detected_skills:
            matched_skills.append(skill)
        else:
            missing_skills.append(skill)

    match_score = int(
        (len(matched_skills) / len(company_skills))
        * 100
    )

    return match_score, matched_skills, missing_skills