# /run.py
import os

from config import app_config
from app import create_app

if __name__ == '__main__':
  # env_name = os.getenv('FLASK_ENV')
  env_name = 'development'
  app = create_app(env_name)
  # run app
  app.run(host='0.0.0.0',port = 5600)

