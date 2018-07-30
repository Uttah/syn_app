from django.contrib.auth import authenticate, login, logout
from graphene import String, Boolean, Field, Mutation

from crm.schema.mutation import SngyMutation
from .types import BasicUserType
from ..decorators import allow


# noinspection PyUnusedLocal
class Login(SngyMutation):
	class Meta:
		description = 'Вход пользователя в систему'

	class Input:
		login = String(required=True, description='Логин пользователя')
		password = String(required=True, description='Пароль пользователя')

	user = allow(Field(BasicUserType, description='Информация о залогиненом пользователе'))
	success = allow(Boolean(required=True, description='Успех операции'))

	@staticmethod
	def mutate_and_get_payload(root, info, **kwargs):
		user = authenticate(info.context, **kwargs)
		if user is not None:
			login(info.context, user)
		return Login(user=user, success=user is not None)


# noinspection PyUnusedLocal
class Logout(Mutation):
	class Meta:
		description = 'Выход пользователя из системы'

	success = allow(Boolean(required=True, description='Успех операции'))

	@staticmethod
	def mutate(root, info):
		if info.context.user.is_authenticated:
			logout(info.context)
			return Logout(success=True)
		else:
			return Logout(success=False)
