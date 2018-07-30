import graphene
from .types import NotificationType
from ..models import Notification


# noinspection PyMethodMayBeStatic,PyUnusedLocal
class Query(graphene.ObjectType):
	get_notice = graphene.List(NotificationType)
	get_all_notice = graphene.List(NotificationType)

	def resolve_get_notice(self, info):
		return Notification.objects.filter(purpose=info.context.user, confirmed=False).order_by('date')[0:3]

	def resolve_get_all_notice(self, info):
		return Notification.objects.filter(purpose=info.context.user)
