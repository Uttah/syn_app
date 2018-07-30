import graphene
from django.db.models import Q
from graphene_django import DjangoObjectType
from crm.schema.types import IntID
from projects.schema.types import ProjectType
from reports.models import Report, FuncRole, Process, SubProcess, Place
from graphene.types.datetime import Date
from datetime import datetime
from calendar import monthrange


class ReportType(DjangoObjectType):
	class Meta:
		model = Report


class FuncRoleType(DjangoObjectType):
	class Meta:
		model = FuncRole
		exclude_fields = ('report_set',)


class ProcessType(DjangoObjectType):
	class Meta:
		model = Process
		exclude_fields = ('report_set',)


class SubProcessType(DjangoObjectType):
	class Meta:
		model = SubProcess
		exclude_fields = ('report_set',)


class PlaceType(DjangoObjectType):
	class Meta:
		model = Place
		exclude_fields = ('report_place',)


class PagedReports(graphene.ObjectType):
	reports = graphene.List(ReportType)
	total_count = graphene.Int()


class DateRangeType(graphene.InputObjectType):
	month_start = graphene.String()
	month_end = graphene.String()

	def get_range(self, filtered, filtering_by):

		def get_q_object(filtering_by, date1, date2, type):
			filter_key = '{}__{}'.format(filtering_by, type)
			if type == 'gte':
				d = {filter_key: date1}
			elif type == 'lte':
				d = {filter_key: date2}
			else:
				d = {filter_key: (date1, date2)}
			return Q(**d)

		date1, date2 = self.get_dates()
		if not date1 and not date2:
			return filtered
		if date1 and date2:
			return filtered.filter(get_q_object(filtering_by, date1, date2, type='range'))
		if date1 and not date2:
			return filtered.filter(get_q_object(filtering_by, date1, None, type='gte'))
		if not date1 and date2:
			return filtered.filter(get_q_object(filtering_by, None, date2, type='lte'))
		return filtered

	def get_two_date_range(self, filtered, by_begin, by_end):

		date1, date2 = self.get_dates()
		if date1:
			filtered = filtered.filter(**{'{}__gt'.format(by_end): date1})
		if date2:
			filtered = filtered.filter(**{'{}__lt'.format(by_begin): date2})
		return filtered

	def get_dates(self):
		_dateStart = self.month_start
		_dateEnd = self.month_end
		date1 = None
		date2 = None
		if _dateStart:
			year_start = int('20' + _dateStart[-2:])
			month_start = int(_dateStart[:-2])
			date1 = datetime(year_start, month_start, 1)
		if _dateEnd:
			year_end = int('20' + _dateEnd[-2:])
			month_end = int(_dateEnd[:-2])
			date2 = datetime(year_end, month_end, 1)
			date2 = date2.replace(day=monthrange(year_end, month_end)[1])
		return date1, date2


class ReportsFilter(graphene.InputObjectType):
	only_own_projects = graphene.Boolean()
	worker = IntID()
	projects = graphene.List(IntID)
	state = IntID()
	func_role = IntID()
	process = IntID()
	sub_process = IntID()
	date_range = DateRangeType()


class ReportHours(graphene.ObjectType):
	report_date = Date()
	sum = graphene.Float()
	projects = graphene.String()
	day_off = graphene.Boolean()


class HoursType(graphene.ObjectType):
	reports = graphene.List(ReportHours)
	month_sum = graphene.Float()


class ProjectsStatsType(graphene.ObjectType):
	project = graphene.String()
	description = graphene.String()
	sum = graphene.Float()


class FilloutType(graphene.ObjectType):
	has_work_days = graphene.Int()
	days_missing = graphene.Int()
	short_name = graphene.String()


class PagedFillouts(graphene.ObjectType):
	fillouts = graphene.List(FilloutType)
	total_count = graphene.Int()


class WorkingDay(graphene.ObjectType):
	date = Date()


class AnalysisFilter(graphene.InputObjectType):
	name = graphene.String()
	filter = graphene.List(IntID)
	sortBy = graphene.String()
	desc = graphene.Boolean()


class AnalysisNode(graphene.ObjectType):
	name = graphene.String()
	hours = graphene.Float()
	money = graphene.Float()
	# Без лямбды невозможно использовать самого себя в качестве чилдрена
	children = graphene.List(lambda: AnalysisNode)


class RegistryCollisionsStateProjectType(graphene.ObjectType):
	project = graphene.Field(ProjectType)
	reports = graphene.List(ReportType)
	sum_hours = graphene.Float()
