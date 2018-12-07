
from app import app

app.config.from_object('config.DevelopmentConfig')

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000)


