import json

data = []
with open("output/courses_url.json", "r") as f:
    data = json.load(f)

combined = []
for li in data:
    combined.extend(li)

combined = list(set(combined))
with open("all_courses_link.json", "w") as f:
    json.dump(combined, f, indent=4)
