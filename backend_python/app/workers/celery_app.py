from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "automacao_gp_workers",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Sao_Paulo",
    enable_utc=True,
    beat_schedule={
        # Periodical lead discovery task
        "periodic-lead-search-every-6-hours": {
            "task": "app.workers.tasks.scheduled_lead_search",
            "schedule": 21600.0,  # every 6 hours
            "args": ("Clínica Odontológica", "São Paulo, SP"),
        },
    },
)
