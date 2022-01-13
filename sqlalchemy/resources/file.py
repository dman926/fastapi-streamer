from fastapi import APIRouter, Header, HTTPException, UploadFile, Form, File
from starlette.responses import StreamingResponse
import os
from io import BufferedReader
import mimetypes
from database.db import engine
from database.models import media
from sqlalchemy.orm.exc import NoResultFound

router = APIRouter(
	prefix='/file',
	tags=['File']
)

def is_safe_path(basedir, path) -> bool:
	return basedir == os.path.commonpath((basedir, os.path.abspath(path)))

@router.post('/upload')
async def upload_file(file: UploadFile = File(...), folder: str = Form('')):
	try:
		if not is_safe_path(os.getcwd(), folder) or file.filename == '' or (len(folder) > 0 and folder[0] == '/'): # Enforce required filename and that folders can't start with `/`
			raise HTTPException
		filesPath = os.path.join(os.getcwd(), 'files')
		outputFolderPath = os.path.join(filesPath, *folder.split('/'))
		outputPath = os.path.join(outputFolderPath, file.filename)
		if os.path.exists(outputPath):
			raise HTTPException
		os.makedirs(outputFolderPath)
		with open(outputPath, 'wb+') as f:
			length = f.write(file.file.read())
		mimetype = file.content_type
		if not mimetype:
			mimetype = mimetypes.guess_type(file.filename)[0]
		with engine.connect() as conn:
			ins = media.insert().values(folder=folder, filename=file.filename, mimetype=mimetype, length=length)
			conn.execute(ins.compile())
			conn.commit()
		return 'ok'			
	except HTTPException:
		raise HTTPException(status_code=400, detail='Validation Error')
	except Exception as e:
		raise e

@router.get('/stream')
def stream(filename: str, folder: str = '', range: str = Header('bytes=0-')):
	CONTENT_CHUNK_SIZE = 1024 * 14 # feel free to play around with this number to maximize efficiency
	try:
		def get_stream_and_size_and_mimetype(filename: str, folder: str):
			path = os.path.join(os.getcwd(), 'files', folder, filename)
			f = open(path, 'rb')
			with engine.connect() as conn:
				stmt = media.select().where(media.c.folder==folder, media.c.filename==filename)
				mediaObj = conn.execute(stmt.compile()).one()
				length = mediaObj.length
				mimetype = mediaObj.mimetype
			return f, length, mimetype
		def iterfile(file_stream: BufferedReader, chunk_size: int, start: int, size: int):
			bytes_read = 0
			file_stream.seek(start)
			while bytes_read < size:
				bytes_to_read = min(chunk_size, size - bytes_read)
				yield file_stream.read(bytes_to_read)
				bytes_read += bytes_to_read
			file_stream.close()
		if not is_safe_path(os.getcwd(), folder):
			raise OSError
		start_byte = int(range.split('=')[-1].split('-')[0])
		chunk_size = CONTENT_CHUNK_SIZE
		file_stream, size, mimetype = get_stream_and_size_and_mimetype(filename, folder)
		if start_byte + chunk_size > size:
			chunk_size = size - 1 - start_byte
		if not mimetype:
			mimetype = mimetypes.guess_type(filename)[0]
		return StreamingResponse(
			content=iterfile(
				file_stream,
				chunk_size,
				start_byte,
				size
			),
			status_code=206,
			headers={
				'Accept-Ranges': 'bytes',
				'Content-Range': f'bytes {start_byte}-{start_byte+chunk_size}/{size - 1}',
				'Content-Type': mimetype,
				'Content-Disposition': f'inline; filename={filename}'
			},
			media_type=mimetype
		)
	except (OSError, NoResultFound):
		raise HTTPException(status_code=404, detail='file not found')
	except Exception as e:
		raise e