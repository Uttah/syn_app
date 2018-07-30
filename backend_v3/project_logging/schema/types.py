import graphene
from graphene.types.datetime import DateTime
from users.schema.types import BasicUserType


class JournalType(graphene.ObjectType):
	date = DateTime()
	user = graphene.Field(BasicUserType)
	instance = graphene.String()
	change = graphene.String()


class AllModelsType(graphene.ObjectType):
	id = graphene.String()
	name = graphene.String()
