from simoc_server import redis_url

result_backend = redis_url
broker_url = redis_url

imports = ('celery_worker.tasks',)

worker_prefetch_multiplier = 1
task_acks_late = True
