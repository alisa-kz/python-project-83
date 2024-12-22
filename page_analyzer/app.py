import psycopg2
import os
import validators

from dotenv import load_dotenv
from flask import Flask, render_template, request, flash, redirect, url_for, get_flashed_messages
from datetime import datetime
from urllib.parse import urlparse
from psycopg2.extras import DictCursor
from page_analyzer.urls_repo import UrlsRepository


load_dotenv()
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
# conn = psycopg2.connect(DATABASE_URL)

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
    # sql = "INSERT INTO urls (name, created_at) VALUES (%s, %s)"
    # sql_select = "SELECT * FROM urls WHERE name=%s"
    # sql_id = "SELECT id FROM urls WHERE name=%s"
    # with conn:
    #     with conn.cursor() as curs:
    #         curs.execute(sql_select, (url, ))
    #         url_ex = curs.fetchone()
    #         if url_ex:
    #             flash("Страница уже существует", "alert alert-info")
    #         else:
    #             curs.execute(sql, (url, now_date))
    #             flash("Страница успешно добавлена", "alert alert-success")
    #         curs.execute(sql_id, (url, ))
    #         url_id = curs.fetchone()[0]
    #     conn.commit()
    return redirect(url_for("show_url", id=url_id), code=302)


@app.route("/urls/<id>")
def show_url(id):
    # sql = "SELECT * FROM urls WHERE id=%s"
    # with conn:
    #     with conn.cursor(cursor_factory=DictCursor) as curs:
    #         curs.execute(sql, (id,))
    #         url = curs.fetchone()
    #     conn.commit()
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
    # sql = "SELECT * FROM urls ORDER BY id DESC"
    # with conn:
    #     with conn.cursor(cursor_factory=DictCursor) as curs:
    #         curs.execute(sql)
    #         urls = curs.fetchall()
    #     conn.commit()
    urls = repo.get_content()
    messages = get_flashed_messages(with_categories=True)
    return render_template(
        "urls.html",
        urls=urls,
        messages=messages
    )


@app.post("/urls/<id>/checks")
def check_url(id):
    check_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    repo.check_save(id, check_date)
    checks = repo.checks_get(id)
    url = repo.find(id)
    ch_messages = get_flashed_messages(with_categories=True)
    return render_template(
        "show.html",
        url=url,
        checks=checks,
        ch_messages=ch_messages
    )
