from django.db import connection
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils.timezone import get_current_timezone
from datetime import date
from MySQLdb import connect
from users.models import User, Bonus, Position, Occupation
from absences.models import AbsenceReason, Absence
from projects.models import State, Project
from reports.models import Place, Process, SubProcess, FuncRole, Report, ProjectState
from companies.models import Requisites, Company
from salary.models import DayOff
from menu.models import TopMenu, MenuItem, Permission


class Command(BaseCommand):
	def handle(self, *args, **options):
		def setval(table, sequence):
			c.execute("""
				SELECT `AUTO_INCREMENT`
				FROM INFORMATION_SCHEMA.TABLES
				WHERE TABLE_SCHEMA = 'sngy_reports' AND TABLE_NAME = '%s';
			""" % table)
			_id = c.fetchone()[0] - 1
			cursor = connection.cursor()
			cursor.execute("SELECT setval(%s, %s, True);", [sequence, _id])
			cursor.fetchall()
			cursor.close()

		db = connect(host='office.sngy.ru', port=3306, db='sngy_reports', user='remote', passwd='sngy2017', use_unicode=True,
		             charset='utf8')
		tz = get_current_timezone()

		# Добавляем компании и реквизиты
		synergy_req = Requisites.objects.create(inn='3445119239', kpp='344501001', ogrn='1113460006021', okpo='92974129',
		                                        account='40702810603100601648',
		                                        bank='Ростовский филиал ПАО БАНКА «ФК Открытие», г. Ростов-на-Дону',
		                                        bik='046015065', kor_account='30101810760150000065')
		synergy_e_req = Requisites.objects.create(inn='3460016301', kpp='346001001', ogrn='1143443017541', okpo='22430942',
		                                          account='40702810700000005683',
		                                          bank='ОАО“АКБ”КОР”',
		                                          bik='041806799', kor_account='30101810100000000799')
		synergy = Company.objects.create(name='ООО "Синергия"', short_name='С', requisites_id=synergy_req.id)
		Company.objects.create(name='ООО "Синергия-Инжиниринг"', short_name='СИ', requisites_id=synergy_e_req.id)

		# Добавляем должности (только Синергия)
		c = db.cursor()
		c.execute('SELECT * FROM post')
		columns = tuple([d[0] for d in c.description])
		while True:
			data = c.fetchone()
			if not data:
				break
			data = dict(zip(columns, data))
			Position.objects.create(id=data['id'], name=data['name'], company_id=synergy.id)

		setval('post', 'users_position_id_seq')
		c.close()
		print('Скопировал конпании и должности')

		# Модель User / Occupation
		c = db.cursor()
		c.execute('SELECT * FROM user')
		columns = tuple([d[0] for d in c.description])
		while True:
			data = c.fetchone()
			if not data:
				break
			data = dict(zip(columns, data))
			email = data['login']
			if data['post'] in (32, 22):
				email = None
			if data['fired'][0]:
				data['work_phone'] = None
			u = User.objects.create(id=data['id'], login=data['login'], last_name=data['last_name'].strip(),
			                        first_name=data['first_name'].strip(), patronym=data['patronym'].strip(),
			                        work_phone=data['work_phone'], personal_phone=data['personal_phone'], email=email,
			                        password=data['password'], salt=data['salt'], transportation=data['transportation'],
			                        healthy=data['healthy'][0], fired=data['fired'][0],
			                        is_super_user=(data['id'] in (1, 2, 106, 5, 6, 4)))
			if not u.fired:
				Occupation.objects.create(user_id=data['id'], position_id=data['post'], salary=data['salary'],
				                          base=data['base'], advance=data['advance'], fraction=data['fraction'],
				                          by_hours=data['by_hours'][0], hire_date=date(2017, 1, 1))

		setval('user', 'users_user_id_seq')
		c.close()
		print('Скопировал пользователей')

		# Модель AbsenceReason
		c = db.cursor()
		c.execute('SELECT * FROM absence_reason')
		columns = tuple([d[0] for d in c.description])
		while True:
			data = c.fetchone()
			if not data:
				break
			data = dict(zip(columns, data))
			AbsenceReason.objects.create(id=data['id'], name=data['name'], deleted=data['deleted'][0])

		setval('absence_reason', 'absences_absencereason_id_seq')
		c.close()

		# Модель Absence
		c = db.cursor()
		c.execute('SELECT * FROM absence_view')
		columns = tuple([d[0] for d in c.description])
		while True:
			data = c.fetchone()
			if not data:
				break
			data = dict(zip(columns, data))
			absence = Absence.objects.create(id=data['id'], user_added_id=data['added'], worker_id=data['worker'],
			                                 begin=data['beginning'], end=data['ending'], time=str(data['time_counted']),
			                                 reason_id=data['reason'], comment=data['comment'], locked=data['locked'][0])
			Absence.objects.filter(id=absence.id).update(time_added=tz.localize(data['time_added']))
		setval('absence', 'absences_absence_id_seq')
		c.close()

		# Модель State
		c = db.cursor()
		c.execute('SELECT * FROM state')
		columns = tuple([d[0] for d in c.description])
		while True:
			data = c.fetchone()
			if not data:
				break
			data = dict(zip(columns, data))
			State.objects.create(id=data['id'], name=data['name'], letter=data['name'][4], deleted=data['deleted'][0])

		setval('state', 'projects_state_id_seq')
		c.close()
		print('Скопировал отсутствия')

		# Модель Project
		c = db.cursor()
		c.execute('SELECT * FROM project')
		columns = tuple([d[0] for d in c.description])
		while True:
			data = c.fetchone()
			if not data:
				break
			data = dict(zip(columns, data))
			Project.objects.create(id=data['id'], number=data['number'], description=data['description'], gip_id=data['gip'],
			                       state_id=data['state'], comment=data['comment'])

		setval('project', 'projects_project_id_seq')
		c.close()
		print('Скопировал проекты')

		# Модель Place
		c = db.cursor()
		c.execute('SELECT * FROM place')
		columns = tuple([d[0] for d in c.description])
		while True:
			data = c.fetchone()
			if not data:
				break
			data = dict(zip(columns, data))
			kind = None
			if data['id'] == 4:
				kind = 'C'
			if data['id'] == 8:
				kind = 'N'
			Place.objects.create(id=data['id'], name=data['name'], kind=kind, deleted=data['deleted'][0])

		setval('place', 'reports_place_id_seq')
		c.close()

		# Модель Process
		c = db.cursor()
		c.execute('SELECT * FROM process')
		columns = tuple([d[0] for d in c.description])
		while True:
			data = c.fetchone()
			if not data:
				break
			data = dict(zip(columns, data))
			Process.objects.create(id=data['id'], name=data['name'], deleted=data['deleted'][0])

		setval('process', 'reports_process_id_seq')
		c.close()

		# Модель SubProcess
		c = db.cursor()
		c.execute('SELECT * FROM sub_process')
		columns = tuple([d[0] for d in c.description])
		while True:
			data = c.fetchone()
			if not data:
				break
			data = dict(zip(columns, data))
			kind = None
			if data['id'] in (47, 32, 38, 59, 45):
				kind = 'D'
			if data['id'] in (26, 27):
				kind = 'A'
			if data['id'] in (21, 19):
				kind = 'P'
			SubProcess.objects.create(id=data['id'], process_id=data['process'], name=data['name'], kind=kind,
			                          deleted=data['deleted'][0])

		setval('sub_process', 'reports_subprocess_id_seq')
		c.close()

		# Модель FuncRole
		# Получаем данные из таблицы post
		post_data = []
		c = db.cursor()
		c.execute('SELECT * FROM post')
		columns = tuple([d[0] for d in c.description])
		while True:
			data = c.fetchone()
			if not data:
				break
			post_data.append(dict(zip(columns, data)))
		c.close()

		c = db.cursor()
		c.execute('SELECT * FROM func_role')
		columns = tuple([d[0] for d in c.description])
		while True:
			data = c.fetchone()
			if not data:
				break
			data = dict(zip(columns, data))
			kind = None
			if data['id'] in (17, 18, 24, 26):
				kind = 'W'

			func_role = FuncRole.objects.create(id=data['id'], name=data['name'], kind=kind, deleted=data['deleted'][0])
			for p in post_data:
				f = data
				f_posts = f['post']
				if f['post']:
					f_posts = f['post'].split(',')
				else:
					f_posts = []
				if p['executor_only'][0] == 1:
					if f['id'] in (17, 18, 24, 26):
						func_role.positions.add(Position.objects.get(id=p['id']))
					continue
				if (p['static_only'][0] == 0 and f['dynamic'][0] == 1) or str(p['id']) in f_posts:
					func_role.positions.add(Position.objects.get(id=p['id']))

		setval('func_role', 'reports_funcrole_id_seq')
		c.close()
		print('Скопировал вспомогательные таблицы')

		# Модель Report и таблица ProjectState
		where = ''
		if settings.DEBUG:
			where = " WHERE report_date > '2017-11-01'"
		c = db.cursor()
		c.execute('SELECT COUNT(*) FROM report' + where)
		total_reports = c.fetchone()[0]
		c.close()
		c = db.cursor()
		c.execute('SELECT * FROM report' + where)
		columns = tuple([d[0] for d in c.description])
		index = 0
		while True:
			index = index + 1
			if index % 100 == 0:
				print('Скопировано отчетов {} из {} ({:.0%})'.format(index, total_reports, index / total_reports))
			data = c.fetchone()
			if not data:
				break
			data = dict(zip(columns, data))
			car = None
			gas = None
			if data['car']:
				car = data['car'][0].upper()
			if data['gas']:
				gas = data['gas'][0].upper()
			if data['process'] == 0:
				data['process'] = None
				data['sub_process'] = None
			time_checked = data['time_checked']
			if time_checked:
				time_checked = tz.localize(time_checked)
			report = Report.objects.create(id=data['id'], user_added_id=data['user_added'], worker_id=data['worker'],
			                               report_date=data['report_date'], func_role_id=data['func_role'],
			                               process_id=data['process'], sub_process_id=data['sub_process'], task=data['task'],
			                               time_spent=str(data['time_spent']), place_id=data['place'],
			                               distance=data['distance'], car=car, gas=gas, where_from=data['where_from'],
			                               where_to=data['where_to'], money_spent=data['money_spent'],
			                               checked_by_id=data['checked_by'], time_checked=time_checked,
			                               quality_grade=data['quality_grade'], time_grade=data['time_grade'],
			                               vc_project=data['vc_project'], vc_digits=data['vc_digits'],
			                               vc_digits_minor=data['vc_digits_minor'], model=data['model'],
			                               comment=data['comment'], exported=data['exported'],
			                               record_counted=data['record_counted'], day_off_call=data['dayOffCall'][0],
			                               night_shift=data['night_shift'][0],
			                               responsible_work_paid=data['responsible_work_paid'][0],
			                               night_shifts_paid=data['night_shifts_paid'][0], checked_hr=data['checked_HR'][0],
			                               deleted=data['deleted'][0])
			Report.objects.filter(id=report.id).update(time_edited=tz.localize(data['time_edited']))
			try:
				project = Project.objects.get(number=data['project_num'])
				ProjectState.objects.create(project_id=project.id, state_id=data['project_state'], report_id=report.id)
			except Project.DoesNotExist:
				continue

		setval('report', 'reports_report_id_seq')
		c.close()
		print('Скопировал отчеты')

		# Модель Bonus
		c = db.cursor()
		c.execute('SELECT * FROM bonus')
		columns = tuple([d[0] for d in c.description])
		while True:
			data = c.fetchone()
			if not data:
				break
			data = dict(zip(columns, data))
			project = Project.objects.get(number=data['project'])
			bonus = Bonus.objects.create(id=data['id'], user_added_id=data['user_added'], user_id=data['user'],
			                             project_id=project.id, amount=data['amount'], description=data['description'],
			                             month=data['month'], counted=data['counted'][0])
			Bonus.objects.filter(id=bonus.id).update(time_added=tz.localize(data['time_added']))

		setval('bonus', 'users_bonus_id_seq')
		c.close()
		print('Скопировал премии и вычеты')

		# Модель DayOff
		c = db.cursor()
		c.execute('SELECT * FROM days_off')
		columns = tuple([d[0] for d in c.description])
		while True:
			data = c.fetchone()
			if not data:
				break
			data = dict(zip(columns, data))
			DayOff.objects.create(date=data['date'])

		c.close()
		print('Скопировал выходные даты')

		# Модель меню
		reports = MenuItem.objects.create(text='Табели', link='/reports', sorting=0)
		manage_reports = MenuItem.objects.create(text='Отчеты сотрудников', link='/manage_reports', sorting=0)
		users = MenuItem.objects.create(text='Сотрудники', link='/users', sorting=0)
		projects = MenuItem.objects.create(text='Проекты', link='/projects', sorting=1)

		view_full = Permission.objects.get(codename__exact='view_full_user')
		positions = MenuItem.objects.create(text='Должности', link='/positions', sorting=2)
		positions.required_permissions.add(view_full)

		view_bonus = Permission.objects.get(codename__exact='view_all_bonus')
		bonuses = MenuItem.objects.create(text='Премии и вычеты', link='/bonuses', sorting=1)
		bonuses.required_permissions.add(view_bonus)

		manage_absences = Permission.objects.get(codename__exact='manage_absences')
		absences = MenuItem.objects.create(text='Отсутствия сотрудников', link='/absences', sorting=0)
		absences.required_permissions.add(manage_absences)

		admin = MenuItem.objects.create(text='Панель администрирования', link='/admin/', sorting=0)

		# Модель заголовков меню
		TopMenu.objects.create(text='Сотруднику', sorting=0, position=None).items.add(reports)
		TopMenu.objects.create(text='Руководителю проекта', sorting=1, position=None).items.add(manage_reports)
		TopMenu.objects.create(text='Компания', sorting=2, position=None).items.add(users, projects, positions)
		TopMenu.objects.create(text='Специалисту по персоналу', sorting=3, position_id=20).items.add(positions, absences)
		TopMenu.objects.create(text='Экономисту', sorting=4, position_id=21).items.add(positions, bonuses, absences)
		TopMenu.objects.create(text='Администратору', sorting=20, position_id=17).items.add(admin)
