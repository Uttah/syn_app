from graphene_django import DjangoObjectType
from graphene import String, Interface, Int, ObjectType, List, Enum, InputObjectType, Float, Boolean, Field
from graphene.types.datetime import Date
from crm.schema.types import IntID
from ..models import User, Position, Occupation, Coefficients, Bonus
from reports.schema.types import FuncRole
import os
from django.conf import settings


class GenderChoicesPropertyEnum(Enum):
	MALE = 'M'
	FEMALE = 'F'


# noinspection PyUnusedLocal
class UserType(Interface):
	class Meta:
		description = 'Абстрактный интерфейс пользователя'

	id = IntID(required=True)
	full_name = String()
	short_name = String()
	func_roles = List(IntID)
	gender = GenderChoicesPropertyEnum()
	positions = List(String, description='Список должностей')
	avatar = String()

	@staticmethod
	def resolve_func_roles(self, info):
		values = FuncRole.objects.filter(positions__user__id=self.id).values('id')
		return map(lambda item: item['id'], values)

	def resolve_gender(self, info, **kwargs):
		return self.gender

	def resolve_positions(self, info, **kwargs):
		# noinspection PyUnresolvedReferences
		positions = self.positions.select_related('company__client').all()
		return ['{} в {}'.format(position.name, position.company.client.name) for position in positions]

	def resolve_avatar(self, info, **kwargs):
		if self.avatar:
			return self.avatar.url
		else:
			return None



# noinspection PyUnusedLocal
class FullUserType(DjangoObjectType):
	gender = GenderChoicesPropertyEnum()

	class Meta:
		model = User
		interfaces = (UserType,)
		description = 'Объект пользователя с полной информацией (доступно только сотрудникам с правами)'
		exclude_fields = ['password', 'salt', 'gender']

	def resolve_gender(self, info, **kwargs):
		return self.gender


# BasicUserType должен обязательно находиться по коду ниже чем FullUserType чтобы использоваться по-умолчанию
# для полей с типом User
# noinspection PyUnusedLocal
class BasicUserType(DjangoObjectType):
	gender = GenderChoicesPropertyEnum()
	occupations = List(String, description='Список должностей')
	birth_date = Date(description='День рождения')
	has_signature = Boolean(description='Есть подпись')

	class Meta:
		model = User
		interfaces = (UserType,)
		description = 'Объект пользователя с базовой информацией (доступно всем)'
		only_fields = (
			'id', 'last_name', 'first_name', 'patronym', 'work_phone', 'personal_phone', 'email', 'is_superuser', 'fired', 'head')

	def resolve_has_signature(self, info):
		if settings.DEBUG:
			img_path = os.path.abspath('warehouse\static')
			images = os.listdir(img_path)
			# print('images', images)
			for image in images:
				# print(image.rsplit('.')[0])
				if str(self.id) == image.rsplit('.')[0]:
					# print('TRUE')
					return True
			return False
		return False

	def resolve_gender(self, info, **kwargs):
		return self.gender

	def resolve_occupations(self, info, **kwargs):
		# noinspection PyUnresolvedReferences
		return map(lambda occupation: occupation.get_short_name(), self.occupation_set.all())

	def resolve_birth_date(self, info, **kwargs):
		if info.context.user.has_perm('users.view_full_user'):
			return self.birth_date
		else:
			return None


class PagedUsers(ObjectType):
	class Meta:
		description = 'Объект постраничного вывода пользователей'

	users = List(BasicUserType, required=True, description='Список пользователей для запрошенной страницы')
	total_count = Int(required=True, description='Общее количество строк (после фильтрации)')


class PositionType(DjangoObjectType):
	class Meta:
		model = Position


class OccupationType(DjangoObjectType):
	class Meta:
		model = Occupation

	user = Field(FullUserType)


class CoefficientsType(DjangoObjectType):
	avg = Float()
	base = Float()

	class Meta:
		model = Coefficients


class BonusType(DjangoObjectType):
	class Meta:
		model = Bonus


class PagedOccupations(ObjectType):
	class Meta:
		description = 'Объект постраничного вывода занятостей'

	occupations = List(OccupationType, required=True, description='Список занятостей для запрошенной страницы')
	total_count = Int(required=True, description='Общее количество строк (после фильтрации)')


class OccupationFilter(InputObjectType):
	class Meta:
		description = 'Фильтр'

	companies = List(IntID, description='Список ID компаний которые надо отображать')
	positions = List(IntID, description='Список ID должностей которые надо отображать')


class UserAndPositionType(ObjectType):
	user_id = IntID()
	position_id = IntID()
	user = String()
	position = String()
