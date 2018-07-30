from graphene import ObjectType, List, Field, String, Boolean
from crm.schema.types import PagedInput, IntID
from ..models import User, Occupation, Coefficients, Bonus
from ..decorators import permission_required, allow
from .types import PagedUsers, PagedOccupations, BasicUserType, FullUserType, OccupationType, OccupationFilter, \
	CoefficientsType, BonusType, UserAndPositionType
from .login import Login, Logout
from .user import AddUser, ModifyUser, FireUser, HireUser, ChangePassword, ChangeOwnPassword, SetSuperUser, SaveUserAvatar
from .occupation import UpdateOccupation
from .coefficients import UpdateCoefficients
from .bonuses import CreateBonus, DeleteBonus, UpdateBonus
from .replace_user import ReplaceUser
from .positions import AssignPosition, RemovePosition


# noinspection PyMethodMayBeStatic,PyUnusedLocal
class Query(ObjectType):
	all_users = List(BasicUserType, subordinate=Boolean(), search=String(), description='Список всех пользователей с краткой информацией')
	paged_users = Field(PagedUsers, paged=PagedInput(required=True),
	                    description='Постраничный вывод базовых пользователей')
	current_user_permissions = List(String, required=True, description='Список разрешений данного пользователя')
	current_user = allow(Field(BasicUserType, description='Базовая информация о залогиненом пользователе'))
	user = Field(FullUserType, user_id=IntID(required=True), description='Полная информация о пользователе по его ID')
	user_positions = List(OccupationType,
	                      user_id=IntID(required=True,
	                                    description='Если указан, то возвращются занятости для конкретного пользователя'),
	                      description='Список занятости пользователей в компаниях')
	paged_occupations = Field(PagedOccupations, paged=PagedInput(required=True), filters=OccupationFilter(required=True),
	                          description='Постраничный вывод финансовой информации пользователей')
	all_occupations = List(OccupationType)
	all_coefficients = List(CoefficientsType)
	all_bonuses = List(BonusType)
	all_users_and_positions = List(UserAndPositionType)

	def resolve_all_users(self, info, **kwargs):
		return User.objects.list_all_users(info, **kwargs)

	def resolve_paged_users(self, info, paged):
		paged = {k: v for k, v in paged.items() if v is not None}
		result = User.objects.list_paged_users(**paged, show_fired=info.context.user.has_perm('users.view_full_user'))
		keys = ('users', 'total_count')
		return PagedUsers(**dict(zip(keys, result)))

	def resolve_current_user_permissions(self, info):
		return info.context.user.get_all_permissions()

	def resolve_current_user(self, info):
		if info.context.user.is_authenticated:
			return info.context.user
		else:
			return None

	@permission_required('users.view_full_user')
	def resolve_user(self, info, user_id):
		return User.objects.get(id=user_id)

	@permission_required('users.view_full_user')
	def resolve_user_positions(self, info, user_id):
		return Occupation.objects.filter(user_id=user_id).select_related('position__company').all()

	@permission_required('users.view_occupations')
	def resolve_paged_occupations(self, info, paged, **kwargs):
		paged = {k: v for k, v in paged.items() if v is not None}
		result = Occupation.objects.list_paged_occupations(**kwargs, **paged)
		keys = ('occupations', 'total_count')
		return PagedOccupations(**dict(zip(keys, result)))

	@permission_required('users.view_occupations')
	def resolve_all_occupations(self, info):
		return Occupation.objects.all()

	@permission_required('users.view_all_coefficients')
	def resolve_all_coefficients(self, info):
		return Coefficients.objects.all()

	@permission_required('users.view_all_bonus')
	def resolve_all_bonuses(self, info):
		return Bonus.objects.all().order_by('-id')

	def resolve_all_users_and_positions(self, info):
		result = []
		for u in User.objects.all():
			for p in u.positions.select_related('company__client').all():
				pos_name = '{} в {}'.format(p.name, p.company.client.name)
				result.append(UserAndPositionType(user_id=u.id, position_id=p.id, user=u.short_name, position=pos_name))
		return result


class Mutation(ObjectType):
	login = allow(Login.Field())
	logout = Logout.Field()
	add_user = AddUser.Field()
	modify_user = ModifyUser.Field()
	fire_user = FireUser.Field()
	hire_user = HireUser.Field()
	change_user_password = ChangePassword.Field()
	change_own_password = ChangeOwnPassword.Field()
	set_super_user = SetSuperUser.Field()
	update_occupation = UpdateOccupation.Field()
	update_coefficients = UpdateCoefficients.Field()
	create_bonus = CreateBonus.Field()
	delete_bonus = DeleteBonus.Field()
	update_bonus = UpdateBonus.Field()
	replace_user = ReplaceUser.Field()
	assign_position = AssignPosition.Field()
	remove_position = RemovePosition.Field()
	save_user_avatar = SaveUserAvatar.Field()
