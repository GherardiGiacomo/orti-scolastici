import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker

from src.py.utils import get_db_url, parse_db_url

DB_URL = get_db_url()


engine = create_engine(DB_URL)

try:
    conn = engine.connect()
except OperationalError:
    host, port, user, password, database = parse_db_url(DB_URL)
    conn = psycopg2.connect(host=host, port=port, user=user, password=password)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(f"CREATE DATABASE {database}")
    cur.execute(f"GRANT ALL PRIVILEGES ON DATABASE {database} TO {user}")
    cur.close()  # type: ignore  # noqa: PGH003
    conn.close()
    conn = engine.connect()

DBSession = sessionmaker(bind=engine)
session = DBSession()
