import os.path
import mimetypes
from django.http import HttpResponse, HttpResponseRedirect
from synergycrm.exceptions import SngyException
from .models import Document


def download(request):
	if not request.user.is_authenticated:
		return HttpResponseRedirect('/')
	kind = request.GET.get('kind')
	id = request.GET.get('id')
	if not kind or not id:
		raise SngyException('Указаны не все параметры')
	try:
		file = Document.objects.get(id=id, document_kind__eng_name=kind).file
		name = os.path.split(file.name)[-1].split('_', maxsplit=1)[1]
		content_type = mimetypes.guess_type(name)[0]
		response = HttpResponse(file.read(), content_type=content_type)
		response['Content-Disposition'] = 'attachment; filename=%s' % name
		return response
	except Document.DoesNotExist:
		raise SngyException('Такого файла не существует')



