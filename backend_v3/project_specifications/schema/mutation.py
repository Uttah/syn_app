from graphene import ObjectType, String, Boolean, List, Field
from crm.schema.mutation import SngyMutation
from crm.schema.types import IntID
from .types import SpecificationsPositionsType, Specification, SpecificationsPositions, SpecificationType
from warehouse.models import GoodKind
from synergycrm.exceptions import SngyException
from django.db import models


class CreateSpecification(SngyMutation):
	result = Boolean()

	class Input:
		project = IntID(required=True)
		pressmark = String(required=True)
		document_name = String(required=True)
		object_name = String(required=True)
		organization = String(required=True)
		section_name = String(required=True)
		state = String(required=True)
		workers_data = String()
		dates = List(String)

	def mutate_and_get_payload(self, info, **kwargs):
		kwargs['user_created'] = info.context.user
		kwargs['project_id'] = kwargs.pop('project')
		new_spec = Specification.objects.create(**kwargs)
		new_spec.editors.add(info.context.user)
		return CreateSpecification(result=True)


def check_spec_editing(specification, user, before_approval=True):
	if before_approval and specification.approved:
		raise SngyException('Спецификация уже утверждена')
	editors = [s for s in specification.editors.all()]
	editors.append(specification.project.gip)
	if user not in editors:
		raise SngyException('У вас нет прав на редактирование этой спецификации')


class ChangeSpecification(SngyMutation):
	result = Boolean()

	class Input:
		id = IntID(required=True)
		project = IntID(required=True)
		pressmark = String(required=True)
		document_name = String(required=True)
		object_name = String(required=True)
		organization = String(required=True)
		section_name = String(required=True)
		state = String(required=True)
		workers_data = String()
		dates = List(String)

	def mutate_and_get_payload(self, info, id, **kwargs):
		specification = Specification.objects.select_related('project__gip').get(id=id)
		check_spec_editing(specification, info.context.user)
		kwargs['project_id'] = kwargs.pop('project')
		for k, v in kwargs.items():
			setattr(specification, k, v)
		specification.save()
		return ChangeSpecification(result=True)


class DeleteSpecification(SngyMutation):
	result = Boolean()

	class Input:
		id = IntID(required=True)

	def mutate_and_get_payload(self, info, **kwargs):
		specification = Specification.objects.select_related('project__gip').get(id=kwargs['id'])
		if specification.project.gip != info.context.user:
			raise SngyException('У вас нет прав на удаление этой спецификации')
		specification.delete()
		return DeleteSpecification(result=True)


class ChangeSpecificationsPositions(SngyMutation):
	result = Boolean()

	class Input:
		specification_id = IntID(required=True)
		new_sequence = List(IntID)

	def mutate_and_get_payload(self, info, new_sequence, specification_id):
		check_spec_editing(Specification.objects.select_related('project__gip').get(id=specification_id), info.context.user)
		old_specifications_positions = list(SpecificationsPositions.objects.filter(specification_id=specification_id) \
		                                    .order_by('position_in_table'))
		# if len(new_sequence != len(old_specifications_positions)):
		#     raise Exception('Ошибка: разное количество полей. Обновите страницу')
		new_positions = new_sequence[:]
		# Старая последовательность позиций ВСЕГДА равна {0, 1, 2, 3, 4 итд}
		# В for'е получаем new_positions - Список НОВОЙ последовательности позиций
		for index in range(len(new_sequence)):
			id_item = old_specifications_positions[index].id
			new_index = new_sequence.index(id_item)
			new_positions[index] = new_index

		# Применение новых позиций_в_таблице по списку новых позиций new_positions
		for index in new_positions:
			old_specifications_positions[index].position_in_table = new_sequence.index(
				old_specifications_positions[index].id)
			old_specifications_positions[index].save()
		return ChangeSpecificationsPositions(result=True)


