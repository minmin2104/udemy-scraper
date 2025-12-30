# Udemy Scraper

This branch contain the repository for the udemy scraper that is more reliable
than the rewrite version or master branch.

## Note

- [x] **Phase 1**
1. Browse https://www.udemy.com/sitemap.xml
2. Extract the XML data
3. Go to each course xml sitemap
4. Get all the url in each course sitemap
5. Store it in JSON file

**Phase 2**
1. Loop through all url in JSON file
2. Get the slug
3. Access the data through this url
    - https://www.udemy.com/api-2.0/courses/{slug}/?fields[course]=@all
    - https://www.udemy.com/api-2.0/course-landing-components/{slug}/me/?components=curriculum_context
4. Store the result in JSON file
