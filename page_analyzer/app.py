from dotenv import load_dotenv
from flask import Flask, render_template
import os


load_dotenv()
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")


@app.route("/")
def main():
    return render_template("main.html")