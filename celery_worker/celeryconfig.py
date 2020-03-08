import os

redis_host = os.environ.get("REDIS_HOST", 'localhost')
redis_port = os.environ.get("REDIS_PORT", '6379')
redis_password = os.environ.get("REDIS_PASSWORD", '')

broker_url = result_backend = 'redis://:{}@{}:{}/'.format(redis_password, redis_host, redis_port)

imports = ('celery_worker.tasks',)

worker_prefetch_multiplier = 1
task_acks_late = True
