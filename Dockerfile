# ベースイメージ
FROM python:3.9

# 作業ディレクトリの設定
WORKDIR /app

# 必要なファイルをコピー
COPY ./app /app

# パッケージのインストール
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ポートの解放
EXPOSE 8000

# 環境変数の設定（APIキーは.envファイルから読み込む）
ENV PYTHONUNBUFFERED=1

# エントリポイント
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]