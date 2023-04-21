import os
import random
import requests

from flask_wtf import FlaskForm
from flask import Flask, render_template, request
from wtforms import StringField, PasswordField, BooleanField, SubmitField

app = Flask(__name__)
app.template_folder = "Templates"
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['TESTING'] = True
app.config['DEBUG'] = True


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
def main_page():
    return render_template('main_page.html')


@app.route('/films')
def films():
    # count = request.args.get('count')
    # print(count)
    films_dict = {'films': [
        [{'name': 'Герои Энвелла (сериал)', 'poster': get_high_image('https://st.kp.yandex.net/images/sm_film/1072974.jpg'),
         'rating': 9.3, 'name_len': len('Герои Энвелла (сериал)')},
        {'name': 'Он вам не Димон', 'poster': get_high_image('https://st.kp.yandex.net/images/no-poster.gif'), 'name_len': len('Он вам не Димон'), 'rating': 4.0},
        {'name': 'Голубая планета 2 (мини-сериал)', 'poster': get_high_image('https://st.kp.yandex.net/images/sm_film/1073233.jpg'), 'name_len': len('Голубая планета 2 (мини-сериал)'), 'rating': 9.1},
        {'name': 'Самадхи, Часть 1. Майя, иллюзия обособленного ЯСамадхи, Часть 1. Майя, иллюзия обособленного ЯСамадхи, Часть 1. Майя, иллюзия обособленного Я', 'name_len': len('Самадхи, Часть 1. Майя, иллюзия обособленного ЯСамадхи, Часть 1. Майя, иллюзия обособленного ЯСамадхи, Часть 1. Майя, иллюзия обособленного Я'), 'poster': get_high_image('https://st.kp.yandex.net/images/sm_film/1101247.jpg'), 'rating': 9.1},
        {'name': 'Энчантималс. Дом, милый дом (ТВ)', 'name_len': len('Энчантималс. Дом, милый дом (ТВ)'), 'poster': get_high_image('https://st.kp.yandex.net/images/sm_film/1101316.jpg'), 'rating': 9.0}],
        [{'name': 'Герои Энвелла (сериал)',
          'poster': get_high_image('https://st.kp.yandex.net/images/sm_film/1072974.jpg'),
          'rating': 9.3, 'name_len': len('Герои Энвелла (сериал)')},
         {'name': 'Он вам не Димон', 'poster': get_high_image('https://st.kp.yandex.net/images/no-poster.gif'),
          'name_len': len('Он вам не Димон'), 'rating': 4.0},
         {'name': 'Голубая планета 2 (мини-сериал)',
          'poster': get_high_image('https://st.kp.yandex.net/images/sm_film/1073233.jpg'),
          'name_len': len('Голубая планета 2 (мини-сериал)'), 'rating': 9.1},
         {
             'name': 'Самадхи, Часть 1. Майя, иллюзия обособленного ЯСамадхи, Часть 1. Майя, иллюзия обособленного ЯСамадхи, Часть 1. Майя, иллюзия обособленного Я',
             'name_len': len(
                 'Самадхи, Часть 1. Майя, иллюзия обособленного ЯСамадхи, Часть 1. Майя, иллюзия обособленного ЯСамадхи, Часть 1. Майя, иллюзия обособленного Я'),
             'poster': get_high_image('https://st.kp.yandex.net/images/sm_film/1101247.jpg'), 'rating': 9.1},
         {'name': 'Энчантималс. Дом, милый дом (ТВ)', 'name_len': len('Энчантималс. Дом, милый дом (ТВ)'),
          'poster': get_high_image('https://st.kp.yandex.net/images/sm_film/1101316.jpg'), 'rating': 9.0}],
        [{'name': 'Al Hayba (сериал)', 'name_len': len('Al Hayba (сериал)'), 'poster': get_high_image('https://st.kp.yandex.net/images/no-poster.gif'), 'rating': 6.0}]]}
    return render_template('all_films.html', films_dict=films_dict)


@app.route('/film')
def film_page():
    return render_template("film_first_example.html")


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


@app.route('/registration')
def registration():
    return render_template("registration_page.html")


def main():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='127.0.0.1', port=port)


if __name__ == '__main__':
    main()
