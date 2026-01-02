def filter_courses_data(data: dict):
    return {
        "id": data.get("id"),
        "title": data.get("title"),
        "headline": data.get("headline"),
        "url": data.get("url"),
        "price": data.get("price"),
        "instructor": {
            "name": data.get("visible_instructors", [{}])[0].get("display_name"),
            "job_title": data.get("visible_instructors", [{}])[0].get("job_title"),
            "image": data.get("visible_instructors", [{}])[0].get("image_100x100")
        },
        "course_image": data.get("image_750x422"),
        "description": data.get("description"),
        "stats": {
            "avg_rating": data.get("avg_rating"),
            "num_reviews": data.get("num_reviews"),
            "num_subscribers": data.get("num_subscribers"),
            "content_length": data.get("content_info"),
            "num_lectures": data.get("num_published_lectures")
        },
        "category": {
            "primary": data.get("primary_category", {}).get("title"),
            "subcategory": data.get("primary_subcategory", {}).get("title")
        },
        "learning_details": {
            "level": data.get("instructional_level"),
            "requirements": data.get("requirements_data", {}).get("items", []),
            "objectives": data.get("what_you_will_learn_data", {}).get("items", [])
        },
        "features": {
            "has_certificate": data.get("has_certificate"),
            "has_closed_caption": data.get("has_closed_caption"),
            "caption_languages": data.get("caption_languages", [])
        },
        "last_update_date": data.get("last_update_date")
    }


def filter_curriculum_data(data: dict):
    # Access the nested data dictionary
    curriculum_data = data.get("curriculum_context", {}).get("data", {})

    filtered_sections = []
    for section in curriculum_data.get("sections", []):
        # Filter individual lectures within the section
        lectures = [
            {
                "title": item.get("title"),
                "duration": item.get("content_summary"),
                "is_previewable": item.get("can_be_previewed")
            }
            for item in section.get("items", [])
        ]

        # Build the section object
        filtered_sections.append({
            "section_title": section.get("title"),
            "lecture_count": section.get("lecture_count"),
            "content_length": section.get("content_length_text"),
            "lectures": lectures
        })

    return {
        "curriculum": {
            "total_lectures": curriculum_data.get("num_of_published_lectures"),
            "total_estimated_time": curriculum_data.get("estimated_content_length_text"),
            "sections": filtered_sections
        }
    }
