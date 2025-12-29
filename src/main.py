"""
Author: Muhammad Amin Bin Mohd Kafri

The step this script took:
    Phase 1
    1. Browse https://www.udemy.com/sitemap.xml
    2. Extract the XML data
    3. Go to each course xml sitemap
    4. Get all the url in each course sitemap
    5. Store it in JSON file

    Phase 2
    1. Loop through all url in JSON file
    2. Get the slug
    3. Access the data through this url
        - https://www.udemy.com/api-2.0/courses/{slug}/?fields[course]=@all
        - https://www.udemy.com/api-2.0/course-landing-components/{slug}/me/?components=curriculum_context
    4. Store the result in JSON file
"""

from botasaurus.browser import browser, Driver


@browser
def scraper(driver: Driver, data):
    pass


if __name__ == "__main__":
    pass
