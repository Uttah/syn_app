"""synergycrm URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
	https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
	1. Add an import:  from my_app import views
	2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
	1. Add an import:  from other_app.views import Home
	2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
	1. Import the include() function: from django.conf.urls import url, include
	2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView
from .settings import DEBUG
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header = 'Администрирование «Синергия»'


def _csrf_exempt(view_func):
	"""
	Функция оборачивает GraphQL API в вызов csrf_exempt,
	который позволяет избавиться от ошибок при запросах с другого хоста (в режиме разработки).
	На продакшене функция возвращает необернутый view_func, чтобы обеспечить защиту от CSRF.
	CSRF - https://en.wikipedia.org/wiki/Cross-site_request_forgery
	"""
	if DEBUG:
		return csrf_exempt(view_func)
	else:
		return view_func

urlpatterns = \
	static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + \
	static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + [
		url(r'^admin/', admin.site.urls),
		url(r'^api_v1', _csrf_exempt(GraphQLView.as_view(graphiql=DEBUG, batch=not DEBUG))),
		url(r'^', include('crm.urls'))
	]
