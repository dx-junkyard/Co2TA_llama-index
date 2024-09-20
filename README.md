# Dockerイメージのビルド
docker build -t co2_backend .

# コンテナの起動
docker run -d -v $(pwd)/app:/app --name co2_backend --env-file .env -p 8000:8000 co2_backend

curl -X POST "http://localhost:8000/get_form/" -H "Content-Type: application/json" -d '{"text": "太陽光パネルを設置したい"}'
