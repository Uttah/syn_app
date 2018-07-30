import graphene
from crm.schema.mutation import SngyMutation
from crm.schema.types import IntID
from ..models import User, Position
from synergycrm.exceptions import SngyException
from users.decorators import permission_required


class AssignPosition(SngyMutation):
	result = graphene.Boolean()

	class Input:
		user = IntID()
		position = IntID()

	@permission_required('users.can_assign_position')
	def mutate_and_get_payload(self, info, user, position):
		try:
			user = User.objects.get(id=user)
		except User.DoesNotExist:
			raise SngyException('Нет такого сотрудника')
		if Position.objects.filter(id=position).exists():
			user.positions.add(position)
		else:
			raise SngyException('Нет такой должности')
		return AssignPosition(result=True)


class RemovePosition(SngyMutation):
	result = graphene.Boolean()

	class Input:
		user = IntID()
		position = IntID()

	@permission_required('users.can_remove_position')
	def mutate_and_get_payload(self, info, user, position):
		try:
			user = User.objects.get(id=user)
		except User.DoesNotExist:
			raise SngyException('Нет такого пользователя')
		if user.positions.filter(id=position).exists():
			position = Position.objects.get(id=position)
			user.positions.remove(position)
		else:
			raise SngyException('Нет такой должности у сотрудника')
		return RemovePosition(result=True)
