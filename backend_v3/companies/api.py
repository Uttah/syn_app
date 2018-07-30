from graphene_django import DjangoObjectType
from graphene import List, ObjectType
from users.schema.types import PositionType
from .models import Company


class CompanyType(DjangoObjectType):
	class Meta:
		model = Company

	position_set = List(PositionType, description='Список должностей компании')

	def resolve_position_set(self, info):
		return self.position_set.all()


# noinspection PyMethodMayBeStatic,PyUnusedLocal
class Query(ObjectType):
	all_companies = List(CompanyType, description='Список всех компаний')

	def resolve_all_companies(self, info):
		return Company.objects.prefetch_related('position_set').all()
