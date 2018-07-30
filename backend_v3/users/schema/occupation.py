from graphene import Boolean, Int, Field
from crm.schema.mutation import SngyMutation
from crm.schema.types import IntID
from .types import OccupationType, Occupation
from ..decorators import permission_required


# noinspection PyUnusedLocal
class UpdateOccupation(SngyMutation):
	class Meta:
		description = 'Обновление данных занятости'

	class Input:
		occupation_id = IntID(required=True)
		salary = Int()
		fraction = Int()
		base = Int()
		advance = Int()
		by_hours = Boolean()
		fixed_hour = Int()
		transportation = Int()

	occupation = Field(OccupationType)

	@staticmethod
	@permission_required('users.change_occupation')
	def mutate_and_get_payload(root, info, occupation_id, **kwargs):
		occupation = Occupation.objects.get(id=occupation_id)
		for k, v in kwargs.items():
			setattr(occupation, k, v)
		occupation.save()
		return UpdateOccupation(occupation=occupation)
