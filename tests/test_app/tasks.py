from .app import app


@app.task(bind=True)
def debug(self):
    pass
