import graphene
from crm.schema.mutation import SngyMutation
from crm.schema.types import IntID
from users.models import Bonus
from .types import BonusType
from users.decorators import permission_required
from synergycrm.exceptions import SngyException


class CreateBonus(SngyMutation):
	bonus = graphene.Field(BonusType)

	class Input:
		user_id = IntID(required=True)
		project_id = IntID(required=True)
		amount = graphene.Int(required=True)
		cash = graphene.Boolean(required=True)
		installments = graphene.Int(required=True)
		description = graphene.String(required=True)

	@permission_required('users.add_bonus')
	def mutate_and_get_payload(self, info, **kwargs):
		if kwargs['amount'] > 0 and info.context.user.id != 5:
			raise SngyException('Только генеральный директор может устанавливать сумму больше 0')
		if kwargs['installments'] < 1: kwargs['installments'] = 1
		bonus = Bonus.objects.create(user_added=info.context.user, **kwargs)
		return CreateBonus(bonus=bonus)


class DeleteBonus(SngyMutation):
	result = graphene.Boolean()

	class Input:
		id = IntID(required=True)

	@permission_required('users.delete_bonus')
	def mutate_and_get_payload(self, info, id):
		bonus = Bonus.objects.get(id=id)
		if bonus.month:
			raise SngyException('Этот бонус или вычет нельзя удалить, т.к. он уже учтен в зарплате')
		if info.context.user.has_perm('users.edit_all_bonuses') or info.context.user == bonus.user_added:
			bonus.delete()
		else:
			raise SngyException('Вы не можете удалить этот бонус или вычет')
		return DeleteBonus(result=True)


class UpdateBonus(SngyMutation):
	bonus = graphene.Field(BonusType)

	class Input:
		id = IntID(required=True)
		user_id = IntID(required=True)
		project_id = IntID(required=True)
		amount = graphene.Int(required=True)
		cash = graphene.Boolean(required=True)
		installments = graphene.Int(required=True)
		description = graphene.String(required=True)

	@permission_required('users.change_bonus')
	def mutate_and_get_payload(self, info, id, **kwargs):
		if kwargs['amount'] > 0 and info.context.user.id != 5:
			raise SngyException('Только генеральный директор может устанавливать сумму больше 0')
		if kwargs['installments'] < 1: kwargs['installments'] = 1
		bonus = Bonus.objects.get(id=id)
		if bonus.month:
			raise SngyException('Этот бонус или вычет нельзя изменять, т.к. он уже учтен в зарплате')
		if info.context.user.has_perm('users.edit_all_bonuses') or info.context.user == bonus.user_added:
			[setattr(bonus, f, kwargs[f]) for f in kwargs]
			bonus.save()
		else:
			raise SngyException('Вы не можете редактировать этот бонус или вычет')
		return UpdateBonus(bonus=bonus)
