# Запуск
1. Для запуска приложения создайте файл .env в папке infra по аналогии с infra/.env.example.

2. Запустите базу данных 
```
docker compose -f infra/docker-compose.database.yaml up -d
```

3. Запустите приложение 
```
docker compose -f infra/docker-compose.app.yaml up -d --build
```

Сваггер будет доступен по пути: `http://localhost:8000/docs`