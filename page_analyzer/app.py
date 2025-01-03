import os
from datetime import datetime

import requests
from dotenv import load_dotenv
from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from page_analyzer.data_builder import data_build
from page_analyzer.urls import normalize, validate
from page_analyzer.urls_repo import UrlsRepository

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

repo = UrlsRepository(DATABASE_URL)


@app.route("/")
def main():
    return render_template("index.html")


@app.post("/urls")
def get_url():
    url_dict = request.form.to_dict()
    url_full = url_dict['url']
    errors = validate(url_full)
    if errors:
        flash("Некорректный URL", "alert alert-danger")
        return (
            render_template(
                "index.html",
                url=url_full,
                errors=errors
            ),
            422,
        )
    url = normalize(url_full)
    now_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    url_id, unique = repo.save(url, now_date)
    if unique:
        flash("Страница успешно добавлена", "alert alert-success")
    else:
        flash("Страница уже существует", "alert alert-info")
    return redirect(url_for("show_url", id=url_id), code=302)


@app.route("/urls/<id>")
def show_url(id):
    url = repo.find(id)
    checks = repo.checks_get(id)
    return render_template(
        "show.html",
        url=url,
        checks=checks
    )


@app.route("/urls")
def show_all_urls():
    urls = repo.get_content()
    return render_template(
        "urls.html",
        urls=urls
    )


@app.post("/urls/<id>/checks")
def check_url(id):
    url = repo.find(id)
    url_name = url[1]
    try:
        response = requests.get(url_name)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        flash('Произошла ошибка при проверке', 'alert alert-danger')
        checks = repo.checks_get(id)
        return render_template(
            "show.html",
            url=url,
            checks=checks
        )
    check_data = data_build(response, id)
    check_id = repo.check_save(check_data)
    if check_id:
        flash("Страница успешно проверена", "alert alert-success")
    checks = repo.checks_get(id)
    return render_template(
        "show.html",
        url=url,
        checks=checks
    )
