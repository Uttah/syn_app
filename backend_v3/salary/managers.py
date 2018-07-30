from datetime import date, timedelta
from django.db.models import F
from django.db.models import Count, Subquery, OuterRef, Sum, Manager
from django.db.models.functions import Extract
from dateutil.relativedelta import relativedelta


def generate_b7_export():
	from .models import GradeCoefficient
	from reports.models import Report
	from users.models import GlobalCoefficient
	from .calculation import cost_hours

	limit = date.today() + relativedelta(months=-6)
	sub_query = Report.objects.filter(id=OuterRef('id')).annotate(count=Count('projects__number')).values('count')
	hours = Sum(Extract('time_spent', 'EPOCH') / Subquery(sub_query) / 3600)
	filtered = Report.objects.filter(exported__lt=2, deleted=0, checked_by__isnull=False, report_date__gte=limit)
	value_fields = ('id', 'worker_id',
	                'worker__last_name', 'worker__first_name', 'worker__patronym',
	                'report_date', 'func_role_id', 'func_role__name', 'process__name', 'sub_process__kind',
	                'sub_process__name', 'task', 'place__name', 'place__kind', 'money_spent', 'quality_grade',
	                'time_grade', 'comment', 'projectstate__project__number',
	                'projectstate__project__gip__last_name', 'projectstate__project__gip__first_name',
	                'projectstate__project__gip__patronym',
	                'projectstate__state__name',
	                'car', 'gas', 'distance')
	values = filtered.values(*value_fields)
	result = values.annotate(hours=hours).order_by('report_date')

	global_coeffs = {gc['name']: gc['value'] for gc in GlobalCoefficient.objects.values('name', 'value')}
	grade_coeffs = {(gc['quality'], gc['time']): gc['coefficient'] for gc in
	                GradeCoefficient.objects.values('quality', 'time', 'coefficient')}

	def construct_name(last, first, patronym):
		if patronym:
			return '{} {} {}'.format(last, first, patronym)
		else:
			return '{} {}'.format(last, first)

	def convert_to_time(_hours):
		_hours *= 3600
		_hours, seconds = divmod(_hours, 3600)
		minutes, seconds = divmod(seconds, 60)
		_hours = int(_hours)
		minutes = int(minutes)
		seconds = round(seconds)
		if seconds > 59:
			minutes += 1
			seconds = 0
		if minutes > 59:
			_hours += 1
			minutes = 0
		return '{:01d}:{:02d}:{:02d}'.format(_hours, minutes, seconds)

	class Object:
		pass

	list_result = []
	id_storage = {}
	for r in result:
		user_obj = Object()
		setattr(user_obj, 'id', r['worker_id'])
		str_mnth = str(r['report_date'].year) + str(r['report_date'].month)
		costs = cost_hours(user_obj, str_mnth)
		working_cost = 0
		home_cost = 0
		welding_cost = 0
		driving_cost = 0
		grades_cost = 0
		if r['place__kind'] != 'N':
			working_cost = r['hours'] * costs['salary']
			if r['func_role_id'] == 24:
				welding_cost = working_cost * global_coeffs['welding_surcharge']
			if r['sub_process__kind'] == 'D':
				if r['car'] == 'D':
					driving_cost = r['distance'] * global_coeffs['private_car']
				elif r['gas'] == 'D':
					driving_cost = r['distance'] * global_coeffs['private_car_duty_gas']
				else:
					driving_cost = r['distance'] * global_coeffs['private_car_private_gas']
			if r['quality_grade'] is not None and r['time_grade'] is not None:
				grade = grade_coeffs.get((r['quality_grade'], r['time_grade']), 0)
				if grade > 0:
					grade -= 1
				grades_cost = working_cost * grade
			totals = working_cost + welding_cost + driving_cost + grades_cost
		else:
			home_cost = r['hours'] * costs['base']
			totals = home_cost
		worker_name = construct_name(r['worker__last_name'], r['worker__first_name'], r['worker__patronym'])
		gip_name = construct_name(r['projectstate__project__gip__last_name'], r['projectstate__project__gip__first_name'],
		                          r['projectstate__project__gip__patronym'])
		time_spent = convert_to_time(r['hours'])

		def csv_escape(text):
			if text:
				if text[0] == '-':
					text = text[1:]
				return '"' + text.strip().replace('"', '""') + '"'
			else:
				return ''

		def handle_nones(item):
			if item is None:
				return ''
			else:
				return str(item)

		# Обеспечиваем уникальность id путем добавления буквенного индекса
		idx = r['id']
		current_index = id_storage.get(idx, None)
		if current_index is None:
			id_storage[idx] = 'a'
			str_idx = str(idx)
		else:
			str_idx = str(idx) + current_index
			current_index = chr(ord(current_index) + 1)
			id_storage[idx] = current_index

		row = list()
		row.append(str_idx)
		row.append(worker_name)
		row.append(r['report_date'].isoformat())
		row.append(r['func_role__name'])
		row.append('SNGY{:07d}'.format(r['projectstate__project__number']))
		row.append(gip_name)
		row.append(r['projectstate__state__name'])
		row.append(handle_nones(r['process__name']))
		row.append(handle_nones(r['sub_process__name']))
		row.append(csv_escape(r['task']))
		row.append(time_spent)
		row.append(r['place__name'])
		row.append(handle_nones(r['money_spent']))
		row.append(handle_nones(r['quality_grade']))
		row.append(handle_nones(r['time_grade']))
		row.append(csv_escape(r['comment']))
		row.append('{:.2f}'.format(working_cost).replace('.', ','))
		row.append('{:.2f}'.format(home_cost).replace('.', ','))
		row.append(handle_nones(r['money_spent']))
		row.append('{:.2f}'.format(welding_cost).replace('.', ','))
		row.append('{:.2f}'.format(driving_cost).replace('.', ','))
		row.append('{:.2f}'.format(grades_cost).replace('.', ','))
		row.append('{:.2f}'.format(totals).replace('.', ','))

		list_result.append(';'.join(row))

	head = 'ID;Исполнитель;Дата задачи;Функ. Роль;№ проекта;ГИП;Этап проекта;Процесс;Подпроцесс;'
	head += 'Задача;Времени потрачено;Место;Затраты на проезд;Оценка качества;Оценка срока;Комментарий;За рабочие часы;'
	head += 'За простой дома;Передвижение на объект;Доплата за сварку;Водительские;Доплата за оценки;Оплата'

	result = b'\xef\xbb\xbf'.decode('utf-8') + head + '\n' + '\n'.join(list_result)
	return result


class SalaryPaymentManager(Manager):
	def list_paged_payments(self, offset, first, sort_by, desc=False, search='', filters=None):
		last = offset + first
		salary_payment = self.filter()
		if sort_by == 'user':
			sort_field = F('user__first_name')
		elif sort_by == 'amount':
			sort_field = F('amount')
		elif sort_by == 'advance':
			sort_field = F('advance')
		elif sort_by == 'company':
			sort_field = F('company')
		if desc:
			sort_field = sort_field.desc()
		if first < 0:
			return [], 0
		salary_payment = salary_payment.order_by(sort_field)
		tc = salary_payment.count()
		return salary_payment[offset:last], tc


class DayOffManager(Manager):
	def calculate_end_date(self, begin, working_days, including=True):
		if working_days < 1:
			return begin
		# Определяем ориентировочный конец периода (если бы в периоде не было ни одного выходного)
		if including:
			working_days -= 1
		end = begin + timedelta(days=working_days)
		days_off = self.filter(date__range=(begin, end)).count()
		# Граничный случай
		if days_off == 0:
			return end
		else:
			return self.calculate_end_date(end + timedelta(days=1), days_off)
