from extensions import db

# 多對多關聯表
board_game_tags = db.Table(
    'board_game_tags',
    db.Column('board_game_id', db.Integer, db.ForeignKey('board_game.boardGameId')),
    db.Column('tag_id',        db.Integer, db.ForeignKey('board_game_tag.tagId'))
)


class BoardGameTag(db.Model):
    __tablename__ = 'board_game_tag'

    tagId   = db.Column(db.Integer, primary_key=True)
    tagName = db.Column(db.String(100), nullable=False)

    @staticmethod
    def getAllTag() -> list['BoardGameTag']:
        return BoardGameTag.query.all()

    @staticmethod
    def getTagName(id: int) -> str | None:
        tag = db.session.get(BoardGameTag, id)
        return tag.tagName if tag else None
