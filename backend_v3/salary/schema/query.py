import pickle
from calendar import monthrange
from datetime import timedelta, date as Date
from graphene import ObjectType, List, Field, String
from django.db.models import Q, F
from django.core.exceptions import ObjectDoesNotExist
from reports.models import Report
from companies.models import Company
from users.models import User, GlobalCoefficient, Bonus, Occupation, Position
from users.schema.types import BonusType
from .types import OrderType, TotalsType, MonthType, UserMonthsType, UsersMonthsType, UserSalaryInfoType, \
	GradeCoefficientType, PagedSalaryPayments, AccrualType, CompanyAccrualType, SumAvgYearType
from ..models import DayOff, Order, SalaryArchive, GradeCoefficient, CoefficientsArchive, SalaryPayment
from ..calculation import ReportClassifier, cost_hours, work_hours_in_month, get_salary_limits, get_last_salary_month, \
	flush_cache
from users.decorators import permission_required
from crm.schema.types import IntID, PagedInput
from ..managers import generate_b7_export
from synergycrm.exceptions import SngyException


def calculation_all_salary_in_month(user_id=None, company_filter=None):
	limits = get_salary_limits(get_last_salary_month())
	# Общие фильтры для получения записей для начисления ЗП
	general_filters = Q(checked_by__isnull=False) & Q(deleted=False) & Q(report_date__lte=limits[1])
	# Рабочие часы (то, что хотя бы проверено ГИПом
	work_hours = Q(record_counted=0)
	# Оценки - то, что проверено ГИПом, либо уже закрыто с новопроставленными оценками
	grades = Q(record_counted__lt=2) & Q(quality_grade__isnull=False) & Q(time_grade__isnull=False)
	# Доплата за назначение ответственным по проекту
	responsible = Q(projects__order__isnull=False) & Q(projects__order__responsible_id=F('worker')) & \
	              Q(responsible_work_paid=False) & Q(projects__order__date__lte=F('report_date')) & Q(func_role__kind='R')
	# Ночные смены, которые проверены, но не оплачены
	night_shifts = Q(checked_hr=True) & Q(night_shifts_paid=False)

	# Любая запись должна быть проверена, не удалена и попадать в зарплатный месяц,
	# а так же удовлетворять хотя бы одному из доп. условий
	filters = general_filters & (work_hours | grades | responsible | night_shifts)

	reports = Report.objects.select_related('worker', 'worker__occupation', 'place', 'process', 'sub_process', 'func_role'). \
		prefetch_related('projects', 'worker__positions')

	if user_id:
		reports = reports.filter(worker_id=user_id)

	if company_filter:
		reports = reports.filter(worker__occupation__main_company_id=company_filter)

	reports = reports.filter(filters).distinct('id')
	classifier = ReportClassifier(reports)

	# Запрашиваем выходные
	days_off = DayOff.objects.filter(date__lte=limits[1]).values('date')
	days_off = {v['date'] for v in days_off}

	# Считаем часы
	classifier.sum_hours(days_off=days_off)
	totals = classifier.totals()
	attributes = ['work_hours', 'overtime', 'home', 'welding', 'healthy_day', 'transport_office', 'night',
	              'positive_grade', 'negative_grade', 'ideal_grade', 'order', 'sick', 'work_hours_money',
	              'overtime_money', 'home_money', 'welding_money', 'healthy_day_money', 'night_money',
	              'positive_grade_money', 'negative_grade_money', 'ideal_grade_money', 'transport_money',
	              'private_car', 'duty_car', 'transport_office_money', 'order_money', 'vacation_money', 'sick_money']

	str_month = str(limits[0].year) + str(limits[0].month)
	users_data = User.objects.filter(fired=False).select_related()
	users = {}
	for u in classifier.storage.storage:
		months = {}
		for m in classifier.storage.storage[u].storage:
			m_totals = {}
			for a in attributes:
				if isinstance(getattr(classifier.storage.storage[u].storage[m].totals, a), timedelta):
					m_totals[a] = '{0:.2f}'.format(
						getattr(classifier.storage.storage[u].storage[m].totals, a).total_seconds() / 3600)
				else:
					m_totals[a] = getattr(classifier.storage.storage[u].storage[m].totals, a)
			sum_totals_month = sum([float(m_totals[t]) for t in m_totals])
			if sum_totals_month:
				months[m] = m_totals
		totals = {}
		for a in attributes:
			if isinstance(getattr(classifier.storage.storage[u].totals, a), timedelta):
				totals[a] = '{0:.2f}'.format(getattr(classifier.storage.storage[u].totals, a).total_seconds() / 3600)
			else:
				totals[a] = getattr(classifier.storage.storage[u].totals, a)
		bonus = classifier.storage.storage[u].totals.bonus
		advance = classifier.storage.storage[u].totals.advance
		salary = None
		base = None
		fraction = None
		by_hours = None
		transportation = None
		healthy = None
		coefficients = {}
		max_hour = None
		avg = None
		for u_obj in users_data:
			if u_obj.id == u:
				cost_hour = cost_hours(u_obj, str_month)['salary']
		base_cost_hour = None
		for u_obj in users_data:
			if u_obj.id == u:
				salary = u_obj.occupation.salary
				base = u_obj.occupation.base
				fraction = u_obj.occupation.fraction
				by_hours = u_obj.occupation.by_hours
				transportation = u_obj.occupation.transportation
				healthy = u_obj.healthy
				try:
					coefficients['general'] = u_obj.coefficients.general
					coefficients['welding'] = u_obj.coefficients.welding
					coefficients['experience'] = u_obj.coefficients.experience
					coefficients['etech'] = u_obj.coefficients.etech
					coefficients['schematic'] = u_obj.coefficients.schematic
					coefficients['initiative'] = u_obj.coefficients.initiative
					coefficients['discipline'] = u_obj.coefficients.discipline
					max_hour = u_obj.coefficients.max_hour
					avg = u_obj.coefficients.avg
					base_cost_hour = avg * max_hour
				except ObjectDoesNotExist:
					pass
		users[u] = (months, totals, bonus, advance, salary, base, fraction, by_hours, transportation, healthy,
		            coefficients, max_hour, avg, cost_hour, base_cost_hour)
	return dict(users=users, classifier=classifier, attributes=attributes)


