import requests
from flask import Flask, render_template, request, session, url_for, send_from_directory, jsonify
from werkzeug.utils import redirect
from flask_mail import Mail, Message
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from data import db_session
from data.chat import Chats
from data.friends import Friend
from data.messages import Message
from data.posts import Posts
from data.send_email import send_email
from data.users import User
from forms.friends_search_form import FriendsSearchForm
from forms.loginform import LoginForm
from forms.user import RegisterForm
from flask_avatars import Avatars
import os
import random


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
    print(filename)
    app.config['AVATARS_SAVE_PATH'] = os.path.join(f'{os.getcwd()}/static/avatars')
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
    if request.method == 'POST':
        message = request.form['message_user_input']
        if message:
            db_sess = db_session.create_session()
            chat = db_sess.query(Chats).filter((
                                                       Chats.users == f'{user_id}, {current_user.id}') | (
                                                           Chats.users == f'{current_user.id}, {user_id}')).first()
            id = chat.id
            message_user = Message(
                content=message, chat_id=id, user_id=current_user.id
            )
            db_sess.add(message_user)
            db_sess.commit()
        return redirect(f"/message/{user_id}")



    else:
        db_sess = db_session.create_session()
        chat = db_sess.query(Chats).filter((
            Chats.users == f'{user_id}, {current_user.id}') | (Chats.users == f'{current_user.id}, {user_id}')).first()
        if chat:
            id = chat.id
        else:
            chat = Chats(
                users=f'{current_user.id}, {user_id}'
            )
            db_sess.add(chat)
            db_sess.commit()
            db_sess = db_session.create_session()
            chat = db_sess.query(Chats).filter((
                Chats.users == f'{user_id}, {current_user.id}') | (Chats.users == f'{current_user.id}, {user_id}')).first()
            id = chat.id

        messages = db_sess.query(Message).filter(Message.chat_id == id).all()
    friends = db_sess.query(User).filter(current_user.id != User.id).all()
    return render_template('message.html', messages=messages, friends=friends)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/register_email', methods=['GET', 'POST'])
def reqister_email():
    if request.method == 'POST':
        if request.form['mail_user'] != '':
            email = request.form['mail_user']
            return redirect(f"/confirm_email/{email}")
    return render_template('register_email.html', title='Регистрация')


@app.route('/confirm_email/<email>', methods=['GET', 'POST'])
def confirm_email(email):
    if request.method == 'POST':
        if "back" in list(dict(request.form).keys()):
            return redirect('/register_email')
        if "return_code" in list(dict(request.form).keys()):
            return redirect(f'/confirm_email/{email}')

        if "code_user" in list(dict(request.form).keys())[0]:
            code = list(dict(request.form).keys())[0].split('-')[1]
            if code == request.form[list(dict(request.form).keys())[0]]:
                return redirect(f'/register/{email}',)
            else:
                return render_template('mail_confirmation.html', code=code)

    else:
        message = random.randint(10000, 99999)
        send_email(str(message), email)

        return render_template('mail_confirmation.html', code=message)
    return render_template('mail_confirmation.html')


@app.route('/register/<email>', methods=['GET', 'POST'])
def reqister(email):
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   email=email,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == email).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   email=email,
                                   message="Пользователь с такой почтой уже есть")
        if db_sess.query(User).filter(User.name == form.name.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   email=email,
                                   message="Пользователь с таким именем уже есть")

        user = User(
            name=form.name.data,
            email=email
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    print(1)
    return render_template('register.html',  email=email, title='Регистрация', form=form)


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
    if request.method == 'POST':
        data = request.form
        input_name = data['friends_search']
        users = db_sess.query(User).filter(User.name.like(input_name)).filter(User.id != current_user.id).all()
    else:
        users = db_sess.query(User).filter(User.id != current_user.id).all()

    return render_template('friends.html', title='Friends', users=users)


@app.route('/follow_user/<user_id>', methods=['GET', 'POST'])
def follow_user(user_id):
    db_sess = db_session.create_session()
    my_user = db_sess.query(User).filter(User.id == current_user.id).first()
    user = db_sess.query(User).filter(User.id == user_id).first()
    followings = my_user.followings
    followers = user.followers
    if followings and followers:
        followings = followings.split(', ')
        followers = followers.split(', ')
        followed = False

        if str(current_user.id) in followers and str(user_id) in followings:
            index_followings = followings.index(str(user_id))
            index_followers = followers.index(str(current_user.id))
            del followings[index_followings]
            del followers[index_followers]

        elif str(current_user.id) in followers and not str(user_id) in followings:
            index_followers = followers.index(str(current_user.id))
            del followers[index_followers]

        elif not str(current_user.id) in followers and str(user_id) in followings:

            index_followings = followings.index(str(user_id))
            del followings[index_followings]

        else:
            followings.append(str(user_id))
            followers.append(str(current_user.id))
            followed = True
        followers_count = len(followers)
        followings = ', '.join(followings)
        followers = ', '.join(followers)
        my_user.followings = followings
        user.followers = followers

        db_sess.commit()
        return jsonify({'followers': followers_count, "followed": followed})
    else:
        my_user.followings = str(user_id)
        user.followers = str(current_user.id)
        db_sess.commit()
        return jsonify({'followers': 1, "followed": True})


@app.route('/message/', methods=['GET', 'POST'])
def message_1():

    db_sess = db_session.create_session()
    friends = db_sess.query(User).filter(current_user.id != User.id).all()
    return render_template('message.html', friends=friends)


def main():
    app.run(port=8081, host='127.0.0.1')


if __name__ == '__main__':
    db_session.global_init("db/blogs.db")
    main()
