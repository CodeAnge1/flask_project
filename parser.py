import requests

from films_data import films_db_session
from films_data.films import Film
from bs4 import BeautifulSoup


def main():
    film_counter = 0
    db_name = "db/films.db"
    films_db_session.global_init(db_name)
    db_sess = films_db_session.create_session()
    films_in_base = db_sess.query(Film).all()
    for year in range(2023, 1884, -1):
        for page in range(1, 25):
            response = requests.get(url=f"https://www.kinopoisk.ru/s/type/film/list/1/order/rating/m_act[year]"
                                        f"/{year}/page/{page}/200")
            soup = BeautifulSoup(response.text, 'lxml')
            try:
                if "К сожалению, по вашему запросу ничего не найдено..." in soup.find('h2',
                                                                                      class_="textorangebig").text:
                    break
            except AttributeError:
                pass
            search_results = soup.find(class_="search_results search_results_last")
            films = search_results.find_all(class_="element") + search_results.find_all(
                class_="element width_2") + search_results.find_all(class_="element width_3") + search_results.find_all(
                class_="element width_4") + search_results.find_all(class_="element width_5") + search_results.find_all(
                class_="element width_6") + search_results.find_all(class_="element width_7")
            for film in films:
                film_counter += 1
                print(film_counter)
                right = film.find(class_="right")
                try:
                    rating = right.find("div").text
                except AttributeError:
                    rating = -1.0

                picture_link = "https://st.kp.yandex.net" + film.find("p", class_="pic").find('a').find('img').get(
                    "title")
                film_info = film.find("div", class_="info")
                name = film_info.find("p", class_="name").find("a").text
                in_films = False
                for item in films_in_base:
                    if item.name == name or item.original_name == name:
                        in_films = True
                        break
                if not in_films:
                    try:
                        type_of_film = film_info.find_all("span", class_="gray")[1].find("i").find("a").get("films_data-type")
                    except AttributeError:
                        try:
                            type_of_film = film_info.find_all("span",
                                                              class_="gray")[1].find('a',
                                                                                     class_='lined '
                                                                                            'js-serp-metrika').get(
                                "films_data-type")
                        except AttributeError:
                            type_of_film = "Unknown"
                    time = film_info.find_all("span", class_="gray")[0].text
                    try:
                        time_and_original = time.split(', ')
                        if len(time_and_original) > 1:
                            original_name = time_and_original[0]
                        else:
                            original_name = None
                        time = time_and_original[-1]
                    except Exception:
                        original_name = None
                    if "мин" not in time:
                        time = "Unknown"
                    gray = film_info.find_all("span", class_="gray")[1].text.split('\n')
                    country = gray[0].split(',')[0]
                    if "..." in country:
                        country = country.split('...')[0]
                    genres = gray[1].split(', ')
                    for x in range(0, len(genres)):
                        if '(' in genres[x]:
                            genres[x] = genres[x].replace('(', '')
                        if ')' in genres[x]:
                            genres[x] = genres[x].replace(')', '')
                        if '...' in genres[x]:
                            genres[x] = genres[x].replace('...', '')
                        if '\t' in genres[x]:
                            genres[x] = genres[x].replace('\t', '')
                    genres = str(genres)
                    film_id = film_info.find("p", class_="name").find("a").get("href").split('/')[2]
                    trailer_link = f"https://widgets.kinopoisk.ru/discovery/film/{film_id}?noAd=1&hidden=&onlyPlayer=1"
                    res = requests.get(trailer_link)
                    if res.status_code != 200:
                        trailer_link = None

                    link_to_source = "https://www.kinopoisk.ru" + film_info.find("p", class_="name").find("a").get(
                        "href")
                    result = (
                        name, original_name, rating, time, country, genres, year, picture_link,
                        trailer_link, type_of_film, link_to_source, None)
                    film_row = Film()
                    film_row.name, film_row.original_name, film_row.rating, film_row.duration, \
                        film_row.country, film_row.genres, film_row.year, film_row.poster_link, \
                        film_row.trailer_link, film_row.type_of_film, film_row.source_link, \
                        film_row.description = result
                    db_sess.add(film_row)
                    db_sess.commit()


if __name__ == '__main__':
    main()
