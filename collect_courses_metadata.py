import json
import random
from my_log import MyLog
from datetime import datetime
from botasaurus.soupify import soupify
from markdownify import markdownify as md
from botasaurus.browser import browser, Driver


my_log = MyLog()


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


def get_course_metadata(soup, driver, url):
    # Get the title here. Every title has unique attribute data-purpose
    # with unique value lead-title
    title_tag = soup.find('h1', attrs={'data-purpose': 'lead-title'})
    title = title_tag.text
    my_log.log(f'Title: {title}')

    # Get headline here
    title_headline = soup.find('div', attrs={'data-purpose': 'lead-headline'})
    headline = title_headline.text
    my_log.log(f'Headline: {headline}')

    # Get locale
    locale_div = soup.find('div', attrs={'data-purpose': 'lead-course-locale'})
    locale = locale_div.text
    my_log.log(f'Locale: {locale}')

    # Rating numbers
    span_rating = soup.find('span', attrs={'data-purpose': 'rating-number'})
    rating = span_rating.text
    my_log.log(f'Rating: {rating} / 5')

    # Get enrollment
    enroll_div = soup.find('div', attrs={'data-purpose': 'enrollment'})
    enrollment = enroll_div.text
    my_log.log(f'Enrollment: {enrollment}')

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
        my_log.log(f'Stats: {coco_stats_list}')

    # Get instructor name
    span_instructor = soup.find('div', attrs={
        'data-purpose': 'instructor-name-top'})
    instructor = span_instructor.find('a').text
    my_log.log('Instructor: {instructor}')

    # TODO: This checking if free need to be changed
    # Instead of looking at the price text,
    # look at body's attribute instead
    price_text_div = soup.find('div', attrs={
        'data-purpose': 'course-price-text'
        })
    is_free = is_courses_free(price_text_div)
    my_log.log(f'Is Free: {is_free}')

    course_objectives = []
    if is_free:
        div_content_wrapper = soup.find(
                'div', attrs={'data-purpose': 'content-container-wrapper'})
        course_objectives = get_free_courses_objective(div_content_wrapper)
    else:
        course_objectives = get_paid_courses_objective(soup)

    my_log.log(f'Found {len(course_objectives)} objectives')
    for obj in course_objectives:
        my_log.log(obj)

    # Get courses requirements
    requirements = []
    div_req = soup.find('h2', attrs={'data-purpose': 'requirements-title'})
    ul_req_cont = div_req.find_next('ul')
    div_req_content = ul_req_cont.find_all(
            'div', attrs={'class': 'ud-block-list-item-content'})
    for div in div_req_content:
        requirements.append(div.text)

    my_log.log(f'Found {len(requirements)} requirements')
    my_log.log('Requirements:')
    for req in requirements:
        my_log.log(req)

    # Get description
    desc_div = soup.find('div', attrs={'data-purpose': 'safely-set-inner-html:description:description'})
    desc_div_str = str(desc_div)
    description = md(desc_div_str)
    my_log.log('Description:')
    my_log.log(description)

    # Get target audience
    div_target = soup.find('div', attrs={'data-purpose': 'target-audience'})
    ul_target = div_target.find('ul')
    target_audience = md(str(ul_target))
    my_log.log(f'Target audience: {target_audience}')

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

    for key, value in curriculum_content.items():
        my_log.log(f'{key}:')
        for item in value:
            my_log.log(f' - {item}')

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


@browser(reuse_driver=True, output_formats=['JSON', 'EXCEL'])
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
    courses_links = get_courses_links('./output/scrap_course_href.json')[:3]

    courses_metadata = []
    for link in courses_links:
        url = f'{base_url}{link}'
        print(f'Scraping: {url}', end='...')
        my_log.log(f'---------- {url} ----------')
        driver.get(
                url,
                bypass_cloudflare=True,
                wait=random.randint(4, 10)
                )
        soup = soupify(driver.page_html)
        metadata_json = dict()
        try:
            metadata_json = get_course_metadata(soup, driver, url)
        except Exception as e:
            my_log.log(f'Failed on {url}:\n{e}\n')
            print('Skipping')
            continue
        courses_metadata.append(metadata_json)
        my_log.log('\n')
        print('Done')

    print(f'Get metadata for {len(courses_metadata)} courses')
    return courses_metadata


if __name__ == '__main__':
    start_time = datetime.now()
    scrap_course_metadata()
    end_time = datetime.now()
    elapsed = end_time - start_time
    my_log.log(f'Elapsed time: {elapsed}')
    my_log.log(f'Total second: {elapsed.total_seconds()}')
