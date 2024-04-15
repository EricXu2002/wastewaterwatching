import requests
from bs4 import BeautifulSoup
from flask_login import UserMixin, LoginManager, login_user, login_required, current_user, logout_user
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
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

app.config["SECRET_KEY"] = 'wastewaterwatchingkey'

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"

db.init_app(app)

class Topic(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(unique=True)
    user: Mapped[str]
    description: Mapped[str]

class Comment(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    user: Mapped[str]
    text: Mapped[str]
    topicId: Mapped[str]

class User(UserMixin, db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    name: Mapped[str]


login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return User.query.get(int(user_id))


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
@login_required
def forum():
    if request.method == "POST":
        topic = Topic(
            title=request.form["title"],
            description=request.form["description"],
            user=current_user.name
        )
        db.session.add(topic)
        db.session.commit()
        
    topics = db.session.execute(db.select(Topic)).scalars()

    return render_template('forum/index.html', topics=topics, name=current_user.name)

@app.route('/forum/topic/<int:id>', methods=["GET", "POST"])
@login_required
def topic(id):
    if request.method == "POST":
        comment = Comment(
            text=request.form["text"],
            topicId=id,
            user=current_user.name
        )
        db.session.add(comment)
        db.session.commit()
    
    topic = db.get_or_404(Topic, id)
    comments = Comment.query.filter_by(topicId=id).all()
    return render_template('forum/topic.html', topic=topic, comments=comments, name=current_user.name)

@app.route('/login')
def login():
    if current_user.is_authenticated:
        flash("You are already logged in.")
        return redirect(url_for('index'))
    
    return render_template('login.html')

@app.route('/login', methods=["POST"])
def login_post():

    #log in dude
    email = request.form.get("email")
    password = request.form.get("password")
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        flash("Please check your login details and try again.")
        return redirect(url_for('login'))
    
    login_user(user, remember=remember)

    return redirect(url_for('forum'))

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/signup', methods=["POST"])
def signup_post():
    # validate and add user
    email = request.form.get("email")
    name = request.form.get("name")
    password = request.form.get("password")

    user = User.query.filter_by(email=email).first()

    if user:
        flash("Error! Email already in use.")
        return redirect(url_for('signup'))
    
    new_user = User(email=email, name=name, password=generate_password_hash(password, method='scrypt'))

    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('login'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)
