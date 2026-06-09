from flask import Blueprint, render_template, request
from models.board_game_tag import BoardGameTag
from services.search import Search

public_bp = Blueprint('public', __name__)


@public_bp.route('/')
def index():
    tags   = BoardGameTag.getAllTag()
    name   = request.args.get('name', '').strip()
    tag_id = request.args.get('tag_id', type=int)
    games  = Search.searchBoardGames(tag_id, name)
    return render_template('index.html', games=games, tags=tags,
                           name=name, tag_id=tag_id)
