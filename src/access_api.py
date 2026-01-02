import json
from botasaurus.browser import browser, Driver
from my_log import MyLog
import time
import os
import filter_courses_json

MAX_RUNTIME_SECONDS = 3 * 60 * 60
START_TIME = time.time()
mylog = MyLog()
log = mylog.log
log_time = mylog.log_time
BATCH_NUM = os.getenv("BATCH_NUM")


def get_courses_links(path):
    courses_link_path = path
    links = []
    with open(courses_link_path, "r") as f:
        links = json.load(f)
    return links


@browser(
        cache=True,
        output=f"batch_{BATCH_NUM}",
        parallel=5,
        max_retry=5
        )
def get_course_data(driver: Driver, data):
    if time.time() - START_TIME > MAX_RUNTIME_SECONDS:
        log("Time limit reached. Skipping remaining task")
        return None
    log(f"Scraping: {data}")
    slug = data.rstrip("/").split("/course/")[1]
    link_1 = f"https://www.udemy.com/api-2.0/courses/{slug}/?fields[course]=@all"  # noqa

    driver.short_random_sleep()
    driver.google_get(link_1, bypass_cloudflare=True)
    course_json = driver.get_text("pre")
    course_data = json.loads(course_json)
    if "id" not in course_data:
        return None
    course_id = course_data["id"]
    filtered_course = filter_courses_json.filter_courses_data(course_data)

    link_2 = f"https://www.udemy.com/api-2.0/course-landing-components/{course_id}/me/?components=curriculum_context"  # noqa
    driver.short_random_sleep()
    driver.google_get(link_2, bypass_cloudflare=True)
    curriculum_json = driver.get_text("pre")
    curriculum_data = json.loads(curriculum_json)
    filtered_curriculum = filter_courses_json.filter_curriculum_data(curriculum_data)

    data = {
            "url": data,
            "course_data": filtered_course,
            "curriculum_data": filtered_curriculum,
            }
    return data


def get_processed_url(path):
    try:
        with open(path, "r") as f:
            processed = json.load(f)
    except FileNotFoundError:
        processed = []
    return processed


def write_processed_url(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)


@log_time
def main():
    path = f"batches/batch_{BATCH_NUM}.json"
    links = get_courses_links(path)
    get_course_data(links[:3])


if __name__ == "__main__":
    main()
