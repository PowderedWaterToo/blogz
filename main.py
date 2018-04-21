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
        return '<User %r>' % self.username

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id')) 

    def __init__(self, title, body, user):
        self.title = title
        self.body = body
        self.user = user


@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("logged in")
            print(session)
            return redirect('/newpost')
        else:
            flash('user info is bunk', 'error')

    return render_template('login.html')

@app.route('/signup', methods=['POST','GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']  
        
        #TODO - validate user's data

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        else:
            #TODO - use better message
            return '<h1>Duplicate user</h1>'
        
    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')


@app.route('/')
def index():
    return redirect('/blog')


@app.route('/blog', methods=['POST', 'GET'])
def blog():

    blog_id = request.args.get("id")
    if blog_id:
        blog = Blog.query.get(blog_id)
        return render_template('blog_single.html', title="Blogs y'all!", blog=blog)
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