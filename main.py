from fastapi import FastAPI

app = FastAPI(debug=True)

@app.get('/')
async def test():
	return 'hello world'

if __name__== '__main__':
	import uvicorn
	uvicorn.run('main:app', reload=True)