import os
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from functools import wraps
from werkzeug.utils import secure_filename

from models.account import Account
from models.board_game import BoardGame
from models.board_game_tag import BoardGameTag
from services.search import Search
from services.check import Check


def _save_image(file) -> str:
    """上傳圖片存入 static/image/，回傳相對路徑（image/filename）"""
    filename = secure_filename(f"{uuid.uuid4().hex}_{file.filename}")
    file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
    return f'image/{filename}'

admin_bp = Blueprint('admin', __name__)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('請先登入管理後台', 'warning')
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated


# ── 登入 / 登出 ───────────────────────────────────────────────────────────────

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':
        acc = request.form.get('account', '').strip()
        pwd = request.form.get('password', '')

        # Check 負責驗證帳密
        result = Check.checkAccount(acc, pwd)
        if result == 'ok':
            Account.login(acc, pwd)
            user = Account.query.filter_by(account=acc).first()
            flash(f'歡迎回來，{user.getUserName()}！', 'success')
            return redirect(url_for('admin.dashboard'))

        flash(result, 'danger')

    return render_template('login.html')


@admin_bp.route('/logout')
def logout():
    try:
        Check.checkLogout()   # 確認有 session 才執行登出
    except ValueError as e:
        flash(str(e), 'warning')
        return redirect(url_for('public.index'))
    Account.logout()
    flash('已成功登出系統', 'info')
    return redirect(url_for('public.index'))


# ── 管理後台 ──────────────────────────────────────────────────────────────────

@admin_bp.route('/admin')
@login_required
def dashboard():
    if not Check.checkConnectDb():
        flash('資料庫連線失敗，請稍後再試', 'danger')
        return render_template('admin/dashboard.html', games=[], tags=[],
                               name='', tag_id=None)

    tags   = BoardGameTag.getAllTag()
    name   = request.args.get('name', '').strip()
    tag_id = request.args.get('tag_id', type=int)

    # Check 驗證搜尋參數
    check_result = Check.checkSearch(tag_id, name)
    if check_result != 'ok':
        flash(check_result, 'danger')
        name, tag_id = '', None

    games = Search.searchBoardGames(tag_id, name)
    return render_template('admin/dashboard.html', games=games, tags=tags,
                           name=name, tag_id=tag_id)


# ── 新增桌遊（三段驗證對應序列圖）────────────────────────────────────────────

@admin_bp.route('/admin/games/add', methods=['GET', 'POST'])
@login_required
def add_game():
    tags = BoardGameTag.getAllTag()

    if request.method == 'POST':
        name     = request.form.get('name', '').strip()
        age      = request.form.get('age', '').strip()
        people   = request.form.get('people', '').strip()
        time     = request.form.get('time', '').strip()
        tag      = request.form.getlist('tags')
        img_file = request.files.get('img')
        img_name = img_file.filename if img_file else ''

        # 第一關：checkAddButton — 表面必填檢查
        result = Check.checkAddButton(name, age, people, time, img_name, tag)
        if result != 'ok':
            flash(result, 'danger')
            return render_template('admin/add_game.html', tags=tags)

        # 第二關：checkAddInput — 格式驗證
        result = Check.checkAddInput(name, age, people, time, img_name, tag)
        if result != 'ok':
            flash(result, 'danger')
            return render_template('admin/add_game.html', tags=tags)

        # 第三關：checkAddDB — 資料庫重複確認
        result = Check.checkAddDB(name, age, people, time, img_name, tag)
        if result != 'ok':
            flash(result, 'warning')
            return render_template('admin/add_game.html', tags=tags)

        # 全部通過 → 儲存圖片 → BoardGame 執行新增
        img_path = _save_image(img_file) if img_file and img_file.filename else ''
        BoardGame.addBoardGame(name=name, age=age, people=people,
                               time=time, img=img_path, tag=tag)
        flash(f'「{name}」已成功新增！', 'success')
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/add_game.html', tags=tags)


# ── 編輯桌遊 ──────────────────────────────────────────────────────────────────

@admin_bp.route('/admin/games/<int:game_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_game(game_id):
    game = BoardGame.getGameDetails(game_id)
    if not game:
        flash('找不到該桌遊', 'danger')
        return redirect(url_for('admin.dashboard'))

    tags = BoardGameTag.getAllTag()

    if request.method == 'POST':
        name     = request.form.get('name', '').strip()
        age      = request.form.get('age', '').strip()
        people   = request.form.get('people', '').strip()
        time     = request.form.get('time', '').strip()
        tag      = request.form.getlist('tags')
        img_file = request.files.get('img')
        img_name = img_file.filename if img_file and img_file.filename else ''

        # checkupdate — 一次涵蓋存在性、格式、重複名稱
        result = Check.checkupdate(game_id, name, age, people, time, img_name, tag)
        if result != 'ok':
            flash(result, 'danger')
            return render_template('admin/edit_game.html', game=game, tags=tags)

        # 有上傳新圖片才取代，否則保留原路徑
        if img_file and img_file.filename:
            img_path = _save_image(img_file)
        else:
            img_path = game.boardGameImageUrl or ''

        BoardGame.updateBoardGame(Id=game_id, name=name, age=age, people=people,
                                  time=time, img=img_path, tag=tag)
        flash(f'「{name}」已成功更新！', 'success')
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/edit_game.html', game=game, tags=tags)


# ── 刪除桌遊 ──────────────────────────────────────────────────────────────────

@admin_bp.route('/admin/games/<int:game_id>/delete', methods=['POST'])
@login_required
def delete_game(game_id):
    # checkDelete — 確認桌遊存在才執行刪除
    result = Check.checkDelete(game_id)
    if result != 'ok':
        flash(result, 'danger')
        return redirect(url_for('admin.dashboard'))

    game = BoardGame.getGameDetails(game_id)
    name = game.boardGameName
    BoardGame.deleteBoardGame(game_id)
    flash(f'「{name}」已成功刪除！', 'success')
    return redirect(url_for('admin.dashboard'))
