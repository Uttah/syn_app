from graphene import String, Boolean, Int, Field
from graphene.types.datetime import DateTime, Date

from crm.schema.mutation import SngyMutation
from crm.schema.types import IntID
from .types import FullUserType, GenderChoicesPropertyEnum
from ..decorators import permission_required, user_passes_test
from ..models import User, Occupation
from synergycrm.exceptions import SngyException


# noinspection PyUnusedLocal
class AddUser(SngyMutation):
	class Input:
		login = String(required=True)
		last_name = String(required=True)
		first_name = String(required=True)
		patronym = String()
		password = String(required=True)
		hire_date = Date(required=True)
		company = IntID(required=True)


	user = Field(FullUserType, description='Добавленный пользователь или null при провале')

	@permission_required('users.add_user')
	def mutate_and_get_payload(self, info, company, **kwargs):
		# Удаляем пароль из словаря, так как он нужен нам отдельно
		password = kwargs.pop('password')
		new_user = User(**kwargs)
		new_user.set_password(password)
		new_user.save()
		# Создаем новую занятость для пользователя
		new_user.occupation = Occupation(user_id=new_user.id, base=0, advance=0, main_company_id=company)
		new_user.occupation.save()
		return AddUser(user=new_user)


# noinspection PyUnusedLocal
class ModifyUser(SngyMutation):
	class Input:
		id = IntID(required=True)
		login = String(required=True)
		last_name = String(required=True)
		first_name = String(required=True)
		patronym = String()
		work_phone = String()
		personal_phone = String()
		email = String()
		gender = GenderChoicesPropertyEnum(required=True)
		healthy = Boolean(required=True)
		birth_date = DateTime()
		hire_date = DateTime(required=True)
		fire_date = DateTime()
		head = IntID()

	user = Field(FullUserType, description='Измененный пользователь')

	@permission_required('users.edit_user')
	def mutate_and_get_payload(self, info, **kwargs):
		user_to_modify = User.objects.get(id=kwargs.pop('id'))
		if kwargs.get('head'): kwargs['head_id'] = kwargs['head']; del kwargs['head']
		for key, value in kwargs.items():
			setattr(user_to_modify, key, value)
		user_to_modify.save()
		return ModifyUser(user=user_to_modify)


# noinspection PyUnusedLocal
class FireUser(SngyMutation):
	class Input:
		user_id = IntID(required=True)
		fire_date = DateTime(required=True)

	success = Boolean(required=True)

	@permission_required('users.fire_user')
	def mutate_and_get_payload(self, info, user_id, fire_date):
		user = User.objects.get(id=user_id)
		user.fire(fire_date).save()
		return FireUser(success=True)


# noinspection PyUnusedLocal
class HireUser(SngyMutation):
	class Input:
		user_id = IntID(required=True)

	success = Boolean(required=True)

	@permission_required('users.hire_user')
	def mutate_and_get_payload(self, info, user_id):
		user = User.objects.get(id=user_id)
		user.fired = False
		user.fire_date = None
		user.save()
		return HireUser(success=True)


# noinspection PyUnusedLocal
class ChangePassword(SngyMutation):
	class Input:
		user_id = IntID(required=True)
		password = String(required=True)

	success = Boolean(required=True)

	@permission_required('users.edit_user')
	def mutate_and_get_payload(self, info, user_id, password):
		user = User.objects.get(id=user_id)
		user.set_password(password).save()
		return ChangePassword(success=True)


# noinspection PyUnusedLocal
class ChangeOwnPassword(SngyMutation):
	class Input:
		password = String(required=True)

	success = Boolean(required=True)

	@staticmethod
	def mutate_and_get_payload(self, info, password):
		info.context.user.set_password(password).save()
		return ChangePassword(success=True)


# noinspection PyUnusedLocal
class SetSuperUser(SngyMutation):
	class Input:
		user_id = IntID(required=True)
		is_superuser = Boolean(required=True)

	success = Boolean(required=True)

	@user_passes_test(lambda u: u.is_superuser, msg='403::Только суперпользователь может изменять это')
	def mutate_and_get_payload(self, info, user_id, is_superuser):
		user = User.objects.get(id=user_id)
		user.is_superuser = is_superuser
		user.save()
		return SetSuperUser(success=True)


class SaveUserAvatar(SngyMutation):
	image_path = String()

	class Input:
		user_id = IntID(required=True)

	def mutate_and_get_payload(self, info, user_id):
		if not info.context.FILES.get('file'):
			raise SngyException('Отсутствует файл')
		user = User.objects.get(id=user_id)
		user.avatar.delete()
		user.avatar = info.context.FILES['file']
		user.save()
		return SaveUserAvatar(image_path=user.avatar.url)
