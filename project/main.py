from flask import Blueprint, render_template
from . import db
import requests
from bs4 import BeautifulSoup

main = Blueprint("main", __name__)

def scrape_news():
    url = "https://en.wikipedia.org/wiki/Fukushima_nuclear_accident#References"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    headlines = []
    for headline in soup.find_all("h3", class_="headline"):
        headlines.append(headline.text)
    return headlines

"""
class Topic(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str]

class Comment(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str]
    topicId: Mapped[str]


with app.app_context():
    db.create_all()

"""


# PAGE ROUTES

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/map')
def map():
    return render_template('map.html')

@main.route('/news')
def news():
    headlines = scrape_news()
    return render_template('news.html', headlines = headlines)

@main.route('/forum', methods=["GET", "POST"])
def forum():
    """ if request.method == "POST":
        topic = Topic(
            title=request.form["title"],
            description=request.form["description"],
        )
        db.session.add(topic)
        db.session.commit()
        
    topics = db.session.execute(db.select(Topic)).scalars()

    return render_template('forum/index.html', topics=topics) """
    return render_template('forum/index.html', topics=[])

@main.route('/forum/topic/<int:id>', methods=["GET", "POST"])
def topic(id):
    """ if request.method == "POST":
        comment = Comment(
            text=request.form["text"],
            topicId=id
        )
        db.session.add(comment)
        db.session.commit()
    
    topic = db.get_or_404(Topic, id)
    comments = Comment.query.filter_by(topicId=id).all()
    return render_template('forum/topic.html', topic=topic, comments=comments) """
    return render_template('forum/topic.html', topic='', comments=[])


