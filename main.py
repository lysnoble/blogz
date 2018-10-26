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
    body = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30))
    password = db.Column(db.String(100))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'list_blogs', 'index', 'signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route("/")
def index():
    users = User.query.all()
    return render_template("index.html", title="Home", users=users)

@app.route("/blog")
def list_blogs():
    if request.args.get('id'):
        post_id = request.args.get('id')
        post = Blog.query.get(post_id)
        return render_template("post.html", post=post)
    elif request.args.get('user'):
        owner = request.args.get('user')
        posts = Blog.query.filter_by(owner_id=owner).all()
        return render_template("userpage.html", posts=posts)
    else:
        posts = Blog.query.all()
        return render_template("blog.html", title="Blog", posts=posts)

        

@app.route("/newpost", methods=['POST', 'GET'])
def newpost():
    
    owner = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']

        new_blog = Blog(title, body, owner)
        db.session.add(new_blog)
        db.session.commit()

        new_blog_route = '/blog?id=' + str(new_blog.id)
        return redirect(new_blog_route)
    else:
        return render_template("newpost.html", title="New Post")

@app.route("/signup", methods=['POST', 'GET'])
def signup():
    if request.method == 'GET':
        return render_template("signup.html", title="Sign Up")
    else:
        username = str(request.form["username"])
        password = str(request.form["password"])
        verify = str(request.form["verify"])

        username_error = ""
        password_error = ""
        verify_error = ""

        if not username:
            username_error = "Please enter a username"
        elif len(username) < 3:
            username_error = "Username is too short"
        elif len(username) > 20:
            username_error = "Username is too long"
        else:
            for char in username:
                if char == " ":
                    username_error = "That is not a vaild username"

        if not password:
            password_error = "Please enter a password"
        elif len(password) < 3:
            password_error = "Password is too short"
        elif len(password) > 20:
            password_error = "Password is too long"
        else:
            for char in password:
                if char == " ":
                    password_error = "That is not a vaild password"

        if verify != password:
            verify_error = "Passwords do not match"

        if not username_error and not password_error and not verify_error:
            existing_user = User.query.filter_by(username=username).first()
            if not existing_user:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect('/newpost')
            else:
                return render_template("signup.html", title="Signup", 
                username_error="That username already exists")
        else:
            return render_template("signup.html", title="Signup", 
            username_error=username_error, password_error=password_error,
            verify_error=verify_error)

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if not user:
            username_error = "That username does not exist"
            return render_template("login.html", title="Log In", 
            username_error=username_error)
        elif user.password != password:
            password_error = "Incorrect password"
            return render_template("login.html", title="Log In", 
            password_error=password_error)
        else:
            session['username'] = username
            return redirect('/newpost')
    else:
        return render_template("login.html", title="Login")

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

if __name__ == '__main__':
    app.run()
