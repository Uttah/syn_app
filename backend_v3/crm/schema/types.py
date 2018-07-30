from graphene import ObjectType, InputObjectType, Int, String, Boolean
from graphene.types import Scalar
from graphql.language.ast import IntValue, StringValue


class PagedList(ObjectType):
	total_count = Int(required=True, description='Общее количество строк (после фильтрации)')


class PagedInput(InputObjectType):
	offset = Int(required=True, description='Индекс начала')
	first = Int(required=True, description='Количество элементов')
	sort_by = String(required=True, description='Поле для сортировки (см. справку по запросу для доступных значений)')
	desc = Boolean(description='Направление сортировки')
	search = String(description='Строка фильтрации')


class IntID(Scalar):
	serialize = int
	parse_value = int

	@staticmethod
	def parse_literal(ast):
		if isinstance(ast, IntValue):
			return ast.value
		if isinstance(ast, StringValue):
			return int(ast.value)
