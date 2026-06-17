from werkzeug.security import check_password_hash

_ALLOWED_IMG_EXT = {'jpg', 'jpeg', 'png', 'gif', 'webp'}


def _valid_img(filename: str) -> bool:
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    return ext in _ALLOWED_IMG_EXT


class Check:
    item: str = None  # 最近驗證的帳號屬性（對應 UML item: attribute）

    # ── 登入 / 登出 ───────────────────────────────────────────────────────────

    @staticmethod
    def checkAccount(account: str, password: str) -> str:
        """驗證帳號密碼，正確回傳 'ok'，錯誤回傳錯誤訊息"""
        from models.account import Account
        user = Account.query.filter_by(account=account).first()
        if user and check_password_hash(user.password, password):
            Check.item = account
            return 'ok'
        return '帳號或密碼錯誤'

    # ── 新增桌遊兩段驗證（對應序列圖）────────────────────────────────────────
    @staticmethod
    def checkAddInput(name: str, age: str, people: str,
                      time: str, img: str, tag: list) -> str:
        """第一關：確認送出後的完整格式驗證"""
        if not name or not name.strip():
            return '桌遊名稱為必填欄位'
        if img and not _valid_img(img):
            return '僅支援 jpg、jpeg、png、gif、webp 格式'
        if age and len(age) > 50:
            return '適合年齡欄位過長'
        if people and len(people) > 50:
            return '遊戲人數欄位過長'
        if time and len(time) > 50:
            return '遊戲時長欄位過長'
        if tag and not isinstance(tag, list):
            return '分類格式錯誤'
        if len(name.strip()) > 200:
            return '桌遊名稱不可超過 200 字'
        if age and not any(c.isdigit() for c in age):
            return '適合年齡須包含數字，例如：10+'
        if people and len(people) > 50:
            return '遊戲人數格式有誤'
        if time and len(time) > 50:
            return '遊戲時長格式有誤'
        if img and not _valid_img(img):
            return '僅支援 jpg、jpeg、png、gif、webp 格式'
        if tag and len(tag) > 2:
            return '分類數量過多，最多 2 個'
        return 'ok'

    @staticmethod
    def checkAddDB(name: str, age: str, people: str,
                      time: str, img: str, tag: list) -> str:
        """第二關：確認資料庫中無完全相同的桌遊（名稱 + 人數組合）"""
        from models.board_game import BoardGame
        existing = BoardGame.query.filter_by(boardGameName=name.strip()).first()
        if existing:
            detail = f'（人數：{existing.boardGamePeople}）' if existing.boardGamePeople else ''
            return f'已存在名稱為「{name}」的桌遊{detail}'
        return 'ok'

    # ── 刪除 / 搜尋 / 更新驗證 ───────────────────────────────────────────────

    @staticmethod
    def checkDelete(id: int) -> str:
        """確認要刪除的桌遊存在"""
        from models.board_game import BoardGame
        game = BoardGame.getGameDetails(id)
        if not game:
            return f'找不到 ID 為 {id} 的桌遊'
        return 'ok'

    @staticmethod
    def checkSearch(tagId: int, name: str) -> str:
        """驗證搜尋參數合法性"""
        if tagId is not None and tagId < 0:
            return '分類 ID 不合法'
        if name and len(name) > 200:
            return '搜尋名稱過長'
        return 'ok'

    @staticmethod
    def checkupdate(Id: int, name: str, age: str, people: str,
                    time: str, img: str, tag: list) -> str:
        """驗證更新資料：桌遊存在、欄位格式正確、無同名衝突"""
        from models.board_game import BoardGame
        game = BoardGame.getGameDetails(Id)
        if not game:
            return f'找不到 ID 為 {Id} 的桌遊'
        if not name or not name.strip():
            return '桌遊名稱為必填欄位'
        if len(name.strip()) > 200:
            return '桌遊名稱不可超過 200 字'
        if age and len(age) > 50:
            return '適合年齡欄位過長'
        if people and len(people) > 50:
            return '遊戲人數欄位過長'
        if time and len(time) > 50:
            return '遊戲時長欄位過長'
        if img and not _valid_img(img):
            return '僅支援 jpg、jpeg、png、gif、webp 格式'
        if tag and len(tag) > 10:
            return '分類數量過多，最多 10 個'
        duplicate = BoardGame.query.filter(
            BoardGame.boardGameName == name.strip(),
            BoardGame.boardGameId != Id
        ).first()
        if duplicate:
            return f'已存在名稱為「{name}」的桌遊'
        return 'ok'

    # ── 資料庫連線 ────────────────────────────────────────────────────────────

    @staticmethod
    def checkConnectDb() -> bool:
        """測試資料庫連線是否正常"""
        try:
            from extensions import db
            db.session.execute(db.text('SELECT 1'))
            return True
        except Exception:
            return False

    @staticmethod
    def checkDB() -> str:
        """回傳資料庫狀態摘要"""
        if not Check.checkConnectDb():
            return '資料庫連線失敗'
        from models.board_game import BoardGame
        count = BoardGame.query.count()
        return f'資料庫連線正常，共 {count} 筆桌遊資料'
