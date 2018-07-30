from django.db import models
from clients.managers import ClientManager, ContactManager, ClientHistoryManager


class OrganizationForm(models.Model):
	name = models.CharField('Название', max_length=150)

	class Meta:
		ordering = ['name']
		verbose_name = 'Организационно-правовая форма'
		verbose_name_plural = 'Организационно-правовые формы'

	def __str__(self):
		return self.name


class ClientKind(models.Model):
	name = models.CharField('Наименование', max_length=100)

	class Meta:
		ordering = ['name']
		verbose_name = 'Вид контрагента'
		verbose_name_plural = 'Виды контрагентов'

	def __str__(self):
		return self.name


class ClientRelation(models.Model):
	name = models.CharField('Наименование', max_length=100)

	class Meta:
		ordering = ['name']
		verbose_name = 'Взаимоотношение'
		verbose_name_plural = 'Взаимоотношения'

	def __str__(self):
		return self.name


class Client(models.Model):
	objects = ClientManager()

	name = models.CharField('Наименование', max_length=100)
	kind = models.ForeignKey('clients.ClientKind', null=True)
	relation = models.ForeignKey('clients.ClientRelation', null=True)
	full_name = models.CharField('Полное наименование', max_length=100, null=True)
	INN = models.CharField('ИНН', max_length=12, null=True)
	KPP = models.CharField('КПП', max_length=9, null=True)
	OKPO = models.CharField('Код по ОКПО', max_length=8, null=True)
	OGRN = models.CharField('Код по ОГРН', max_length=13, null=True)
	legal_address = models.CharField('Юр. адрес', max_length=250, null=True)
	street_address = models.CharField('Фактический адрес', max_length=250, null=True)
	phone_number = models.CharField('Телефон', max_length=100, null=True)
	manager = models.ForeignKey('users.User', verbose_name='Менеджер', null=True)
	other = models.CharField('Другое', max_length=100, null=True)

	class Meta:
		ordering = ['name']
		verbose_name = 'Контрагент'
		verbose_name_plural = 'Контрагенты'
		permissions = (
			('view_clients', 'Разрешение на просмотр всех Контрагентов, Клиентов и Истории взаимодействия'),
		)

	def __str__(self):
		return self.name


class Contact(models.Model):
	objects = ContactManager()

	last_name = models.CharField('Фамилия', max_length=50)
	first_name = models.CharField('Имя', max_length=50)
	patronum = models.CharField('Отчество', max_length=50, null=True)
	position = models.CharField('Должность', max_length=100, null=True)
	phone_number = models.CharField('Телефон', max_length=100, null=True)
	client = models.ForeignKey('clients.Client', verbose_name='Контрагент')

	class Meta:
		verbose_name = 'Контакт'
		verbose_name_plural = 'Контакты'


class ClientHistory(models.Model):
	objects = ClientHistoryManager()

	client = models.ForeignKey('clients.Client', verbose_name='Контрагент')
	contacts = models.ManyToManyField('clients.Contact', through='ClientHistoryContact', verbose_name='Контакты')
	date = models.DateField(verbose_name='Дата')
	interaction = models.TextField('Что сделано')
	result = models.TextField('Результат')
	next_step_date = models.DateField(verbose_name='Дата следующего шага')
	next_step = models.TextField('Следующий шаг')
	was_deleted = models.BooleanField('Удалён', default=False)

	class Meta:
		ordering = ['date']
		verbose_name = 'История взаимодействия'
		verbose_name_plural = 'Истории взаимодействий'


class ClientHistoryContact(models.Model):
	contact = models.ForeignKey('clients.Contact', on_delete=models.PROTECT)
	client_history = models.ForeignKey('clients.ClientHistory')
