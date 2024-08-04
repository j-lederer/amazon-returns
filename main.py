from website import create_app

# app, celery= create_app()
#Used to use this in Render for start command: celery -A main.celery worker -B --loglevel=info
app = create_app()

if __name__ == '__main__':
  
    app.run(host='0.0.0.0', debug=False)