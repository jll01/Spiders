from celery import Celery

app = Celery('celery_template', include=['celery_template.tasks'])
app.config_from_object('celery_template.config')


if __name__ == '__main__':
    app.start()
