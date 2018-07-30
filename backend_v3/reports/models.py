from django.db import models
from django.utils import timezone
from .managers import ReportManager
from synergycrm.sngy_model import SngyModel


class FuncRole(models.Model):
	KIND_CHOICES = (
		('W', 'Исполнитель'),
		('R', 'Ответственный')
	)
	name = models.CharField('Название', max_length=100)
	kind = models.CharField('Тип', max_length=1, choices=KIND_CHOICES, null=True, blank=True)
	positions = models.ManyToManyField('users.Position', verbose_name='Должности')
	deleted = models.BooleanField('Удален', default=False)

	class Meta:
		verbose_name = 'Функциональная роль'
		verbose_name_plural = 'Функциональные роли'
		ordering = ['name']

	def __str__(self):
		return self.name


class Process(models.Model):
	KIND_CHOICES = (
		('N', 'Ночные смены'),
	)

	name = models.CharField('Название', max_length=100)
	kind = models.CharField('Тип', max_length=1, choices=KIND_CHOICES, null=True, blank=True)
	deleted = models.BooleanField('Удален', default=False)

	class Meta:
		verbose_name = 'Процесс'
		verbose_name_plural = 'Процессы'
		ordering = ['name']

	def __str__(self):
		return self.name


class SubProcess(models.Model):
	KIND_CHOICES = (
		('D', 'Вождение'),
		('R', 'Проезд пассажиром'),
		('A', 'Сборка'),
		('P', 'Проектирование'),
		('W', 'Работа на объекте')
	)

	process = models.ForeignKey("reports.Process", verbose_name='Процесс')
	name = models.CharField('Название', max_length=100)
	deleted = models.BooleanField('Удален', default=False)
	kind = models.CharField('Тип', max_length=1, choices=KIND_CHOICES, null=True, blank=True)

	class Meta:
		verbose_name = 'Подпроцесс'
		verbose_name_plural = 'Подпроцессы'
		ordering = ['name']

	def __str__(self):
		return self.name


class Place(models.Model):
	KIND_CHOICES = (
		('C', 'По городу'),
		('N', 'Нет работы'),
		('O', 'Волгоградский офис')
	)

	name = models.CharField('Места', max_length=150)
	kind = models.CharField('Тип', max_length=1, choices=KIND_CHOICES, null=True, blank=True)
	deleted = models.BooleanField('Удален', default=False)

	def __str__(self):
		return self.name

	class Meta:
		verbose_name = 'Место'
		verbose_name_plural = 'Места'
		ordering = ['name']


class Report(SngyModel):
	DUTY = 'D'
	PRIVATE = 'P'
	CAR_CHOICES = (
		(DUTY, 'Служебный'),
		(PRIVATE, 'Личный')
	)
	GAS_CHOICES = (
		(DUTY, 'Служебный'),
		(PRIVATE, 'Личный')
	)

	objects = ReportManager()

	user_added = models.ForeignKey('users.User', related_name='report_user_added', verbose_name='Добавил')
	time_edited = models.DateTimeField('Время изменения', default=timezone.now)
	worker = models.ForeignKey('users.User', related_name='report_worker', verbose_name='Исполнитель')
	report_date = models.DateField('Дата')
	func_role = models.ForeignKey('reports.FuncRole', verbose_name='Функциональная роль')
	projects = models.ManyToManyField('projects.Project', through='ProjectState')
	process = models.ForeignKey('reports.Process', verbose_name='Процесс', null=True, blank=True)
	sub_process = models.ForeignKey('reports.SubProcess', verbose_name='Подпроцесс', null=True, blank=True)
	tasks = models.ForeignKey('tasks.Task', null=True, related_name='tasks', verbose_name='Задачи')
	task = models.TextField('Задача', null=True, blank=True)
	time_spent = models.TimeField('Затраченное время')
	time_from = models.TimeField('С', null=True, blank=True)
	time_to = models.TimeField('По', null=True, blank=True)
	place = models.ForeignKey('reports.Place', related_name='report_place', verbose_name='Место')
	distance = models.FloatField('Расстояние', null=True, blank=True)
	car = models.CharField('Автомобиль', max_length=1, choices=CAR_CHOICES, null=True, blank=True)
	gas = models.CharField('Бензин', max_length=1, choices=GAS_CHOICES, null=True, blank=True)
	where_from = models.CharField('Адрес отправления', max_length=150, null=True, blank=True)
	where_to = models.CharField('Адрес назначения', max_length=150, null=True, blank=True)
	money_spent = models.PositiveSmallIntegerField('Денег затрачено', null=True, blank=True)
	checked_by = models.ForeignKey('users.User', null=True, blank=True, verbose_name='Проверил')
	time_checked = models.DateTimeField('Время проверки', null=True, blank=True)
	quality_grade = models.PositiveSmallIntegerField('Оценка качества', null=True, blank=True)
	time_grade = models.PositiveSmallIntegerField('Оценка срока', null=True, blank=True)
	vc_project = models.PositiveSmallIntegerField(null=True, blank=True)
	vc_digits = models.PositiveSmallIntegerField(null=True, blank=True)
	vc_digits_minor = models.PositiveSmallIntegerField(null=True, blank=True)
	model = models.CharField('Модель', max_length=255, null=True, blank=True)
	comment = models.TextField('Комментарий', null=True, blank=True)
	exported = models.PositiveSmallIntegerField('Экспортирован', default=0)
	record_counted = models.PositiveSmallIntegerField(default=0)
	day_off_call = models.BooleanField(default=False)
	night_shift = models.BooleanField(default=False)
	responsible_work_paid = models.BooleanField(default=False)
	night_shifts_paid = models.BooleanField(default=False)
	checked_hr = models.BooleanField('Проверено Галиной', default=False)
	deleted = models.BooleanField('Удален', default=False)

	class Meta:
		verbose_name = 'Отчет'
		verbose_name_plural = 'Отчеты'
		permissions = (
			('global_manage', 'Управление всеми отчетами'),
			('change_fields_after_month', 'Изменение записи табеля после закрытия месяца')
		)

	def __str__(self):
		return str(self.report_date)


class ProjectState(models.Model):
	project = models.ForeignKey('projects.Project', on_delete=models.PROTECT)
	state = models.ForeignKey('projects.State')
	report = models.ForeignKey('reports.Report')
