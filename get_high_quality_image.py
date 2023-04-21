import requests


def get_high_image(low_image):
    response = requests.get(low_image)
    response_url = response.url
    medium_quality_image = f"https://avatars.mds.yandex.net/get-kinopoisk-image/{response_url.split('/')[-3]}/{response_url.split('/')[-2]}/300x450"
    return medium_quality_image
