from flask import Flask, render_template, request, session, url_for, jsonify
from werkzeug.utils import redirect, send_from_directory
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from data import db_session
from data.chat import Chats
from data.friends import Friend
from data.messages import Message
from data.posts import Posts
from data.users import User
from forms.friends_search_form import FriendsSearchForm
from forms.loginform import LoginForm
from forms.user import RegisterForm
from flask_avatars import Avatars
import os
from itsdangerous import URLSafeTimedSerializer, SignatureExpired

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__name__))
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['AVATARS_SIZE_TUPLE'] = (30, 60, 250)
app.config['AVATARS_SAVE_PATH'] = os.path.join(f'{os.getcwd()}/static/avatars')
login_manager = LoginManager()
login_manager.init_app(app)
avatars = Avatars(app)


@app.route('/avatars/<path:filename>')
def get_avatar(filename):
    return send_from_directory(app.config['AVATARS_SAVE_PATH'], filename)


@app.route('/')
@app.route('/index')
def index():
    return render_template("base.html")


@app.route('/profile/<string:name>', methods=['GET', 'POST'])
def profile(name):
    db_sess = db_session.create_session()

    if current_user.is_authenticated:
        user = db_sess.query(User).filter(User.name == name).first()
        name = user.name
        image = user.image
        about = user.about
        github = user.github
        mail = user.second_email
        id = user.id
        posts = db_sess.query(Posts).filter(user.id == Posts.user_id)
        number = len(list(posts))
    else:
        return redirect(f'/base')
    if request.method == 'POST':
        try:

            data = dict(request.form)
            print(data)
            keys = list(data.keys())[0]
        except Exception:
            pass

        try:
            image_dict = dict(request.files)
            keys_image = list(image_dict.keys())[0]
        except Exception:
            pass

        try:
            if 'delete_agree' in keys:
                id2 = keys.split('-')[-1]
                db_sess = db_session.create_session()
                posts = db_sess.query(Posts).filter((Posts.id == id2),
                                                    Posts.user == current_user).first()
                if posts.image:
                    path = os.path.join(f'{os.getcwd()}/static/post_image')
                    os.remove(path + '/' + posts.image)
                if posts:
                    db_sess.delete(posts)
                    db_sess.commit()
                return redirect(f'/profile/{current_user.name}')
        except Exception:
            pass

        try:
            if 'about_user' in data or 'git_hub' in data or 'mail_user' in data:
                db_sess = db_session.create_session()

                user = db_sess.query(User).filter(User.id == current_user.id).first()
                if data['about_user']:
                    print(1)
                    user.about = data['about_user']
                if data['git_hub']:
                    print(2)
                    user.github = data['git_hub']
                if data['mail_user']:
                    print(3)
                    user.second_email = data['mail_user']
                db_sess.commit()
                return redirect(f'/profile/{current_user.name}')
        except Exception:
            pass

        try:

            if (keys != 'about' and 'about' in keys) or (
                    not str(request.files[keys_image]).split()[1] == "''" and 'file-' in keys_image):
                about = data[keys]
                id = keys.split('-')[1]
                db_sess = db_session.create_session()

                posts = db_sess.query(Posts).filter(Posts.id == id,
                                                    Posts.user_id == current_user.id
                                                    ).first()
                if not str(request.files[keys_image]).split()[1] == "''":
                    try:
                        if not posts.image:
                            print(1)
                            app.config['AVATARS_SAVE_PATH'] = os.path.join(f'{os.getcwd()}/static/post_image')
                            image = avatars.save_avatar(image_dict[keys_image])

                        else:
                            print(2)
                            path = os.path.join(f'{os.getcwd()}/static/post_image')
                            os.remove(path + '/' + posts.image)
                            app.config['AVATARS_SAVE_PATH'] = os.path.join(f'{os.getcwd()}/static/post_image')
                            print(image_dict[keys_image])
                            image = avatars.save_avatar(image_dict[keys_image])
                    except Exception:
                        image = posts.image
                else:
                    image = posts.image

                if posts:
                    posts.content = about
                    posts.image = image
                    db_sess.commit()
                    return redirect(f'/profile/{current_user.name}')
        except Exception:
            pass
        try:
            if request.form['about'] or not str(request.files['file1']).split()[1] == "''":
                data = request.files
                raw_filename = ''
                if keys_image == 'file1':
                    app.config['AVATARS_SAVE_PATH'] = os.path.join(f'{os.getcwd()}/static/post_image')

                    raw_filename = avatars.save_avatar(image_dict[keys_image])
                posts1 = Posts(content=request.form['about'],
                               user_id=current_user.id, image=raw_filename)
                db_sess.add(posts1)
                db_sess.commit()
        except Exception:
            if not str(request.files['file3']).split()[1] == "''":
                f = request.files.get('file3')
                app.config['AVATARS_SAVE_PATH'] = os.path.join(f'{os.getcwd()}/static/avatars')
                raw_filename = avatars.save_avatar(f)
                session['raw_filename'] = raw_filename
                return redirect(url_for('crop'))

    return render_template('profile.html', name=name, about=about, id=id, posts=posts, image=image, github=github,
                           mail=mail, count=number)


