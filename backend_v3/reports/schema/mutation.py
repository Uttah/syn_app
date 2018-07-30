from datetime import datetime, timedelta
import graphene
from django.utils import timezone
from graphene.types.datetime import Date, Time
from reports.models import Report, Process, SubProcess, FuncRole, ProjectState, Place
from projects.models import Project
from crm.schema.mutation import SngyMutation
from crm.schema.types import IntID
from .types import ReportType
from synergycrm.exceptions import SngyException

# Список внешних ключей (имен полей).
keys = ['user_added', 'worker', 'func_role', 'place', 'project', 'process', 'sub_process', 'tasks']


# Проверка "kwargs" для создания и обновления
def check_kwargs(kwargs, info):
	# Проверка, дата "С" не должна быть больше даты "По"
	if kwargs.get('time_from') and kwargs.get('time_to'):
		if kwargs['time_from'] > kwargs['time_to']:
			raise SngyException('Время "С" больше времени "По"')
	else:
		kwargs['time_from'] = None
		kwargs['time_to'] = None

	# Проверка, выбранная дата не должна быть больше сегодняшней.
	if kwargs['report_date'] > datetime.now().date():
		raise SngyException('Дата отчета находится в будущем')

	# Очищаем флаг ночной смены если процесс не соответствует
	if kwargs.get('process'):
		process_obj = Process.objects.get(id=kwargs['process'])
		if process_obj.kind != 'N':
			kwargs['night_shift'] = False

	place_obj = Place.objects.get(id=kwargs['place'])

	# Очищаем неиспользуемые поля, если нет работы.
	if place_obj.kind == 'N':
		kwargs['process'] = None
		kwargs['sub_process'] = None
		kwargs['model'] = None
		kwargs['task'] = None
		kwargs['vc_project'] = None
		kwargs['vc_digits'] = None
		kwargs['vc_digits_minor'] = None
		kwargs['distance'] = None
		kwargs['car'] = None
		kwargs['gas'] = None
		kwargs['where_from'] = None
		kwargs['where_to'] = None
		kwargs['quality_grade'] = None
		kwargs['time_grade'] = None
		kwargs['comment'] = None

	# Если работа есть.
	sub_process_obj = None
	if place_obj.kind != 'N' and kwargs.get('sub_process'):
		sub_process_obj = SubProcess.objects.get(id=kwargs['sub_process'])

		# Очищение неиспользуемых полей, т.е. полей, которые должны быть "null". Зависит от выбранного подпроцесса.
		if sub_process_obj.kind == 'D':
			kwargs['model'] = None
			kwargs['task'] = None
			kwargs['vc_project'] = None
			kwargs['vc_digits'] = None
			kwargs['vc_digits_minor'] = None

		if sub_process_obj.kind != 'D':
			kwargs['distance'] = None
			kwargs['car'] = None
			kwargs['gas'] = None
			kwargs['where_from'] = None
			kwargs['where_to'] = None

	# Если работа на объекте - вносим затраты > 50
	if place_obj.kind == 'C':
		money_spent = kwargs.get('money_spent', 0)
		# Сначала проверяем money_spent на None, так как None нельзя сравнивать с Int
		if money_spent:
			if money_spent < 50:
				kwargs['money_spent'] = None
	else:
		kwargs['money_spent'] = None

	projects = kwargs['projects']
	filter_projects = Project.objects.filter(id__in=projects).values('id', 'gip')
	gip = set([p['gip'] for p in filter_projects])

	# Переменная "gip" должна содержать множество с одним элементом - id ГИПа.
	# Если множество содержит больше одного элемента, значит проекты выбраны от разных ГИПов.
	if len(gip) > 1:
		raise SngyException('Указанные проекты имеют разных ГИПов')
	gip = gip.pop()

	func_role_obj = FuncRole.objects.get(id=kwargs['func_role'])
	user = info.context.user
	user_is_gip = gip == user.id or user.has_perm('reports.global_manage')
	if user_is_gip:
		# Очищаем оценки, если залогиненный пользователь является ГИПом и при этом является исполнителем.
		if user.id == kwargs['worker']:
			kwargs['quality_grade'] = None
			kwargs['time_grade'] = None
			kwargs['comment'] = None
	else:
		# Очищаем оценки, если тип функциональной роли не "Исполнитель" и при этом
		# залогиненный пользователь является исполнителем.
		if not (func_role_obj.kind == 'W' and user.id != kwargs['worker']):
			kwargs['quality_grade'] = None
			kwargs['time_grade'] = None
			kwargs['comment'] = None

	if sub_process_obj and sub_process_obj.kind == 'D':
		reports_day = Report.objects.filter(worker_id=kwargs['worker'], report_date=kwargs['report_date'], deleted=False,
		                                    sub_process__kind='D')
		if kwargs.get('id'):
			reports_day = reports_day.exclude(id=kwargs['id'])
		times_spent = [timedelta(hours=r.time_spent.hour, minutes=r.time_spent.minute) for r in reports_day]
		time_spent = sum(times_spent, timedelta(0))
		time_spent = time_spent + timedelta(hours=kwargs['time_spent'].hour, minutes=kwargs['time_spent'].minute)
		if time_spent > timedelta(hours=8):
			raise SngyException('Количество часов вождения за {:%d.%m.%Y} превысило 8.'.format(kwargs['report_date']))

	reports_day = Report.objects.filter(worker_id=kwargs['worker'], report_date=kwargs['report_date'], deleted=False)
	if kwargs.get('id'):
		reports_day = reports_day.exclude(id=kwargs.get('id'))
	times_spent = [timedelta(hours=r.time_spent.hour, minutes=r.time_spent.minute) for r in reports_day]
	time_spent = sum(times_spent, timedelta(0))
	time_spent = time_spent + timedelta(hours=kwargs['time_spent'].hour, minutes=kwargs['time_spent'].minute)
	if time_spent.days:
		raise SngyException('Количество часов за {:%d.%m.%Y} превысило 24 часа.'.format(kwargs['report_date']))

	return kwargs


