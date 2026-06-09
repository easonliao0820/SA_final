from flask import Blueprint, render_template, request, flash
from models.board_game_tag import BoardGameTag
from services.search import Search
from services.check import Check

public_bp = Blueprint('public', __name__)


@public_bp.route('/')
def index():
    db_status = Check.checkDB()
    if db_status == '資料庫連線失敗':
        flash(db_status, 'danger')
        return render_template('index.html', games=[], tags=[],
                               name='', tag_id=None)

    tags   = BoardGameTag.getAllTag()
    name   = request.args.get('name', '').strip()
    tag_id = request.args.get('tag_id', type=int)
    games  = Search.searchBoardGames(tag_id, name)
    return render_template('index.html', games=games, tags=tags,
                           name=name, tag_id=tag_id)
