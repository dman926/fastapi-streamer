from mongoengine import connect, disconnect

def initialize_db() -> None:
	# host='mongodb://localhost/<DATABASE NAME>'
	connect(host='mongodb://localhost/fastapi-test')

def close_db() -> None:
	disconnect()