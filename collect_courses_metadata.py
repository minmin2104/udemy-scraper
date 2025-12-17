import json
import random
from botasaurus.browser import browser, Driver, Wait
from botasaurus.soupify import soupify
from markdownify import markdownify as md


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


def is_courses_free(div_price_tag):
    is_free = False
    spans = div_price_tag.find_all('span')
    for span in spans:
        if span.text == "Free":
            is_free = True
            break
    return is_free


def get_free_courses_objective(div_content):
    obj_div = div_content.find_all(
            'div',
            attrs={'class': 'objective--objective-item--0gf07'})
    obj = []
    for div in obj_div:
        obj_span = div.find('span')
        obj.append(obj_span.text)

    return obj


def get_paid_courses_objective(soup):
    obj_div = soup.find_all('div', attrs={'data-purpose': 'objective'})
    obj = []
    for elem in obj_div:
        obj_span = elem.find('span')
        obj.append(obj_span.text)
    return obj


@browser(reuse_driver=True)
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
    - objective @ content-container-wrapper
    - requirements: div.ud-block-list-item-content
    - safely-set-inner-html:description:description
    - course content

    For free courses, click `show more` and `expand all section`
    For paid courses, click `expand all section` only
    '''
    base_url = 'https://udemy.com'
    courses_links = get_courses_links('./output/scrap_course_href.json')
    paid_url = f'{base_url}{courses_links[0]}'
    print(f'Targeting {paid_url} for testing...')
    free_url = f'{base_url}{courses_links[1]}'
    print(f'Targeting {free_url} for testing...')

    wait_time = [Wait.SHORT, Wait.LONG]
    url = paid_url

    driver.get(
            url,
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

    # Get instructor name
    span_instructor = soup.find('div', attrs={
        'data-purpose': 'instructor-name-top'})
    instructor = span_instructor.find('a').text
    print('Instructor:', instructor)

    # TODO: This checking if free need to be changed
    # Instead of looking at the price text,
    # look at body's attribute instead
    price_text_div = soup.find('div', attrs={
        'data-purpose': 'course-price-text'
        })
    is_free = is_courses_free(price_text_div)
    print('Is Free:', is_free)

    # Clicking necessary button
    expand_content_button = driver.get_element_containing_text(
            'Expand all sections')
    if expand_content_button:
        expand_content_button.click()

    show_more_button = driver.get_element_containing_text('Show more')
    if show_more_button:
        show_more_button.click()

    course_objectives = []
    if is_free:
        div_content_wrapper = soup.find(
                'div', attrs={'data-purpose': 'content-container-wrapper'})
        course_objectives = get_free_courses_objective(div_content_wrapper)
    else:
        course_objectives = get_paid_courses_objective(soup)

    print(f'Found {len(course_objectives)} objectives')
    print('Courses Objs:', course_objectives)

    # Get courses requirements
    requirements = []
    div_req = soup.find('h2', attrs={'data-purpose': 'requirements-title'})
    ul_req_cont = div_req.find_next('ul')
    div_req_content = ul_req_cont.find_all(
            'div', attrs={'class': 'ud-block-list-item-content'})
    for div in div_req_content:
        requirements.append(div.text)

    print(f'Found {len(requirements)} requirements')
    print(requirements)

    # Get description
    desc_div = soup.find('div', attrs={'data-purpose': 'safely-set-inner-html:description:description'})
    desc_div_str = str(desc_div)
    description = md(desc_div_str)

    # Get target audience
    div_target = soup.find('div', attrs={'data-purpose': 'target-audience'})
    ul_target = div_target.find('ul')
    target_audience = md(str(ul_target))

    # Get course content
    curriculum_div = soup.find('div', attrs={'data-purpose': 'course-curriculum'})
    # Get heading of a subtitle
    curriculum_div_content = curriculum_div.find_all('div', attrs={'class': 'accordion-panel-module--panel--Eb0it section--panel--qYPjj'})
    curriculum_content = dict()
    for div in curriculum_div_content:
        sec_cont = div.find('span', attrs={'data-purpose': 'section-content'})
        span_header = sec_cont.previous_sibling
        header = span_header.get_text()
        curriculum_content[header] = []
        curr_contents = div.find_all('span', attrs={'data-testid': 'course-lecture-title'})
        for cont in curr_contents:
            curriculum_content[header].append(cont.get_text())

    print(curriculum_content)

    return {
            'Url': url,
            'Title': title,
            'Headline': headline,
            'Locale': locale,
            'Rating': f'{rating} / 5',
            'Enrollment': enrollment,
            'Instructor': instructor,
            'Curriculum Stats': coco_stats_list,
            'Course Objective': course_objectives,
            'Requirements': requirements,
            'Description': description,
            'Target audience': target_audience,
            'Curriculum Content': curriculum_content
            }


if __name__ == '__main__':
    scrap_course_metadata()
