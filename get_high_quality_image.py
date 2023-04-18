import requests

link = "https://st.kp.yandex.net/images/sm_film/4786341.jpg"
response = requests.get(link)
response_url = response.url
medium_quality_image = f"https://avatars.mds.yandex.net/get-kinopoisk-image/{response_url.split('/')[-3]}/{response_url.split('/')[-2]}/300x450"

print(medium_quality_image)
