from resume_parser import extract_text
from skill_matcher import find_skills

resume_text = extract_text("resume/My_Resume (2).pdf")

skills = find_skills(resume_text)

print("\nDetected Skills:\n")

for skill in skills:
    print("✅", skill)
from skill_matcher import find_skills
from scorer import calculate_score

resume_text = extract_text("resume/My_Resume (2).pdf")

skills = find_skills(resume_text)

score = calculate_score(skills, resume_text)

print("\nDetected Skills:\n")

for skill in skills:
    print("✅", skill)

print(f"\nResume Score: {score}/100")