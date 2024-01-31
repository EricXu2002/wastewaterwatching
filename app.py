from flask import Flask, render_template
import requests
from bs4 import BeautifulSoup

def scrape_news():
    url = "https://en.wikipedia.org/wiki/Fukushima_nuclear_accident#References"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    headlines = []
    for headline in soup.find_all("h3", class_="headline"):
        headlines.append(headline.text)
    return headlines

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/map')
def map():
    return render_template('map.html')

@app.route('/news')
def news():
    headlines = scrape_news()
    return render_template('news.html', headlines = headlines)

@app.route('/forum')
def forum():
    return render_template('forum.html')

