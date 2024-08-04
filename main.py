from website import create_app
from flask import Flask

# app, celery= create_app()
#Used to use this in Render for start command: celery -A main.celery worker -B --loglevel=info
app = create_app()
# celery = app.extensions["celery"]
from celery import Celery, Task
def celery_init_app(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app

celery = celery_init_app(app)

if __name__ == '__main__':
  
    app.run(host='0.0.0.0', debug=False)