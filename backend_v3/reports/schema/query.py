import datetime
from calendar import monthrange
from django.db.models import Q
import graphene
from crm.schema.types import IntID
from reports.models import Report, FuncRole, Process, SubProcess, Place, ProjectState
from .types import ReportType, FuncRoleType, ProcessType, SubProcessType, PlaceType, PagedReports, ReportsFilter, \
	HoursType, ReportHours, ProjectsStatsType, PagedFillouts, FilloutType, WorkingDay, AnalysisFilter, AnalysisNode, \
	DateRangeType, RegistryCollisionsStateProjectType
from crm.schema.types import PagedInput
from salary.models import DayOff
from projects.analyze import MonthClassifier, BaseDateClassifier


# noinspection PyMethodMayBeStatic,PyUnusedLocal
class Query(graphene.ObjectType):
	all_func_roles = graphene.List(FuncRoleType, description="Список всех функциональных ролей")
	all_processes = graphene.List(ProcessType, description="Список всех процессов")
	all_sub_processes = graphene.List(SubProcessType, description="Список всех подпроцессов")
	all_places = graphene.List(PlaceType, description="Список всех мест")
	get_report = graphene.Field(ReportType, report_id=IntID(), description="Информация об определенном репорте")
	paged_reports = graphene.Field(PagedReports, gip=graphene.Boolean(), paged=PagedInput(required=True),
	                               filters=ReportsFilter(), description="Постраничный вывод репортов с фильтрацией")
	hours = graphene.Field(HoursType, date=graphene.String(required=True))
	projects_stats = graphene.List(ProjectsStatsType, date=graphene.String(required=True))
	working_days = graphene.List(WorkingDay, date=graphene.String(required=True))
	paged_fillouts = graphene.Field(PagedFillouts, paged=PagedInput(required=True),
	                                date=graphene.String(required=True),
	                                description="Постраничный вывод fillouts с фильтрацией")
	project_analysis = graphene.Field(AnalysisNode, filters=graphene.List(AnalysisFilter), limits=DateRangeType(),
	                                  description="В папке reports")
	registry_collisions_state_projects = graphene.List(RegistryCollisionsStateProjectType)

	def resolve_all_func_roles(self, info):
		return FuncRole.objects.all()

	def resolve_all_processes(self, info):
		return Process.objects.all()

	def resolve_all_sub_processes(self, info):
		return SubProcess.objects.all()

	def resolve_all_places(self, info):
		return Place.objects.all()

	def resolve_get_report(self, info, report_id):
		report = Report.objects.select_related('user_added', 'checked_by').prefetch_related('projects__gip').get(
			id=report_id)
		user = info.context.user
		return report

	def resolve_paged_reports(self, info, paged, **kwargs):
		reports, total_count = Report.objects.list_paged_reports(user=info.context.user, **paged, **kwargs)
		return PagedReports(reports=reports, total_count=total_count)

	def resolve_paged_fillouts(self, info, date, paged):
		users_type, tc = Report.objects.fillouts(date, paged)
		users_type = [FilloutType(**params) for params in users_type]
		return PagedFillouts(fillouts=users_type, total_count=tc)

	def resolve_hours(self, info, **kwargs):
		reports, month_sum = Report.objects.sum_hours(user=info.context.user, _date=kwargs.get('date'))
		reports = [ReportHours(sum="{0:.2f}".format(args.pop('sum').total_seconds() / 3600), **args) for args in reports]
		return HoursType(reports=reports, month_sum=month_sum)

	def resolve_projects_stats(self, info, **kwargs):
		reports = Report.objects.sum_projects(user=info.context.user, _date=kwargs.get('date'))
		reports = [ProjectsStatsType(sum="{0:.2f}".format(args['sum']),
		                             project=args['projects__number'], description=args['projects__description']) for args
		           in reports]
		return reports

	def resolve_working_days(self, info, date):
		year = int('20' + date[-2:])
		month = int(date[:-2])
		date = datetime.date(year, month, 1)
		last_day = monthrange(year, month)[1]
		month_days = [datetime.date(year, month, i + 1) for i in range(last_day)]
		days_off = DayOff.objects.filter(date__range=(month_days[0], month_days[-1])).values('date')
		days_off = [d['date'] for d in days_off]
		month_days = list(set(month_days) - set(days_off))
		return [WorkingDay(d) for d in month_days]

	def resolve_project_analysis(self, info, filters, limits):

		def fillout_node(node, storage, name, filter_sort, parent_storage=None):
			setattr(node, '_id', name)
			if parent_storage:
				name = parent_storage.get_node_name(name)
			node.name = name
			node.hours = storage.totals.hours
			node.money = storage.totals.money
			# Спускаемся рекурсивно до MonthClassifier
			if type(storage) is MonthClassifier:
				return node
			for child_name, child_storage in storage.storage.items():
				new_node = AnalysisNode(children=list())
				new_node = fillout_node(new_node, child_storage, child_name, filter_sort[1:], parent_storage=storage)
				node.children.append(new_node)
			if len(node.children) and len(filter_sort):
				sort_by = filter_sort[0]
				if issubclass(type(storage), BaseDateClassifier) and sort_by['field'] == 'name':
					node.children.sort(key=lambda item: getattr(item, '_id'), reverse=sort_by['desc'])
				else:
					node.children.sort(key=lambda item: getattr(item, sort_by['field']), reverse=sort_by['desc'])
			return node

		result = Report.objects.project_analyze(info.context.user, filters, limits)
		if result:
			root = AnalysisNode(children=list())
			return fillout_node(root, result, 'Итого', [{'field': f.sortBy, 'desc': f.desc} for f in filters])
		else:
			return None

	def resolve_registry_collisions_state_projects(self, info):
		data = {}
		q = (Q(state_id=1) & ~Q(report__process_id__in=(1, 2, 3, 10))) | \
		    (Q(state_id=2) & ~Q(report__process_id__in=(1, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13))) | \
		    (Q(state_id=3) & ~Q(report__process_id__in=(1, 3, 10, 11)))
		project_states = ProjectState.objects.filter(report__deleted=False).filter(q).select_related('report', 'project'). \
			distinct('project__number', 'report_id').order_by('project__number', 'report_id')
		for ps in project_states:
			if ps.project not in data:
				data[ps.project] = []
			data[ps.project].append(ps.report)
		result = []
		for p, rs in data.items():
			sum_hours = sum(datetime.timedelta(hours=r.time_spent.hour, minutes=r.time_spent.minute).total_seconds() / 3600 for r in rs)
			result.append(RegistryCollisionsStateProjectType(project=p, reports=rs, sum_hours=sum_hours))
		return result
