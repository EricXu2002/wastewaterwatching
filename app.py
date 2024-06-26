import requests
from bs4 import BeautifulSoup
from flask_login import UserMixin, LoginManager, login_user, login_required, current_user, logout_user
from flask import Flask, render_template, request, redirect, url_for, flash, app, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from flask_cors import CORS
from sqlalchemy import Integer, String

def scrapeNewsForPlant(name):
    url = "https://www.google.com/search?sca_esv=eae1723b12d3aedd&sca_upv=1&sxsrf=ACQVn09QkUKH8wY_0xE3odg95y8YGb7_LQ:1712595997604&q=" + name + "&tbm=nws&source=lnms&prmd=ivnmbtz&sa=X&ved=2ahUKEwihsdKgjbOFAxUQM1kFHahzCEYQ0pQJegQICBAB&biw=1280&bih=631&dpr=1.5"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    headlines=[]
    links=[]
    for headline in soup.find_all('h3'):
        headlines.append(headline.text)
        #links.append(headline.get("href"))
        #print(headline.get("href"))
    soup = BeautifulSoup(response.content, "html.parser")
    for item in soup.select('a', jsname_=".YKoRaf", class_='.WlydOe', href = True):
        link = item.get("href")
        if(link[0:7] == "/url?q="):
            end = link.find("&sa")
            if(end != -1):
                links.append(link[7:end])
                print(item["href"][7:end])
    links.pop(0)
    links.pop(0)
    links.pop()
    links.pop()
    return headlines, links
    

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
CORS(app)

@app.route('/scrape_news_map', methods=['GET'])
def scrape_news_map():
    plant_name = request.args.get('name')
    headlines, links = scrapeNewsForPlant(plant_name)
    return jsonify({'headlines': headlines, 'links': links})

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
    headlines, links = scrapeNewsForPlant("Radiation")
    headlines2, links2 = scrape_news()
    headlines += headlines2
    links += links2
    return render_template('news.html', headlines=headlines, links=links)

@app.route('/forum', methods=["GET"])
# @login_required
def forum():

    curr_name = 'Guest'

    if current_user.is_authenticated:
        curr_name = current_user.name
            
    topics = db.session.execute(db.select(Topic)).scalars()

    return render_template('forum/index.html', topics=topics, name=curr_name)

@app.route('/forum/newtopic', methods=["GET","POST"])
@login_required
def new_topic():
    if request.method == "POST":
        topic = Topic(
            title=request.form["title"],
            description=request.form["description"],
            user=current_user.name
        )
        db.session.add(topic)
        db.session.commit()
    
    return render_template('forum/newtopic.html', name=current_user.name)

@app.route('/forum/topic/<int:id>', methods=["GET", "POST"])
# @login_required
def topic(id):

    curr_name = 'Guest'

    if current_user.is_authenticated:
        curr_name = current_user.name
    
    topic = db.get_or_404(Topic, id)
    comments = Comment.query.filter_by(topicId=id).all()
    return render_template('forum/topic.html', topic=topic, comments=comments, name=curr_name)

@app.route('/forum/topic/<int:id>/newcomment', methods=["GET","POST"])
@login_required
def new_comment(id):
    if request.method == "POST":
        print(request.form)
        comment = Comment(
            text=request.form["text"],
            topicId=id,
            user=current_user.name
        )
        db.session.add(comment)
        db.session.commit()
    
    topic = db.get_or_404(Topic, id)
    comments = Comment.query.filter_by(topicId=id).all()
    return render_template('forum/newcomment.html', topic=topic, comments=comments, name=current_user.name)

@app.route('/login')
def login():
    if current_user.is_authenticated:
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
