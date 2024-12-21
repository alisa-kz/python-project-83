import psycopg2
import os
import validators

from dotenv import load_dotenv
from flask import Flask, render_template, request, flash, redirect, url_for, get_flashed_messages
from datetime import datetime
from urllib.parse import urlparse
from psycopg2.extras import DictCursor


class UrlsRepository:
    def __init__(self, db_url):
        self.db_url = db_url

    def get_connection(self):
        return psycopg2.connect(self.db_url)

    def get_content(self):
        sql = "SELECT * FROM urls ORDER BY id DESC"
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as curs:
                curs.execute(sql)
                urls = curs.fetchall()
            conn.commit()
            return urls

    def find(self, id):
        sql = "SELECT * FROM urls WHERE id=%s"
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as curs:
                curs.execute(sql, (id,))
                url = curs.fetchone()
            conn.commit()
            return url

    def save(self, url, now_date):
        sql = "INSERT INTO urls (name, created_at) VALUES (%s, %s)"
        sql_select = "SELECT * FROM urls WHERE name=%s"
        sql_id = "SELECT id FROM urls WHERE name=%s"
        with self.get_connection() as conn:
            with conn.cursor() as curs:
                curs.execute(sql_select, (url, ))
                url_ex = curs.fetchone()
                if url_ex:
                    flash("Страница уже существует", "alert alert-info")
                else:
                    curs.execute(sql, (url, now_date))
                    flash("Страница успешно добавлена", "alert alert-success")
                curs.execute(sql_id, (url, ))
                url_id = curs.fetchone()[0]
            conn.commit()
        return url_id

    # def destroy(self, id):
    #     with self.get_connection() as conn:
    #         with conn.cursor() as cur:
    #             cur.execute("DELETE FROM users WHERE id = %s", (id,))
    #         conn.commit()