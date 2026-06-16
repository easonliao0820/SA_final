from models.board_game import BoardGame
from models.board_game_tag import BoardGameTag


class Search:

    @staticmethod
    def searchBoardGames(tagId: int, name: str) -> list[BoardGame]:
        query = BoardGame.query
        if name:
            query = query.filter(BoardGame.boardGameName.contains(name))
        if tagId:
            query = query.filter(
                BoardGame.boardGameTag.any(BoardGameTag.tagId == tagId)
            )
        return query.all()

    @staticmethod
    def getAllGames() -> list[BoardGame]:
        return BoardGame.query.all()
