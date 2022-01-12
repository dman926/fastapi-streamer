# import the FastAPI object
from fastapi import FastAPI

# define the FastAPI app with the debug flag so we get more output in case something goes wrong
app = FastAPI(debug=True)

@app.on_event('startup')
async def startup():
	print('-- STARTING UP --')
	from database.db import initialize_db
	initialize_db()
	from resources.routes import initialize_routes
	initialize_routes(app)
	print('-- STARTED UP --')

@app.on_event('shutdown')
async def shutdown():
	print('-- SHUTTING DOWN --')
	from database.db import close_db
	close_db()
	print('-- SHUT DOWN --')

# if this file is run directly
if __name__== '__main__':
	import uvicorn
	# start up uvicorn with the reload flag so it restarts whenever we change a file (turn off in production)
	uvicorn.run('main:app', reload=True)