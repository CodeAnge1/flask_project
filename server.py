import os
import random

from flask import Flask, render_template

app = Flask(__name__)
app.template_folder = "Templates"


@app.route('/')
def main_page():
    return render_template('base.html')


@app.route('/film')
def film_page():
    return render_template("film_example.html")


def main():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='127.0.0.1', port=port)


if __name__ == '__main__':
    main()
