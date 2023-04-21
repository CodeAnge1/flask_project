import sqlite3
import requests

from bs4 import BeautifulSoup


def main():
    counter = 0
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
                counter += 1
                right = film.find(class_="right")
                try:
                    rating = right.find("div").text
                except AttributeError:
                    rating = "Unknown"
                list_ = right.find(class_="links").find_all("li")

                picture_link = "https://st.kp.yandex.net" + film.find("p", class_="pic").find('a').find('img').get(
                    "title")
                film_info = film.find("div", class_="info")
                name = film_info.find("p", class_="name").find("a").text
                in_films = False
                for elem in cursor.execute("""SELECT name FROM films""").fetchall():
                    if elem[0] == name:
                        in_films = True
                        break
                if not in_films:
                    try:
                        type_of_film = film_info.find_all("span", class_="gray")[1].find("i").find("a").get("data-type")
                    except AttributeError:
                        try:
                            type_of_film = film_info.find_all("span", class_="gray")[1].find('a', class_='lined js-serp-metrika').get("data-type")
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
                    gray = film_info.find_all("span", class_="gray")[1].text.split('\n')
                    country = gray[0].split(',')[0]
                    genres = gray[1]

                    film_id = film_info.find("p", class_="name").find("a").get("href").split('/')[2]

                    trailer_link = f"https://widgets.kinopoisk.ru/discovery/film/{film_id}?noAd=1&hidden=&onlyPlayer=1"
                    res = requests.get(trailer_link)
                    if res.status_code != 200:
                        trailer_link = None

                    actor_link = f"https://www.kinopoisk.ru/film/{film_id}/cast/#actor"
                    res = requests.get(actor_link)
                    if res.status_code == 200:
                        try:
                            actors = {}
                            soup_3 = BeautifulSoup(res.text, 'lxml')
                            table = soup_3.find('div', class_="block_left")
                            roles = []
                            for i in table.find_all('a'):
                                if "name=" in str(i):
                                    roles.append(str(i).split('"')[1])
                            for keys in roles:
                                actors[keys] = []
                            x = -1
                            for num, actor_about in zip(table.find_all('div', class_="num"),
                                                        table.find_all('div', class_="actorInfo")):
                                if num.text == '1.':
                                    x += 1
                                actor_info = {
                                    'photo': "https://st.kp.yandex.net" + actor_about.find('div', class_="photo").find(
                                        'a').get(
                                        'href'),
                                    'name': actor_about.find('div', class_="info").find('div', class_="name").find(
                                        'a').text,
                                    "source_link": "https://www.kinopoisk.ru/" + actor_about.find('div',
                                                                                                  class_="info").find(
                                        'div', class_="name").find('a').get("href")
                                }

                                actors[roles[x]].append(actor_info)
                        except AttributeError:
                            actors = None
                    else:
                        actors = None
                    if not time:
                        time = 'Unknown'

                    link_to_source = "https://www.kinopoisk.ru" + film_info.find("p", class_="name").find("a").get(
                        "href")
                    result = (name, original_name, rating, time, country, genres, year, picture_link, trailer_link, type_of_film,
                              actor_link, str(actors), link_to_source)
                    cursor.execute("INSERT INTO films VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", result)
                    connector.commit()
                print(counter)


if __name__ == '__main__':
    db_name = "films_data.db"
    connector = sqlite3.connect(db_name, timeout=30)
    cursor = connector.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS films(
    name TEXT,
    original_name TEXT,
    rating TEXT,
    time TEXT,
    country TEXT,
    genres TEXT,
    year INT,
    poster_link TEXT,
    trailer_link TEXT,
    type_of_film TEXT,
    actor_link TEXT,
    actors TEXT,
    source TEXT);
    """)
    main()
