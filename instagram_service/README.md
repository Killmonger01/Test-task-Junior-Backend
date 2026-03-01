# Instagram Sync Service

Django + DRF сервис для синхронизации контента из Instagram и управления комментариями через API.

## Стек

- Python 3.11, Django 4.2, Django REST Framework
- PostgreSQL 15
- Docker & Docker Compose

---

## Быстрый старт

### 1. Клонировать репозиторий

```bash
git clone <your-repo-url>
cd instagram_service
```

### 2. Настроить переменные окружения

```bash
cp .env.example .env
```

По умолчанию `.env` уже настроен на работу с **mock-сервером** — никаких дополнительных токенов получать не нужно.

> **Для работы с реальным Instagram API:** замените `INSTAGRAM_ACCESS_TOKEN` на реальный токен из Meta Developer Dashboard, а `INSTAGRAM_GRAPH_API_URL` на `https://graph.instagram.com`.

### 3. Запустить проект

```bash
docker-compose up --build
```

Поднимаются 3 контейнера:

| Контейнер | Порт | Описание |
|-----------|------|----------|
| `web` | `8000` | Django API сервер |
| `db` | `5432` | PostgreSQL |
| `mock_instagram` | `8888` | Mock Instagram Graph API |

Сервис доступен по адресу **http://localhost:8000**.

---

## Mock Instagram API

Проект включает встроенный mock-сервер, который эмулирует Instagram Graph API:

- **15 фейковых постов** с реалистичными данными
- **Пагинация** (по 5 постов на страницу, 3 страницы) — демонстрирует автоматический обход всех страниц
- **Создание комментариев** — с валидацией media_id
- **Ошибки** — корректные error response для несуществующих постов

Переключение между mock и реальным API — одна переменная в `.env`:
```
# Mock:
INSTAGRAM_GRAPH_API_URL=http://mock_instagram:8888

# Real:
INSTAGRAM_GRAPH_API_URL=https://graph.instagram.com
```

---

## API Endpoints

### Синхронизация постов
```bash
curl -X POST http://localhost:8000/api/sync/
```
Выкачивает все посты из Instagram (или mock-сервера), обходит пагинацию, сохраняет в БД с upsert-логикой.

### Список постов
```bash
curl http://localhost:8000/api/posts/
```
Возвращает посты из локальной БД с курсорной пагинацией (CursorPagination).

### Создание комментария
```bash
curl -X POST http://localhost:8000/api/posts/1/comment/ \
  -H "Content-Type: application/json" \
  -d '{"text": "Great post!"}'
```
`{id}` — внутренний PK поста в БД. Отправляет комментарий в Instagram API, при успехе сохраняет локально.

---

## Тестирование

```bash
# Через Docker:
docker-compose exec web python manage.py test instagram_app

# Или локально:
python manage.py test instagram_app
```

Тесты используют `unittest.mock` для мокирования Instagram API — реальные HTTP-запросы не выполняются.

Покрытые сценарии:
- Успешное создание комментария (проверка записи в БД и ответа API)
- Пост не найден в локальной БД → 404
- Пост есть в БД, но удалён из Instagram → 502
- Пустой текст комментария → 400

---

## Архитектура

```
instagram_service/
├── docker-compose.yml
├── Dockerfile
├── .env.example
├── manage.py
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── instagram_app/
│   ├── models.py              # Post, Comment
│   ├── serializers.py         # DRF сериализаторы
│   ├── views.py               # Тонкие views → делегируют в services
│   ├── urls.py                # Маршрутизация API
│   ├── pagination.py          # CursorPagination
│   ├── admin.py               # Django Admin
│   ├── services/
│   │   ├── instagram_client.py  # HTTP-клиент для Instagram Graph API
│   │   └── sync_service.py      # Бизнес-логика (синхронизация, комментарии)
│   └── tests/
│       └── test_comments.py     # Интеграционные тесты
└── mock_instagram/
    └── server.py                # Mock-сервер Instagram Graph API
```

### Разделение ответственности

- **`instagram_client.py`** — транспортный слой: HTTP-запросы, обработка ошибок API, пагинация
- **`sync_service.py`** — бизнес-логика: upsert постов, создание комментариев
- **`views.py`** — тонкий слой: валидация запроса, делегирование в сервисы, формирование ответа
- **`mock_instagram/server.py`** — автономный HTTP-сервер для локальной разработки
