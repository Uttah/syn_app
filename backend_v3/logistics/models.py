from django.db import models
from .managers import LogisticsRequestManager, TransferRequestManager, LogisticsRequestPositionManager
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class LogisticsRequest(models.Model):
	who_requested = models.ForeignKey('users.User', verbose_name="Кто потребовал")
	when_requested = models.DateField('Когда потребовал')
	deadline = models.DateField('Крайний срок')
	limit = models.Q(app_label='project_specifications', model='specification')
	content_type = models.ForeignKey(ContentType, limit_choices_to=limit, null=True)
	object_id = models.PositiveIntegerField(null=True, blank=True)
	reason = GenericForeignKey('content_type', 'object_id')
	responsible = models.ManyToManyField('users.User', related_name='LogisticsRequest_responsible', verbose_name='Ответственные')
	ready_for_work = models.BooleanField('Передана логисту', default=False)
	location = models.ForeignKey('warehouse.Location', verbose_name='Склад для заявки')

	objects = LogisticsRequestManager()

	class Meta:
		ordering = ['when_requested']
		verbose_name = 'Заявка на закупку'
		verbose_name_plural = 'Заявки на закупки'
		permissions = {
			('is_logist', 'Является логистом'),
		}

	def __str__(self):
		return '{} {} - основание {}'.format(self.when_requested, self.who_requested.short_name, self.reason)


class LogisticsTask(models.Model):
	name = models.CharField('Название задачи', max_length=250, default='Задача на закупку')
	responsible = models.ForeignKey('users.User', verbose_name='Ответственный', null=True, blank=True)
	created_date = models.DateField('Дата формирования', auto_now_add=True)
	files = models.ManyToManyField('documents.Document', blank=True)
	work_started = models.BooleanField('Не доработана', default=False)

	class Meta:
		ordering = ['created_date']
		verbose_name = 'Задача на закупку'
		verbose_name_plural = 'Задачи на закупки'

	def __str__(self):
		if self.responsible:
			return '{} {}'.format(self.created_date, self.responsible.short_name)
		return '{} Отсутствует'.format(self.created_date)


class LogisticsRequestPosition(models.Model):
	number = models.PositiveIntegerField(verbose_name='Номер п/п')
	count = models.FloatField(verbose_name='Необходимое количество')
	good_kind = models.ForeignKey('warehouse.GoodKind', verbose_name='Вид товара', on_delete=models.PROTECT)
	unit = models.ForeignKey('warehouse.Unit', verbose_name='Единица измерения', on_delete=models.PROTECT)
	request = models.ForeignKey('logistics.LogisticsRequest', verbose_name='Заявка на закупку', on_delete=models.PROTECT)
	task = models.ForeignKey('logistics.LogisticsTask', verbose_name='Задача на закупку', null=True, blank=True, on_delete=models.PROTECT)
	order_date = models.DateField('Дата заказа', null=True, blank=True)
	expected_date = models.DateField('Ожидаемая дата поставки', null=True, blank=True)
	delivery_days = models.PositiveSmallIntegerField('Срок поставки в рабочих днях', default=0)
	deadline = models.DateField('Необходимая дата поставки')
	finished_date = models.DateField('Фактическая дата выполнения', null=True, blank=True)
	canceled_position = models.ForeignKey('self', verbose_name='Отмененная позиция', null=True, blank=True)
	canceled = models.BooleanField('Отменено', default=False)

	objects = LogisticsRequestPositionManager()

	class Meta:
		ordering = ['request__when_requested', 'number']
		verbose_name = 'Заявочная позиция'
		verbose_name_plural = 'Заявочные позиции'

	def __str__(self):
		return '{}: {} - {}'.format(self.number, self.good_kind, self.request)


class TransferRequest(models.Model):
	who_requested = models.ForeignKey('users.User', verbose_name="Кто запросил")
	where = models.ForeignKey('warehouse.Location', verbose_name="Куда", null=True)
	ready_to_go = models.BooleanField(verbose_name="Готова к выполнению", default=False)
	creation_date = models.DateField(verbose_name="Дата создания")
	worker = models.ForeignKey('users.User', related_name='TransferRequest_worker', verbose_name='Исполнитель', null=True)
	completed = models.BooleanField(verbose_name="Выполнена", default=False)

	objects = TransferRequestManager()

	class Meta:
		ordering = ['who_requested']
		verbose_name = 'Заявка на перемещение'
		verbose_name_plural = 'Заявки на перемещени'
		permissions = (
			('can_work_transfer_request', 'Может брать заявки в работу'),
		)


class TransferPosition(models.Model):
	good = models.ForeignKey('warehouse.Good', verbose_name="Складская позиция")
	count = models.FloatField(verbose_name="Количество")
	transferred = models.IntegerField(verbose_name="Перемещено", null=True)
	transfer_request = models.ForeignKey('logistics.TransferRequest', verbose_name="Заявка на перемещение")
	logistics_request_position = models.ForeignKey('logistics.LogisticsRequestPosition', verbose_name="Заявочная позиция",
	                                               null=True)

	class Meta:
		ordering = ['good']
		verbose_name = 'Позиция перемещения'
		verbose_name_plural = 'Позиции перемещений'