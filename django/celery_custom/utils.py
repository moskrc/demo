import time
import logging
from celery.signals import task_failure
from django.conf import settings
from django.db import connection
from webapp.models import NetworkInstall, NIS_INSTALLING, NIS_FAILED, NIS_SUCCESS
from celery import task, current_task, chain
from django.utils import timezone
from logs.models import CeleryLog, CeleryKpiLog


def emulate_task(network, logger, **kwargs):
    logger.info('emulate task')
    time.sleep(1)
    return {'data': 'local'}

class DbLogHandler(logging.Handler):
    def __init__(self, task_id):
        self.task_id = task_id
        logging.Handler.__init__(self)

    def emit(self, record):
        try:
            network_install = NetworkInstall.objects.filter(task_id=self.task_id).first()
            CeleryLog.objects.create(task=network_install, level=record.levelname, message=record.message, created=timezone.now())
        except:
            pass
        return


class CustomCeleryLogger(object):
    def __init__(self, task_id):
        self.logger = logging.getLogger()
        handler_db = DbLogHandler(task_id)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler_file = logging.FileHandler('/tmp/%s.log' % task_id)

        handler_db.setFormatter(formatter)
        handler_file.setFormatter(formatter)
        self.logger.addHandler(handler_db)
        self.logger.addHandler(handler_file)


        def process_failure_signal(exception, traceback, sender, task_id, signal, args, kwargs, einfo, **kw):
            exc_info = (type(exception), exception, traceback)
            self.logger.error(
                'Celery job exception: %s(%s)' % (exception.__class__.__name__, exception),
                exc_info=exc_info,
                extra={
                    'data': {
                        'task_id': task_id,
                        'sender': sender,
                        'args': args,
                        'kwargs': kwargs,
                    }
                }
            )

        task_failure.connect(process_failure_signal)

    def get_logger(self):
        return self.logger


class TaskStep(object):
    def __init__(self, name, action, manager):
        self.name = name
        self.action = action
        self.manager = manager

    def get_name(self):
        return self.name

    def run(self, *args, **kwargs):
        return self.action(*args, **kwargs)

    def __unicode__(self):
        return u'%s' % self.get_name()


class TaskStepManager(object):
    def __init__(self, task, **kwargs):
        self.logger = CustomCeleryLogger(task.request.id).get_logger()
        self.task = task
        self.steps = []
        self.extra = kwargs.get('extra', {})

    def add_step(self, name, module):
        if getattr(settings, "LOCAL_VERSION", False):
            self.steps.append(TaskStep(name, emulate_task, self))
        else:
            self.steps.append(TaskStep(name, module.action, self))

    def add_steps(self, steps):
        for step in steps:
            self.add_step(*step)

    def start(self, network, user):
        network_install, created = NetworkInstall.objects.get_or_create(network=network)
        network_install.status = NIS_INSTALLING
        network_install.author = user.username
        network_install.task_id = self.task.request.id
        network_install.save()

        if 'steps' not in network_install.data:
            network_install.data['steps'] = {}

        for i in range(0, len(self.steps)):
            try:
                self.logger.info('Running step #%s (%s)... ' % (i, self.steps[i].get_name()))

                # Close MySQL connection while running
                connection.close()

                process_percent = int(100 * float(i + 1) / float(len(self.steps)))

                start_time = int(time.time())

                current_task.update_state(state='PROGRESS',
                                          meta={'process_percent': process_percent,
                                                'state': self.steps[i].get_name(),
                                                'step': i,
                                                'steps': len(self.steps),
                                                'created': start_time,
                                                'data': network_install.data})

                if 's%s' % i not in network_install.data['steps'] or 'success' not in network_install.data['steps'][
                            's%s' % i]:
                    network_install.data['steps']['s%s' % i] = {}

                    # process the step and save the result to DB
                    res = self.steps[i].run(network, self.logger, **self.extra)

                    network_install.data['steps']['s%s' % i]['success'] = res
                    self.logger.info('Done')

            except Exception as e:
                network_install.data['steps']['s%s' % i]['error'] = str(e)
                network_install.status = NIS_FAILED
                # send_notification_email(network, False)
                print e
                raise e

            finally:
                elapsed_time = int(time.time()) - start_time
                network_install.data['steps']['s%s' % i]['elapsed_time'] = elapsed_time
                network_install.save()

                result = 'OK' if 'success' in network_install.data['steps']['s%s' % i] else 'FAILED'

                CeleryKpiLog.objects.create(task=network_install, step_num=i, result=result,
                                            elapsed=time.strftime('%H:%M:%S', time.gmtime(elapsed_time)))

        network_install.status = NIS_SUCCESS
        network_install.save()

        return True
