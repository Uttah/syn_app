from graphene import String, Int, ObjectType, List, Boolean, InputObjectType
from graphene.types.datetime import Date
from graphene_django import DjangoObjectType
from crm.schema.types import IntID
from ..models import AbsenceReason, Absence
from reports.schema.types import DateRangeType


class AbsenceReasonType(DjangoObjectType):
	class Meta:
		model = AbsenceReason


class AbsenceType(DjangoObjectType):
	class Meta:
		model = Absence


class PagedAbsences(ObjectType):
	class Meta:
		description = 'Объект постраничного вывода отсутсвий'

	absences = List(AbsenceType, required=True, description='Список отсутсвий для запрошенной страницы')
	total_count = Int(required=True, description='Общее количество строк (после фильтрации)')


class AbsenceFilter(InputObjectType):
	class Meta:
		description = 'Фильтр'

	reason = List(IntID, required=True, description='Причина отсутствия')
	position = IntID(description='Должность отсутствующего')
	show_fired = Boolean(description='Показывать уволенных')
	date_range = DateRangeType(description='Период')


class AbsenceWorkingDaysType(ObjectType):
	end = Date()
	working_days = Int()