# noinspection PyMethodMayBeStatic,PyUnusedLocal
class Query(ObjectType):
	all_orders = List(OrderType)
	all_salary_in_month = Field(UsersMonthsType, user_id=IntID(), date=String(required=True), company_filter=IntID())
	user_salary_info = Field(UserSalaryInfoType, date=String(required=True))
	user_salary_bonus_info = List(BonusType, date=String())
	last_salary_month = String()
	all_grade_coefficients = List(GradeCoefficientType)
	b7_export = String()
	paged_salary_payments = Field(PagedSalaryPayments, paged=PagedInput())
	accruals = List(CompanyAccrualType)
	user_salary_sum_avg_year = Field(SumAvgYearType, date=String())

	def resolve_all_salary_in_month(self, info, user_id=None, date=None, company_filter=None):
		if user_id != info.context.user.id and not info.context.user.has_perm('users.view_salary'):
			raise SngyException('Недостаточно прав')

		flush_cache()
		date = Date(int('20' + date[-2:]), int(date[:-2]), 1)
		if date > get_last_salary_month().date():
			calculation_result = calculation_all_salary_in_month(user_id, company_filter)
			users = calculation_result['users']
			classifier = calculation_result['classifier']
			attributes = calculation_result['attributes']
		else:
			users = {}
			r_totals = {}
			if user_id:
				try:
					users[user_id] = pickle.loads(SalaryArchive.objects.get(worker_id=user_id, date=date).object)
				except SalaryArchive.DoesNotExist:
					pass
			else:
				archive = SalaryArchive.objects.filter(date=date)
				users = {a.worker_id: pickle.loads(a.object) for a in archive}
				for u in users:
					for obj in users[u][1].items():
						try:
							r_totals[obj[0]] += float(obj[1])
						except KeyError:
							r_totals[obj[0]] = 0
							r_totals[obj[0]] += float(obj[1])
				for k in r_totals:
					r_totals[k] = '{0:.2f}'.format(r_totals[k])

				r_totals = TotalsType(**r_totals)

		result = []
		db_users = {u.id: u for u in User.objects.select_related('occupation')}
		for u in users:
			user = db_users[u]
			months = []
			for m in users[u][0]:
				totals = TotalsType(**users[u][0][m])
				months.append(MonthType(month=m, totals=totals))
			totals = TotalsType(**users[u][1])
			bonus = users[u][2]
			advance = users[u][3]
			result.append(UserMonthsType(user=user, months=months, totals=totals, bonus=bonus, advance=advance))

		if date > get_last_salary_month().date():
			r_totals = {}
			for a in attributes:
				if isinstance(getattr(classifier.storage.totals, a), timedelta):
					r_totals[a] = '{0:.2f}'.format(getattr(classifier.storage.totals, a).total_seconds() / 3600)
				else:
					r_totals[a] = getattr(classifier.storage.totals, a)
			r_totals = TotalsType(**r_totals)

		return UsersMonthsType(users=result, totals=r_totals)

	def resolve_user_salary_info(self, info, date):
		fields = ['general', 'welding', 'experience', 'etech', 'schematic', 'initiative', 'discipline']
		date = Date(int('20' + date[-2:]), int(date[:-2]), 1)
		if date > get_last_salary_month().date():
			date = get_salary_limits(get_last_salary_month())[1]
			str_month = str(date.year) + str(date.month)
			work_hours = work_hours_in_month(str_month)
			costs = cost_hours(info.context.user, str_month)
			salary = info.context.user.occupation.salary
			base = info.context.user.occupation.base
			advance = info.context.user.occupation.advance
			if not salary:
				coefficients = {obj.name: obj.value for obj in GlobalCoefficient.objects.all() if obj.name in fields}
				my_coefficients = info.context.user.coefficients
				for f in fields:
					coefficients['my_' + f] = getattr(my_coefficients, f)
				base_cost_hour = my_coefficients.avg * my_coefficients.max_hour
				return UserSalaryInfoType(salary=salary, base=base, cost_hour=costs['salary'], advance=advance,
				                          work_hours_in_month=work_hours, avg=my_coefficients.avg,
				                          base_cost_hour=base_cost_hour, **coefficients)
			return UserSalaryInfoType(salary=salary, base=base, cost_hour=costs['salary'], advance=advance,
			                          work_hours_in_month=work_hours)
		else:
			user_data = pickle.loads(SalaryArchive.objects.get(date=date, worker=info.context.user).object)
			if len(user_data) > 4:
				salary = user_data[4]
				base = user_data[5]
				advance = user_data[3]
				cost_hour = user_data[13]
				base_cost_hour = user_data[14]
				str_month = str(date.year) + str(date.month)
				work_hours = work_hours_in_month(str_month)
				my_coefficients = user_data[10]
				if my_coefficients:
					coefficients = pickle.loads(CoefficientsArchive.objects.get(date=date).global_coefficients)
					coefficients = {c['name']: c['value'] for c in coefficients if c['name'] in fields}
					for f in fields:
						coefficients['my_' + f] = my_coefficients[f]
					avg = user_data[12]
					return UserSalaryInfoType(salary=salary, base=base, advance=advance, cost_hour=cost_hour,
					                          base_cost_hour=base_cost_hour, work_hours_in_month=work_hours, avg=avg,
					                          **coefficients)
				return UserSalaryInfoType(salary=salary, base=base, advance=advance, cost_hour=cost_hour,
					                          base_cost_hour=base_cost_hour, work_hours_in_month=work_hours)
			else:
				return UserSalaryInfoType()

	def resolve_user_salary_bonus_info(self, info, date=None):
		if date:
			last_day = monthrange(year=int('20' + date[-2:]), month=int(date[:-2]))[1]
			date = Date(year=int('20' + date[-2:]), month=int(date[:-2]), day=last_day)
		bonuses = Bonus.objects.filter(user=info.context.user, month=date)
		return bonuses

	def resolve_user_salary_sum_avg_year(self, info, date):
		end = Date.today()
		year = int('20' + date[-2:])
		if year < end.year:
			end = end.replace(year=year, month=12, day=31)
		begin = end.replace(day=1, month=1)
		sum_year = 0
		archive = SalaryArchive.objects.filter(worker=info.context.user, date__range=(begin, end))
		for d in archive:
			data = pickle.loads(d.object)
			totals = data[1]
			sum_year += sum(totals[mn] for mn in totals if mn.endswith('_money') and mn not in ('ideal_grade_money', 'negative_grade_money'))
			sum_year -= totals['negative_grade_money']
			sum_year += data[2] # бонус
			sum_year += totals['private_car'] + totals['duty_car']
		avg_year = sum_year / end.month
		return SumAvgYearType(sum_year=sum_year, avg_year=avg_year)

	@permission_required('users.view_order')
	def resolve_all_orders(self, info):
		return Order.objects.all()

	def resolve_last_salary_month(self, info):
		date = get_salary_limits(get_last_salary_month())[1]
		return str(date.year) + str(date.month)

	def resolve_all_grade_coefficients(self, info):
		return GradeCoefficient.objects.all()

	@permission_required('salary.generate_b7_export')
	def resolve_b7_export(self, info):
		return generate_b7_export()

	@permission_required('salary.can_view_salarypayment')
	def resolve_paged_salary_payments(self, info, paged, **kwargs):
		paged = {k: v for k, v in paged.items() if v is not None}
		result = SalaryPayment.objects.list_paged_payments(**kwargs, **paged)
		keys = ('salary_payments', 'total_count')
		return PagedSalaryPayments(**dict(zip(keys, result)))

	@permission_required('users.view_salary')
	def resolve_accruals(self, info):
		users = calculation_all_salary_in_month()['users']

		companies = {c.id: [] for c in Company.objects.all()}
		companies['cash'] = []

		user_objects = {u.id: u for u in User.objects.all()}

		for id in users:
			advance = users[id][3]
			bonus = users[id][2]
			# users[id][1] - totals по пользователю
			main_part = sum(users[id][1][m] for m in users[id][1] if m.endswith('_money') and m not in
			                ('ideal_grade_money', 'negative_grade_money', 'vacation_money')) + bonus - advance - \
			            users[id][1]['negative_grade_money']
			auto = users[id][1]['private_car'] + users[id][1]['duty_car']
			other = users[id][1]['vacation_money']

			salary_payments = SalaryPayment.objects.filter(user_id=id, company__minimize_salary=True)
			for sp in salary_payments:
				if sp.company == user_objects[id].occupation.main_company:
					main_part = main_part - sp.amount
				else:
					main_part = main_part - (sp.advance + sp.amount)
				if main_part < 0:
					main_part_result = main_part
				else:
					main_part_result = sp.amount
				companies[sp.company_id].append(AccrualType(user=user_objects[id].short_name, bonus=0,
				                                                advance=sp.advance, main_part=main_part_result))

			positions = Position.objects.filter(user=id, company__minimize_salary=False)
			if positions:
				companies[positions[0].company_id].append(AccrualType(user=user_objects[id].short_name,
							bonus=bonus, advance=advance, main_part=main_part))
			else:
				if not auto and not other and main_part < 0:
					pass
				else:
					companies['cash'].append(AccrualType(user=user_objects[id].short_name, auto=auto, other=other,
				                                      bonus=bonus, advance=advance, main_part=main_part))

		result = []

		for c_id in companies:
			companies[c_id] = sorted(companies[c_id], key=lambda obj: obj.user) # Сортировка
			if c_id != 'cash':
				result.append(CompanyAccrualType(id=c_id, name=Company.objects.get(id=c_id).client.name, accruals=companies[c_id]))
			else:
				result.append(CompanyAccrualType(id=c_id, name='Наличными', accruals=companies[c_id]))

		return result

