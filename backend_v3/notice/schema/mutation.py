import graphene
from crm.schema.mutation import SngyMutation
from crm.schema.types import IntID
from synergycrm.exceptions import SngyException
from ..models import Notification


class ConfirmNotification(SngyMutation):
	result = graphene.Boolean()

	class Input:
		id = IntID(required=True)

	def mutate_and_get_payload(self, info, id):
		try:
			notification = Notification.objects.get(id=id)
			if notification.purpose != info.context.user:
				raise SngyException('Это не ваше уведомление')
			notification.confirmed = True
			notification.save()
		except Notification.DoesNotExist:
			raise SngyException('Такого уведомления нет')
		return ConfirmNotification(result=True)


class Mutation(graphene.ObjectType):
	confirm_notification = ConfirmNotification.Field()
