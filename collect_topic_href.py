'''
Author: https://github.com/minmin2104

This script is meant to be run once and with dev
interaction. The data it produce is in the ./json_data/topic_courses_href.json

NOTE: NO NEED TO RUN THIS SCRIPT AGAIN
'''

from botasaurus.soupify import soupify
from botasaurus.browser import browser, Driver, Wait

URL = 'https://udemy.com'


def get_popular_ai_topic_href():
    pass


@browser
def scrap_topic_href(driver: Driver, data):
    '''
    This script will scrape link to the topic for
    collect_courses_href.py to use
    '''
    driver.get(
            URL,
            bypass_cloudflare=True,
            wait=Wait.LONG
            )
    href = []
    for i in range(13):
        soup = soupify(driver.page_html)
        html_a_tags = soup.find_all('a', attrs={'data-testid': 'browse-nav-item'})
        for tag in html_a_tags:
            curr_href = tag.get('href')
            if curr_href and '/courses' in curr_href:
                href.append(curr_href)
        driver.prompt()

    href = list(set(href))
    return {
            'href': href
            }


if __name__ == '__main__':
    scrap_topic_href()
