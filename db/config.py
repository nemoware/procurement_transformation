import os

from peewee import *

user = os.environ['DB_USER']
password = os.environ['DB_PASSWORD']
db_name = os.environ['DB_NAME']

db_handle = PostgresqlDatabase(
    db_name, user=user,
    password=password,
    host='localhost'
)
