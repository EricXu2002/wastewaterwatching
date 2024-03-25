import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String

def scrape_news():
    #url = "https://en.wikipedia.org/wiki/Fukushima_nuclear_accident#References"
    url = "https://www.independent.co.uk/topic/fukushima"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    headlines = []
    links = []
    print("getting headlines")
    for headline in soup.find_all(["h2", "a"], class_="title"):
        headlines.append(headline.text)
        links.append("https://www.independent.co.uk/"+headline.get("href"))
        #linkElement = headline.find("a")
        #if linkElement:
        #    links.append(linkElement.get("href"))
        #    print(linkElement.get("href"))
        #    print("hi")
    return headlines, links


app = Flask(__name__)

# SQLAlchemy and DB setup

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"

db.init_app(app)

class Topic(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str]

class Comment(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str]
    topicId: Mapped[str]

class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    name: Mapped[str]


with app.app_context():
    db.create_all()

# PAGE ROUTES

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
    headlines, links = scrape_news()
    return render_template('news.html', headlines=headlines, links=links)

@app.route('/forum', methods=["GET", "POST"])
def forum():
    if request.method == "POST":
        topic = Topic(
            title=request.form["title"],
            description=request.form["description"],
        )
        db.session.add(topic)
        db.session.commit()
        
    topics = db.session.execute(db.select(Topic)).scalars()

    return render_template('forum/index.html', topics=topics)

@app.route('/forum/topic/<int:id>', methods=["GET", "POST"])
def topic(id):
    if request.method == "POST":
        comment = Comment(
            text=request.form["text"],
            topicId=id
        )
        db.session.add(comment)
        db.session.commit()
    
    topic = db.get_or_404(Topic, id)
    comments = Comment.query.filter_by(topicId=id).all()
    return render_template('forum/topic.html', topic=topic, comments=comments)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/logout')
def logout():
    return "logout"


if __name__ == "__main__":
    app.run(debug=True)
