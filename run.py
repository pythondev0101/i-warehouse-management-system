import os
from app import create_app,db
from dotenv import load_dotenv


load_dotenv()
config_name = os.getenv('FLASK_ENV')
app = create_app(config_name)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)