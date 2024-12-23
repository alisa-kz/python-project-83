import os
from datetime import datetime
from urllib.parse import urlparse

import requests
import validators
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from flask import (
    Flask,
    flash,
    get_flashed_messages,
    redirect,
    render_template,
    request,
    url_for,
)

from page_analyzer.urls_repo import UrlsRepository

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

repo = UrlsRepository(DATABASE_URL)


@app.route("/")
def main():
    return render_template("index.html")


def validate(url):
    errors = {}
    if len(url) > 255:
        errors["big_len"] = "Адрес сайта не должен превышать 255 символов"
    if not validators.url(url):
        errors["not_valid"] = "Неправильный адрес"
    return errors


@app.post("/urls")
def get_url():
    url_dict = request.form.to_dict()
    url_full = url_dict['url']
    errors = validate(url_full)
    if errors:
        flash("Некорректный URL", "alert alert-danger")
        messages = get_flashed_messages(with_categories=True)
        return (
            render_template(
                "index.html",
                url=url_full,
                errors=errors,
                messages=messages
            ),
            422,
        )
    url_norm = urlparse(url_full)
    url = url_norm.scheme + "://" + url_norm.hostname
    now_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    url_id = repo.save(url, now_date)
    return redirect(url_for("show_url", id=url_id), code=302)


@app.route("/urls/<id>")
def show_url(id):
    url = repo.find(id)
    checks = repo.checks_get(id)
    messages = get_flashed_messages(with_categories=True)
    return render_template(
        "show.html",
        url=url,
        checks=checks,
        messages=messages
    )


@app.route("/urls")
def show_all_urls():
    urls = repo.get_content()
    messages = get_flashed_messages(with_categories=True)
    return render_template(
        "urls.html",
        urls=urls,
        messages=messages
    )


@app.post("/urls/<id>/checks")
def check_url(id):
    check_data = {}
    check_data['id'] = id
    url = repo.find(id)
    url_name = url[1]
    try:
        response = requests.get(url_name)
        response.raise_for_status()
        code = response.status_code
        check_data['code'] = code
        bs = BeautifulSoup(response.text, 'html.parser')
        h1 = bs.h1.string
        check_data['h1'] = h1
        title = bs.title.string
        check_data['title'] = title
        metas = bs.find_all('meta')
        for meta in metas:
            if meta.get('name') == 'description':
                content = meta['content']
                check_data['content'] = content
                break
            else:
                check_data['content'] = None
    except requests.exceptions.RequestException:
        flash('Произошла ошибка при проверке', 'alert alert-danger')
        ch_messages = get_flashed_messages(with_categories=True)
        checks = repo.checks_get(id)
        return render_template(
            "show.html",
            url=url,
            checks=checks,
            ch_messages=ch_messages
        )
    ch_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    check_data['ch_date'] = ch_date
    repo.check_save(check_data)
    checks = repo.checks_get(id)
    ch_messages = get_flashed_messages(with_categories=True)
    return render_template(
        "show.html",
        url=url,
        checks=checks,
        ch_messages=ch_messages
    )
