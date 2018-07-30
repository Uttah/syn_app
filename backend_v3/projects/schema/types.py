import graphene
from crm.schema.types import IntID
from graphene_django import DjangoObjectType
from projects.models import Project, State, ProjectAnalysisSchema


class StateType(DjangoObjectType):
	class Meta:
		model = State


class ProjectType(DjangoObjectType):
	class Meta:
		model = Project
		exclude_fields = ('report_set', 'bonus_set',)


class PagedProjects(graphene.ObjectType):
	projects = graphene.List(ProjectType)
	total_count = graphene.Int()


class ProjectsFilter(graphene.InputObjectType):
	number = graphene.Int()
	gip = IntID()
	state = IntID()
	manager = IntID()
	customer = IntID()


class ProjectAnalysisSchemaType(DjangoObjectType):
	class Meta:
		model = ProjectAnalysisSchema
