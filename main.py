from flask import Flask, render_template, redirect, url_for
import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-key-for-development")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/games")
def list_games():
    # This route would normally fetch games data from a database
    # But as requested, we're not implementing the backend logic
    return render_template("games.html")


@app.route("/create-game", methods=["GET"])
def create_game_form():
    return render_template("create_game.html")


@app.route("/create-game", methods=["POST"])
def create_game():
    # This route would normally process the form submission
    # But as requested, we're not implementing the backend logic
    # Just redirect back to the index page for now
    return redirect(url_for("index"))


@app.route("/start-game", methods=["POST"])
def start_game():
    # This route would normally process the game start request
    # But as requested, we're not implementing the backend logic
    # Just redirect back to the games list for now
    return redirect(url_for("list_games"))


def main():
    app.run(
        debug=os.environ.get("FLASK_DEBUG", "true").lower() == "true",
        host=os.environ.get("FLASK_HOST", "127.0.0.1"),
        port=int(os.environ.get("FLASK_PORT", 5000)),
    )


if __name__ == "__main__":
    main()
