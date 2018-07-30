from django.contrib.auth import login, logout
import graphene
from crm.schema.mutation import SngyMutation
from crm.schema.types import IntID
from users.models import User


class ReplaceUser(SngyMutation):
	result = graphene.Boolean()

	class Input:
		user_id = IntID(required=True)

	def mutate_and_get_payload(self, info, **kwargs):
		if info.context.user.is_superuser:
			logout(info.context)
			user = User.objects.get(id=kwargs.get('user_id'))
			login(info.context, user)
			return ReplaceUser(result=True)
		return ReplaceUser(result=False)

