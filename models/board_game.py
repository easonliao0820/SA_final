import json
from pathlib import Path
from extensions import db
from models.board_game_tag import board_game_tags

GAMES_JSON = Path(__file__).parent.parent / 'data' / 'games.json'


def _sync_games_json() -> None:
    games_data = []
    for g in BoardGame.query.all():
        games_data.append({
            'name':   g.boardGameName,
            'age':    g.boardGameAge    or '',
            'people': g.boardGamePeople or '',
            'time':   g.boardGameTime   or '',
            'img':    g.boardGameImageUrl or '',
            'tags':   [t.tagId for t in g.boardGameTag],
        })
    GAMES_JSON.write_text(
        json.dumps({'games': games_data}, ensure_ascii=False, indent=2),
        encoding='utf-8'
    )


class BoardGame(db.Model):
    __tablename__ = 'board_game'

    boardGameId       = db.Column(db.Integer, primary_key=True)
    boardGameName     = db.Column(db.String(200), nullable=False)
    boardGameAge      = db.Column(db.String(50))
    boardGamePeople   = db.Column(db.String(50))
    boardGameTime     = db.Column(db.String(50))
    boardGameImageUrl = db.Column(db.String(500))
    boardGameTag      = db.relationship(
        'BoardGameTag', secondary=board_game_tags, backref='games'
    )

    @staticmethod
    def getGameDetails(id: int) -> 'BoardGame | None':
        return db.session.get(BoardGame, id)

    @staticmethod
    def addBoardGame(name: str, age: str, people: str,
                     time: str, img: str, tag: list) -> None:
        from models.board_game_tag import BoardGameTag
        game = BoardGame(
            boardGameName=name,
            boardGameAge=age,
            boardGamePeople=people,
            boardGameTime=time,
            boardGameImageUrl=img or None
        )
        for tid in tag:
            t = db.session.get(BoardGameTag, int(tid))
            if t:
                game.boardGameTag.append(t)
        db.session.add(game)
        db.session.commit()
        _sync_games_json()

    @staticmethod
    def updateBoardGame(Id: int, name: str, age: str, people: str,
                        time: str, img: str, tag: list) -> None:
        from models.board_game_tag import BoardGameTag
        game = db.session.get(BoardGame, Id)
        if not game:
            return
        game.boardGameName     = name
        game.boardGameAge      = age
        game.boardGamePeople   = people
        game.boardGameTime     = time
        game.boardGameImageUrl = img or None
        game.boardGameTag      = []
        for tid in tag:
            t = db.session.get(BoardGameTag, int(tid))
            if t:
                game.boardGameTag.append(t)
        db.session.commit()
        _sync_games_json()

    @staticmethod
    def deleteBoardGame(Id: int) -> None:
        game = db.session.get(BoardGame, Id)
        if game:
            db.session.delete(game)
            db.session.commit()
            _sync_games_json()
