from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from typing import Optional

engine: Optional[Engine] = None

def initialize_db() -> None:
	global engine
	# '<DB TYPE>:///<DATABASE NAME>'
	engine = create_engine('sqlite:///fastapi-test.sqlite3', echo=True, future=True)
	if engine:
		from .models import create_tables
		create_tables(engine)

def close_db() -> None:
	if engine:
		engine.dispose()