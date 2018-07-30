from datetime import datetime, timedelta
from calendar import monthrange
from functools import reduce
from django.db import models
from .models import DayOff, GradeCoefficient, Order, SalaryArchive
from users.models import GlobalCoefficient, Coefficients, Bonus, Occupation, User
from absences.models import Absence


def get_salary_limits(_last_salary_month):
	r = monthrange(_last_salary_month.year, _last_salary_month.month)
	d = timedelta(days=r[1])
	begin = _last_salary_month + d
	r = monthrange(begin.year, begin.month)
	d = timedelta(days=r[1] - 1)
	end = begin + d
	return begin, end


last_salary_month = None


def get_last_salary_month():
	global last_salary_month
	if last_salary_month is None:
		archive_max = SalaryArchive.objects.aggregate(max=models.Max('date'))
		if archive_max['max']:
			last_salary_month = datetime.combine(archive_max['max'], datetime.min.time())
		else:
			last_salary_month = datetime(2017, 12, 1)
	return last_salary_month


work_hours = {}


def work_hours_in_month(date, first_date=None):
	global work_hours
	if date not in work_hours or first_date is not None:
		begin_month = datetime(year=int(date[0:4]), month=int(date[4:]), day=1).date()
		days = monthrange(begin_month.year, begin_month.month)[1]
		end_month = begin_month.replace(day=days)
		# Если первая дата попадает в этот месяц
		if first_date is not None and begin_month < first_date < end_month:
			begin_month = first_date
			days = (end_month - begin_month).days + 1
		day_off = DayOff.objects.filter(date__range=(begin_month, end_month))
		hours = (days - len(day_off)) * 8
		work_hours[date] = hours
	return work_hours[date]


global_coefficients = None
user_coefficients = None
grade_coefficients = None
max_grade_coefficient = None
absences = None
orders = None
user_salaries = {}
occupations = None


def cost_hours(user, date, kistanov_place=None):
	global global_coefficients
	global user_salaries
	global occupations
	global user_coefficients
	if (user.id, date) not in user_salaries:
		hours = work_hours_in_month(date)
		if occupations is None:
			occupations = Occupation.objects.values('by_hours', 'fixed_hour', 'fraction', 'salary', 'base', 'user_id'). \
				filter(user__fired=False).order_by('user_id')
			occupations = {o['user_id']: {
				'by_hours': o['by_hours'], 'fraction': o['fraction'], 'salary': o['salary'],
				'base': o['base'], 'fixed_hour': o['fixed_hour']}
				for o in occupations}
		if user.id in occupations:
			occupation = occupations[user.id]
			hours = hours * occupation['fraction'] / 100
			if not occupation['salary']:
				salary = 0
			else:
				salary = occupation['salary'] / hours
			if not occupation['base']:
				base = 0
			else:
				base = occupation['base'] / hours
			occupation_salary = occupation['salary']
			if kistanov_place in (3, 4):
				occupation_salary = None  # Чтобы выполнилось условие ниже
			if occupation_salary is None and occupation['by_hours'] and not occupation['fixed_hour']:
				if global_coefficients is None:
					global_coefficients = {d['name']: d['value'] for d in GlobalCoefficient.objects.values('name', 'value')}
				if user_coefficients is None:
					user_coefficients = Coefficients.objects.all()
					user_coefficients = {uc.user_id: uc for uc in user_coefficients}
				coeffs = user_coefficients[user.id]
				salary = coeffs.avg * coeffs.max_hour * (global_coefficients['default_work_hours'] / hours)
			if occupation['fixed_hour']:
				salary = occupation['fixed_hour']
			result = {'base': base, 'salary': salary}
		else:
			result = {'base': 0, 'salary': 0}
		if user.id != 28:
			user_salaries[(user.id, date)] = result
	if user.id == 28:
		return result
	return user_salaries[(user.id, date)]


def time_for_calculation(time):
	return time.total_seconds() / 3600


def flush_cache():
	global last_salary_month
	global work_hours
	global global_coefficients
	global user_coefficients
	global grade_coefficients
	global max_grade_coefficient
	global absences
	global orders
	global user_salaries
	global occupations
	last_salary_month = None
	work_hours = {}
	global_coefficients = None
	user_coefficients = None
	grade_coefficients = None
	max_grade_coefficient = None
	absences = None
	orders = None
	user_salaries = {}
	occupations = None


