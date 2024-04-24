from flask import render_template, request, redirect, url_for, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, current_user, logout_user, login_required

from config import app, db, login_manager
from models import Post, Author
from forms import PostForm, AuthorForm, LoginForm

from flask_wtf.csrf import CSRFProtect

SECRET_KEY = 'Мой секретный ключ'
app.config['SECRET_KEY'] = SECRET_KEY
csrf = CSRFProtect(app)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Author, user_id)


@app.route('/', methods=['GET', 'POST'])
def index():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        username = login_form.username.data
        password = login_form.password.data
        user = Author.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('get_authors_id', authors_id=user.id))
    return render_template('index.html', form=login_form)


@app.route("/get", methods=['GET'])
def get_list():
    posts = Post.query.all()
    serializer = []
    for post in posts:
        serializer.append({
            'id': post.id,
            'title': post.title,
            'text': post.text,
            'author': post.user_post.username
        })
    return jsonify(serializer)


@app.route('/authors', methods=['GET', 'POST'])

def get_authors():
    authorForm = AuthorForm()
    if request.method == 'POST':
        if authorForm.validate_on_submit():
            username = authorForm.username.data
            password = authorForm.password.data
            hashed_password = generate_password_hash(password)
            author = Author(username=username, password=hashed_password)
            db.session.add(author)
            db.session.commit()
    authors = Author.query.all()
    return render_template('authors.html', authors=authors, form=authorForm)


@app.route('/authors/<int:authors_id>', methods=['GET', 'POST'])
@login_required
def get_authors_id(authors_id):
    postForm = PostForm()
    if request.method == 'POST':
        if postForm.validate_on_submit():
            title = postForm.title.data
            text = postForm.text.data
            post = Post(title=title, text=text, author=authors_id)
            db.session.add(post)
            db.session.commit()
    a = authors_id
    b = url_for('get_authors_id', authors_id=a)
    posts = Post.query.filter_by(author=authors_id).all()
    return render_template('authors_id.html', form=postForm, b=b, posts=posts)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html', error=error), 404


@app.errorhandler(403)
def not_permitted(error):
    return render_template('403.html', error=error), 403


@app.errorhandler(401)
def not_authorized(error):
    return render_template('401.html', error=error), 401

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host='127.0.0.1', port=8080, debug=True)
