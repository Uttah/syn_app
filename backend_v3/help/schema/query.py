from graphene import ObjectType, String
from django.conf import settings
from os import path
from codecs import open
from salary.models import GradeCoefficient
from users.models import GlobalCoefficient


# noinspection PyMethodMayBeStatic,PyUnusedLocal
class Query(ObjectType):
	help_md_text = String()

	def resolve_help_md_text(self, info):
		raw_md_path = path.join(settings.STATIC_ROOT, 'files/help.md')
		with open(raw_md_path, 'r', 'utf-8') as content_file:
			content = content_file.read()

		global_coefficients = {v['name']: v['value'] for v in GlobalCoefficient.objects.values('name', 'value')}
		global_coefficients['assembler_base'] = 200
		replaces = ('assembler_base', 'default_work_hours', 'welding_surcharge', 'health', 'private_car_private_gas',
		            'private_car_duty_gas', 'private_car')
		for r in replaces:
			content = content.replace(r, str(global_coefficients[r]).replace('.', ','))

		grade_table = ''
		grade_coefficients = GradeCoefficient.objects.values_list('quality', 'time', 'coefficient')
		grade_coefficients = map(lambda _row: map(lambda _item: str(_item), _row), grade_coefficients)
		for row in grade_coefficients:
			grade_table += '|' + '|'.join(row) + '|\n'
		content = content.replace('grade_table', grade_table)
		return content