class DateStats:
	def __init__(self, **kwargs):
		self.work_hours = kwargs.get('work_hours', timedelta())
		self.overtime = kwargs.get('overtime', timedelta())
		self.home = kwargs.get('home', timedelta())
		self.welding = kwargs.get('welding', timedelta())
		self.healthy_day = kwargs.get('healthy_day', 0)
		self.transport_office = kwargs.get('transport_office', 0)
		self.night = kwargs.get('night', timedelta())
		self.positive_grade = kwargs.get('positive_grade', timedelta())
		self.negative_grade = kwargs.get('negative_grade', timedelta())
		self.ideal_grade = kwargs.get('ideal_grade', timedelta())
		self.order = kwargs.get('order', timedelta())
		self.sick = kwargs.get('sick', timedelta())

		self.work_hours_money = kwargs.get('work_hours_money', 0)
		self.overtime_money = kwargs.get('overtime_money', 0)
		self.home_money = kwargs.get('home_money', 0)
		self.welding_money = kwargs.get('welding_money', 0)
		self.healthy_day_money = kwargs.get('healthy_day_money', 0)
		self.night_money = kwargs.get('night_money', 0)
		self.positive_grade_money = kwargs.get('positive_grade_money', 0)
		self.negative_grade_money = kwargs.get('negative_grade_money', 0)
		self.ideal_grade_money = kwargs.get('ideal_grade_money', 0)
		self.transport_money = kwargs.get('transport_money', 0)
		self.private_car = kwargs.get('private_car', 0)
		self.duty_car = kwargs.get('duty_car', 0)
		self.transport_office_money = kwargs.get('transport_office_money', 0)
		self.order_money = kwargs.get('order_money', 0)
		self.vacation_money = kwargs.get('vacation_money', 0)
		self.sick_money = kwargs.get('sick_money', 0)

	def __add__(self, other):
		attributes = ['work_hours', 'overtime', 'home', 'welding', 'healthy_day', 'transport_office', 'night',
		              'positive_grade', 'negative_grade', 'ideal_grade', 'order', 'sick', 'work_hours_money',
		              'overtime_money', 'home_money', 'welding_money', 'healthy_day_money', 'night_money',
		              'positive_grade_money', 'negative_grade_money', 'ideal_grade_money', 'transport_money',
		              'private_car', 'duty_car', 'transport_office_money', 'order_money', 'vacation_money', 'sick_money']
		kwargs = {}
		for a in attributes:
			self_value = getattr(self, a)
			other_value = getattr(other, a)
			setattr(self, a, self_value + other_value)
			kwargs[a] = self_value + other_value
		return DateStats(**kwargs)


