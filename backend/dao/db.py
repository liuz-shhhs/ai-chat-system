import pymysql
from config.settings import MYSQL_CONFIG

def get_conn():
    return pymysql.connect(**MYSQL_CONFIG)