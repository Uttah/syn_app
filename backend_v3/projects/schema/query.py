import graphene
from projects.models import State, Project, ProjectAnalysisSchema
from users.models import GlobalCoefficient
from crm.schema.types import IntID
from .types import StateType, ProjectType, ProjectsFilter, PagedProjects, ProjectAnalysisSchemaType
from crm.schema.types import PagedInput


# noinspection PyMethodMayBeStatic,PyUnusedLocal
class Query(graphene.ObjectType):
	all_states = graphene.List(StateType, description="Список всех этапов проектов")
	all_projects = graphene.List(ProjectType, current_gip=graphene.Boolean(), search=graphene.String(), gip=IntID(),
	                             require=graphene.List(IntID,
	                                                   description='Список ID проектов, информацию о которых необходимо вернуть вне зависимости от прочих совпавших условий'),
	                             description="Список проектов с фильтрацией")
	paged_projects = graphene.Field(PagedProjects, paged=PagedInput(required=True), filters=ProjectsFilter())
	get_hour_prime_cost = graphene.Int()
	filter_schemas = graphene.List(ProjectAnalysisSchemaType)

	def resolve_all_states(self, info):
		return State.objects.all()

	def resolve_all_projects(self, info, **kwargs):
		return Project.objects.load_projects(info, **kwargs)

	def resolve_paged_projects(self, info, paged, **kwargs):
		projects, total_count = Project.objects.paged_projects(**paged, **kwargs)
		return PagedProjects(projects=projects, total_count=total_count)

	def resolve_filter_schemas(self, info):
		return ProjectAnalysisSchema.objects.load_schemas(user=info.context.user)

	def resolve_get_hour_prime_cost(self, info):
		try:
			return GlobalCoefficient.objects.get(name='hour_prime_cost').value
		except:
			return 450
