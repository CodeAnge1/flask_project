import requests

from films_data import films_db_session
from films_data.films import Film


def get_high_image(low_image):
    if "no-poster.gif" in low_image:
        medium_quality_image = "../static/images/not_found.jpg"
    else:
        response = requests.get(low_image)
        response_url = response.url
        medium_quality_image = f"https://avatars.mds.yandex.net/get-kinopoisk-image/{response_url.split('/')[-3]}/{response_url.split('/')[-2]}/300x450"
    return medium_quality_image


def main():
    db_name = "db/films.db"
    films_db_session.global_init(db_name)
    db_sess = films_db_session.create_session()
    for i in db_sess.query(Film).all():
        if i.high_poster_link is None:
            i.high_poster_link = get_high_image(i.poster_link)
            db_sess.commit()


if __name__ == '__main__':
    main()
