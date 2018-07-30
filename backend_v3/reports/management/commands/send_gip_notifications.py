from django.utils import timezone
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from users.models import User
from projects.models import Project
from salary.models import DayOff


class Command(BaseCommand):
	def handle(self, *args, **options):
		def make_correct_form(num):
			if 10 <= num <= 20:
				return 'отчётов'
			num %= 10
			if num == 1:
				return 'отчёт'
			if 2 <= num <= 4:
				return 'отчёта'
			if num > 4:
				return 'отчётов'
			return 'отчетов'

		days = DayOff.objects.filter(date=timezone.now())
		if len(days) > 0:
			return
		else:
			users = User.objects.all()
			for u in users:
				projects = Project.objects.filter(gip=u)
				message_projects = {}
				for p in projects:
					reports = p.report_set.filter(checked_by=None, deleted=False)
					if len(reports):
						number = '%05d' % p.number
						message_projects[number] = len(reports)
				if message_projects:
					subject = 'Непроверенные отчёты'
					message = 'Доброе утро, %s %s!\n\n' % (u.first_name, u.patronym)
					message += 'У вас есть отчёты исполнителей, требующие проверки, по следующим проектам:\n'
					for p in message_projects.keys():
						message += 'проект № %s - %s %s\n' % (p, message_projects[p], make_correct_form(int(message_projects[p])))
					message += '\n\nПроверить отчёты и выставить оценки можно в нашей корпоративной системе учета' \
					           ' по адресу http://office.sngy.ru/manage\n\n'
					message += 'Это письмо сгенерировано автоматически и отвечать на него не нужно.'
					send_mail(subject, message, 'report@sngy.ru', [u.email])
