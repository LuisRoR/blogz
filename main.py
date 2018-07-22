from flask import Flask, request, redirect, render_template, session, flash
from app import app, db
from models import Blog, User
import cgi
from sqlalchemy import desc

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index', 'list_blogs']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

def validate_entry(title, body):
    result = ""
    blog_title = title
    blog_body = body
    blog_title_error = ''
    blog_body_error = ''

    if blog_title == '':
        blog_title_error = "Plese fill in the title"
    if blog_body == '':
        blog_body_error = "Please fill in the body"

    if blog_title_error or blog_body_error: 
        return render_template('blog_new_post.html', 
            blog = blog_title, body = blog_body,
            blog_title_error = blog_title_error,
            blog_body_error = blog_body_error
            )
    return result

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
            if user:
                if password != user.password:
                    flash('Incorrect password, try again!', 'error')
                    return redirect ('/login')  
            else:  
                flash('User does not exist, try again!', 'error')     
            return redirect ('/login') 
        
    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username= request.form['username']
        password = request.form['password']
        verify_password = request.form['verify']

        if username == '' or password == '' or verify_password == '':
            flash('One or more fields are invalid, try again', 'error') 
            return redirect ('/signup')
        if password != verify_password:
            flash('Passwords do not match, try again', 'error') 
            return redirect ('/signup')
    
        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        else:
            flash('Username already exists, try again!', 'error')

    return render_template('signup.html')      

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

@app.route('/', methods=[ 'GET'])
def index():
    users = User.query.all()
    return render_template('index.html',
        title="Index", 
        users=users) 


@app.route('/blog', methods=['POST', 'GET'])
def list_blogs(): 
    if request.method == 'POST': 
        blog_title = request.form['blog']
        blog_body = request.form['body']
       
        error_page = validate_entry(blog_title, blog_body)
        if error_page:
            return error_page

        #succes
        owner = User.query.filter_by(username=session['username']).first()
        new_blog = Blog(blog_title, blog_body, owner, pub_date=None)
        db.session.add(new_blog)
        db.session.commit()

        new_blog_id = new_blog.id
        return redirect(f'/display_blog?id={new_blog_id}') 


    """
    GET
    """
    if (request.method == 'GET'):
        blogs = Blog.query.all()
        blogs = Blog.query.order_by(Blog.pub_date.desc()).all()
        users = User.query.all()

    return render_template('blog_listings.html',
        title="Build A Blog", 
        blogs=blogs,
        users=users) 

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    if request.method == 'GET':
        return render_template('blog_new_post.html')
    return redirect('/')

@app.route('/display_blog', methods=['GET', 'POST'])
def display_blog():

    blog_id = int(request.args['id'])
    blog = Blog.query.get(blog_id)
   
    user = User.query.filter_by(id=blog.owner_id).first()

    db.session.add(user)
    db.session.commit()

    db.session.add(blog)
    db.session.commit()

    return render_template('display_blog.html', blog=blog, user=user)  

@app.route('/singleUser', methods=['GET'])
def single_user():
    user_id = int(request.args['id'])
    
    user = User.query.filter_by(id=user_id).first()
    owner = user_id
    blogs = Blog.query.all()
    blogs = Blog.query.filter_by(owner_id=owner).all()

    return render_template('singleUser.html', blogs=blogs, user=user) 
if __name__ == '__main__':
    app.run()
