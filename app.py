#################################################
# Dependencies
#################################################
import time
from splinter import Browser
from bs4 import BeautifulSoup as bs
from pymongo import MongoClient
from datetime import date
from flask import Flask, render_template, redirect
#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# MongoDB Setup
#################################################
client = MongoClient("mongodb://localhost:27017")
db = client.mission_to_mars

#################################################
# Flask Routes
#################################################
@app.route("/")
def index():
    #use mars_info collection from mission_to_marsDB
    #query information from the collection and save to new_info

    #if no database and collection yet (first-time), call scrape function and use
    #the scrape information to output object.
    # if (new_info == None):
    #     db.mars_info.insert_one(output)
    new_info_cursor = db.mars_data.find().sort([('date', -1)]).limit(1)

    for new_info in new_info_cursor: 

        news = new_info['news']
        feature_image = new_info['feature_image']
        weather = new_info['weather']
        facts = new_info['facts']
        hemispheres_image = new_info['hemispheres_image']
        
    return render_template('index.html', news = news, weather = weather, featured_image = feature_image, facts = facts, hemispheres_image = hemispheres_image)

        
# Route when the scrape button is click by user in the index.html
# Calls the scrape methods

@app.route("/scrape")
def scrape_new_data():
    
    from mars_scrape import mars_scrape

    executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
    browser = Browser('chrome', **executable_path, headless=False)

    scrape_results = mars_scrape(browser)

    db.mars_data.remove({})
    db.mars_data.update({}, scrape_results, upsert=True)

    browser.quit()

    return redirect("/", code=302)

if __name__ == "__main__":
    app.run(debug=True)