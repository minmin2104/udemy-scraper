'''
Author: Muhammad Amin Bin Mohd Kafri
Description: Fetch all the courses link in format of "/courses/foo"
'''
import time
import json
import random
from my_log import MyLog
from datetime import datetime
from botasaurus.soupify import soupify
from botasaurus.browser import browser, Driver, Wait


TOPIC_COURSES_HREF_PATH = './json_data/topic_courses_href.json'
BASE_URL = 'https://www.udemy.com'
my_log = MyLog()
log = my_log.log


def log_both(message, end='\n'):
    print(message, end=end)
    log(message, end=end)


def get_topic_courses_href():
    data = dict()
    with open(TOPIC_COURSES_HREF_PATH, 'r') as f:
        data = json.load(f)
    return data['href']


def has_data_page(tag):
    return tag.has_attr('data-page')


def get_all_href(driver: Driver):
    return driver.get_all_links(
            'h3 a',
            url_contains_text='/course',
            wait=Wait.LONG
            )


def scrape_page(driver, url, page):
    curr_href = []
    try:
        if page > 1:
            paged_url = f'{url}?p={page}'
            driver.get(paged_url, bypass_cloudflare=True)
            driver.short_random_sleep()
            driver.wait_for_element(
                    'h3[data-purpose="course-title-url"]',
                    wait=Wait.LONG
                    )

        driver.short_random_sleep()
        curr_href = get_all_href(driver)
    except Exception:
        scrape_page(driver, url, page)
    return curr_href


@browser(
        output='attempt_5_courses',
        parallel=5,
        reuse_driver=True,
        async_queue=True,
        cache=True
        )
def scrap_course_href(driver: Driver, data):
    rand_sleep = random.uniform(2, 12)
    log_both(f'Sleeping for {rand_sleep}')
    time.sleep(rand_sleep)
    courses_links = []
    original_url = data if BASE_URL in data else f'{BASE_URL}{data}'

    try:
        log_both(f'----- {original_url} -----')

        # Access first page
        driver.get(
                original_url,
                bypass_cloudflare=True)

        driver.short_random_sleep()
        driver.wait_for_element(
                'h3[data-purpose="course-title-url"]',
                wait=Wait.LONG)
        driver.short_random_sleep()

        # Get maximum page number
        soup = soupify(driver.page_html)
        pages_a = soup.find_all(has_data_page)
        max_page = 1
        for page_a in pages_a:
            curr_page = page_a['data-page']
            if int(curr_page) > max_page:
                max_page = int(page_a.string)
        max_page_log = f'Max page: {max_page}'
        log_both(max_page_log)

        for page in range(1, max_page + 1):
            if page > 1:
                paged_url = f'{original_url}?p={page}'
                driver.get(paged_url, bypass_cloudflare=True)
                driver.short_random_sleep()
                driver.wait_for_element(
                        'h3[data-purpose="course-title-url"]',
                        wait=Wait.LONG
                        )

            driver.short_random_sleep()

            soup = soupify(driver.page_html)
            curr_href = get_all_href(driver)
            courses_links.extend(curr_href)

            log_both(f'Page {page}/{max_page} | \
Links found: {len(curr_href)} | {original_url}')
    except Exception as e:
        log_both(f"Error scraping {original_url}: {str(e)}")
        return {'url': original_url, 'courses_links': courses_links,
                'error': True,
                'last_page': page
                }

    # remove duplicate courses href
    distinct_links = list(set(courses_links))
    log_both(f'Found {len(distinct_links)} distinct courses')

    return {'url': original_url, 'courses_links': distinct_links}


if __name__ == '__main__':
    main_course_pages = get_topic_courses_href()[:5]
    start_time = datetime.now()
    res = scrap_course_href(data=main_course_pages)
    end_time = datetime.now()

    all_courses_href = []
    with open('./json_data/all_courses_href.json', 'w') as f:
        for item in res:
            all_courses_href.extend(item['courses_links'])
        json.dump({'courses_link': all_courses_href}, f, indent=4)

    elapsed_time = end_time - start_time
    log_both(f'Elapsed time: {elapsed_time}')
    log_both(f'Total second: {elapsed_time.total_seconds()}')
