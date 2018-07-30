from datetime import timedelta
from graphene import ObjectType, List, Field, Int
from graphene.types.datetime import Date
from crm.schema.types import PagedInput
from .types import PagedAbsences, AbsenceFilter, Absence, AbsenceReasonType, AbsenceReason, AbsenceWorkingDaysType
from .mutations import AddAbsence, UpdateAbsence, DeleteAbsence
from salary.models import DayOff


# noinspection PyMethodMayBeStatic,PyUnusedLocal
class Query(ObjectType):
	paged_absences = Field(PagedAbsences, paged=PagedInput(required=True), filters=AbsenceFilter(),
	                       description='Постраничное отображение отсутствий')
	absence_reasons = List(AbsenceReasonType)
	absence_working_days = Field(AbsenceWorkingDaysType, begin=Date(required=True), end=Date(), working_days=Int())

	def resolve_paged_absences(self, info, paged, **kwargs):
		paged = {k: v for k, v in paged.items() if v is not None}
		result = Absence.objects.list_paged_absences(info, **kwargs, **paged)
		keys = ('absences', 'total_count')
		return PagedAbsences(**dict(zip(keys, result)))

	def resolve_absence_reasons(self, info):
		return AbsenceReason.objects.all()

	def resolve_absence_working_days(self, info, begin, end=None, working_days=None):
		if end:
			all_days = end - begin
			days_off = timedelta(days=DayOff.objects.filter(date__range=(begin, end)).count())
			working_days = (all_days - days_off).days + 1   # Добавляем 1 день, так как дата окончания включена в период
			return AbsenceWorkingDaysType(working_days=working_days)

		if working_days:
			end = DayOff.objects.calculate_end_date(begin, working_days)
			return AbsenceWorkingDaysType(end=end)


class Mutation(ObjectType):
	add_absence = AddAbsence.Field()
	update_absence = UpdateAbsence.Field()
	delete_absence = DeleteAbsence.Field()
