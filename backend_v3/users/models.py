import os.path
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.models import _user_has_perm, _user_has_module_perms
from django.db import models
from .managers import UserManager, OccupationManager
from django.utils.crypto import get_random_string, constant_time_compare
from hashlib import sha1, sha256
from synergycrm.sngy_model import SngyModel


class Position(models.Model):
	name = models.CharField(max_length=255, verbose_name='название')
	company = models.ForeignKey('companies.Company', on_delete=models.PROTECT, verbose_name='компания')

	class Meta:
		unique_together = ('name', 'company')
		verbose_name = 'должность'
		verbose_name_plural = 'должности'
		ordering = ['name']
		permissions = (
			('can_assign_position', 'Может назначать на должности'),
			('can_remove_position', 'Может снимать с должностей'),
		)

	def __str__(self):
		return self.company.short_name + ' - ' + self.name


def avatar_directory_path(instance, filename):
	# Хешируем входной файл
	instance.avatar.open()
	contents = instance.avatar.read()
	hasher = sha1()
	hasher.update(contents)
	# Используем хеш в качестве имени файла
	path = 'avatars/{}{}'.format(hasher.hexdigest(), os.path.splitext(filename)[1])
	return path


class User(AbstractBaseUser, PermissionsMixin):
	MALE = 'M'
	FEMALE = 'F'
	GENDER_CHOICES = (
		(MALE, 'Мужской'),
		(FEMALE, 'Женский')
	)

	login = models.CharField('Логин', max_length=64, unique=True)
	avatar = models.ImageField('Аватар', upload_to=avatar_directory_path, null=True, blank=True)
	last_name = models.CharField('Фамилия', max_length=50)
	first_name = models.CharField('Имя', max_length=50)
	patronym = models.CharField('Отчество', max_length=50, null=True, blank=True)
	work_phone = models.CharField('Рабочий телефон', max_length=11, null=True, default=None, blank=True)
	personal_phone = models.CharField('Личный телефон', max_length=11, null=True, default=None, blank=True)
	email = models.CharField('Электронная почта', max_length=64, null=True, default=None, blank=True)
	password = models.CharField(max_length=64)
	salt = models.CharField(max_length=64)
	positions = models.ManyToManyField('users.Position', verbose_name='Должности')
	gender = models.CharField('Пол', max_length=1, choices=GENDER_CHOICES, default=MALE)
	birth_date = models.DateField('Дата рождения', null=True, blank=True)
	healthy = models.BooleanField('Не курит', default=False)
	hire_date = models.DateField('Дата приема')
	fire_date = models.DateField('Дата увольнения', null=True, default=None, blank=True)
	fired = models.BooleanField('Уволен', default=False)
	head = models.ForeignKey('self', related_name='user_head', verbose_name='Линейный руководитель', null=True)

	class Meta:
		verbose_name = 'пользователь'
		verbose_name_plural = 'пользователи'
		permissions = (
			('view_full_user', 'Может просматривать полную информацию о сотрудниках'),
			('edit_user', 'Может редактировать информацию сотрудников'),
			('hire_user', 'Может нанимать сотрудников'),
			('fire_user', 'Может увольнять сотрудников'),
			('view_salary', 'Может просматривать з.п.'),
			('can_close_salary', 'Может закрывать з.п.'),
			('change_hour_prime_cost', 'Может изменять себестоимость человеко/часа'),
			('view_warehouse', 'Может просматривать склад')
		)
		ordering = ['last_name', 'first_name', 'patronym']

	objects = UserManager()

	USERNAME_FIELD = 'login'
	EMAIL_FIELD = 'email'

	@property
	def full_name(self):
		return self.get_full_name()

	@property
	def short_name(self):
		return self.get_short_name()

	@property
	def is_staff(self):
		return self.is_superuser

	@property
	def is_active(self):
		return not self.fired

	def __str__(self):
		return '{} <{}>'.format(self.full_name, self.login)

	def get_full_name(self):
		if self.patronym:
			return '{} {} {}'.format(self.last_name, self.first_name, self.patronym)
		else:
			return '{} {}'.format(self.last_name, self.first_name)

	def get_short_name(self):
		if self.patronym:
			return '{} {}. {}.'.format(self.last_name, self.first_name[0:1], self.patronym[0:1])
		else:
			return '{} {}.'.format(self.last_name, self.first_name[0:1])

	def set_password(self, raw_password):
		salt = get_random_string(64)
		hasher = sha256()
		raw_password = raw_password + '_' + salt
		hasher.update(raw_password.encode('utf-8'))
		self.salt = salt
		self.password = hasher.hexdigest()
		return self

	def check_password(self, raw_password):
		hasher = sha256()
		raw_password = raw_password + '_' + self.salt
		hasher.update(raw_password.encode('utf-8'))
		return constant_time_compare(hasher.hexdigest(), self.password)

	def has_perm(self, perm, obj=None):
		# Не уволенные суперпользователи имеют весь доступ
		if not self.fired and self.is_superuser:
			return True
		return _user_has_perm(self, perm, obj)

	def has_module_perms(self, app_label):
		# Не уволенные суперпользователи имеют весь доступ
		if not self.fired and self.is_superuser:
			return True
		return _user_has_module_perms(self, app_label)

	def fire(self, fire_date):
		props = {
			'fired': True,
			'work_phone': None,
			'email': None,
			'fire_date': fire_date
		}
		for k, v in props.items():
			setattr(self, k, v)
		return self