# Класс для подсчета часов за отдельный день
class DateCalculator:
	_global_coefficients = None

	def __init__(self):
		self.storage = list()
		self.current_date = None
		self.work_hours = timedelta()
		self.overtime = timedelta()
		self.home = timedelta()
		self.welding = timedelta()
		self.healthy_day = False
		self.transport_office = False
		self.night = timedelta()
		self.positive_grade = timedelta()
		self.negative_grade = timedelta()
		self.ideal_grade = timedelta()
		self.order = timedelta()
		self.order_hours = timedelta()  # Временная, значение присваивается к self.order
		self.sick = timedelta()

		self.work_hours_money = 0
		self.overtime_money = 0
		self.home_money = 0
		self.welding_money = 0
		self.healthy_day_money = 0
		self.night_money = 0
		self.positive_grade_money = 0
		self.negative_grade_money = 0
		self.ideal_grade_money = 0
		self.transport_money = 0
		self.private_car = 0
		self.duty_car = 0
		self.transport_office_money = 0
		self.order_money = 0
		self.vacation_money = 0
		self.sick_money = 0

		self.kistanov_place = None

	def append(self, reports):
		try:
			iterator = iter(reports)
		except TypeError:
			self.storage.append(reports)
			self.user = reports.worker
			self.str_month = str(reports.report_date.year) + str(reports.report_date.month)
			if not self.current_date:
				self.current_date = reports.report_date
			else:
				assert self.current_date == reports.report_date, 'DateCalculator.append() takes reports with the same report date'
		else:
			[self.append(report) for report in reports]

	def get_totals(self):
		healthy_day = 0
		if self.healthy_day:
			healthy_day = 1
		transport_day = 0
		if self.transport_office:
			transport_day = 1
		return DateStats(work_hours=self.work_hours, overtime=self.overtime, home=self.home, welding=self.welding,
		                 healthy_day=healthy_day, transport_office=transport_day, transport_money=self.transport_money,
		                 night=self.night,
		                 private_car=self.private_car, duty_car=self.duty_car, positive_grade=self.positive_grade,
		                 negative_grade=self.negative_grade, ideal_grade=self.ideal_grade, order=self.order,
		                 sick=self.sick, work_hours_money=self.work_hours_money,
		                 overtime_money=self.overtime_money, home_money=self.home_money, welding_money=self.welding_money,
		                 healthy_day_money=self.healthy_day_money, night_money=self.night_money,
		                 positive_grade_money=self.positive_grade_money, negative_grade_money=self.negative_grade_money,
		                 ideal_grade_money=self.ideal_grade_money, transport_office_money=self.transport_office_money,
		                 order_money=self.order_money, vacation_money=self.vacation_money, sick_money=self.sick_money)

	def calculate(self, days_off):
		global global_coefficients
		day_norm = timedelta(hours=8)
		day_hours = timedelta()
		if global_coefficients is None:
			global_coefficients = {d['name']: d['value'] for d in GlobalCoefficient.objects.values('name', 'value')}
		for report in self.storage:
			if report.worker.id == 28:
				self.kistanov_place = report.place.id
			time_spent = timedelta(hours=report.time_spent.hour, minutes=report.time_spent.minute)
			if report.record_counted == 0:
				global absences
				user_absences = [a for a in absences if
				                 a['worker_id'] == self.user.id and
				                 a['begin'] <= self.current_date and
				                 a['end'] >= self.current_date]
				# Если не попадает в отпуск
				if not user_absences:
					if self.current_date not in days_off:
						# Если день не выходной
						# Сидение без работы считаем отдельно
						if report.place.kind == 'N':
							self.home += time_spent
						else:
							day_hours += time_spent
					else:
						# Если день выходной, то вся работа идет в преработки
						if report.place.kind != 'N':
							self.overtime += time_spent
				else:
					costs = cost_hours(self.user, self.str_month)
					self.vacation_money += time_for_calculation(time_spent) * costs['salary']
			# Сварка
			# TODO: придумать что-нибудь для задания нескольких типов одной функциональной роли (массив типов в БД?)
			positions_id = [p['id'] for p in self.user.positions.all().values()]
			if report.place.kind != 'N' and report.func_role_id == 24 and \
				32 not in positions_id and 37 not in positions_id and report.record_counted == 0:
				self.welding += time_spent
			# Проезд до объектов
			if report.money_spent and report.record_counted == 0:
				self.transport_money += (report.money_spent - global_coefficients['minimal_transport'])
			# Проезд до офиса
			if report.place.kind == 'O' and report.record_counted == 0:
				self.transport_office = True
			# Оценки
			if report.quality_grade is not None and report.time_grade is not None and report.record_counted <= 1:
				global grade_coefficients, max_grade_coefficient
				if grade_coefficients is None:
					grade_coefficients = GradeCoefficient.objects.values('quality', 'time', 'coefficient')
				grade_coefficient = next((g['coefficient'] for g in grade_coefficients
				                          if g['quality'] == report.quality_grade and g['time'] == report.time_grade), 0)
				if grade_coefficient > 1:
					self.positive_grade += (grade_coefficient - 1) * time_spent
				else:
					self.negative_grade += (1 - grade_coefficient) * time_spent
				if max_grade_coefficient is None:
					max_grade_coefficient = max(grade_coefficients, key=lambda g: g['coefficient'])['coefficient']
				self.ideal_grade += (max_grade_coefficient - 1) * time_spent
			# Ночные смены
			if report.night_shift and report.checked_hr and not report.night_shifts_paid:
				self.night += time_spent
			# Амортизация
			if report.distance and report.car and report.gas and report.record_counted == 0:
				if report.car == 'P' and report.gas == 'P':
					self.private_car += report.distance * global_coefficients['private_car_private_gas']
				if report.car == 'P' and report.gas == 'D':
					self.private_car += report.distance * global_coefficients['private_car_duty_gas']
				if report.car == 'D':
					self.duty_car += report.distance * global_coefficients['private_car']
			# Ответственные
			func_roles = {11: global_coefficients['gip_order_surcharge'],
			              12: global_coefficients['manufacturer_order_surcharge'],
			              13: global_coefficients['pnr_order_surcharge'],
			              27: global_coefficients['master_order_surcharge']}
			# TODO: изменить report.place.id на какой-нибудь тип
			if not report.responsible_work_paid and report.place_id in [3, 4] and report.sub_process.kind not in ['D', 'R'] \
				and report.func_role.kind == 'R':
				global orders
				reports_projects = [r.id for r in report.projects.all()]
				filtered_orders = [o for o in orders if
				                   o['responsible_id'] == self.user.id and
				                   o['project_id'] in reports_projects and
				                   o['date'] <= report.report_date]
				for _ in filtered_orders:
					if report.func_role_id in func_roles:
						self.order += time_spent / len(report.projects.all()) * func_roles[report.func_role_id]
						self.order_hours += time_spent / len(report.projects.all())

		# Если больше нормы - то переработка
		if day_hours > day_norm and self.current_date not in days_off:
			self.overtime += day_hours - day_norm
			self.work_hours = day_norm
		else:
			self.work_hours = day_hours
		# ЗОЖ
		health_norm = timedelta(hours=4)
		if (self.work_hours >= health_norm or self.overtime >= health_norm) and self.user.healthy:
			self.healthy_day = True

		# Считаем деньги
		costs = cost_hours(self.user, self.str_month, self.kistanov_place)
		self.work_hours_money = time_for_calculation(self.work_hours) * costs['salary']
		self.overtime_money = time_for_calculation(self.overtime) * costs['salary']
		self.home_money = time_for_calculation(self.home) * costs['base']
		self.welding_money = time_for_calculation(self.welding) * costs['salary'] * global_coefficients['welding_surcharge']
		if self.healthy_day:
			self.healthy_day_money = global_coefficients['health']
		self.night_money = time_for_calculation(self.night) * costs['salary'] * global_coefficients['night']
		self.positive_grade_money = time_for_calculation(self.positive_grade) * costs['salary']
		self.negative_grade_money = time_for_calculation(self.negative_grade) * costs['salary']
		self.ideal_grade_money = time_for_calculation(self.ideal_grade) * costs['salary']
		if self.transport_office:
			self.transport_office_money = self.user.occupation.transportation
		self.order_money = time_for_calculation(self.order) * costs['salary']
		self.order = self.order_hours


