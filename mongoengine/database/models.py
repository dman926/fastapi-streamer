from mongoengine import Document, StringField, FileField, BooleanField

class Media(Document):
	folder = StringField(required=True)
	filename = StringField(unique_with='folder', required=True)
	file = FileField()