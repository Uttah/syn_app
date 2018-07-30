import graphene
from graphene_django import DjangoObjectType
from crm.schema.types import IntID
from tasks.models import Task


class TaskType(DjangoObjectType):
	class Meta:
		model = Task


class TasksOnProjects(graphene.ObjectType):
	tasks = graphene.List(TaskType)
	total_count = graphene.Int()


class TasksFilter(graphene.InputObjectType):
	projects = graphene.List(IntID)
