import json
from botasaurus.browser import browser, Driver
from my_log import MyLog


mylog = MyLog()
log = mylog.log
log_time = mylog.log_time


def get_courses_links():
    courses_link_path = "all_courses_link.json"
    links = []
    with open(courses_link_path, "r") as f:
        links = json.load(f)
    return links


@browser(
        output="test_5_course_data",
        parallel=5,
        max_retry=5
        )
def get_course_data(driver: Driver, data):
    slug = data.rstrip("/").split("/course/")[1]
    link_1 = f"https://www.udemy.com/api-2.0/courses/{slug}/?fields[course]=@all"  # noqa

    driver.short_random_sleep()
    driver.google_get(link_1, bypass_cloudflare=True)
    course_json = driver.get_text("pre")
    course_data = json.loads(course_json)
    course_id = course_data["id"]

    link_2 = f"https://www.udemy.com/api-2.0/course-landing-components/{course_id}/me/?components=curriculum_context"  # noqa
    driver.short_random_sleep()
    driver.google_get(link_2, bypass_cloudflare=True)
    curriculum_json = driver.get_text("pre")

    curriculum_data = json.loads(curriculum_json)
    data = {
            "url": data,
            "course_data": course_data,
            "curriculum_data": curriculum_data,
            }
    return data


@log_time
def main():
    links = get_courses_links()[:5]
    get_course_data(links)


if __name__ == "__main__":
    main()
