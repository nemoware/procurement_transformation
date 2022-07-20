import os

from peewee import *

from api.common import env_var

user = env_var('DB_USER', 'postgres')
password = env_var('DB_PASSWORD')
db_name = env_var('DB_NAME', 'procurement_transformation')
host = env_var('DB_HOST', 'localhost')
port = env_var('DB_port', 5432)

db_handle = PostgresqlDatabase(
    db_name,
    user=user,
    password=password,
    host=host,
    port=port
)
