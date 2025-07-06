# Learning Management System (LMS) with Django, Celery and Stripe

## Установка и запуск с Poetry

### Предварительные требования
- Docker и Docker Compose
- Python 3.9+
- Poetry

### 1. Настройка окружения

Скопируйте файл окружения и заполните значения:
```bash
cp .env.example .env
```
nano .env  # или откройте в любом редакторе

#### Обязательные переменные для заполнения:

SECRET_KEY - сгенерируйте новый ключ Django

POSTGRES_* - данные для подключения к PostgreSQL

STRIPE_API_KEY - тестовый ключ из Stripe Dashboard

STRIPE_PUBLIC_KEY - публичный ключ Stripe

### 2. Запуск сервисов
Соберите и запустите контейнеры в фоновом режиме:
```bash
docker-compose up -d --build
```
### 3. Проверка работы сервисов
Бэкенд:
```bash
http://localhost:8000/admin
```
Redis:
```bash
docker exec -it lms_redis redis-cli ping
```
### 4. Первоначальная настройка
Создайте миграции и суперпользователя:
```bash
docker-compose exec backend poetry run python manage.py migrate
docker-compose exec backend poetry run python manage.py createsuperuser
```

#### Управление зависимостями
Добавить новую зависимость:
```bash
poetry add package-name
```
Обновить lock-файл (без обновления версий):
```bash
poetry lock --no-update
```
#### Работа с платежами (Stripe)
##### Тестовые карты
Используйте следующие тестовые данные для оплаты:

Успешный платеж: 4242 4242 4242 4242

Отклоненный платеж: 4000 0000 0000 0002

##### Проверка платежей
Просмотр статуса платежа:
```bash
curl http://localhost:8000/api/payments/status/1/
```
#### Администрирование
##### Полезные команды
Пересоздать миграции:
```bash
docker-compose exec backend poetry run python manage.py makemigrations
```
Создать суперпользователя:
```bash
docker-compose exec backend poetry run python manage.py createsuperuser
```
Запустить тесты:
```bash
docker-compose exec backend poetry run pytest
```
Остановка сервисов
```bash
docker-compose down -v
```