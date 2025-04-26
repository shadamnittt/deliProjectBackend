from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.auth.auth import router as auth_router
from app.tasks import parse_films_task # Импортируем задачу Celery
from app.api.auth.auth import router as admin_router 
from app.celery_worker import celery_app  

app = FastAPI()

origins = [
    "http://localhost:5173",  # порт, на котором работает твой фронтенд
]

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Открыть доступ с любых источников (для тестирования, потом можешь ограничить)
    allow_credentials=True,  # Позволяет отправлять cookies и заголовки
    allow_methods=["*"],  # Разрешаем все методы (GET, POST и т.д.)
    allow_headers=["*"],  # Разрешаем все заголовки
)

# Подключаем роутер с префиксом /auth
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(admin_router, prefix="/admin", tags=["Admin"])

@app.post("/start-parsing")
async def start_parsing():
    # Запускаем задачу на парсинг в фоновом режиме
    parse_films_task.delay()  # Celery выполняет задачу
    return {"message": "Парсинг начат!"}

