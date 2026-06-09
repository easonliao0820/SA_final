from flask import session
from werkzeug.security import check_password_hash
from extensions import db


class Account(db.Model):
    __tablename__ = 'account'

    userId   = db.Column(db.Integer, primary_key=True)
    userName = db.Column(db.String(100), nullable=False)
    account  = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    token    = db.Column(db.String(200))

    # ── 查詢 ──────────────────────────────────────────────────────────────────

    def getUserName(self) -> str:
        return self.userName

    def checkLogin(self) -> bool:
        return session.get('user_id') == self.userId

    # ── 認證 ──────────────────────────────────────────────────────────────────

    @staticmethod
    def login(account: str, password: str) -> None:
        user = Account.query.filter_by(account=account).first()
        if user and check_password_hash(user.password, password):
            session['user_id']   = user.userId
            session['user_name'] = user.userName

    @staticmethod
    def logout() -> None:
        session.clear()

