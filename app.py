from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String

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
    return render_template('news.html')

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


if __name__ == "__main__":
    app.run(debug=True)
