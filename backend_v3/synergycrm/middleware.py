from django.http.request import QueryDict


class Kwargs:
	def __init__(self, kwargs):
		self.kwargs = kwargs

	def get(self, k):
		return self.kwargs.get(k)


class IfBatchIsTrueWhenUploadFile:
	def __init__(self, get_response):
		self.get_response = get_response

	def __call__(self, request):
		from synergycrm.settings import DEBUG
		if not DEBUG and request.FILES:
			dict = {k: request.POST[k] for k in request.POST}
			request.POST = QueryDict('', mutable=True)
			request.POST.update({Kwargs(dict): None})
		response = self.get_response(request)

		return response
