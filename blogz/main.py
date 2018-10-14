from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
import cgi
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True    
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:qwerty123@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)
app.secret_key = 'aq44363cervg25vybu5v'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(120))
    datetime = db.Column(db.DateTime)
    date = db.Column(db.Date)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.datetime = datetime.now()
        self.date = datetime.now().date()
        self.owner = owner

    def __repr__(self):
        return '<Blog %r)>' % (self.title, self.body, self.owner)

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['/signup', '/login', '/blog', '/']
    if request.path not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/newpost')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])    
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify_password = request.form['verify-password']

        if not verify_username(username):
            username_error = "Please enter a valid username."
        else: 
            username_error = ""
        if not verify_password_length(password):
            password_valid_error = "Please enter a valid password."
        else:
            password_valid_error = ""
        if not verify_passwords_match(password, verify_password):
            password_match_error = "Passwords do not match."
        else:
            password_match_error = ""
   
        if not username_error and not password_valid_error and not password_match_error:
            existing_user = User.query.filter_by(username=username).first()
            if not existing_user:
                username_duplicate_error = "Username not available."
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect('/newpost')
            else:
                return render_template('signup.html', username_duplicate_error = username_duplicate_error)
        else:
            return render_template('signup.html', username_error = username_error, password_valid_error = password_valid_error, password_match_error = password_match_error)

    return render_template('signup.html')

def verify_username(username):
    number_of_characters = len(username)
    if number_of_characters > 3 and number_of_characters < 20:
        return True
    return False

def verify_password_length(password):
    number_of_characters = len(password)
    if number_of_characters > 3 and number_of_characters < 20:
            if " " not in password:
                return True       
    return False

def verify_passwords_match(password, verify_password):
    if password == verify_password:
        return True
    return False

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')

@app.route("/newpost", methods=['POST'])
def add_new_post():
    body = request.form.get('body')
    title = request.form.get('title')
    owner = User.query.filter_by(username=session['username']).first()

    if body == "":
        blog_body_blank_error = "Please fill in the body."
    else: blog_body_blank_error = ""

    if title == "":
        blog_title_blank_error = "Please fill in the title."
    else: blog_title_blank_error = ""

    if not blog_title_blank_error and not blog_body_blank_error:
            if request.method == 'POST':
                new_blog = Blog(title, body, owner)
                db.session.add(new_blog)
                db.session.commit()
                url = "/blog?id=" + str(new_blog.id)
                return redirect(url)
    else:
        return render_template('newpost.html', blog_body_blank_error = blog_body_blank_error, blog_title_blank_error = blog_title_blank_error, logged_in_user = logged_in_user)

@app.route("/blog", methods=['GET', 'POST'])
def display_blog_posts():
    blog_id = request.args.get('id')
    owner_id = request.args.get('user')
    if (owner_id):
        user_blogs = Blog.query.filter_by(owner_id = owner_id).all()
        return render_template('singleUser.html', user_blogs = user_blogs)
    if (blog_id):
        blog_post = Blog.query.get(blog_id)
        return render_template('single-post.html', blog_post = blog_post)

    blogs = Blog.query.order_by(desc(Blog.datetime))
    return render_template('blog.html', blogs=blogs)

@app.route('/', methods=['POST', 'GET'])
def index():
    owner_id = request.args.get('user')
    if (owner_id):
        user_blogs = Blog.query.filter_by(owner_id = owner_id).all()
        return render_template('singleUser.html', user_blogs = user_blogs)

    users = User.query.all()
    return render_template('index.html', users=users)

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    return render_template('newpost.html')

if __name__ == "__main__":
    app.run()