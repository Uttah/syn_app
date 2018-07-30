from django.template.defaultfilters import date as get_date
from salary.calculation import Classifier, SalaryArchive, get_last_salary_month, cost_hours
from salary.models import CoefficientsArchive
from graphene.utils.str_converters import to_snake_case
from users.models import GlobalCoefficient
import inspect
import sys
import pickle

salary_cache = {}

# def get_worker_salary(worker_id, month, hours):
# 	class Object:
# 		pass
#
# 	last_salary = get_last_salary_month()
# 	mnth = str(month.year) + str(month.month)
# 	if last_salary.date() < month:
# 		worker = Object()
# 		setattr(worker, 'id', worker_id)
# 		cost = cost_hours(worker, mnth)['salary']
# 	else:
# 		global salary_cache
# 		key = (worker_id, month)
# 		if key not in salary_cache:
# 			archive = SalaryArchive.objects.all()
# 			for a in archive:
# 				cache_key = (a.worker_id, a.date)
# 				salary_cache[cache_key] = a.object
# 		if key not in salary_cache:
# 			return 0
# 		obj = pickle.loads(salary_cache[key])[0][mnth]
# 		work_hours = float(obj['work_hours'])
# 		if work_hours == 0:
# 			overtime = float(obj['overtime'])
# 			if overtime == 0:
# 				return 0
# 			else:
# 				cost = float(obj['overtime_money']) / overtime
# 		else:
# 			cost = float(obj['work_hours_money']) / work_hours
# 	return hours * cost


hour_prime_cost_cache = {}


def get_worker_salary(worker_id, month, hours):
	global hour_prime_cost_cache
	last_salary = get_last_salary_month()
	if last_salary.date() < month:
		if hour_prime_cost_cache.get(month):
			hour_prime_cost = hour_prime_cost_cache[month]
		else:
			try:
				hour_prime_cost = GlobalCoefficient.objects.get(name='hour_prime_cost').value
			except GlobalCoefficient.DoesNotExist:
				hour_prime_cost = 450
			hour_prime_cost_cache[month] = hour_prime_cost
	else:
		if hour_prime_cost_cache.get(month):
			hour_prime_cost = hour_prime_cost_cache[month]
		else:
			try:
				global_coefficients = pickle.loads(CoefficientsArchive.objects.get(date=month).global_coefficients)
				hour_prime_cost = None
				for d in global_coefficients:
					if d['name'] == 'hour_prime_cost':
						hour_prime_cost = d['value']
				if not hour_prime_cost:
					hour_prime_cost = 450
			except CoefficientsArchive.DoesNotExist:
				hour_prime_cost = 450
			hour_prime_cost_cache[month] = hour_prime_cost
	return hours * hour_prime_cost


class NodeStats:
	def __init__(self, **kwargs):
		self.hours = kwargs.get('hours', 0)
		self.money = kwargs.get('money', 0)

	def __add__(self, other):
		return NodeStats(hours=self.hours + other.hours, money=self.money + other.money)


class RootClassifier:
	def __init__(self, storage_class):
		self.storage = storage_class()

	def append(self, value_list):
		for val in value_list:
			self.storage.append(val)

	def get_totals(self):
		return self.storage.get_totals()


class CostCalculator:
	def __init__(self):
		self.storage = list()

	def append(self, value):
		self.storage.append(value)

	def get_totals(self):
		hours = 0
		money = 0
		for value in self.storage:
			money += get_worker_salary(value['worker_id'], value['mnth'], value['hours'])
			hours += value['hours']
		return NodeStats(hours=hours, money=money)


class MonthClassifier(Classifier):
	def __init__(self):
		super().__init__(lambda item: item['mnth'], CostCalculator, NodeStats)


class BaseDateClassifier(Classifier):
	def __init__(self, key_func, underlying_type, **kwargs):
		super().__init__(lambda item: item['mnth'], underlying_type, NodeStats)

	def get_node_name(self, date):
		return get_date(date, 'F Y')


# Классификатор с возможностью кеширования имен для возвращаемых объектов по их id
class CachedClassifier(Classifier):
	name_cache = {}

	def __init__(self, *args, cache_name=None, cache_init_func=None):
		super().__init__(*args, totals_type=NodeStats)
		# Если кеш с cache_name не существует, то создаем его и вызываем cache_init_func для его заполнения
		if cache_name not in CachedClassifier.name_cache and cache_init_func:
			cache = {}
			CachedClassifier.name_cache[cache_name] = cache
			cache_init_func(cache)
		self.cache = CachedClassifier.name_cache.get(cache_name, None)

	def get_node_name(self, entity_id):
		return self.cache[entity_id]


def worker_cache_init(cache):
	from users.models import User
	objects = User.objects.all()
	for user in objects:
		cache[user.id] = user.short_name


def project_cache_init(cache):
	from .models import Project
	objects = Project.objects.all()
	for project in objects:
		cache[project.id] = str(project)


def process_cache_init(cache):
	from reports.models import Process
	objects = Process.objects.all()
	for process in objects:
		cache[process.id] = process.name
	cache[None] = 'Нет процесса'


def sub_process_cache_init(cache):
	from reports.models import SubProcess
	objects = SubProcess.objects.select_related('process').all()
	for sub_process in objects:
		cache[sub_process.id] = '{} - {}'.format(sub_process.process.name, sub_process.name)
	cache[None] = 'Нет подпроцесса'


def func_role_cache_init(cache):
	from reports.models import FuncRole
	objects = FuncRole.objects.all()
	for func_role in objects:
		cache[func_role.id] = func_role.name


def place_cache_init(cache):
	from reports.models import Place
	objects = Place.objects.all()
	for place in objects:
		cache[place.id] = place.name


def project_state_cache_init(cache):
	from projects.models import State
	objects = State.objects.all()
	for state in objects:
		cache[state.id] = state.name


def get_class_hierarchy(group_list):
	# Фабрика классов-классификаторов
	def ClassFactory(name, *args, **kwargs):
		base = kwargs.pop('base', CachedClassifier)

		def __init__(self):
			base.__init__(self, *args, **kwargs)

		return type(name, (base,), {'__init__': __init__})

	# Собираем все функции в этом модуле чтобы выбрать нужную для инициализации кеша имен узлов
	func_set = {name: obj for name, obj in inspect.getmembers(sys.modules[__name__]) if inspect.isfunction(obj)}
	func_set = {name.replace('_cache_init', ''): obj for name, obj in func_set.items() if name.endswith('_cache_init')}
	# Собираем классы в этом модуле, чтобы использовать кастомные классификаторы если они нужны
	class_set = {name: obj for name, obj in inspect.getmembers(sys.modules[__name__]) if inspect.isclass(obj)}
	class_set = {name.replace('Base', ''): obj for name, obj in class_set.items() if name.endswith('Classifier')}

	# Создаем классы динамически, начиная с MonthClassifier и в обратном порядке по group_list
	last_class = MonthClassifier
	for group in group_list[::-1]:
		group_name = group[0]
		class_name = group_name[0:1].capitalize() + group_name[1:] + 'Classifier'
		cache_name = to_snake_case(group_name)
		cache_init_func = func_set.get(cache_name, None)
		group_key = group[1]
		kwargs = {
			'cache_name': cache_name,
			'cache_init_func': cache_init_func,
		}
		if class_name in class_set:
			kwargs['base'] = class_set[class_name]
		last_class = ClassFactory(class_name, lambda item, _group=group_key: item[_group], last_class, **kwargs)

	return RootClassifier(last_class)
