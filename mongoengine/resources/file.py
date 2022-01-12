from fastapi import APIRouter, Header, HTTPException, UploadFile, Form, File
from starlette.responses import StreamingResponse
from io import BufferedReader
import mimetypes
from mongoengine.errors import DoesNotExist, NotUniqueError
from database.models import Media

router = APIRouter(
	prefix='/file',
	tags=['File']
)

@router.post('/upload')
async def upload_file(file: UploadFile = File(...), folder: str = Form('')):
	try:
		if file.filename == '' or (len(folder) > 0 and folder[0] =='/'): # Enforce required filename and that folders can't start with `/``
			raise HTTPException
		mimetype = file.content_type
		if not mimetype:
			mimetype = mimetypes.guess_type(file.filename)[0]
		media = Media(folder=folder, filename=file.filename)
		media.file.put(file.file, content_type=mimetype)
		media.save()
		return str(media.id)
	except HTTPException:
		raise HTTPException(status_code=400, detail='Validation Error')
	except NotUniqueError:
		raise HTTPException(status_code=400, detail='Not Unique')
	except Exception as e:
		raise e

@router.get('/stream')
def stream(filename: str, folder: str = '', range: str = Header('bytes=0')):
	CONTENT_CHUNK_SIZE = 1024 * 14 # feel free to play around with this number to maximize efficiency
	try:
		def get_stream_and_size_and_mimetype(filename: str, folder: str):
			f = Media.objects.get(filename=filename, folder=folder)
			return f.file, f.file.length, f.file.content_type
		def iterfile(file_stream: BufferedReader, chunk_size: int, start: int, size: int):
			bytes_read = 0
			file_stream.seek(start)
			while bytes_read < size:
				bytes_to_read = min(chunk_size, size - bytes_read)
				yield file_stream.read(bytes_to_read)
				bytes_read += bytes_to_read
			file_stream.close()
		start_byte = int(range.split('=')[-1].split('-')[0])
		chunk_size = CONTENT_CHUNK_SIZE
		file_stream, size, mimetype = get_stream_and_size_and_mimetype(filename, folder)
		if not mimetype:
			mimetype = mimetypes.guess_type(filename)[0]
		if start_byte + chunk_size > size:
			chunk_size = size - 1 - start_byte
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
	except (DoesNotExist, OSError):
		raise HTTPException(status_code=404, detail='file not found')
	except Exception as e:
		raise e