@app.route('/crop', methods=['GET', 'POST'])
def crop():
    if request.method == 'POST':
        x = request.form.get('x')
        y = request.form.get('y')
        w = request.form.get('w')
        h = request.form.get('h')
        filenames = avatars.crop_avatar(session['raw_filename'], x, y, w, h)
        path = os.path.join(f'{os.getcwd()}/static/avatars')
        os.remove(path + '/' + filenames[0])
        os.remove(path + '/' + filenames[1])
        os.remove(path + '/' + session['raw_filename'])
        try:
            os.rename(path + '/' + filenames[2], path + '/' + current_user.name + '.jpg')
            db_sess = db_session.create_session()
            user = db_sess.query(User).filter(User.id == current_user.id,
                                              ).first()
            user.image = current_user.name + '.jpg'
            db_sess.commit()
        except Exception:
            os.remove(path + '/' + current_user.name + '.jpg')
            os.rename(path + '/' + filenames[2], path + '/' + current_user.name + '.jpg')
            db_sess = db_session.create_session()
            user = db_sess.query(User).filter(User.id == current_user.id,
                                              ).first()
            user.image = current_user.name + '.jpg'
            db_sess.commit()

        return redirect(f'/profile/{current_user.name}')

    return render_template('crop.html')


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/message/<user_id>', methods=['GET', 'POST'])
def message(user_id):
    db_sess = db_session.create_session()
    chat = db_sess.query(Chats).filter(
        Chats.users == f'{user_id}, {current_user.id}' or Chats.users == f'{current_user.id}, {user_id}').first()
    if chat:
        id = chat.id
    else:
        chat = Chats(
            users=f'{current_user.id}, {user_id}'
        )
        db_sess.add(chat)
        db_sess.commit()
        db_sess = db_session.create_session()
        chat = db_sess.query(Chats).filter(
            Chats.users == f'{user_id}, {current_user.id}' or Chats.users == f'{current_user.id}, {user_id}').first()
        id = chat.id


    if request.method == 'POST':
        pass
    messages = db_sess.query(Message).filter(Message.chat_id == id).all()
    print(id)
    print(messages)
    return render_template('message.html', messages=messages)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пользователь с такой почтой уже есть")
        if db_sess.query(User).filter(User.name == form.name.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пользователь с таким именем уже есть")

        user = User(
            name=form.name.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/like_post/<post_id>', methods=['POST'])
@login_required
def like(post_id):
    db_sess = db_session.create_session()
    post = db_sess.query(Posts).filter((Posts.id == post_id)).first()
    members = post.likes
    if members:
        members = members.split(', ')
        liked = False
        if str(current_user.id) in members:
            index = members.index(str(current_user.id))
            del members[index]
        else:
            members.append(str(current_user.id))
            liked = True
        count_likes = len(members)
        members = ', '.join(members)
        post.likes = members

        db_sess.commit()
        return jsonify({"likes": count_likes, "liked": liked})
    else:
        post.likes = str(current_user.id)
        db_sess.commit()
        return jsonify({"likes": 1, "liked": True})


@app.route('/friends', methods=['GET', 'POST'])
def friends():
    db_sess = db_session.create_session()
    form = FriendsSearchForm()
    if request.method == 'POST':
        data = request.form
        input_name = data['friends_search']
        users = db_sess.query(User).filter(User.name == input_name).all()
        friends = db_sess.query(Friend).filter(Friend.name == input_name).all()

    else:
        users = db_sess.query(User).all()
        friends = db_sess.query(Friend).all()
    return render_template('friends.html', title='Friends', users=users, friends=friends, form=form)


def main():
    app.run(port=8082, host='127.0.0.1')


if __name__ == '__main__':
    db_session.global_init("db/blogs.db")
    main()
