'''
Author: Muhammad Amin Bin Mohd Kafri
Description: Fetch all the courses link in format of "/courses/foo"
'''
import random
from botasaurus.browser import browser, Driver, Wait
from botasaurus.soupify import soupify


@browser(reuse_driver=True)
def scrap_course_href(driver: Driver, data):
    """
    According to the source code of botasaurus
    class Wait:
        SHORT = 4
        LONG = 8
        VERY_LONG = 16
    """
    wait_time = [Wait.SHORT, Wait.LONG, Wait.VERY_LONG]

    # Access first page
    page = 1
    topic = 'prompt-engineering'
    url = f'https://www.udemy.com/topic/{topic}/?p={page}'
    driver.get(
            url,
            bypass_cloudflare=True,
            wait=random.choice(wait_time)
            )

    # Get maximum page number
    soup = soupify(driver.page_html)
    pages_a = soup.find_all('a', attrs={
        'class': 'ud-btn ud-btn-medium ud-btn-ghost ud-btn-text-sm pagination_page__R2UQQ'
        })
    max_page = 1
    for page_a in pages_a:
        print(page_a.string)
        if int(page_a.string) > max_page:
            max_page = int(page_a.string)
    print(f'Max page: {max_page}')

    courses_links = []
    while page <= max_page:
        courses_links += driver.get_all_links(
                'h3 a',
                url_contains_text='/course/',
                wait=random.choice(wait_time)
                )
        page = page + 1
        url = f'https://www.udemy.com/topic/{topic}/?p={page}'
        driver.get(
                url,
                bypass_cloudflare=True,
                wait=random.choice(wait_time)
                )
        driver.sleep(5)

    # remove duplicate courses href
    courses_links = list(set(courses_links))
    print(f'Found {len(courses_links)} distinct courses')

    return {
            'courses_links': courses_links
    }


if __name__ == '__main__':
    scrap_course_href()
