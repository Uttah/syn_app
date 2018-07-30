import graphene
from django.db import models
from graphene import ObjectType, Field, List
from project_specifications.schema.types import PagedSpecificationType, SpecificationsPositionsType, SpecificationType,\
	GOSTType
from project_specifications.models import Specification, SpecificationsPositions, GOST
from crm.schema.types import PagedInput, IntID
from synergycrm.exceptions import SngyException
from logistics.models import LogisticsRequest


class Query(ObjectType):
	paged_specification = Field(PagedSpecificationType, paged=PagedInput(required=True))
	specifications_positions = List(SpecificationsPositionsType, filters=IntID())
	all_specification = List(SpecificationType)
	all_gosts = List(GOSTType)
	descriptions_info = List(graphene.String, filters=IntID(required=True))
	selected_specification = Field(SpecificationType, specification_id=IntID())
	get_specification_id_by_logistic = Field(IntID, logistic_id=IntID(required=True))

	def resolve_paged_specification(self, info, paged):
		specifications, total_count = Specification.objects.list_paged_specifications(info.context.user, **paged)
		return PagedSpecificationType(specifications=specifications, total_count=total_count)

	def resolve_specifications_positions(self, info, **kwargs):
		result = SpecificationsPositions.objects.load_specifications_positions(info, **kwargs)
		if result:
			return result
		return []

	def resolve_all_specification(self, info):
		user = info.context.user
		return Specification.objects.filter(models.Q(project__gip=user) | models.Q(editors=user))

	def resolve_all_gosts(self, info):
		return GOST.objects.all()

	def resolve_descriptions_info(self, info, **kwargs):
		return SpecificationsPositions.objects.load_descriptions_info(info, **kwargs)

	def resolve_selected_specification(self, info, specification_id=None):
		try:
			if not specification_id:
				return None
			return Specification.objects.get(id=specification_id)
		except Specification.DoesNotExist:
			raise SngyException('Спецификация не найдена')

	def resolve_get_specification_id_by_logistic(self, info, logistic_id):
		try:
			lr = LogisticsRequest.objects.get(id=logistic_id)
			return Specification.objects.get(id=lr.reason.id).id
		except Specification.DoesNotExist:
			raise SngyException('Спецификация не найдена')