# noinspection PyUnusedLocal
class CreateReport(SngyMutation):
	report = graphene.Field(ReportType)

	class Input:
		worker = IntID(required=True)
		report_date = Date(required=True)
		func_role = IntID(required=True)
		projects = graphene.List(IntID, required=True)
		process = IntID()
		sub_process = IntID()
		task = graphene.String()
		time_spent = Time(required=True)
		time_from = Time()
		time_to = Time()
		place = IntID(required=True)
		distance = graphene.Float()
		car = graphene.String()
		gas = graphene.String()
		where_from = graphene.String()
		where_to = graphene.String()
		money_spent = graphene.Int()
		vc_project = graphene.Int()
		vc_digits = graphene.Int()
		vc_digits_minor = graphene.Int()
		model = graphene.String()
		night_shift = graphene.Boolean()
		quality_grade = graphene.Int()
		time_grade = graphene.Int()
		comment = graphene.String()
		tasks = IntID()

	@staticmethod
	def mutate_and_get_payload(root, info, **kwargs):
		kwargs = check_kwargs(kwargs, info)
		projects = kwargs['projects']
		del kwargs['projects']
		report = Report()
		report.user_added = info.context.user

		# Если отчет добавляет ГИП, тогда отчет автоматически становится проверенным.
		if Project.objects.get(id=projects[0]).gip == info.context.user:
			report.checked_by = info.context.user
			report.time_checked = timezone.now()

		# Добавляем к полям модели полученные значения.
		# "keys" - это глобальный список внешних ключей (имен полей).
		[setattr(report, f + '_id' if f in keys else f, kwargs.get(f)) for f in kwargs.keys()]
		report.save()
		projects_states = Project.objects.filter(id__in=projects).values('id', 'state_id')
		for ps in projects_states:
			ProjectState.objects.create(project_id=ps['id'], state_id=ps['state_id'], report_id=report.id)
		return CreateReport(report=report)


# noinspection PyUnusedLocal
class DeleteReport(SngyMutation):
	result = graphene.Boolean()

	class Input:
		id = graphene.Int(required=True)
		deleted = graphene.Boolean()

	@staticmethod
	def mutate_and_get_payload(root, info, **kwargs):
		try:
			report = Report.objects.get(id=kwargs.get('id'))
			user = info.context.user

			# Проверка, если залогиненный пользователь не является создателем отчета и при этом не является ГИПом
			# и не имеет прав на общее редактирование отчетов.
			user_is_not_gip = report.projects.all()[0].gip != user and not user.has_perm('reports.global_manage')
			if report.user_added != user and user_is_not_gip:
				raise SngyException('Этот отчет вам не принадлежит')

			# Проверка, если отчет проверен или удален и при этом залогиненный пользователь не является ГИПом.
			if (report.checked_by or report.deleted) and user_is_not_gip:
				raise SngyException('Отчет уже проверен или удален')

			# Если "deleted" существует, тогда просто помечаем отчет как удаленный.
			if kwargs.get('deleted'):
				report.deleted = True
				report.save()

			# Если залогиненный пользователь добавил отчет, тогда удаляем его.
			elif report.user_added == user and report.checked_by is None:
				report.delete()

			# Если залогиненный пользователь добавил отчет, отчет проверен и при этом, залогиненный пользователь является
			# гипом проекта, тогда помечаем его как удаленный.
			elif report.user_added == user and report.checked_by and not user_is_not_gip:
				report.deleted = True
				report.save()
			return DeleteReport(result=True)
		except Report.DoesNotExist:
			return DeleteReport(result=False)


