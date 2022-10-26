import celery
import os
from pymongo import MongoClient

env = os.environ

mongodb_pass   = os.environ['MONGODB_INITIAL_PRIMARY_ROOT_PASSWORD']
mongoport      = os.environ['MONGODB_INITIAL_PRIMARY_PORT_NUMBER']

def create_worker_from(WorkerClass, celery_config='celery_common.config'):
    """
    Create worker instance given WorkerClass
    :param WorkerClass: WorkerClass to perform task
    :type WorkerClass: subclass of celery.Task
    :param celery_config: celery config module, default 'celery_tasks.celery_config'. This depends on
                            project path
    :type celery_config: str
    :return: celery app instance and worker task instance
    :rtype: tuple of (app, worker_task)
    """
    assert issubclass(WorkerClass, celery.Task)
    app = celery.Celery()
    app.config_from_object(celery_config)
    app.conf.update(task_default_queue=WorkerClass.name)  # update worker queue
    worker_task = app.register_task(WorkerClass())

    return app, worker_task

def connectToMongo():
    mongo_db = MongoClient([f'mongodb-primary:{mongoport}',f'mongodb-secondary:{mongoport}',f'mongodb-arbiter:{mongoport}'],
                                 replicaSet='replicaset',
                                 username='root',
                                 password=mongodb_pass,
                                )
    return mongo_db
