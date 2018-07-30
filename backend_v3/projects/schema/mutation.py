import os
from django.db import models
from django.core.mail import send_mail
import graphene
from projects.models import Project, ProjectAnalysisSchema
from warehouse.models import Location
from users.models import GlobalCoefficient, User
from crm.schema.mutation import SngyMutation
from crm.schema.types import IntID
from .types import ProjectType, ProjectAnalysisSchemaType
from synergycrm.settings import PROJECTS_DIR, DEBUG
from graphene.types.datetime import Date
from users.decorators import permission_required
from synergycrm.exceptions import SngyException


def format_project_folder(project):
	number = '%06d' % project.number
	if project.customer:
		customer = project.customer.name
		customer = customer[0:30].replace('"', '')
	else:
		customer = ''
	description = project.description[:70].replace('"', '').strip().strip('.')
	for ch in ['\n', '"', '/', '\\', ':', '*', '?', '>', '<', '|']:
		if ch in customer:
			customer = customer.replace(ch, '_')
		if ch in description:
			description = description.replace(ch, '_')
	return 'SNGY%s_%s_%s' % (number, customer, description)


class ProjectStateChange(SngyMutation):
	result = graphene.Boolean()

	class Input:
		projects = graphene.List(IntID, required=True)
		state = IntID(required=True)
		date_filter = Date(required=True)

	@permission_required('projects.change_project_state_batch')
	def mutate_and_get_payload(self, info, projects, state, date_filter):
		from reports.models import ProjectState
		user = info.context.user
		ProjectState.objects.filter(project__gip=user, project__in=projects, report__report_date__gte=date_filter).update(
			state_id=state)
		return ProjectStateChange(result=True)


class CreateFiltersSchema(SngyMutation):
	schema = graphene.Field(ProjectAnalysisSchemaType)

	class Input:
		name = graphene.String(required=True)
		filters_row = graphene.String(required=True)

	def mutate_and_get_payload(self, info, name, filters_row):
		if len(name) == 0:
			raise SngyException('Введите название')
		name = name
		filters_schema = filters_row
		user_created = info.context.user
		schema = ProjectAnalysisSchema.objects.get_or_create(user_created=user_created, name=name)[0]
		schema.filters_schema = filters_schema
		schema.save()
		return CreateFiltersSchema(schema=schema)


class DeleteFiltersSchema(SngyMutation):
	result = graphene.Boolean()

	class Input:
		id = IntID(required=True)

	def mutate_and_get_payload(self, info, id):
		schema = ProjectAnalysisSchema.objects.get(id=id)
		schema.delete()
		return DeleteFiltersSchema(result=True)


class CreateProject(SngyMutation):
	project = graphene.Field(ProjectType)

	class Input:
		description = graphene.String(required=True)
		gip_id = IntID()
		state_id = IntID(required=True)
		budget = graphene.Int()
		customer_id = IntID()
		manager_id = IntID()
		comment = graphene.String()

	def mutate_and_get_payload(self, info, **kwargs):
		kwargs['state_id'] = 8
		if not kwargs.get('gip_id'):
			kwargs['gip_id'] = info.context.user.id
		number = Project.objects.all().aggregate(models.Max('number'))['number__max'] + 1
		user_created_id = info.context.user.id
		kwargs['description'] = kwargs['description'][:70]
		project = Project.objects.create(number=number, user_created_id=user_created_id, **kwargs)
		warehouse_name = 'Склад "%05d"' % project.number
		Location.objects.create(name=warehouse_name, project=project)
		# Создание папок под проект на сервере
		path = PROJECTS_DIR + format_project_folder(project)
		try:
			os.mkdir(path)
			os.mkdir(path + '/1. ИСХОДНЫЕ ДАННЫЕ')
			os.mkdir(path + '/2. КОММЕРЧЕСКАЯ ИНФОРМАЦИЯ')
			os.mkdir(path + '/3. ПРОЕКТНАЯ ДОКУМЕНТАЦИЯ')
			os.mkdir(path + '/4. РАБОЧАЯ ДОКУМЕНТАЦИЯ')
			os.mkdir(path + '/5. ИСПОЛНИТЕЛЬНАЯ ДОКУМЕНТАЦИЯ')
		except (PermissionError, FileNotFoundError) as e:
			if not DEBUG:
				subject = 'Проблема с созданием папок для проектов'
				message = 'Ошибка: "%s"\n' % e
				message += 'Номер проекта: %s' % number
				emails = User.objects.filter(id__in=(1, 106)).values('email')
				for d in emails:
					send_mail(subject, message, 'report@sngy.ru', [d['email']])
		return CreateProject(project=project)


class DeleteProject(SngyMutation):
	result = graphene.Boolean()

	class Input:
		id = IntID(required=True)

	def mutate_and_get_payload(self, info, id):
		project = Project.objects.get(id=id)
		if project.projectstate_set.all():
			raise SngyException('The project has reports')
		if project.bonus_set.all():
			raise SngyException('The project has bonus')
		project.delete()
		return DeleteProject(result=True)


class UpdateProject(SngyMutation):
	project = graphene.Field(ProjectType)

	class Input:
		id = IntID(required=True)
		description = graphene.String(required=True)
		gip_id = IntID()
		state_id = IntID(required=True)
		budget = graphene.Int()
		customer_id = IntID()
		manager_id = IntID()
		comment = graphene.String()

	def mutate_and_get_payload(self, info, id, **kwargs):
		project = Project.objects.get(id=id)
		if info.context.user.has_perm('user.change_project') or project.user_created == info.context.user:
			if not kwargs.get('gip_id'):
				kwargs['gip_id'] = info.context.user.id
			kwargs['description'] = kwargs['description'][:70]
			if kwargs['state_id'] != project.state_id and not info.context.user.has_perm('projects.change_project_state'):
				raise SngyException('Недостаточно прав на изменение этапа проекта')
			[setattr(project, f, kwargs[f]) for f in kwargs.keys()]
			project.save()
			return UpdateProject(project=project)
		else:
			raise SngyException('Недостаточно прав')


class ChangeHourPrimeCost(SngyMutation):
	result = graphene.Boolean()

	class Input:
		value = graphene.Int(required=True)

	def mutate_and_get_payload(self, info, value):
		if info.context.user.id != 5:
			raise SngyException('Изменять может только Давыдов!')
		GlobalCoefficient.objects.filter(name='hour_prime_cost').update(value=value)
		return ChangeHourPrimeCost(result=True)


class Mutation(graphene.ObjectType):
	create_project = CreateProject.Field()
	# delete_project = DeleteProject.Field()
	update_project = UpdateProject.Field()
	create_filters_schema = CreateFiltersSchema.Field()
	delete_filters_schema = DeleteFiltersSchema.Field()
	change_hour_prime_cost = ChangeHourPrimeCost.Field()
	project_state_change = ProjectStateChange.Field()