class Occupation(SngyModel):
	user = models.OneToOneField('users.User', verbose_name='Сотрудник')
	salary = models.PositiveIntegerField('Зарплата, руб', null=True, default=0, blank=True)
	base = models.PositiveIntegerField('Оклад, руб')
	advance = models.PositiveIntegerField('Аванс, руб')
	fraction = models.PositiveSmallIntegerField('Ставка, %', default=100)
	by_hours = models.BooleanField('Почасовая оплата', default=True)
	fixed_hour = models.PositiveSmallIntegerField('Фиксированная стоимость часа', default=None, null=True, blank=True)
	transportation = models.PositiveSmallIntegerField('Затраты на проезд', default=0)
	main_company = models.ForeignKey('companies.Company', related_name='+', verbose_name='Основная компания')

	class Meta:
		verbose_name = "Занятость"
		verbose_name_plural = "Занятости"
		ordering = ('user__last_name', 'user__first_name')
		permissions = (
			('view_occupations', 'Может просматривать ставки'),
		)

	objects = OccupationManager()

	def __str__(self):
		return '{} ({} р. - {} р. - {} р.)'.format(self.user.short_name, self.salary, self.base, self.advance)

	@property
	def history_name(self):
		return '{} - {}'.format(self.id, self.user.short_name)

	@classmethod
	def history_related(cls):
		return ['user'], None


class Department(models.Model):
	head = models.ForeignKey('users.Position', on_delete=models.PROTECT)
	name = models.CharField(max_length=255)
	users = models.ManyToManyField('users.Occupation')


class GlobalCoefficient(models.Model):
	name = models.CharField('Название', primary_key=True, max_length=250)
	description = models.CharField('Описание', max_length=350)
	value = models.FloatField('Значение')

	# private_car_private_gas = 'А/м личный + свой бензин, р/км'
	# private_car_duty_gas = 'А/м личный + бензин фирмы, р/км'
	# private_car = 'А/м служебный, р/км'
	# health = 'ЗОЖ, р/день'
	# night = 'Ночные'
	# minimal_transport = 'Транспорт, р/день'
	# welding_surcharge = 'Доплата за сварку'
	# gip_order_surcharge = 'Доплата ГИПу-отв.'
	# manufacturer_order_surcharge = 'Доплата пр-лю работ-отв.'
	# pnr_order_surcharge = 'Доплата отв. за ПНР'
	# master_order_surcharge = 'Доплата мастеру-отв.'
	# default_work_hours = 'Рабочих часов в месяце по умолчанию'

	class Meta:
		verbose_name = "Глобальный коэффициент"
		verbose_name_plural = "Глобальные коэффициенты"

	def __str__(self):
		return self.description


class Coefficients(models.Model):
	user = models.OneToOneField('users.User', null=True, verbose_name='Сотрудник')
	general = models.FloatField('СМР общее')
	welding = models.FloatField('Навык сварочных работ')
	experience = models.FloatField('Опыт работы в компании')
	etech = models.FloatField('Знание основ электротехники')
	schematic = models.FloatField('Чтение схем')
	initiative = models.FloatField('Инициативность')
	discipline = models.FloatField('Дисциплина, прилежность')
	max_hour = models.PositiveIntegerField('Максимальная стоимость часа', default=200)
	# Кеш для весов коэффициентов
	weights = None

	class Meta:
		verbose_name = "Коэффициенты"
		verbose_name_plural = "Коэффициенты"
		permissions = (
			('view_all_coefficients', 'Может просматривать и изменять все коэффициенты'),
			('view_sub_coefficients', 'Может просматривать и изменять коэффициенты подчиненных'),
		)
		ordering = ('user__last_name', 'user__first_name', 'user__patronym')

	def __str__(self):
		return self.user.short_name

	@property
	def avg(self):
		fields = ['general', 'welding', 'experience', 'etech', 'schematic', 'initiative', 'discipline']
		avg = 0
		if Coefficients.weights is None:
			weights = GlobalCoefficient.objects.filter(name__in=fields).values('name', 'value')
			Coefficients.weights = {weight['name']: weight['value'] for weight in weights}
		for f in fields:
			avg += getattr(self, f) * Coefficients.weights[f]
		avg = float("{0:.2f}".format(avg))
		return avg

	@property
	def base(self):
		return int(self.max_hour * self.avg)


class Bonus(SngyModel):
	user_added = models.ForeignKey('users.User', related_name='bonus_user_added', verbose_name='Добавил')
	time_added = models.DateTimeField(auto_now=True)
	user = models.ForeignKey('users.User', verbose_name='Сотрудник')
	project = models.ForeignKey('projects.Project', on_delete=models.PROTECT, verbose_name='Проект')
	amount = models.IntegerField('Сумма')
	cash = models.BooleanField('Наличными', default=False)
	description = models.CharField('Описание', max_length=500)
	month = models.DateField(null=True, blank=True)
	counted = models.BooleanField(default=False)
	installments = models.IntegerField('Рассрочка', default=1)

	class Meta:
		verbose_name = "Бонус"
		verbose_name_plural = "Бонусы"
		permissions = (
			('view_all_bonus', 'Может просматривать бонусы'),
			('edit_all_bonuses', 'Может редактировать все бонусы'),
		)

	def __str__(self):
		return self.user.short_name
