import os
import random
import requests

from flask_caching import Cache
from users_data.users import User
from films_data.films import Film
from films_data import films_db_session
from users_data import users_db_session
from forms.user import RegistrationForm, ConfirmForm, LoginForm
from flask import Flask, render_template, request, url_for, redirect
from flask_login import LoginManager, login_user, login_required, logout_user

FILMS_PER_PAGE = 50

films_db_name = "db/films.db"
films_db_session.global_init(films_db_name)
films_db_sess = films_db_session.create_session()

users_db_name = "db/users.db"
users_db_session.global_init(users_db_name)
users_db_sess = users_db_session.create_session()

app = Flask(__name__)
app.template_folder = "Templates"
app.config['SECRET_KEY'] = os.urandom(36)
app.config['TESTING'] = True
app.config['DEBUG'] = True
app.config['CACHE_TYPE'] = "SimpleCache"
app.config['CACHE_DEFAULT_TIMEOUT'] = 180
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./db/films.db'

cache = Cache(app)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return users_db_sess.query(User).get(user_id)


def get_high_image(low_image):
    if "no-poster.gif" not in low_image:
        response = requests.get(low_image)
        response_url = response.url
        medium_quality_image = f"https://avatars.mds.yandex.net/get-kinopoisk-image/{response_url.split('/')[-3]}/{response_url.split('/')[-2]}/300x450"
    else:
        medium_quality_image = "../static/images/not_found.jpg"
    return medium_quality_image


@app.route('/')
@app.route('/home')
def home():
    return render_template('main_page.html')


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    form = RegistrationForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('registration.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        if users_db_sess.query(User).filter(User.email == form.email.data).first() \
                or users_db_sess.query(User).filter(User.login == form.login.data).first():
            return render_template('registration.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            login=form.login.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        users_db_sess.add(user)
        users_db_sess.commit()
        return redirect('/')
    return render_template('registration.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = users_db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect('/')
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


# @app.route('/confirm_mail', methods=['POST', 'GET'])
# def confirm(data):
#     form = ConfirmForm()
#     message = "Ваш код подтверждения - " + str(confirmation_code)
#     send_mail(receiver, message)
#     render_template('confirm.html', form=form)
#     if form.validate_on_submit():
#         if form.code.data != confirmation_code:
#             return render_template('confirm.html', title='Регистрация',
#                                    form=form,
#                                    message="Введён неверный код")
#         else:
#             return True
#     return render_template('confirm.html', form=form)
#     #     confirmation_code = random.randrange(100000, 999999)
#     #     message = "Ваш код подтверждения - " + str(confirmation_code)
#     # users_db_sess.add(class_)
#     # users_db_sess.commit()


@app.route('/films')
@app.route('/films/<int:page>')
# @cache.cached()
def films(page=1):
    films_groups = []
    film_group = []
    for x, i in enumerate(films_db_sess.query(Film).limit(FILMS_PER_PAGE).offset((page - 1) * FILMS_PER_PAGE)):
        film_info = {'id': i.film_id, 'name': i.name, 'name_len': len(i.name), 'rating': i.rating}
        if i.high_poster_link:
            film_info['poster'] = i.high_poster_link
        else:
            film_info['poster'] = get_high_image(i.poster_link)
        film_group.append(film_info)
        if len(film_group) == 5:
            films_groups.append(film_group)
            film_group = []
    return render_template('all_films.html', films_groups=films_groups)


@app.route('/film/<int:film_id>')
def film_page(film_id):
    info = films_db_sess.query(Film).get(film_id)
    genres = info.genres
    if "[" in genres:
        genres = genres.replace("[", "")
    if "]" in genres:
        genres = genres.replace("]", "")
    if "\t" in genres:
        genres = genres.replace("\t", "")
    genres = list(genres.split(', '))
    for x in range(len(genres)):
        genres[x] = genres[x].replace("'", "")
    if info.high_poster_link:
        image = info.high_poster_link
    else:
        image = get_high_image(info.poster_link)
        info.high_poster_link = image
        films_db_sess.commit()
    return render_template("film_page.html", image=image, name=info.name, original_name=info.original_name,
                           country=info.country, year=info.year, duration=info.duration, genres=', '.join(genres),
                           source_link=info.source_link, trailer_link=info.trailer_link)


@app.route('/search', methods=['POST', 'GET'])
def search():
    if request.method == 'GET':
        return render_template("search_film.html")
    elif request.method == 'POST':
        print(request.form)
        # for i in request.form:
        #     print(i)
        # for i in range(32):
        #     try:
        #         print(request.form[f'role{i}'])
        #     except Exception:
        #         print('off')
        return "ABOBA"


def main():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='127.0.0.1', port=port)


if __name__ == '__main__':
    main()
