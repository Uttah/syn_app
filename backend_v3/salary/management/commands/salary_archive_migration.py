import pickle
from django.core.management.base import BaseCommand
from users.models import User
from salary.models import SalaryArchive
from MySQLdb import connect

class Command(BaseCommand):

	def handle(self, *args, **options):

		def add_salary():
			nonlocal object, month
			# Считаем бонус
			c = db.cursor()
			c.execute('SELECT * FROM bonus WHERE user=%s AND month=\'%s\';' % (u, month))
			columns = tuple([d[0] for d in c.description])
			while True:
				data = c.fetchone()
				if not data: break
				data = dict(zip(columns, data))
				object[2] += float(data['amount'])
			# Добавляем з.п.
			SalaryArchive.objects.create(date=month, worker_id=u, object=pickle.dumps(tuple(object)))
			object = [{}, {}, 0, 0]
		db = connect(host='10.10.0.10', port=3306, db='sngy_reports', user='remote', passwd='sngy2017', use_unicode=True, charset='utf8')

		users_id = User.objects.filter().values('id')
		users_id = [u['id'] for u in users_id]

		for u in users_id:
			c = db.cursor()
			c.execute('SELECT t1.* FROM salary_archive AS t1 INNER JOIN (SELECT salary_month, worker_id, COUNT(*)  \
				AS count FROM salary_archive WHERE worker_id=%s GROUP BY salary_month) AS t2 \
				USING(salary_month, worker_id) WHERE t2.count > 1 ORDER BY salary_month;' % u)
			columns = tuple([d[0] for d in c.description])
			object = [{}, {}, 0, 0] # (months, totals, bonus, advance)
			month = ''

			c2 = db.cursor()
			c2.execute('SELECT COUNT(*) AS count FROM salary_archive AS t1 INNER JOIN (SELECT salary_month, worker_id, COUNT(*)  \
				AS count FROM salary_archive WHERE worker_id=%s GROUP BY salary_month) AS t2 \
				USING(salary_month, worker_id) WHERE t2.count > 1;' % u)
			columns2 = tuple([d[0] for d in c2.description])
			count = c2.fetchone()
			count = dict(zip(columns2, count))['count']

			while True:
				if count == 0 and month:
					add_salary()
				data = c.fetchone()
				if not data: break
				data = dict(zip(columns, data))
				if month and month != data['salary_month']:
					add_salary()
				month = data['salary_month']
				# Заполняем месяц
				if data['mnth']:
					if data['mnth'][4] == '0':
						data['mnth'] = data['mnth'][:4] + data['mnth'][5]
					object[0][data['mnth']] = {}
					object[0][data['mnth']]['work_hours'] = data['hours']
					object[0][data['mnth']]['overtime'] = data['overtime']
					object[0][data['mnth']]['home'] = data['home_hours']
					object[0][data['mnth']]['welding'] = 0
					object[0][data['mnth']]['healthy_day'] = 0
					object[0][data['mnth']]['transport_office'] = 0
					object[0][data['mnth']]['night'] = data['night_shifts_hours']
					object[0][data['mnth']]['positive_grade'] = 0
					object[0][data['mnth']]['negative_grade'] = 0
					object[0][data['mnth']]['ideal_grade'] = 0
					object[0][data['mnth']]['order'] = data['responsible_work_hours']
					object[0][data['mnth']]['sick'] = data['sick_work_hours']
					object[0][data['mnth']]['work_hours_money'] = float(data['hours_cost'])
					object[0][data['mnth']]['overtime_money'] = float(data['overtime_cost'])
					object[0][data['mnth']]['home_money'] = float(data['home_cost'])
					object[0][data['mnth']]['welding_money'] = float(data['welding_cost'])
					object[0][data['mnth']]['healthy_day_money'] = float(data['health'])
					object[0][data['mnth']]['night_money'] = float(data['night_shifts_cost'])
					object[0][data['mnth']]['positive_grade_money'] = float(data['pos_grades_cost'])
					object[0][data['mnth']]['negative_grade_money'] = float(data['neg_grades_cost'])
					object[0][data['mnth']]['ideal_grade_money'] = float(data['ideal_grades_cost'])
					object[0][data['mnth']]['transport_money'] = float(data['transportation'])
					object[0][data['mnth']]['private_car'] = float(data['auto_personal'])
					object[0][data['mnth']]['duty_car'] = float(data['auto_duty'])
					object[0][data['mnth']]['transport_office_money'] = 0
					object[0][data['mnth']]['order_money'] = float(data['responsible_work_cost'])
					object[0][data['mnth']]['vacation_money'] = float(data['vacation_work_cost'])
					object[0][data['mnth']]['sick_money'] = float(data['sick_work_cost'])

				# Заполняем totals
				else:
					object[1]['work_hours'] = data['hours']
					object[1]['overtime'] = data['overtime']
					object[1]['home'] = data['home_hours']
					object[1]['welding'] = 0
					object[1]['healthy_day'] = 0
					object[1]['transport_office'] = 0
					object[1]['night'] = data['night_shifts_hours']
					object[1]['positive_grade'] = 0
					object[1]['negative_grade'] = 0
					object[1]['ideal_grade'] = 0
					object[1]['order'] = data['responsible_work_hours']
					object[1]['sick'] = data['sick_work_hours']
					object[1]['work_hours_money'] = float(data['hours_cost'])
					object[1]['overtime_money'] = float(data['overtime_cost'])
					object[1]['home_money'] = float(data['home_cost'])
					object[1]['welding_money'] = float(data['welding_cost'])
					object[1]['healthy_day_money'] = float(data['health'])
					object[1]['night_money'] = float(data['night_shifts_cost'])
					object[1]['positive_grade_money'] = float(data['pos_grades_cost'])
					object[1]['negative_grade_money'] = float(data['neg_grades_cost'])
					object[1]['ideal_grade_money'] = float(data['ideal_grades_cost'])
					object[1]['transport_money'] = float(data['transportation'])
					object[1]['private_car'] = float(data['auto_personal']) / 2
					object[1]['duty_car'] = float(data['auto_duty']) / 2
					object[1]['transport_office_money'] = 0
					object[1]['order_money'] = float(data['responsible_work_cost'])
					object[1]['vacation_money'] = float(data['vacation_work_cost'])
					object[1]['sick_money'] = float(data['sick_work_cost'])

				if data['advance']:
					object[3] = float(data['advance'])
				count -= 1
