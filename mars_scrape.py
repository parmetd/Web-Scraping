##################################
# Initialize
##################################
import time
from splinter import Browser
from bs4 import BeautifulSoup as bs
from pymongo import MongoClient
from datetime import date

# Set up Mongo Database
client = MongoClient("mongodb://localhost:27017")
db = client.mission_to_mars

##################################
# Scrape News Function
##################################
def get_mars_news(URL,browser):
    
    browser.visit(URL)
    html_string = browser.html
    soup = bs(html_string, 'lxml')
    
    try:
        
        # Find the latest news content
        news_list = soup.body.find('ul',class_='item_list')
        latest_news = news_list.find('li',class_='slide')
        latest_news_content = latest_news.find('div',class_='list_text')

        # Find latest news Date, Title and Paragraph
        latest_news_date = latest_news_content.find('div',class_='list_date').text
        latest_news_title = latest_news_content.find('div',class_='content_title').text
        latest_news_article = latest_news_content.find('div',class_='article_teaser_body').text
        
        return {"news_date":latest_news_date,"news_title":latest_news_title,"news_article":latest_news_article}
        
    except:
        
        print("Scrape News Fail")

##################################
# Scrape Image Function
##################################
def get_mars_image(URL,browser):
    
    # Press the full image button
    browser.visit(URL)
    button = browser.find_by_id("full_image")
    button.click()
    time.sleep(1) 

    html_string = browser.html

    # Web scraping find the first image
    soup = bs(html_string, 'lxml')

    fancy_box = soup.find('div',id='fancybox-thumbs')
    image_object_list = fancy_box.find_all('a',class_='ready')
    
    image_select = 0
    count = 0
    
    for image_object in image_object_list: 
        
        try: 
        
            select_image_url = "https://www.jpl.nasa.gov" + image_object.img['src']          
            image_select = 1  
            return select_image_url
        
        except:   
            
            count = count + 1
            print(f"Try the {count}-th time of Scrape Image")
        
        if image_select == 1:     
            break  

##################################
# Scrape Weather Function
##################################
def get_mars_weather(URL,browser):

    try:
        
        browser.visit(URL)
        html_string = browser.html
        soup = bs(html_string, 'lxml')
        
        weather_container_list = soup.find_all('li',class_='js-stream-item')
        
        for weather_container in weather_container_list: 
            
            weather_publisher_name = weather_container.find('strong',class_='fullname').text.strip()
            
            if weather_publisher_name == "Mars Weather":
        
                mars_weather = weather_container.find('div',class_='js-tweet-text-container').text.strip()
            
                break
        
        return mars_weather.split('pic')[0]
        
    except:
        
        print("Web Scraping Fail")

##################################
# Scrape Facts Function
##################################
def get_mars_facts(URL,browser): 
    
    try:
        
        browser.visit(URL)
        html_string = browser.html
        soup = bs(html_string, 'lxml')

        mars_fact = {}
        table = soup.find('table',id='tablepress-mars')
        
        for table_row in table.find_all('tr'):
            
            table_row_value = table_row.find_all('td')
            
            key = table_row_value[0].text.strip().replace(':','')
            value = table_row_value[1].text.strip()
            
            mars_fact = {**mars_fact,**{key:value}}
            
        return mars_fact
    
    except:
        
        print("Scrape Facts Fail")

##################################
# Scrape Hemispheres Images
##################################
def get_mars_hemispheres(URL,browser):
    
    mars_hemispheres = []
    
    try:
        browser.visit(URL)     
        html_string = browser.html
        soup = bs(html_string, 'lxml')
        
        image_group = soup.find('div',class_='collapsible results')
        
        image_object_list = image_group.find_all('div',class_='item')
        
        for image_object in image_object_list:
            
            image_title = image_object.find('h3').text.strip()
            
            # Extract full image
            full_image_url = 'https://astrogeology.usgs.gov'+ image_object.find('a')['href'] 
            browser.visit(full_image_url)

            full_image_html_string = browser.html
            full_image_soup = bs(full_image_html_string, 'lxml')
            
            image_url='https://astrogeology.usgs.gov' + str(full_image_soup.find('img','wide-image')['src'])
            
            mars_hemispheres.append({"image_title": image_title, "image_url": image_url})
            
            browser.back()
            
        return mars_hemispheres   
        
    except:
        
        print("Scrape Hemispheres Images Fail")


##################################
# Scrape Function
##################################
def mars_scrape(browser):

    # Web Location
    Mars_News_URL = "https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest" 
    Mars_Image_URL = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    Mars_Weather_URL = "https://twitter.com/marswxreport?lang=en"
    Mars_Facts_URL = "https://space-facts.com/mars/"
    Mars_Hemispheres_URL = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"

    # Call Scrape Function
    scrape_results = {}
    scrape_results['date'] = date.today().strftime('%m/%d/%Y')
    scrape_results['news'] = get_mars_news(Mars_News_URL,browser)
    scrape_results['feature_image'] = get_mars_image(Mars_Image_URL,browser)
    scrape_results['weather'] = get_mars_weather(Mars_Weather_URL,browser)
    scrape_results['facts'] = get_mars_facts(Mars_Facts_URL,browser)
    scrape_results['hemispheres_image'] = get_mars_hemispheres(Mars_Hemispheres_URL,browser)

    browser.quit()

    return scrape_results

##################################
# Load Data to Mongo
##################################
executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
browser = Browser('chrome', **executable_path, headless=False)

scrape_results = mars_scrape(browser)

browser.quit()

db.mars_data.insert_one(scrape_results)


