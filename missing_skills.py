import pandas as pd

def find_missing_skills(found_skills):

    skills_df = pd.read_csv(
        "skills/skills.csv",
        header=None
    )

    all_skills = skills_df[0].tolist()

    missing_skills = []

    for skill in all_skills:

        if skill not in found_skills:
            missing_skills.append(skill)

    return missing_skills