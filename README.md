# Instagram Sync Service

Django + DRF сервис для синхронизации контента из Instagram и управления комментариями.

Проект включает mock-сервер Instagram Graph API, поэтому для запуска и проверки реальный токен не нужен.

## Запуск

```
cd instagram_service
cp .env.example .env
docker-compose up --build
```

После первого запуска нужно создать миграции:

```
docker-compose exec web python manage.py makemigrations instagram_app
docker-compose exec web python manage.py migrate
```

Сервис будет на http://localhost:8000

## API

POST http://localhost:8000/api/sync/ — синхронизация постов из Instagram (mock-сервер отдаёт 15 постов с пагинацией)

GET http://localhost:8000/api/posts/ — список постов из БД (CursorPagination)

POST http://localhost:8000/api/posts/{id}/comment/ — создание комментария. Body (JSON):
```
{"text": "your comment"}
```

## Проверка через Django Admin

Создайте суперпользователя:
```
docker-compose exec web python manage.py createsuperuser
```

Зайдите на http://localhost:8000/admin/ — там видны все посты и комментарии. После sync появятся посты, после отправки комментария — комментарий привязанный к посту.

## Тесты

```
docker-compose exec web python manage.py test instagram_app
```

4 теста: успешное создание комментария, пост не найден в БД (404), пост удалён из Instagram (502), пустой текст (400). Все тесты мокают Instagram API.

## Архитектура

- services/instagram_client.py — HTTP клиент для Instagram Graph API
- services/sync_service.py — бизнес-логика (синхронизация, создание комментариев)
- views.py — тонкие вьюхи, делегируют в сервисы
- mock_instagram/server.py — mock-сервер, эмулирует Instagram Graph API

Переключение на реальный Instagram API — поменять в .env:
```
INSTAGRAM_ACCESS_TOKEN=ваш_токен
INSTAGRAM_GRAPH_API_URL=https://graph.instagram.com
```