# noinspection PyUnusedLocal
class UpdateReport(SngyMutation):
	report = graphene.Field(ReportType)

	class Input:
		id = IntID(required=True)
		worker = IntID(required=True)
		report_date = Date(required=True)
		func_role = IntID(required=True)
		projects = graphene.List(IntID, required=True)
		process = IntID()
		sub_process = IntID()
		tasks = IntID()
		task = graphene.String()
		time_spent = Time(required=True)
		time_from = Time()
		time_to = Time()
		place = IntID(required=True)
		distance = graphene.Float()
		car = graphene.String()
		gas = graphene.String()
		where_from = graphene.String()
		where_to = graphene.String()
		money_spent = graphene.Int()
		vc_project = graphene.Int()
		vc_digits = graphene.Int()
		vc_digits_minor = graphene.Int()
		model = graphene.String()
		night_shift = graphene.Boolean()
		quality_grade = graphene.Int()
		time_grade = graphene.Int()
		comment = graphene.String()

	# Эта мутация очень похожа на мутацию создания отчета. Смотри комментарии у нее.
	@staticmethod
	def mutate_and_get_payload(root, info, **kwargs):
		kwargs = check_kwargs(kwargs, info)
		projects = kwargs.pop('projects')
		report = Report.objects.select_related('user_added').prefetch_related('projects__gip').get(id=kwargs.get('id'))

		# При изменении набора проектов необходимо сбрасывать проверку записи
		current_projects = tuple(report.projects.all())
		projects_reduced = list(project.id for project in current_projects)
		if projects_reduced != projects:
			# Если ГИПы проектов разные, то "распроверить" запись
			if current_projects[0].gip_id != Project.objects.get(id=projects[0]).gip_id:
				report.checked_by = None
				report.time_checked = None

		user = info.context.user
		user_is_gip = current_projects[0].gip == user
		cant_change_report = not user_is_gip and not user.has_perm('reports.global_manage')
		# Не изменять после закрытия месяца
		change_after_closed = not user.has_perm('reports.change_fields_after_month')

		if report.user_added != user and cant_change_report:
			raise SngyException('Этот отчет вам не принадлежит')
		if (report.checked_by or report.deleted) and cant_change_report:
			raise SngyException('Отчет уже проверен или удален')

		# После учета всей записи в зарплате редактирование невозможно
		if report.record_counted == 2 and not change_after_closed:
			allowed_attributes = ('process', 'sub_process', 'func_role')
			kwargs = {k: v for k, v in kwargs.items() if k in allowed_attributes}
		elif report.record_counted == 2:
			raise SngyException('Отчет уже учтен в расчете з/п')

		# После учета в зарплате основной части записи разрешаем изменение только атрибутов оценки
		if report.record_counted == 1 and not change_after_closed:
			allowed_attributes = ('time_grade', 'quality_grade', 'comment', 'process', 'sub_process', 'func_role')
			kwargs = {k: v for k, v in kwargs.items() if k in allowed_attributes}
		elif report.record_counted == 1:
			allowed_attributes = ('time_grade', 'quality_grade', 'comment')
			kwargs = {k: v for k, v in kwargs.items() if k in allowed_attributes}

		[setattr(report, f + '_id' if f in keys else f, kwargs.get(f, getattr(report, f))) for f in kwargs.keys()]
		report.projects.clear()
		# Изменяем время если отчет изменен вносившим, в остальных случаях - оставляем оригинальную дату
		if report.user_added == user and not user_is_gip:
			report.time_edited = timezone.now()
		report.save()
		report.refresh_from_db()
		projects_states = Project.objects.filter(id__in=projects).values('id', 'state_id')
		for ps in projects_states:
			ProjectState.objects.create(project_id=ps['id'], state_id=ps['state_id'], report_id=report.id)
		return UpdateReport(report=report)


# noinspection PyUnusedLocal
class ConfirmReport(SngyMutation):
	report = graphene.Field(ReportType)

	class Input:
		id = graphene.Int(required=True)

	@staticmethod
	def mutate_and_get_payload(root, info, **kwargs):
		try:
			report = Report.objects.get(id=kwargs.get('id'))

			# Если залогиненный пользователь это не ГИП.
			user = info.context.user
			if report.projects.all()[0].gip != user and not user.has_perm('reports.global_manage'):
				raise SngyException('Только ГИП может подтверждать отчеты')

			# Если отчет уже проверен или удален.
			if report.checked_by or report.deleted:
				raise SngyException('Отчет уже проверен или удален')
			report.checked_by = user
			report.time_checked = timezone.now()
			report.save()
			return ConfirmReport(report=report)
		except Report.DoesNotExist:
			return ConfirmReport(report=None)


# noinspection PyUnusedLocal
class RestoreReport(SngyMutation):
	result = graphene.Boolean()

	class Input:
		id = graphene.Int(required=True)

	@staticmethod
	def mutate_and_get_payload(root, info, **kwargs):
		try:
			report = Report.objects.get(id=kwargs.get('id'))

			# Если залогиненный пользователь это не ГИП.
			user = info.context.user
			if report.projects.all()[0].gip != user and not user.has_perm('reports.global_manage'):
				raise SngyException('Только ГИП может восстанавливать отчеты')
			report.deleted = False
			report.save()
			return RestoreReport(result=True)
		except Report.DoesNotExist:
			return RestoreReport(result=False)


class Mutation(graphene.ObjectType):
	create_report = CreateReport.Field()
	delete_report = DeleteReport.Field()
	update_report = UpdateReport.Field()
	confirm_report = ConfirmReport.Field()
	restore_report = RestoreReport.Field()
