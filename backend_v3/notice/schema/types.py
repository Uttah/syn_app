import graphene
from graphene_django import DjangoObjectType
from ..models import Notification


class NotificationType(DjangoObjectType):
	type = graphene.String()

	class Meta:
		model = Notification
