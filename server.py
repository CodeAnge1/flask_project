import os

import requests
from flask import Flask, render_template, request, url_for, redirect
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from config import API_KEYS
from users_data.users import User
from films_data.films import Film
from films_data import films_db_session
from users_data import users_db_session
from forms.user import RegistrationForm, LoginForm

FILMS_PER_PAGE = 50
NO_DESCRIPTION = "FILM_WITHOUT_DESCRIPTION"

films_db_name = "db/films.db"
films_db_session.global_init(films_db_name)
films_db_sess = films_db_session.create_session()

users_db_name = "db/users.db"
users_db_session.global_init(users_db_name)
users_db_sess = users_db_session.create_session()

app = Flask(__name__)
app.template_folder = "Templates"
app.config['SECRET_KEY'] = os.urandom(36)
app.config['CACHE_TYPE'] = "SimpleCache"
app.config['CACHE_DEFAULT_TIMEOUT'] = 360

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return users_db_sess.query(User).get(user_id)


def get_high_image(low_image):
    if "no-poster.gif" not in low_image:
        response = requests.get(low_image)
        response_url = response.url
        medium_quality_image = f"https://avatars.mds.yandex.net/get-kinopoisk-image/{response_url.split('/')[-3]}/" \
                               f"{response_url.split('/')[-2]}/300x450"
    else:
        medium_quality_image = "../static/images/not_found.jpg"
    return medium_quality_image


def get_description(film_id):
    for api_key in API_KEYS:
        headers = {
            'accept': 'application/json',
            'X-API-KEY': api_key,
        }
        response = requests.get(f'https://kinopoiskapiunofficial.tech/api/v2.2/films/{film_id}', headers=headers)
        if response.status_code == 402:
            continue
        elif response.status_code == 200:
            return response.json()
    return None


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
    if current_user.is_authenticated:
        return redirect(url_for('home'))
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


@app.route('/films')
@app.route('/films/<int:page>')
def films(page=1):
    year_f, year_to = 0, 9999
    country, name = "", ""
    params = None
    dict_params = {}
    if '?' in request.url:
        params = "?" + str(request.url).split('?')[-1]
    films_groups = []
    film_group = []
    if params:
        list_of_params = params[1:].split('&')
        for i in list_of_params:
            i = i.split('=')
            dict_params[i[0]] = i[1]
        if dict_params['film_name']:
            name = " ".join(dict_params['film_name'].split('+'))
        if dict_params['film_country']:
            country = dict_params['film_country']
        if dict_params['film_current_year']:
            year = dict_params['film_current_year']
            db_req = films_db_sess.query(Film).filter(Film.year == year, Film.country.like(f"%{country}%"), (
                    Film.name.like(f"%{name}%") | (Film.original_name.like(f"%{name}%"))))
        elif dict_params['year_from'] or dict_params['year_to']:
            if dict_params['year_from']:
                year_f = int(dict_params['year_from'])
            if dict_params['year_to']:
                year_to = int(dict_params['year_to'])
            db_req = films_db_sess.query(Film).filter(year_f <= Film.year, Film.year <= year_to,
                                                      Film.country.like(f"%{country}%"), (
                                                              Film.name.like(f"%{name}%") |
                                                              Film.original_name.like(f"%{name}%")))
        else:
            db_req = films_db_sess.query(Film).filter(Film.country.like(f"%{country}%"), (
                    Film.name.like(f"%{name}%") |
                    Film.original_name.like(f"%{name}%")))
        if dict_params['film_genres']:
            genres = dict_params['film_genres'].split(',+')
            for genre in genres:
                db_req1 = films_db_sess.query(Film).filter(Film.country.like(f"%{country}%"), (
                        Film.name.like(f"%{name}%") | (
                            Film.original_name.like(f"%{name}%"))),
                                Film.genres.like(f"%{genre}%"))
                try:
                    if dict_params['this_only'] == "True":
                        db_req = db_req.intersect(db_req1)
                    else:
                        if genres.index(genre) == 0:
                            db_req = db_req.intersect(db_req1)
                        else:
                            db_req = db_req.union(db_req1)
                except AttributeError:
                    db_req = None
                    break
        count = db_req.count()
    else:
        db_req = films_db_sess.query(Film)
        count = db_req.count()
    if db_req:
        req = db_req.limit(FILMS_PER_PAGE).offset((page - 1) * FILMS_PER_PAGE)
        film_per_page_count = req.count()
        if film_per_page_count < 5:
            for i in req:
                film_info = {'id': i.film_id, 'name': i.name, 'name_len': len(i.name), 'rating': i.rating}
                if i.orig_poster_link:
                    image = i.orig_poster_link
                else:
                    if i.high_poster_link and "no-poster.gif" not in i.poster_link:
                        image = i.high_poster_link[:-7] + "orig"
                    elif i.high_poster_link:
                        image = i.high_poster_link
                    else:
                        image = get_high_image(i.poster_link)
                        if not i.high_poster_link:
                            i.high_poster_link = image
                        if "no-poster.gif" not in i.poster_link:
                            image = image[:-7] + "orig"
                            i.orig_poster_link = image
                film_info['poster'] = i.high_poster_link
                film_group.append(film_info)
            films_groups.append(film_group)
        else:
            for x, i in enumerate(req):
                film_info = {'id': i.film_id, 'name': i.name, 'name_len': len(i.name), 'rating': i.rating}
                if i.orig_poster_link:
                    image = i.orig_poster_link
                else:
                    if i.high_poster_link and "no-poster.gif" not in i.poster_link:
                        image = i.high_poster_link[:-7] + "orig"
                    elif i.high_poster_link:
                        image = i.high_poster_link
                    else:
                        image = get_high_image(i.poster_link)
                        if not i.high_poster_link:
                            i.high_poster_link = image
                        if "no-poster.gif" not in i.poster_link:
                            image = image[:-7] + "orig"
                            i.orig_poster_link = image
                film_info['poster'] = i.high_poster_link
                film_group.append(film_info)
                if len(film_group) == 5:
                    films_groups.append(film_group)
                    film_group = []
                elif len(film_group) < 5 and x == film_per_page_count - 1:
                    films_groups.append(film_group)
                    film_group = []
        max_page = count // 50
        if count % 50 != 0:
            max_page += 1
    else:
        max_page = 0
    return render_template('all_films.html', films_groups=films_groups, page=page, max_page=max_page, params=params)