# Базовый класс с функционалом группировки
# по ключу, возвращаемому key_func и
# имеющему под собой следующий группировщик underlying_type
# в качестве объектов, которые суммируются по классификаторам, используются объекты типа totals_type
class Classifier:
	def __init__(self, key_func, underlying_type, totals_type=DateStats):
		self.storage = dict()
		self.key_func = key_func
		self.underlying_type = underlying_type
		self.totals = None
		self.totals_type = totals_type

	def calculate(self, *args, **kwargs):
		for value in self.storage.values():
			value.calculate(*args, **kwargs)

	def get_totals(self):
		if not self.totals:
			totals = [value.get_totals() for value in self.storage.values()]
			self.totals = reduce(lambda a, b: a + b, totals, self.totals_type())
		return self.totals

	def append(self, report):
		key = self.key_func(report)
		if key not in self.storage:
			self.storage[key] = self.underlying_type()
		self.storage[key].append(report)


# Группировка по конкретной дате
class DateClassifier(Classifier):
	def __init__(self):
		super().__init__(lambda report: report.report_date, DateCalculator)


# Группировка по год+месяц
class MonthClassifier(Classifier):
	def __init__(self):
		super().__init__(lambda report: str(report.report_date.year) + str(report.report_date.month), DateClassifier)


