from celery import Celery


celery = Celery('tasks', broker='redis://localhost:6379')

celery.conf.beat_schedule = {
    'update_lot_status_task1': {
        'task': 'src.auction.tasks.update_lot_status_task',
        'schedule': 60.0,
    },
}

import src.user.tasks  # noqa: F401, E402
import src.auction.tasks  # noqa: F401, E402
