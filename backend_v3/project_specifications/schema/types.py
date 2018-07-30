import graphene
from graphene_django import DjangoObjectType
from ..models import Specification, SpecificationsPositions, GOST


class SpecificationType(DjangoObjectType):
	class Meta:
		model = Specification


class GOSTType(DjangoObjectType):
	class Meta:
		model = GOST


class SpecificationsPositionsType(DjangoObjectType):
	class Meta:
		model = SpecificationsPositions


class PagedSpecificationType(graphene.ObjectType):
	specifications = graphene.List(SpecificationType)
	total_count = graphene.Int()
