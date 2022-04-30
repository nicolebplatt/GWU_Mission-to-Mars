# Import Splinter, BeautifulSoup, and Pandas
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import datetime as dt

def scrape_all():
    # Initiate headless driver for deployment
    # Set up splinter
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)
    # headless set to true because we don't need to watch the script run

    # set news title and paragraph variables
    news_title, news_p = mars_news(browser)

    # Run all scraping functions and store results in dictionary
    data = {
      "news_title": news_title,
      "news_paragraph": news_p,
      "featured_image": featured_image(browser),
      "facts": mars_facts(browser),
      "last_modified": dt.datetime.now(),
      "hemispheres": hemisphere_images(browser)
    }

    # Stop webdriver and return data
    browser.quit()
    return data

# Set up function for app.py code to reuse and update data
def mars_news(browser):
    # Featured Article - Scrape Mars News
    # Visit the mars news site
    url = 'https://redplanetscience.com'
    browser.visit(url)
    # Optional delay for loading the page (wait one second before searching for components)
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Convert browser html to a soup object
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # add try/except for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')

        # Use the parent element to find the first `a` tag and save it as `news_title`
        news_title = slide_elem.find('div', class_='content_title').get_text()

        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()
    except AttributeError:
        return None, None

    return news_title, news_p

def featured_image(browser):
    # Featured Image - Scrape Mars Image
    # Visit JPL Space Images URL
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')
    
    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')
    except AttributeError:
        return None
        
    # Use the base URL to create an absolute URL
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'
    
    return img_url

def mars_facts(browser):
    # Featured Table
    try:
        # use 'read_html" to scrape the facts table into a dataframe
        # Visit Mars Facts
        df = pd.read_html('https://galaxyfacts-mars.com')[0]
    except BaseException:
        return None
    
    # Assign columns and set index of dataframe
    df.columns=['description', 'Mars', 'Earth']
    df.set_index('description', inplace=True)

    # Convert dataframe into HTML format, add bootstrap
    return df.to_html(classes="table table-striped")

def hemisphere_images(browser):
    # Hemisphere images & titles
    # Visit Mars Hemispheres    
    url = 'https://marshemispheres.com/'
    browser.visit(url)

    # Create a list to hold the images and titles.
    hemisphere_image_urls = []

    # Parse the resulting html with soup
    html = browser.html
    hemi_soup = soup(html, 'html.parser')
    links = browser.find_by_css('a.product-item img')
    
    for i in range(len(links)):
        hemisphere = {}
        try:
            # find image in html devtools inspect
            browser.find_by_css('a.product-item img')[i].click()
            
            # find the sample image anchor tag and extract the href & title/h2
            sample_elem = browser.links.find_by_text('Sample').first
            hemisphere['img_url'] = sample_elem['href']
            
            sample_title = browser.find_by_tag('h2').first
            hemisphere['title'] = sample_title.text
        except BaseException:
            return None
        
        hemisphere_image_urls.append(hemisphere)
        browser.back()

    return hemisphere_image_urls

if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())

