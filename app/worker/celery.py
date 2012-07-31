from __future__ import absolute_import
from celery import celery

celery = Celery(broker='amqp://guest@localhost',
				include=['mixr.tasks'],
				backend='amqp://guest@localhost')