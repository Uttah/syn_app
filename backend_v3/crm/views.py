from django.shortcuts import render
from django.middleware.csrf import get_token


# Create your views here.
def index(request):
	# Отсылаем куку при первом GET-запросе
	get_token(request)
	return render(request, 'index.html')
