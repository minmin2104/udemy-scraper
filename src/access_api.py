import json
from botasaurus.browser import browser, Driver
from my_log import MyLog
import time
import os

MAX_RUNTIME_SECONDS = 2 * 60 * 60
START_TIME = time.time()
mylog = MyLog()
log = mylog.log
log_time = mylog.log_time
OUTPUT_NAME = os.getenv("SCRAPE_OUTPUT")


def get_courses_links():
    courses_link_path = "all_courses_link.json"
    links = []
    with open(courses_link_path, "r") as f:
        links = json.load(f)
    try:
        with open("processed.json", "r") as f:
            done = json.load(f)
    except FileNotFoundError:
        done = []
    return list(set(links) - set(done))


@browser(
        cache=True,
        output=OUTPUT_NAME,
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
    links = get_courses_links()
    res = get_course_data(links)

    process_json = "processed.json"
    processed_urls = get_processed_url(process_json)
    processed_urls = set(processed_urls)
    for data in res:
        if data:
            processed_urls.add(data["url"])
    write_processed_url(process_json, list(processed_urls))


if __name__ == "__main__":
    main()
