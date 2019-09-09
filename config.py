import os
import cx_Oracle
from jumpssh import SSHSession
import configparser

class Development(object):
    """
    Development environment configuration
    """
    DEBUG = True
    TESTING = False
    JWT_SECRET_KEY = os.getenv('shadman')
    #SQLALCHEMY_DATABASE_URI = "jdbc:postgresql://192.168.4.176:5432/postgres"

class Production(object):
    """
    Production environment configurations
    """
    DEBUG = False
    TESTING = False
    # SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    #SQLALCHEMY_DATABASE_URI = "jdbc:postgresql://192.168.4.176:5432/postgres"
    JWT_SECRET_KEY = os.getenv('shadman')


config = configparser.ConfigParser()
config.read('dbconnect.ini')

def connect():
    dsn_tns = cx_Oracle.makedsn(host=config['oracleDB']['ip'], port=config['oracleDB']['port'], sid=config['oracleDB']['SID'])
    con = cx_Oracle.connect(user=config['oracleDB']['username'],password=config['oracleDB']['password'],dsn=dsn_tns)
    return con




app_config = {
    'development': Development,
    'production': Production,
}