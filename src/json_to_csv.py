import pandas as pd
import json
import re
import os

CLEANR = re.compile('<.*?>')


def clean_html(raw_html):
    """Removes HTML tags like <p> and <br> for a cleaner CSV."""
    if not raw_html:
        return ""
    return re.sub(CLEANR, '', raw_html).strip()


def create_csv_rows(json_data):
    cd = json_data.get("course_data", {})

    # 1. Prepare Course-Level Data (Repeating Columns)
    # Joining lists into strings so they fit in a single CSV cell
    objectives = " | ".join(cd.get("learning_details", {}).get("objectives", []))
    requirements = " | ".join(cd.get("learning_details", {}).get("requirements", []))

    course_metadata = {
        "Course ID": cd.get("id"),
        "Course Title": cd.get("title"),
        "Headline": cd.get("headline"),
        "Locale": cd.get("locale"),
        "Full URL": f"https://www.udemy.com{cd.get('url')}",
        "Price": cd.get("price"),
        "Instructor Name": cd.get("instructor", {}).get("name"),
        "Instructor Job": cd.get("instructor", {}).get("job_title"),
        "Avg Rating": cd.get("stats", {}).get("avg_rating"),
        "Subscribers": cd.get("stats", {}).get("num_subscribers"),
        "Total Content": cd.get("stats", {}).get("content_length"),
        "Category": cd.get("category", {}).get("primary"),
        "Subcategory": cd.get("category", {}).get("subcategory"),
        "Learning Level": cd.get("learning_details", {}).get("level"),
        "Course Objectives": objectives,
        "Requirements": requirements,
        "Description": clean_html(cd.get("description", "")),
        "Last Updated": cd.get("last_update_date")
    }

    rows = []

    # 2. Iterate through curriculum to create rows
    sections = json_data.get("curriculum_data", {}).get("curriculum", {}).get("sections", [])

    for section in sections:
        section_title = section.get("section_title")
        for lecture in section.get("lectures", []):
            # Create a full row starting with course metadata
            row = course_metadata.copy()
            row.update({
                "Section Title": section_title,
                "Lecture Title": lecture.get("title"),
                "Lecture Duration": lecture.get("duration"),
                "Is Previewable": lecture.get("is_previewable")
            })
            rows.append(row)

    return rows


def dump_to_csv(path, filename):
    rows = []
    with open(path, 'r') as f:
        datas = json.load(f)
        for i, data in enumerate(datas):
            if data:
                print(i, ":", data["url"])
                row = create_csv_rows(data)
                rows.extend(row)
            else:
                print(i, ":", "null")
        df = pd.DataFrame(rows)
        df.to_csv(f"output_csv/{filename}.csv", index=False, encoding="utf-8-sig")
        print(f"Master CSV created with {len(df.columns)} columns and {len(df)} rows.")  # noqa


if __name__ == "__main__":
    DIR_NAME = "output_json"
    entries = os.scandir(DIR_NAME)
    for entry in entries:
        dump_to_csv(entry.path, entry.name.rstrip(".json"))
