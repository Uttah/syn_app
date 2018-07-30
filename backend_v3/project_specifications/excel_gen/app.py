from .input import MyFileInput
from os.path import dirname, join, exists
from os import mkdir
from crm.schema.mutation import SngyMutation
from graphene import ObjectType, String
from crm.schema.types import IntID
from project_specifications.models import SpecificationsPositions
from synergycrm import settings


class CreateExcel(SngyMutation):
	result = String()

	class Input:
		specificaton_id = IntID(required=True)

	def mutate_and_get_payload(self, info, **kwargs):
		spec_path = 'specifications/'
		if settings.DEBUG:
			dir_input = dirname('./project_specifications/static/')
		else:
			dir_input = settings.STATIC_ROOT
		specification_positions = list(SpecificationsPositions.objects.filter(specification_id=kwargs['specificaton_id']).
		                               order_by('position_in_table').values())
		save_path = join(settings.MEDIA_ROOT, spec_path)
		if not exists(save_path):
			mkdir(save_path)
		file_input = MyFileInput(specification_positions, dir_input, save_path)
		# ExcelBook(file_input)
		return CreateExcel(result=join(settings.MEDIA_URL, spec_path, file_input.filename))


class Mutation(ObjectType):
	create_excel = CreateExcel.Field()
