import argparse
from pathlib import Path

from loguru import logger
from sqlalchemy import text

from src.py.connection import conn

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize the database.")
    parser.add_argument("--reset", action="store_true", help="Recreate the tables.")
    args = parser.parse_args()

    try:
        if not conn.dialect.has_schema(conn, "orti_scolastici") or args.reset:
            create_schema_filepath = (
                Path(__file__).parent.parent / "sql" / "create_schema.sql"
            )
            with Path.open(create_schema_filepath, "r") as f:
                query = f.read()
            conn.execute(text(query))
            conn.commit()
            logger.info("Schema created.")
        else:
            logger.info("Schema already exists.")
    except Exception as e:  # noqa: BLE001
        logger.exception(e)
        conn.rollback()
    finally:
        conn.close()