class CreateSpecificationPosition(SngyMutation):
	result = Boolean()

	class Input:
		specification_id = IntID(required=True)
		positional_designation = String()
		good_kind_id = IntID()
		good_position_id = IntID()
		description_info = String()
		unit_id = IntID()
		count = String()
		note = String()
		grouping_name = String()

	def mutate_and_get_payload(self, info, specification_id, **kwargs):
		for key, value in kwargs.items():
			if isinstance(value, str):
				kwargs[key] = value.strip()
		check_spec_editing(Specification.objects.select_related('project__gip').get(id=specification_id), info.context.user)
		# Если создана ГРУППИРОВКА
		if kwargs['grouping_name']:
			specifications_positions = SpecificationsPositions.objects.filter(
				specification_id=specification_id). \
				order_by('position_in_table')
			for index in range(len(specifications_positions)):
				obj = specifications_positions[index]
				obj.position_in_table = index
				obj.save()
			SpecificationsPositions.objects.create(specification_id=specification_id,
			                                       grouping_name=kwargs['grouping_name'],
			                                       position_in_table=len(specifications_positions) + 1)
			return CreateSpecificationPosition(result=True)
		# Если создано ЗАЧЕНИЕ спецификации
		else:
			if not kwargs['good_kind_id']:
				raise SngyException('Ошибка: поле "Вид товара" не заполнено')
			if not kwargs['unit_id']:
				raise SngyException('Ошибка: поле "Единицы измерения" не заполнено')
			if not kwargs['count']:
				raise SngyException('Ошибка: поле "Количество" не заполнено')
			specifications_positions = SpecificationsPositions.objects.filter(
				specification_id=specification_id). \
				order_by('position_in_table')
			for index in range(len(specifications_positions)):
				obj = specifications_positions[index]
				obj.position_in_table = index
				obj.save()

			good_kind = GoodKind.objects.get(id=kwargs['good_kind_id'])
			SpecificationsPositions.objects.create(positional_designation=kwargs['positional_designation'],
			                                       good_kind=good_kind, specification_id=specification_id,
			                                       unit_id=kwargs['unit_id'],
			                                       description_info=kwargs.get('description_info', None),
			                                       count=kwargs['count'],
			                                       note=kwargs['note'],
			                                       position_in_table=len(specifications_positions) + 1)
			return CreateSpecificationPosition(result=True)


class UpdateSpecificationPosition(SngyMutation):
	result = Boolean()

	class Input:
		specification_position_id = IntID(required=True)
		specification_id = IntID(required=True)
		positional_designation = String()
		good_kind_id = IntID()
		description_info = String()
		unit_id = IntID()
		count = String()
		note = String()
		grouping_name = String()

	def mutate_and_get_payload(self, info, specification_id, **kwargs):
		for key, value in kwargs.items():
			if isinstance(value, str):
				kwargs[key] = value.strip()
		check_spec_editing(Specification.objects.select_related('project__gip').get(id=specification_id), info.context.user)
		specification_position = SpecificationsPositions.objects.get(id=kwargs['specification_position_id'])
		# Если изменена ГРУППИРОВКА
		if kwargs['grouping_name'] and specification_position.grouping_name:
			specification_position.grouping_name = kwargs['grouping_name']
			specification_position.save()
			return UpdateSpecificationPosition(result=True)
		if kwargs['grouping_name'] and not specification_position.grouping_name:
			raise SngyException('Ошибка: попытка записать Группировку в Тип товара')
		if not kwargs['grouping_name'] and specification_position.grouping_name:
			raise SngyException('Ошибка: поле "Группировка" на заполнено')
		# Если изменено ЗАЧЕНИЕ спецификации
		if not kwargs['grouping_name']:
			if not kwargs.get('count'):
				raise SngyException('Ошибка: Поле "Количество" не заполнено!')
			if not kwargs.get('unit_id'):
				raise SngyException('Ошибка: Поле "Ед. Изм." не заполнено!')
			good_kind = GoodKind.objects.get(id=kwargs['good_kind_id'])
			specification_position.good_kind = good_kind
			specification_position.specification_id = specification_id
			specification_position.description_info = kwargs.get('description_info')
			specification_position.positional_designation = kwargs['positional_designation']
			specification_position.unit_id = kwargs['unit_id']
			specification_position.count = kwargs['count']
			specification_position.note = kwargs['note']
			specification_position.save()

			return UpdateSpecificationPosition(result=True)