@app.route('/film/<int:film_id>')
def film_page(film_id):
    info = films_db_sess.query(Film).get(film_id)
    genres = info.genres
    if "[" in genres:
        genres = genres.replace("[", "")
    if "]" in genres:
        genres = genres.replace("]", "")
    if r"\t" in genres:
        genres = genres.replace(r"\t", "")
    genres = list(genres.split(', '))
    for x in range(len(genres)):
        genres[x] = genres[x].replace("'", "")
    if info.orig_poster_link:
        image = info.orig_poster_link
    else:
        if info.high_poster_link and "no-poster.gif" not in info.poster_link:
            image = info.high_poster_link[:-7] + "orig"
        else:
            image = get_high_image(info.poster_link)
            if not info.high_poster_link:
                info.high_poster_link = image
            info.high_poster_link = image
            if "no-poster.gif" not in info.poster_link:
                image = image[:-7] + "orig"
            info.orig_poster_link = image
    if not current_user.is_anonymous:
        if info.description:
            description = info.description
        else:
            res = get_description(info.source_link.split('/')[4])
            if res['description']:
                description = res['description']
            else:
                description = NO_DESCRIPTION
            info.description = description
    else:
        description = None
    return render_template("film_page.html", image=image, name=info.name, original_name=info.original_name,
                           country=info.country, year=info.year, duration=info.duration, genres=', '.join(genres),
                           source_link=info.source_link, trailer_link=info.trailer_link, description=description,
                           no_desc=NO_DESCRIPTION)


@app.route('/search', methods=['POST', 'GET'])
def search():
    if request.method == 'GET':
        return render_template("search_film.html")
    elif request.method == 'POST':
        name = request.form.get('film-name', default=" ")
        country = request.form.get('country', default=" ")
        c_year = request.form.get('current-year', default=0)
        year_from = request.form.get('year-from', default=0)
        year_to = request.form.get('year-to', default=9999)
        genres = request.form.getlist('genres')
        only = request.form.get('this-only', default=False)
        if genres:
            for i in genres:
                genres[genres.index(i)] = i.strip()
            genres = ", ".join(genres)
        else:
            genres = ""
        if only:
            only = True
        return redirect(url_for('films', film_name=name, film_country=country, film_current_year=c_year,
                                year_from=year_from, year_to=year_to, film_genres=genres, this_only=only))


def main():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='127.0.0.1', port=port)


if __name__ == '__main__':
    main()
