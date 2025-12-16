import json
import random
from botasaurus.browser import browser, Driver, Wait
from botasaurus.soupify import soupify


def get_courses_links(filename):
    '''
    Read courses link file from output folder
    output/scrap_course_href.json
    load it and return for scrap_course_metadata
    to use
    '''
    payload = None
    try:
        with open(filename, 'r') as f:
            payload = json.load(f)
    except OSError as e:
        print(f'Error reading file {filename}: {e}')
        exit(1)

    courses_links = payload['courses_links']
    return courses_links


@browser
def scrap_course_metadata(driver: Driver, data):
    '''
    references html elemenet with unique attribute
    - url
    - lead-title
    - lead-headline
    - lead-course-locale
    - rating-number
    - enrollment
    - curriculum-stats
    - instructor-name-top
    - what-you-will-learn @ objective--objective-item
    - requirements: div.ud-block-list-item-content
    - safely-set-inner-html:description:description

    For free courses, click `show more` and `expand all section`
    For paid courses, click `expand all section` only
    '''
    base_url = 'https://udemy.com'
    courses_links = get_courses_links('./output/scrap_course_href.json')
    paid_url = f'{base_url}{courses_links[0]}'
    print(f'Targeting {paid_url} for testing...')
    free_url = f'{base_url}{courses_links[1]}'
    print(f'Targeting {free_url} for testing...')

    wait_time = [Wait.SHORT, Wait.LONG, Wait.VERY_LONG]

    driver.get(
            paid_url,
            bypass_cloudflare=True,
            wait=random.choice(wait_time)
            )

    soup = soupify(driver.page_html)

    # Get the title here. Every title has unique attribute data-purpose
    # with unique value lead-title
    title_tag = soup.find('h1', attrs={'data-purpose': 'lead-title'})
    title = title_tag.text
    print('Title:', title)

    # Get headline here
    title_headline = soup.find('div', attrs={'data-purpose': 'lead-headline'})
    headline = title_headline.text
    print('Headline:', headline)

    # Get locale
    locale_div = soup.find('div', attrs={'data-purpose': 'lead-course-locale'})
    locale = locale_div.text
    print('Locale:', locale)

    # Rating numbers
    span_rating = soup.find('span', attrs={'data-purpose': 'rating-number'})
    rating = span_rating.text
    print(f'Rating: {rating} / 5')

    # Get enrollment
    enroll_div = soup.find('div', attrs={'data-purpose': 'enrollment'})
    enrollment = enroll_div.text
    print('Enrollment:', enrollment)

    # Get curriculum stats
    coco_stats = soup.find('div', attrs={'data-purpose': 'curriculum-stats'})
    target_span = coco_stats.find('span')
    coco_stats_list = []
    if target_span:
        full_text = target_span.get_text(strip=True)
        coco_stats_list = full_text.split('•')
        coco_stats_list = [text.strip() for text in coco_stats_list]
        # hhmmsstotal length (not a typo)
        coco_stats_list[-1] = coco_stats_list[-1].replace(
                'total length', ' total length')
        coco_stats_list[-1] = coco_stats_list[-1].replace(
                '\xa0', ' ')
        print('Stats:', coco_stats_list)

    span_instructor = soup.find('div', attrs={
        'data-purpose': 'instructor-name-top'})
    instructor = span_instructor.find('a').text
    print('Instructor:', instructor)

    # Testing clicking necessary button
    expand_content_button = driver.get_element_containing_text(
            'Expand all sections')
    if expand_content_button:
        expand_content_button.click()

    show_more_button = driver.get_element_containing_text('Show more')
    if show_more_button:
        show_more_button.click()

    driver.prompt()


if __name__ == '__main__':
    scrap_course_metadata()
