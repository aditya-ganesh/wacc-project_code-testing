import celery
import logging

logging.basicConfig(level=logging.INFO)

class testCallerTask(celery.Task):
    name = 'test_caller_task'

    def run(self, payload):
        """
        place holder method
        """
        pass



class testRunnerTask(celery.Task):
    name = 'test_runner_task'

    def run(self, payload):
        """
        place holder method
        """
        pass


class databaseHandlerTask(celery.Task):
    name = 'db_handler_task'

    def run(self, payload):
        """
        place holder method
        """
        pass

