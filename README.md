# SA_final

桌遊管理系統，使用 Flask + SQLite 建構。

## 環境需求

- Python 3.8+

## 安裝與執行

### 1. 安裝相依套件

```bash
pip install -r requirements.txt
```

### 2. 啟動伺服器

```bash
python run.py
```

伺服器預設在 `http://localhost:5005` 啟動。

若要指定其他 port：

```bash
python run.py --port 8080
```

首次執行時會自動建立 SQLite 資料庫（`boardgame.db`）並匯入初始資料。

### 3. 預設管理員帳號

| 帳號  | 密碼     |
|-------|----------|
| admin | admin123 |
