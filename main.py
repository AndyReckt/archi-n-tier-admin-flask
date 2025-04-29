from flask import Flask, render_template, redirect, url_for, request, flash
import os
import random
from dotenv import load_dotenv
from model.database import get_db_session, close_db_session
from model.sa_model import Game, Player, PlayerType
from sqlalchemy import desc

# Load environment variables from .env file if it exists
load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-key-for-development")


# Helper functions
def get_game_status(game):
    """Determine the status of a game"""
    if game.current_turn == 0:
        return "not_started"
    elif game.current_turn >= game.nb_max_turn:
        return "finished"
    else:
        return "in_progress"


def count_player_types(players, player_type):
    """Count the number of players of a specific type"""
    return sum(1 for player in players if player.player_type.name == player_type)


def can_start_game(game):
    """Check if a game can be started"""
    # A game can be started if it has at least 4 players and at least one wolf
    if len(game.players) < 4:
        return False

    # Check if there's at least one wolf
    wolf_count = count_player_types(game.players, "WOLF")
    return wolf_count > 0


def get_max_wolves(max_players):
    """Calculate the maximum number of wolves based on 25% rule"""
    return int(max_players * 0.25)


# Register template helpers
@app.context_processor
def inject_helpers():
    return {
        "get_game_status": get_game_status,
        "count_player_types": count_player_types,
        "can_start_game": can_start_game,
        "get_max_wolves": get_max_wolves,
    }


@app.teardown_appcontext
def shutdown_session(exception=None):
    close_db_session()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/games")
def list_games():
    # Get filter status from query param
    status = request.args.get("status", "all")

    # Get database session
    db = get_db_session()

    # Get all games
    games = db.query(Game).order_by(desc(Game.id)).all()

    # Add status to each game
    for game in games:
        game.status = get_game_status(game)

    # Filter games by status
    if status != "all":
        games = [game for game in games if game.status == status]

    return render_template("games.html", games=games, status=status)


@app.route("/create-game", methods=["GET"])
def create_game_form():
    return render_template("create_game.html")


@app.route("/create-game", methods=["POST"])
def create_game():
    # Get form data
    nb_max_turn = int(request.form.get("nb_max_turn", 30))
    width = int(request.form.get("width", 10))
    height = int(request.form.get("height", 10))
    max_players = int(request.form.get("max_players", 4))
    
    # Verify max_players is at least 4
    if max_players < 4:
        max_players = 4
        flash("Le nombre minimum de joueurs a été fixé à 4", "warning")

    # Create a new game
    db = get_db_session()
    game = Game(
        nb_max_turn=nb_max_turn,
        width=width,
        height=height,
        max_players=max_players,
    )
    
    # Save to database
    db.add(game)
    db.commit()

    return redirect(url_for("list_games"))


@app.route("/join-game/<int:game_id>", methods=["GET", "POST"])
def join_game(game_id):
    db = get_db_session()
    game = db.query(Game).filter_by(id=game_id).first()
    
    if not game or get_game_status(game) != "not_started":
        flash("Impossible de rejoindre cette partie", "error")
        return redirect(url_for("list_games"))
    
    # Check if the game has reached the maximum number of players
    if len(game.players) >= game.max_players:
        flash("Cette partie a atteint son nombre maximum de joueurs", "error")
        return redirect(url_for("list_games"))
    
    if request.method == "POST":
        pseudo = request.form.get("pseudo", "")
        
        # Validate pseudo (must be a single letter)
        if len(pseudo) != 1:
            flash("Le pseudo doit être une seule lettre", "error")
            return redirect(url_for("join_game", game_id=game_id))
        
        # Check if pseudo is already taken in this game
        existing_pseudos = [p.pseudo for p in game.players]
        if pseudo in existing_pseudos:
            flash("Ce pseudo est déjà utilisé dans cette partie", "error")
            return redirect(url_for("join_game", game_id=game_id))
        
        # Determine player type randomly, with a maximum of 25% wolves
        max_wolves = get_max_wolves(game.max_players)
        current_wolves = count_player_types(game.players, "WOLF")
        
        # If we already reached the max number of wolves, force villager
        if current_wolves >= max_wolves:
            player_type = PlayerType.VILLAGER
        else:
            # Calculate the remaining wolf slots and total remaining slots
            remaining_wolf_slots = max_wolves - current_wolves
            total_remaining_slots = game.max_players - len(game.players)
            
            # Calculate the probability of being a wolf
            # This ensures we maintain approximately 25% wolves
            wolf_probability = remaining_wolf_slots / total_remaining_slots
            
            # Randomly assign player type based on probability
            player_type = PlayerType.WOLF if random.random() < wolf_probability else PlayerType.VILLAGER
        
        # Create player
        try:
            player = Player(
                pseudo=pseudo, 
                player_type=player_type, 
                field_distance=2 if player_type == PlayerType.WOLF else 1
            )
            game.players.append(player)
            game.board.subscribe_player(player)
            db.commit()
            
            type_str = "LOUP" if player_type == PlayerType.WOLF else "VILLAGEOIS"
            flash(f"Vous avez rejoint la partie en tant que {type_str}", "success")
            return redirect(url_for("list_games"))
        except ValueError as e:
            flash(str(e), "error")
            return redirect(url_for("join_game", game_id=game_id))
    
    # Show the join form
    return render_template("join_game.html", game=game)


@app.route("/view-game/<int:game_id>")
def view_game(game_id):
    # This would be implemented to view a game
    # For now we just redirect to the games list
    return redirect(url_for("list_games"))


@app.route("/start-game", methods=["POST"])
def start_game():
    game_id = request.form.get("game_id")

    # Get the game
    db = get_db_session()
    game = db.query(Game).filter_by(id=game_id).first()

    if not game:
        flash("Partie introuvable", "error")
        return redirect(url_for("list_games"))
    
    if get_game_status(game) != "not_started":
        flash("Cette partie a déjà commencé ou est terminée", "error")
        return redirect(url_for("list_games"))
    
    # Check if there are at least 4 players
    if len(game.players) < 4:
        flash("Il faut au moins 4 joueurs pour démarrer la partie", "error")
        return redirect(url_for("list_games"))
    
    # Check if there's at least one wolf
    wolf_count = count_player_types(game.players, "WOLF")
    if wolf_count == 0:
        flash("Il faut au moins un loup pour démarrer la partie", "error")
        return redirect(url_for("list_games"))

    # Start the game by incrementing the turn counter
    game.current_turn = 1
    db.commit()
    flash("La partie a démarré avec succès", "success")
    return redirect(url_for("list_games"))


def main():
    app.run(
        debug=os.environ.get("FLASK_DEBUG", "true").lower() == "true",
        host=os.environ.get("FLASK_HOST", "127.0.0.1"),
        port=int(os.environ.get("FLASK_PORT", 5000)),
    )


if __name__ == "__main__":
    main()
