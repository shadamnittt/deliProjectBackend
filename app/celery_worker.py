from celery import Celery

# Настройки Celery (используем Redis как брокер)
celery_app = Celery(
    'film_parser',  # Имя задачи
    broker='redis://localhost:6379/0',  # Адрес брокера Redis
    backend='redis://localhost:6379/0',  # Для хранения результатов
)

# Можно добавлять дополнительные настройки, если нужно
celery_app.conf.update(
    task_routes = {
        'tasks.parse_films_task': {'queue': 'film_queue'},
    },
)
