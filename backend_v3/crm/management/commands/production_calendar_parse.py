import requests
from django.core.management.base import BaseCommand
from salary.models import DayOff


class Command(BaseCommand):
	def handle(self, *args, **options):
		access_token = 'ce3efd0d99db1a74155fb5fb5f79e400'
		base_url = 'http://data.gov.ru/api/json/dataset/7708660670-proizvcalendar/version/'
		version = requests.get(base_url + '?access_token=' + access_token)
		version = version.json()[-1]['created']
		content = requests.get(base_url + version + '/content/?access_token=' + access_token)
		content = content.json()
		months = {'Январь': '1', 'Февраль': '2', 'Март': '3', 'Апрель': '4', 'Май': '5', 'Июнь': '6',
		          'Июль': '7', 'Август': '8', 'Сентябрь': '9', 'Октябрь': '10', 'Ноябрь': '11', 'Декабрь': '12'}
		DayOff.objects.all().filter(manual=False).delete()
		for obj in content:
			year = int(obj['Год/Месяц'])
			if year < 2016:
				continue
			for m in months.keys():
				number_month = months[m]
				days = obj[m].split(',')
				for d in days:
					if '*' in d:
						continue
					date = '%s-%s-%s' % (str(year), number_month, d)
					DayOff.objects.create(date=date)
