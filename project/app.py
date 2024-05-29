from flask import render_template, request, redirect, url_for, jsonify
from sqlalchemy import select
from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, current_user, logout_user, login_required

from config import app, db, login_manager, api

from models import Post, Author, engine, Base
from forms import PostForm, AuthorForm, LoginForm

from flask_wtf.csrf import CSRFProtect

from flask_restful import Resource

SECRET_KEY = 'Мой секретный ключ'
app.config['SECRET_KEY'] = SECRET_KEY
csrf = CSRFProtect(app)

session = Session(engine, expire_on_commit=True, autoflush=False)


@login_manager.user_loader
def load_user(user_id):
    return session.get(Author, user_id)


@app.route('/', methods=['GET', 'POST'])
def index():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        username = login_form.username.data
        password = login_form.password.data
        user = session.execute(select(Author).filter_by(username=username)).scalar_one()
        print(f"ответ:{user}")
        if user and check_password_hash(user.password, password):
            if user.username == 'admin':
                login_user(user)
                print(f"логин1", login_user(user))
                return redirect(url_for('admin'))
            else:
                login_user(user)
                return redirect(url_for('get_authors_id', authors_id=user.id))
    with engine.begin() as conn:
        result = conn.execute(
            select(
                (Post.title).label('title'),
                (Post.text).label('text'),
                (Author.username).label('name')
            ).where(Author.id == Post.author)
        )
    return render_template('index.html', form=login_form, result=result)

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    with engine.begin() as conn:
        result = conn.execute(
            select(
                (Author.username).label('name'),
                (Author.id).label('name_id')
            )
        )


    if (current_user.is_authenticated)and(current_user.username == 'admin'):
        return render_template('admin.html', result=result)
    else:
        return 'Ошибка аутентификации!'


@app.route('/admin/<int:authors_id>', methods=['GET', 'POST'])
@login_required
def authors_name(authors_id):
    authorForm = AuthorForm()
    if request.method == 'POST':
        author = session.execute(select(Author).filter_by(id=authors_id)).scalar_one()

        author.username = authorForm.username.data
        author.password = generate_password_hash(authorForm.password.data)
        session.commit()
        return redirect(url_for('admin'))

    authors = session.execute(select(Author).filter_by(id=authors_id)).scalars()
    b = authors_id

    if (current_user.is_authenticated)and(current_user.username == 'admin'):
        return render_template('admin_id.html', b=b, authors=authors, form=authorForm)
    else:
        return 'Ошибка аутентификации!'

@app.route('/admin_del/<int:authors_id>', methods=['GET', 'POST'])
@login_required
def authors_name_del(authors_id):
    authorForm = AuthorForm()
    if request.method == 'POST':
        author_del = session.execute(
            select(Author).filter_by(id=authors_id)).scalar_one()
        session.delete(author_del)
        session.commit()
        return redirect(url_for('admin'))

    b = authors_id

    if (current_user.is_authenticated)and(current_user.username == 'admin'):
        return render_template('admin_del.html', b=b, form=authorForm)
    else:
        return 'Ошибка аутентификации!'



@app.route('/authors', methods=['GET', 'POST'])
def get_authors():
    authorForm = AuthorForm()
    authors = session.scalars(select(Author)).all()
    if request.method == 'POST':
        if authorForm.validate_on_submit():
            username = authorForm.username.data
            password = authorForm.password.data
            hashed_password = generate_password_hash(password)
            author = Author(username=username, password=hashed_password)
            try:
                session.add(author)
                session.commit()
                return redirect(url_for('index'))

            except:
                session.rollback()
                return 'Такой пользователь уже есть, создайте другово.'

    authors = session.scalars(select(Author)).all()
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
            session.add(post)
            session.commit()
    a = authors_id
    b = url_for('get_authors_id', authors_id=a)
    print(type(a))
    posts = session.execute(select(Post).filter_by(author=a)).scalars()
    print(f"ответ2:{posts}")
    if (current_user.is_authenticated)and(current_user.id == authors_id):
        return render_template('authors_id.html', form=postForm, b=b, posts=posts)
    else:
        return 'Ошибка аутентификации!'

@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def get_post_id(post_id):

    postForm = PostForm()
    if request.method == 'POST':
        post = session.execute(select(Post).filter_by(id=post_id)).scalar_one()
        post.title = postForm.title.data
        post.text = postForm.text.data
        session.commit()
        a = post.author
        return redirect(url_for('get_authors_id', authors_id=a))
    posts = session.execute(select(Post).filter_by(id=post_id)).scalars()
    post2 = session.execute(select(Post).filter_by(id=post_id)).scalar_one()
    b = post_id

    if (current_user.is_authenticated) and (current_user.id == post2.author):
        print(f'пост ',current_user)
        return render_template('post_id.html', form=postForm, b=b, post=posts)
    else:
        return 'Ошибка аутентификации!'


@app.route('/posts/<int:post_id>', methods=['GET', 'POST'])
@login_required
def del_post(post_id):
    postForm = PostForm()
    if request.method == 'POST':
        post = session.execute(select(Post).filter_by(id=post_id)).scalar_one()
        session.delete(post)
        session.commit()
        a = post.author
        return redirect(url_for('get_authors_id', authors_id=a))

    posts = session.execute(select(Post).filter_by(id=post_id)).scalars()
    b = post_id
    post2 = session.execute(select(Post).filter_by(id=post_id)).scalar_one()
    if (current_user.is_authenticated) and (current_user.id == post2.author):
        print(f'пост ',current_user)
        return render_template('delete.html', form=postForm, b=b, post=posts)
    else:
        return 'Ошибка аутентификации!'
    #return render_template('delete.html', form=postForm, b=b, post=posts)




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
        Base.metadata.create_all(engine)
    app.run(host='127.0.0.1', port=8080, debug=True)
