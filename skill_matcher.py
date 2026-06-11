import pandas as pd

def find_skills(resume_text):

    skills_df = pd.read_csv("skills/skills.csv", header=None)

    skills = skills_df[0].tolist()

    found_skills = []

    resume_text = resume_text.lower()

    for skill in skills:

        if skill.lower() in resume_text:
            found_skills.append(skill)

    return found_skills