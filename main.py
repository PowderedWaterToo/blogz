from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import cgi

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:build-a-blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))

    def __init__(self, title, body):
        self.title = title
        self.body = body

#@app.before_request
#def require_login():
#    allowed_routes = ['login', 'register']
#    if request.endpoint not in allowed_routes and 'email' not in session:
#        return redirect ('/login')

@app.route('/')
def index():
    return redirect('/blog')

@app.route('/blog', methods=['POST', 'GET'])
def blog():

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        new_entry = Blog(title, body)
        db.session.add(new_entry)
        db.session.commit()

    blog_id = request.args.get("id")
    if blog_id:
        blog = Blog.query.get(blog_id)
        return render_template('blog_single.html', title="Blogs y'all!", blog=blog)
    blog = Blog.query.all()
    return render_template('blog.html', title="Blogs y'all!", blog=blog)

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    if request.method == 'POST':
        btitle = request.form['btitle']
        body = request.form['body']
        terror = ""
        berror = ""

        if (not btitle) or (btitle.strip() == ""):
            terror = "You must write a title."

        if (not body) or (body.strip() == ""):
            berror = "You must write a blog entry if you want your freedom."

        if len(terror)>0 or len(berror)>0:
            return redirect("/newpost?terror=" + terror + "&berror=" + berror + "&btitle=" + btitle + "&body=" + body)
        else:
            new_entry = Blog(btitle, body)
            db.session.add(new_entry)
            db.session.commit()
            new_entry_id = str(new_entry.id)
            return redirect('/blog?id=' + new_entry_id)

    btitle = request.args.get("btitle")
    body = request.args.get("body")
    terror = request.args.get("terror")
    berror = request.args.get("berror")
    return render_template('newpost.html', title="Enter a post!", btitle=btitle and cgi.escape(btitle, quote=True), body=body and cgi.escape(body, quote=True), terror=terror and cgi.escape(terror, quote=True), berror=berror and cgi.escape(berror, quote=True))

@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['email'] = email
            flash("logged in")
            print(session)
            return redirect('/')
        else:
            flash('user info is bunk', 'error')

    return render_template('login.html')

@app.route('/register', methods=['POST','GET'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']  
        
        #TODO - validate user's data

        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = email
            return redirect('/')
        else:
            #TODO - use better message
            return '<h1>Duplicate user</h1>'
        
    return render_template('register.html')

@app.route('/logout')
def logout():
    del session['email']
    return redirect('/')

@app.route('/delete-task', methods=['POST'])
def delete_task():

    task_id = int(request.form['task-id'])
    task = Task.query.get(task_id)
    task.completed = True
    db.session.add(task)
    db.session.commit()

    return redirect('/')


if __name__ == '__main__':
    app.run()