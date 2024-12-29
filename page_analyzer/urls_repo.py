import psycopg2
from psycopg2.extras import DictCursor


class DatabaseConnection:
    def __init__(self, db_url):
        self.db_url = db_url

    def __enter__(self):
        self.conn = psycopg2.connect(self.db_url)
        self.curs = self.conn.cursor(cursor_factory=DictCursor)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.curs.close()
        self.conn.commit()
        self.conn.close()


class UrlsRepository:
    def __init__(self, db_url):
        self.db = DatabaseConnection(db_url)

    def get_content(self):
        sql = """SELECT urls.id, urls.name, MAX(url_checks.created_at)
        AS last_check_date, url_checks.status_code
        FROM urls LEFT JOIN url_checks
        ON urls.id = url_checks.url_id
        GROUP BY urls.id, url_checks.status_code ORDER BY urls.id DESC"""
        with self.db as db:
            db.curs.execute(sql)
            urls = db.curs.fetchall()
            return urls

    def find(self, id):
        sql = "SELECT * FROM urls WHERE id=%s"
        with self.db as db:
            db.curs.execute(sql, (id,))
            url = db.curs.fetchone()
            return url

    def save(self, url, now_date):
        sql = "INSERT INTO urls (name, created_at) VALUES (%s, %s)"
        sql_select = "SELECT * FROM urls WHERE name=%s"
        sql_id = "SELECT id FROM urls WHERE name=%s"
        with self.db as db:
            db.curs.execute(sql_select, (url, ))
            url_ex = db.curs.fetchone()
            unique = False
            if not url_ex:
                db.curs.execute(sql, (url, now_date))
                unique = True
            db.curs.execute(sql_id, (url, ))
            url_id = db.curs.fetchone()[0]
        return url_id, unique

    def check_save(self, check_data):
        sql = """INSERT INTO url_checks (
        url_id, created_at, status_code, h1, title, description
        )
        VALUES (
        %(url_id)s, %(ch_date)s, %(code)s, %(h1)s, %(title)s, %(content)s
        )"""
        sql_id = "SELECT id FROM url_checks WHERE url_id=%s"
        with self.db as db:
            db.curs.execute(sql, check_data)
            db.curs.execute(sql_id, (check_data['url_id'], ))
            check_id = db.curs.fetchone()[0]
            return check_id

    def checks_get(self, url_id):
        sql = "SELECT * FROM url_checks WHERE url_id=%s ORDER BY id DESC"
        with self.db as db:
            db.curs.execute(sql, (url_id, ))
            checks = db.curs.fetchall()
            return checks
