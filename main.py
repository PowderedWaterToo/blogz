from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import cgi

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='user')
    
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return self.username

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id')) 

    def __init__(self, title, body, user):
        self.title = title
        self.body = body
        self.user = user

@app.before_request
def require_login():
    allowed_routes = ['login', 'register', 'index', 'blog']
    if request.endpoint not in allowed_routes and 'username' not in session:
        flash("You must sign in to create a post", 'error')
        return redirect ('/login')

@app.route('/login', methods=['POST','GET'])
def login():
    if session.get('username') is not None:
        flash("Dude, you're already logged in. Logout first, if you want to.", 'error')
        return redirect('/blog')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password != password:
            flash("Your password is wrong! You fool!", 'error')
            print(session)
            return redirect('/login')
        if not user:
            flash("That username doesn't exist! I can't believe you!", 'error')
            print(session)
            return redirect('/login')
        if user and user.password == password:
            session['username'] = username
            flash("logged in, now get write'n!")
            print(session)
            return redirect('/newpost')

    return render_template('login.html')

@app.route('/signup', methods=['POST','GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']  
        existing_user = User.query.filter_by(username=username).first()
        
        if existing_user:
            flash("EXISTING USER!", 'error')
            print(session)
            return redirect('/signup')
        if not username or not password or not verify:
            flash("You must fill in all three fields! Why are you so lazy?", 'error')
            print(session)
            return redirect('/signup')
        if password != verify:
            flash("I know this is hard, but your password needs to match the verified password!", 'error')
            print(session)
            return redirect('/signup')      
        if len(password)<3 or len(username)<3:
            flash("Put a little more effort in and make sure your username and password are both over three characters long", 'error')
            print(session)
            return redirect('/signup')   
        else:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            print(session)
            return redirect('/newpost')

    return render_template('signup.html')

@app.route('/logout')
def logout():
    if session.get('username') is not None:
        del session['username']
        return redirect('/blog')
    else:
        flash("Dude, you're not even logged in", 'error')
        print(session)
        return redirect('/blog')   

@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', title="Blogs y'all!", users=users)


@app.route('/blog', methods=['POST', 'GET'])
def blog():

    blog_id = request.args.get("id")
    blog_user = request.args.get("user")
    if blog_id:
        blog = Blog.query.get(blog_id)
        return render_template('blog_single.html', title="Blogs y'all!", blog=blog)
    if blog_user:
        blog = Blog.query.filter_by(owner_id=blog_user).all()
        return render_template('blog.html', title="Blogs y'all!", blog=blog)
    blog = Blog.query.all()
    return render_template('blog.html', title="Blogs y'all!", blog=blog)


@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    if request.method == 'POST':
        btitle = cgi.escape(request.form['btitle'], quote=True)
        body = cgi.escape(request.form['body'], quote=True)
        terror = ""
        berror = ""

        if (not btitle) or (btitle.strip() == ""):
            terror = "You must write a title."

        if (not body) or (body.strip() == ""):
            berror = "You must write a blog entry if you want your freedom."

        if len(terror)>0 or len(berror)>0:
            return redirect("/newpost?terror=" + terror + "&berror=" + berror + "&btitle=" + btitle + "&body=" + body)
        else:
            user = User.query.filter_by(username=session['username']).first()
            new_entry = Blog(btitle, body, user)
            db.session.add(new_entry)
            db.session.commit()
            new_entry_id = str(new_entry.id)
            return redirect('/blog?id=' + new_entry_id)

    btitle = request.args.get("btitle")
    body = request.args.get("body")
    terror = request.args.get("terror")
    berror = request.args.get("berror")
    return render_template('newpost.html', title="Enter a post!", btitle=btitle, body=body, terror=terror, berror=berror)


if __name__ == '__main__':
    app.run()