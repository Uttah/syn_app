import graphene
from django.core.exceptions import ValidationError
from projects.models import Project
from crm.schema.mutation import SngyMutation
from crm.schema.types import IntID
from tasks.models import Task
from .types import TaskType
from synergycrm.exceptions import SngyException


class AddTask(SngyMutation):
	# модель
	task = graphene.Field(TaskType)

	# Входные данные(аргументы)
	class Input:
		name = graphene.String(required=True)
		project = IntID(required=True)

	@staticmethod
	def mutate_and_get_payload(self, info, name, project):
		proj = Project.objects.get(id=project)
		if proj.gip == info.context.user:
			try:
				task = Task.objects.create(name=name, project=proj)
			except ValidationError:
				raise SngyException('Задача с таким названием уже существует в проекте {:05d}'.format(proj.number))
		else:
			raise SngyException('Вы не являетесь Главным инженером проекта')
		return AddTask(task=task)


# noinspection PyUnusedLocal
class DeleteTask(SngyMutation):
	result = graphene.Boolean()

	class Input:
		id_task = IntID(required=True)

	@staticmethod
	def mutate_and_get_payload(root, info, id_task):
		task = Task.objects.get(id=id_task)
		if task.project.gip == info.context.user:
			try:
				task.delete()
				return DeleteTask(result=True)
			except Task.DoesNotExist:
				return DeleteTask(result=False)
		else:
			raise SngyException('Вы не являетесь Главным инженером проекта')


class EditTask(SngyMutation):
	task = graphene.Field(TaskType)

	class Input:
		name = graphene.String(required=True)
		id_task = IntID(required=True)

	@staticmethod
	def mutate_and_get_payload(root, info, name, id_task):
		if name == '':
			raise SngyException('Введите имя задачи')
		item_task = Task.objects.get(id=id_task)
		if item_task.project.gip != info.context.user:
			raise SngyException('Вы не являетесь Главным инженером проекта')
		item_task.name = name
		item_task.save()
		return EditTask(task=item_task)


class Mutation(graphene.ObjectType):
	add_task = AddTask.Field()
	delete_task = DeleteTask.Field()
	edit_task = EditTask.Field()
