import json
import argparse
from pathlib import Path
from werkzeug.security import generate_password_hash
from app import create_app
from extensions import db

flask_app = create_app()
DATA_DIR = Path(__file__).parent / 'data'


def init_db() -> None:
    accounts_data = json.loads((DATA_DIR / 'accounts.json').read_text(encoding='utf-8'))
    tags_data     = json.loads((DATA_DIR / 'tags.json').read_text(encoding='utf-8'))
    games_data    = json.loads((DATA_DIR / 'games.json').read_text(encoding='utf-8'))

    with flask_app.app_context():
        db.create_all()

        from models.account import Account
        from models.board_game_tag import BoardGameTag
        from models.board_game import BoardGame

        if not Account.query.first():
            a = accounts_data['admin']
            db.session.add(Account(
                userName=a['userName'],
                account=a['account'],
                password=generate_password_hash(a['password'])
            ))

        if not BoardGameTag.query.first():
            for t in tags_data['tags']:
                db.session.add(BoardGameTag(tagId=t['id'], tagName=t['name']))

        db.session.flush()

        if not BoardGame.query.first():
            tags = {t.tagId: t for t in BoardGameTag.query.all()}
            for g in games_data['games']:
                game = BoardGame(
                    boardGameName=g['name'],
                    boardGameAge=g['age'],
                    boardGamePeople=g['people'],
                    boardGameTime=g['time'],
                    boardGameImageUrl=g['img']
                )
                for tid in g['tags']:
                    if tid in tags:
                        game.boardGameTag.append(tags[tid])
                db.session.add(game)

        db.session.commit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=5005, help='監聽 port（預設 5000）')
    args = parser.parse_args()

    init_db()
    flask_app.run(debug=True, port=args.port)