class DeleteSpecificationPosition(SngyMutation):
	result = Boolean()

	class Input:
		specification_position_id = IntID(required=True)

	def mutate_and_get_payload(self, info, specification_position_id):
		pos = SpecificationsPositions.objects.select_related('specification__project__gip').get(
			id=specification_position_id)
		check_spec_editing(pos.specification, info.context.user)
		pos.delete()
		return DeleteSpecificationPosition(result=True)


class DuplicateSpecificationPosition(SngyMutation):
	result = Field(SpecificationsPositionsType)

	class Input:
		id = IntID(required=True)

	def mutate_and_get_payload(self, info, id):
		pos = SpecificationsPositions.objects.select_related('specification__project__gip').get(id=id)
		check_spec_editing(pos.specification, info.context.user)
		new_position_num = pos.position_in_table + 1
		# Сдвигаем все позиции с номером большим либо равным новому на 1 вниз
		SpecificationsPositions.objects.filter(specification=pos.specification,
		                                       position_in_table__gte=new_position_num).update(
			position_in_table=models.F('position_in_table') + 1)
		# Вставляем дубликат в нужную позицию
		pos.pk = None
		pos.position_in_table = new_position_num
		pos.save()
		return DuplicateSpecificationPosition(result=pos)


class SpecificationApproved(SngyMutation):
	result = Boolean()

	class Input:
		id_spec = IntID(required=True)

	def mutate_and_get_payload(self, info, id_spec):
		user = info.context.user
		specification = Specification.objects.get(id=id_spec)
		is_new_positions = SpecificationsPositions.objects.filter(specification_id=id_spec).filter(good_kind__new=True)
		if user.id != specification.project.gip.id:
			raise SngyException('Ошибка: Нет доступа!')
		elif len(is_new_positions) > 0:
			raise SngyException('Ошибка: Есть не утвержденные виды товаров!')
		elif specification.approved:
			raise SngyException('Ошибка: Спецификация уже подтверждена!')
		elif user.id == specification.project.gip.id and len(is_new_positions) == 0 and not specification.approved:
			specification.approved = True
			specification.save()
		return SpecificationApproved(result=True)


class CloneSpecification(SngyMutation):
	result = Field(SpecificationType)

	class Input:
		id_spec = IntID(required=True)

	def mutate_and_get_payload(self, info, id_spec):
		# Клонируем спецификацию
		specification = Specification.objects.select_related('project__gip').get(id=id_spec)
		check_spec_editing(specification, info.context.user, False)
		specification.id = None
		specification.pressmark += ' (копия)'
		specification.save()
		# Добавляем клонирующего в редакторы спецификации (если это не ГИП)
		if specification.project.gip != info.context.user:
			specification.editors.add(info.context.user)
		# Клонируем позиции спецификации
		positions = SpecificationsPositions.objects.filter(specification_id=id_spec)
		for p in positions:
			p.id = None
			p.specification = specification
			p.save()
		return CloneSpecification(result=specification)


class Mutation(ObjectType):
	create_specification = CreateSpecification.Field()
	change_specification = ChangeSpecification.Field()
	delete_specification = DeleteSpecification.Field()
	create_specification_position = CreateSpecificationPosition.Field()
	change_specifications_positions = ChangeSpecificationsPositions.Field()
	update_specification_position = UpdateSpecificationPosition.Field()
	delete_specification_position = DeleteSpecificationPosition.Field()
	duplicate_specification_position = DuplicateSpecificationPosition.Field()
	clone_specification = CloneSpecification.Field()
	specification_approved = SpecificationApproved.Field()
