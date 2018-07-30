from django.db import models
from .managers import SalaryPaymentManager, DayOffManager


class GradeCoefficient(models.Model):
	quality = models.IntegerField('Качество')
	time = models.IntegerField('Срок')
	coefficient = models.FloatField('Коэффициент')

	class Meta:
		verbose_name = 'Оценочный коэффициент'
		verbose_name_plural = 'Оценочные коэффициенты'

	def __str__(self):
		return '%s %s' % (self.quality, self.time)


class DayOff(models.Model):
	date = models.DateField('Дата', unique=True)
	manual = models.BooleanField('Внесен вручную', default=False)

	objects = DayOffManager()

	class Meta:
		verbose_name = 'Выходной день'
		verbose_name_plural = 'Выходные дни'
		ordering = ['date']

	def __str__(self):
		return str(self.date)


class Order(models.Model):
	project = models.ForeignKey('projects.Project', verbose_name='Проект')
	responsible = models.ForeignKey('users.User', verbose_name='Ответственный')
	date = models.DateField('Дата')

	class Meta:
		verbose_name = 'Ответственный'
		verbose_name_plural = 'Ответственные'
		permissions = (
			('view_order', 'Может просматривать ответственных'),
		)

	def __str__(self):
		return str(self.project.number)


class SalaryArchive(models.Model):
	date = models.DateField('Дата')
	worker = models.ForeignKey('users.User', verbose_name='Сотрудник')
	object = models.BinaryField('Объект')

	class Meta:
		permissions = (
			('generate_b7_export', 'Может экспортировать в Б7'),
		)


class CoefficientsArchive(models.Model):
	date = models.DateField('Дата')
	global_coefficients = models.BinaryField('Объект глобальных коэффициентов')
	grade_coefficients = models.BinaryField('Объект оценочных коэффициентов')


class SalaryPayment(models.Model):
	user = models.ForeignKey('users.User', verbose_name='Сотрудник')
	amount = models.PositiveIntegerField('Сумма выплаты')
	advance = models.PositiveIntegerField('Аванс')
	company = models.ForeignKey('companies.Company', verbose_name='Компания')

	objects = SalaryPaymentManager()

	class Meta:
		verbose_name = 'Выплата'
		verbose_name_plural = 'Выплаты'
		ordering = ['user__last_name', 'user__first_name', 'company__short_name']
		permissions = (
			('can_view_salarypayment', 'Может просматривать выплаты по компаниям'),
		)

	def __str__(self):
		return self.user.short_name
