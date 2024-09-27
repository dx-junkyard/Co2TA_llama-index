# Dockerイメージのビルド
docker build -t co2_backend .

# コンテナの起動
docker run -d \
    --rm \
    -v $(pwd)/app:/app \
    --name co2_backend \
    --env-file .env \
    -p 8000:8000 \
    co2_backend \
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# APIテスト
curl -X POST "http://localhost:8000/get_form/" -H "Content-Type: application/json" -d '{"text": "太陽光パネルを設置したい"}'
