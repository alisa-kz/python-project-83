import psycopg2
from psycopg2.extras import DictCursor


class DatabaseConnection:
    def __init__(self, db_url):
        self.db_url = db_url

    def __enter__(self):
        self.conn = psycopg2.connect(self.db_url)
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()


class UrlsRepository:
    def __init__(self, db_url):
        self.db_url = db_url

    def get_content(self):
        sql = """SELECT urls.id, urls.name, MAX(url_checks.created_at)
        AS last_check_date, url_checks.status_code
        FROM urls LEFT JOIN url_checks
        ON urls.id = url_checks.url_id
        GROUP BY urls.id, url_checks.status_code ORDER BY urls.id DESC"""
        with DatabaseConnection(self.db_url) as conn:
            with conn.cursor(cursor_factory=DictCursor) as curs:
                curs.execute(sql)
                urls = curs.fetchall()
            conn.commit()
            return urls

    def find(self, id):
        sql = "SELECT * FROM urls WHERE id=%s"
        with DatabaseConnection(self.db_url) as conn:
            with conn.cursor(cursor_factory=DictCursor) as curs:
                curs.execute(sql, (id,))
                url = curs.fetchone()
            conn.commit()
            return url

    def save(self, url, now_date):
        sql = "INSERT INTO urls (name, created_at) VALUES (%s, %s)"
        sql_select = "SELECT * FROM urls WHERE name=%s"
        sql_id = "SELECT id FROM urls WHERE name=%s"
        with DatabaseConnection(self.db_url) as conn:
            with conn.cursor() as curs:
                curs.execute(sql_select, (url, ))
                url_ex = curs.fetchone()
                unique = False
                if not url_ex:
                    curs.execute(sql, (url, now_date))
                    unique = True
                curs.execute(sql_id, (url, ))
                url_id = curs.fetchone()[0]
            conn.commit()
        return url_id, unique

    def check_save(self, check_data):
        sql = """INSERT INTO url_checks (
        url_id, created_at, status_code, h1, title, description
        )
        VALUES (
        %(url_id)s, %(ch_date)s, %(code)s, %(h1)s, %(title)s, %(content)s
        )"""
        sql_id = "SELECT id FROM url_checks WHERE url_id=%s"
        with DatabaseConnection(self.db_url) as conn:
            with conn.cursor() as curs:
                curs.execute(sql, check_data)
                curs.execute(sql_id, (check_data['url_id'], ))
                check_id = curs.fetchone()[0]
            conn.commit()
        return check_id

    def checks_get(self, url_id):
        sql = "SELECT * FROM url_checks WHERE url_id=%s ORDER BY id DESC"
        with DatabaseConnection(self.db_url) as conn:
            with conn.cursor(cursor_factory=DictCursor) as curs:
                curs.execute(sql, (url_id, ))
                checks = curs.fetchall()
            conn.commit()
            return checks
