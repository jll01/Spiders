from celery import Celery

app = Celery('zongheng_celery', include=['zongheng_celery.tasks'])
app.config_from_object('zongheng_celery.config')


if __name__ == '__main__':
    app.start()
