from flask import Flask, render_template

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
    return render_template('news.html')

@app.route('/forum')
def forum():
    return render_template('forum.html')