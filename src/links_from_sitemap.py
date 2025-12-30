from botasaurus.browser import browser, Driver
from bs4 import BeautifulSoup
from datetime import datetime
import xml.etree.ElementTree as etree


# @request(
#         output=None
#         )
# def get_sub_sitemaps(request: Request, url):
#     response = request.get(url)
#     soup = BeautifulSoup(response.text, "xml")
#     links = [loc.text for loc in soup.find_all('loc')]
#     time.sleep(random.uniform(1, 2))
#     return links

def get_sub_sitemaps(path):
    tree = None
    with open(path, "r") as f:
        tree = etree.parse(f)

    ns = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    sitemaps = tree.findall("ns:sitemap", namespaces=ns)
    courses_xml = []
    for n in sitemaps:
        loc = n.find("ns:loc", ns)
        if "courses.xml" in loc.text:
            courses_xml.append(loc.text)

    return courses_xml


@browser(
        cache=True,
        parallel=5,
        output="courses_url",
        reuse_driver=True,
        max_retry=5
        # add_arguments=["--headless=new"]
        )
def get_courses_url(driver: Driver, url):
    driver.short_random_sleep()
    driver.google_get(url, bypass_cloudflare=True)
    driver.short_random_sleep()
    print(f"On: {url}")
    soup = BeautifulSoup(driver.page_html, "xml")
    links = [loc.text for loc in soup.find_all('loc')]
    print(f"Found {len(links)} links on {url}")
    return links


if __name__ == "__main__":
    start_time = datetime.now()
    sub_sitemaps = get_sub_sitemaps("sitemap.xml")
    courses_link = [link for link in sub_sitemaps if "/courses.xml" in link]
    print(len(courses_link))
    get_courses_url(courses_link)
    end_time = datetime.now()

    elapsed = end_time - start_time
    print(f"Elapsed time: {elapsed}")