# Группировка по id пользователя
class UserClassifier(Classifier):
	def __init__(self):
		super().__init__(lambda report: report.worker_id, MonthClassifier)

	def get_totals(self):
		Classifier.get_totals(self)
		bonuses = Bonus.objects.filter(counted=False, cash=False)
		for u in self.storage:
			self.storage[u].totals.bonus = 0
		for b in bonuses:
			for u in self.storage:
				if b.user_id == u:
					self.storage[u].totals.bonus += b.amount / b.installments
		_occupations = Occupation.objects.all()
		_users = {u.id: u for u in User.objects.all()}
		self.totals.overtime = timedelta(0)
		self.totals.overtime_money = 0
		for u in self.storage:
			o = next((o for o in _occupations if o.user_id == u), None)
			if o:
				hire_date = _users[u].hire_date
				day = hire_date.day
				hire_date = hire_date.replace(day=1)
				salary_month = get_salary_limits(get_last_salary_month())[0].date()
				# Не начислять аванс, если сотрудник был принят позже 15го числа зарплатного месяца
				if hire_date == salary_month and day > 15:
					self.storage[u].totals.advance = 0
				else:
					self.storage[u].totals.advance = o.advance
				if not o.by_hours:
					u = _users[u]
					if not u.fired:
						overtime = self.storage[u.id].totals.overtime
						overtime_money = self.storage[u.id].totals.overtime_money
						work_time = self.storage[u.id].totals.work_hours
						self.storage[u.id].totals.overtime = timedelta(0)

						_last_salary_month = get_salary_limits(get_last_salary_month())[1]
						str_month = str(_last_salary_month.year) + str(_last_salary_month.month)

						# Отложено до лучших времен
						# limits = get_salary_limits(get_last_salary_month())
						# absences = Absence.objects.filter(worker=u, begin__lte=limits[1], end__gte=limits[0]).exclude(
						# 	reason__id=3)
						# absences_time = timedelta(0)
						# for a in absences:
						# 	begin = datetime.combine(a.begin, datetime.min.time())
						# 	if begin < limits[0]:
						# 		begin = limits[0]
						# 	end = datetime.combine(a.end, datetime.min.time())
						# 	if end > limits[1]:
						# 		end = limits[1]
						# 	days = end - begin
						# 	if days:
						# 		hours = days.total_seconds() / 86400 * timedelta(hours=a.time.hour,
						# 		                                                 minutes=a.time.minute).total_seconds() / 3600
						# 		absences_time += timedelta(hours=hours)
						# 	else:
						# 		absences_time += timedelta(hours=a.time.hour, minutes=a.time.minute)

						# Сейчас расчет производится только исходя из недостающих рабочих часов
						if overtime > timedelta(0):
							if _last_salary_month.replace(day=1).date() == u.hire_date.replace(day=1):
								month_hours = timedelta(hours=work_hours_in_month(str_month, first_date=u.hire_date))
							else:
								month_hours = timedelta(hours=work_hours_in_month(str_month))
							if work_time <= month_hours and month_hours - work_time <= overtime:
								overtime = month_hours - work_time
							self.storage[u.id].totals.overtime = overtime

							costs = cost_hours(u, str_month)
							overtime_money = time_for_calculation(overtime) * costs['salary']
							self.storage[u.id].totals.overtime_money = overtime_money
						# Очистка
						for m in self.storage[u.id].storage:
							if m == str_month:
								self.storage[u.id].storage[m].totals.overtime = overtime
								self.storage[u.id].storage[m].totals.overtime_money = overtime_money
							else:
								self.storage[u.id].storage[m].totals.overtime = timedelta(0)
								self.storage[u.id].storage[m].totals.overtime_money = 0
							for d in self.storage[u.id].storage[m].storage:
								self.storage[u.id].storage[m].storage[d].overtime = timedelta(0)
								self.storage[u.id].storage[m].storage[d].overtime_money = 0

				# Суммируем переработки заново
				if type(u) is User:
					u = u.id
				self.totals.overtime += self.storage[u].totals.overtime
				self.totals.overtime_money += self.storage[u].totals.overtime_money

		return self.totals


# Общий класс для группировки отчетов
class ReportClassifier:
	def __init__(self, report_list):
		self.storage = UserClassifier()
		if len(report_list) > 0:
			max_date = max(report_list, key=lambda r: r.report_date).report_date
			min_date = min(report_list, key=lambda r: r.report_date).report_date
			limits = (min_date, max_date)
		else:
			limits = get_salary_limits(get_last_salary_month())
		global absences
		global orders
		if absences is None:
			absences = Absence.objects.filter(begin__lte=limits[1], end__gte=limits[0], reason__id=3). \
				values('worker_id', 'begin', 'end').order_by('begin', 'end')
		if orders is None:
			orders = Order.objects.values('date', 'project_id', 'responsible_id')
		for report in report_list:
			self.storage.append(report)

	def sum_hours(self, *args, **kwargs):
		self.storage.calculate(*args, **kwargs)

	def totals(self):
		return self.storage.get_totals()
