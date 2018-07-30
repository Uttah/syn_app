import graphene
from .types import TasksFilter, TasksOnProjects, TaskType
from tasks.models import Task
from crm.schema.types import PagedInput


# noinspection PyMethodMayBeStatic,PyUnusedLocal
class Query(graphene.ObjectType):
	tasks_in_report = graphene.List(TaskType, filters=TasksFilter(), description="Список задач")

	tasks_on_projects = graphene.Field(TasksOnProjects, paged=PagedInput(required=True),
	                                   filters=TasksFilter(), description="Список задач")

	def resolve_tasks_on_projects(self, info, paged, **kwargs):
		tasks, total_count = Task.objects.list_tasks_on_projects(user=info.context.user, **paged, **kwargs)
		return TasksOnProjects(tasks=tasks, total_count=total_count)

	def resolve_tasks_in_report(self, info, **kwargs):
		return Task.objects.list_tasks_in_report(user=info.context.user, **kwargs)
