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
            new_entry = Blog(btitle, body)
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