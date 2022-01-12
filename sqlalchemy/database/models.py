from re import M
from .db import engine
from sqlalchemy import Table, Column, Integer, String, MetaData
from sqlalchemy.engine.base import Engine

meta = MetaData()

media = Table(
	'media', meta,
	Column('folder', String, primary_key = True),
	Column('filename', String, primary_key = True),
	Column('mimetype', String),
	Column('length', Integer)
)

def create_tables(engine: Engine):
	meta.create_all(engine)