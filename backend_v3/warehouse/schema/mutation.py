from graphene import ObjectType, Float, String, Field, Boolean, List
from django.db import models
from crm.schema.mutation import SngyMutation
from crm.schema.types import IntID
from ..models import Good, GoodKind, Manufacturer, Location, Unit
from project_specifications.models import GOST
from .types import GoodType, GoodKindType, ManufacturerType, WarehouseType
from users.decorators import permission_required
from synergycrm.exceptions import SngyException


# noinspection PyUnusedLocal
class CreateGood(SngyMutation):
	good = Field(GoodType)

	class Input:
		count = Float(required=True)
		unit_id = IntID(required=True)
		note = String()
		defect = Boolean(required=True)
		project_id = IntID()
		good_kind_id = IntID(required=True)
		location_id = IntID(required=True)
		responsible_id = IntID(required=True)

	@permission_required('warehouse.add_good')
	def mutate_and_get_payload(self, info, **kwargs):
		try:
			if Location.objects.get(id=kwargs['location_id']).project.state_id not in (2, 3, 4):
				raise SngyException('Этап проекта не допускает хранение на складе')
		except Location.DoesNotExist:
			raise SngyException('Местоположения не существует')
		try:
			try:
				unit = Unit.objects.get(id=kwargs['unit_id'])
			except Exception:
				raise SngyException('Нет такой единицы')
			if not kwargs['defect'] and not unit.restrict_sum:
				good = Good.objects.get(unit_id=kwargs['unit_id'], good_kind_id=kwargs['good_kind_id'],
				                        location_id=kwargs['location_id'], project_id=kwargs.get('project_id'),
				                        defect=kwargs.get('defect'), responsible_id=kwargs['responsible_id'])
				good.count += kwargs['count']
				good.save()
			else:
				raise Good.DoesNotExist
		except Good.DoesNotExist:
			good = Good.objects.create(**kwargs)
		return CreateGood(good=good)


class UpdateGood(SngyMutation):
	good = Field(GoodType)

	class Input:
		id = IntID(required=True)
		count = Float(required=True)
		unit_id = IntID(required=True)
		note = String()
		defect = Boolean(required=True)
		project_id = IntID()
		good_kind_id = IntID(required=True)
		location_id = IntID(required=True)
		responsible_id = IntID(required=True)

	@permission_required('warehouse.change_good')
	def mutate_and_get_payload(self, info, id, **kwargs):
		try:
			if Location.objects.get(id=kwargs['location_id']).project.state_id not in (2, 3, 4):
				raise SngyException('Этап проекта не допускает хранение на складе')
		except Location.DoesNotExist:
			raise SngyException('Местоположения не существует')
		try:
			unit = Unit.objects.get(id=kwargs['unit_id'])
		except Exception:
			raise SngyException('Нет такой единицы')
		if not kwargs['defect'] and not unit.restrict_sum:
			same_goods = Good.objects.filter(unit_id=kwargs['unit_id'], good_kind_id=kwargs['good_kind_id'],
			                                 location_id=kwargs['location_id'], defect=kwargs.get('defect'),
			                                 project_id=kwargs.get('project_id'),
			                                 responsible_id=kwargs['responsible_id']). \
				exclude(id=id).values('id', 'count')
			total_count = 0
			ids = list()
			for good in same_goods:
				total_count += good['count']
				ids.append(good['id'])
			if len(same_goods):
				Good.objects.filter(id__in=ids).delete()
				kwargs['count'] += total_count
		Good.objects.filter(id=id).update(**kwargs)
		good = Good.objects.get(id=id)
		return UpdateGood(good=good)


class DeleteGood(SngyMutation):
	result = Boolean()

	class Input:
		id = IntID(required=True)

	@permission_required('warehouse.delete_good')
	def mutate_and_get_payload(self, info, id):
		Good.objects.get(id=id).delete()
		return DeleteGood(result=True)


# gosts - список/множество названий ГОСТов (строк)
def handle_gosts(gosts):
	existing_gosts = list(GOST.objects.filter(name__in=gosts))
	existing_gosts_names = {g.name for g in existing_gosts}
	gosts_to_create = gosts - existing_gosts_names
	for g in gosts_to_create:
		new_gost = GOST.objects.create(name=g)
		existing_gosts.append(new_gost)
	return existing_gosts


# noinspection PyUnusedLocal
class CreateGoodKind(SngyMutation):
	good_kind = Field(GoodKindType)

	class Input:
		code = String()
		name = String(required=True)
		manufacturer_name = String(required=True)
		mass = Float()
		good_group_id = IntID()
		analogs = List(IntID)
		gosts = List(String, required=True)
		default_unit = IntID()

	@permission_required('warehouse.add_goodkind')
	def mutate_and_get_payload(self, info, manufacturer_name, analogs=None, **kwargs):
		if kwargs.get('code'):
			kwargs['code'] = kwargs['code'].strip()
			if GoodKind.objects.filter(code=kwargs['code'], manufacturer__name=manufacturer_name).exists():
				raise SngyException('Производитель уже имеет такой артикул')
		manufacturer = Manufacturer.objects.get_or_create(name=manufacturer_name.strip())[0]
		gosts = {g for g in kwargs.pop('gosts', [])}
		try:
			default_unit_id = kwargs.pop('default_unit')
			good_kind = GoodKind.objects.create(manufacturer=manufacturer, default_unit_id=default_unit_id, **kwargs)
			if analogs:
				good_kind.analogs.add(*analogs)
		except Exception as e:
			print(e)
			raise SngyException('Что-то не так')  # Чтобы не показывать ошибку бд
		# Присваиваем ГОСТы
		good_kind.gosts.set(handle_gosts(gosts))
		return CreateGoodKind(good_kind=good_kind)


# noinspection PyUnusedLocal
class UpdateGoodKind(SngyMutation):
	good_kind = Field(GoodKindType)

	class Input:
		id = IntID(required=True)
		code = String()
		name = String(required=True)
		manufacturer_name = String(required=True)
		mass = Float()
		good_group_id = IntID()
		analogs = List(IntID)
		gosts = List(String, required=True)
		default_unit = IntID()

	@permission_required('warehouse.change_goodkind')
	def mutate_and_get_payload(self, info, id, manufacturer_name, analogs=None, **kwargs):
		if not GoodKind.objects.get(id=id).new and not info.context.user.has_perm('warehouse.can_moderate'):
			raise SngyException('Ошибка: Недостаточно прав!')

		if kwargs.get('code'):
			kwargs['code'] = kwargs['code'].strip()
			good_kind = GoodKind.objects.filter(code=kwargs['code'], manufacturer__name=manufacturer_name).exclude(id=id)
			if good_kind:
				good_kind = '%s %s (%s)' % (good_kind[0].code, good_kind[0].name, good_kind[0].manufacturer.name)
				raise SngyException('Производитель уже имеет такой артикул (%s)' % good_kind)
		manufacturer = Manufacturer.objects.get_or_create(name=manufacturer_name.strip())[0]
		gosts = {g for g in kwargs.pop('gosts', [])}
		try:
			GoodKind.objects.filter(id=id).update(manufacturer=manufacturer, **kwargs)
			good_kind = GoodKind.objects.get(id=id)
			if analogs is not None:
				good_kind.analogs.clear()
				good_kind.analogs.add(*analogs)
		except Exception:
			raise SngyException('Что-то не так')
		# Присваиваем ГОСТы
		good_kind.gosts.set(handle_gosts(gosts))
		return UpdateGoodKind(good_kind=good_kind)


class UpdateGoodKindExsistCode(SngyMutation):
	good_kind = Field(GoodKindType)

	class Input:
		id = IntID(required=True)
		code = String(required=True)
		name = String(required=True)
		manufacturer_name = String(required=True)
		action = String(required=True)
		default_unit = IntID()

	@permission_required('warehouse.change_goodkind')
	def mutate_and_get_payload(self, info, id, code, name, manufacturer_name, action):
		if not info.context.user.has_perm('warehouse.can_moderate'):
			raise SngyException('Ошибка: Недостаточно прав!')
		manufacturer = Manufacturer.objects.get_or_create(name=manufacturer_name.strip())[0]
		try:
			if action == 'coincidental':
				good_kind = GoodKind.objects.get(code=code, manufacturer=manufacturer)
				Good.objects.filter(good_kind__id=id).update(good_kind=good_kind)
				GoodKind.objects.get(id=id).delete()
			elif action == 'editable':
				temporary_code = '61ada82902d66da40c84d741fb36de71'
				GoodKind.objects.filter(code=code, manufacturer=manufacturer).update(code=temporary_code)
				GoodKind.objects.filter(id=id).update(code=code, name=name, manufacturer=manufacturer)
				good_kind = GoodKind.objects.get(id=id)
				Good.objects.filter(good_kind__code=temporary_code).update(good_kind=good_kind)
				GoodKind.objects.filter(code=temporary_code).delete()
		except GoodKind.DoesNotExist:
			raise SngyException('Вид товара не найден')  # Чтобы не показывать ошибку бд
		# Суммируем
		goods_dict = Good.objects.filter(good_kind=good_kind).values()
		goods = []
		units = {u.id: u.restrict_sum for u in Unit.objects.all()}
		for g in goods_dict:
			find = False
			for g2 in goods:
				if g2['unit_id'] == g['unit_id'] and g2['location_id'] == g['location_id'] and \
					g2['good_kind_id'] == g['good_kind_id'] and g2['project_id'] == g['project_id'] and \
					g2['responsible_id'] == g['responsible_id'] and g2['defect'] == g['defect'] and not g2['defect'] \
					and not units[g2['unit_id']]:
					g2['count'] += g['count']
					find = True
			if not find:
				goods.append(g)
		Good.objects.filter(good_kind=good_kind).delete()
		for g in goods:
			Good.objects.create(count=g['count'], unit_id=g['unit_id'], location_id=g['location_id'],
			                    note=g['note'], good_kind_id=g['good_kind_id'], project_id=g['project_id'],
			                    defect=g['defect'], responsible_id=g['responsible_id'])
		return UpdateGoodKind(good_kind=good_kind)


class DeleteGoodKind(SngyMutation):
	result = Boolean()

	class Input:
		id = IntID(required=True)

	@permission_required('warehouse.delete_goodkind')
	def mutate_and_get_payload(self, info, id):
		try:
			if not GoodKind.objects.get(id=id).new:
				if info.context.user.has_perm('warehouse.can_moderate'):
					GoodKind.objects.get(id=id).delete()
				else:
					raise SngyException('Ошибка: Недостаточно прав!')
			else:
				GoodKind.objects.get(id=id).delete()
		except models.ProtectedError:
			raise SngyException('Данный вид товара используется товарами на складе')
		return DeleteGoodKind(result=True)


class ConfirmGoodKind(SngyMutation):
	result = Boolean()

	class Input:
		id = IntID(required=True)

	@permission_required('warehouse.can_moderate')
	def mutate_and_get_payload(self, info, id):
		user = info.context.user
		GoodKind.objects.filter(id=id).update(new=False, confirmed_id=user.id)
		return ConfirmGoodKind(result=True)


# noinspection PyUnusedLocal
class CreateManufacturer(SngyMutation):
	manufacturer = Field(ManufacturerType)

	class Input:
		name = String(required=True)

	@permission_required('warehouse.add_manufacturer')
	def mutate_and_get_payload(self, info, name):
		if name == "":
			raise SngyException("Пустое поле")
		try:
			manufacturer = Manufacturer.objects.create(name=name)
		except Exception:
			raise SngyException('Производитель с таким названием уже существует')
		return CreateManufacturer(manufacturer=manufacturer)


# noinspection PyUnusedLocal
class ChangeManufacturer(SngyMutation):
	result = Boolean()

	class Input:
		old_id = IntID(required=True)
		new_id = IntID(required=True)

	@permission_required('warehouse.change_manufacturer')
	def mutate_and_get_payload(self, info, old_id, new_id):
		if old_id == new_id:
			raise SngyException("Выбраны одинаковые поля")
		# Получили все товары от производителя oldId
		# назначаем этим товарам производителя newId
		goods = GoodKind.objects.filter(manufacturer_id=old_id).update(manufacturer_id=new_id)
		return ChangeManufacturer(result=True)


# noinspection PyUnusedLocal
class DeleteManufacturer(SngyMutation):
	result = Boolean()

	class Input:
		id = IntID(required=True)

	@permission_required('warehouse.delete_manufacturer')
	def mutate_and_get_payload(self, info, id):
		try:
			Manufacturer.objects.get(id=id).delete()
		except models.ProtectedError:
			raise SngyException('Данный производитель используется товарами на складе')
		return DeleteManufacturer(result=True)


# noinspection PyUnusedLocal
class RenameManufacturer(SngyMutation):
	result = Boolean()

	class Input:
		id = IntID(required=True)
		name = String(required=True)

	@permission_required('warehouse.change_manufacturer')
	def mutate_and_get_payload(self, info, id, name):
		if name == "":
			raise SngyException("Название не заполнено")
		try:
			Manufacturer.objects.filter(id=id).update(name=name)
		except Exception:
			raise SngyException('Производитель с таким названием уже существует')
		return ChangeManufacturer(result=True)


# noinspection PyUnusedLocal
class CreateWarehouse(SngyMutation):
	warehouse = Field(WarehouseType)

	class Input:
		name = String(required=True)
		project_id = IntID()
		user_id = IntID()

	@permission_required('warehouse.add_location')
	def mutate_and_get_payload(self, info, **kwargs):
		warehouse = Location.objects.create(**kwargs)
		return CreateWarehouse(warehouse=warehouse)


class ChangeWarehouse(SngyMutation):
	result = Boolean()

	class Input:
		old_warehouse = IntID(required=True)
		new_warehouse = IntID(required=True)
		id_good = IntID(required=True)
		count = Float(required=True)
		project_id = IntID()
		responsible_id = IntID(required=True)

	@permission_required('warehouse.change_location')
	def mutate_and_get_payload(self, info, old_warehouse, new_warehouse, id_good, count, responsible_id,
	                           project_id=None):
		try:
			if Location.objects.get(id=new_warehouse).project.state_id not in (2, 3, 4):
				raise SngyException('Этап проекта не допускает хранение на складе')
		except Location.DoesNotExist:
			raise SngyException('Местоположения не существует')
		if old_warehouse == new_warehouse:
			raise SngyException('Перемещение на тот же склад невозможно')
		good = Good.objects.get(id=id_good)
		if good.count < count:
			raise SngyException('В позиции нет такого количества товаров')
		if good.count == count:
			try:
				if good.defect or good.unit.restrict_sum:
					raise Good.DoesNotExist
				good_to = Good.objects.get(unit_id=good.unit_id, good_kind_id=good.good_kind_id,
				                           location_id=new_warehouse, defect=good.defect, responsible_id=responsible_id,
				                           project_id=project_id)
				good_to.count += count
				good_to.save()
				good.delete()
			except Good.DoesNotExist:
				good.location_id = new_warehouse
				good.responsible_id = responsible_id
				good.project_id = project_id
				good.save()
		else:
			try:
				if good.defect or good.unit.restrict_sum:
					raise Good.DoesNotExist
				good_to = Good.objects.get(unit_id=good.unit_id, good_kind_id=good.good_kind_id,
				                           location_id=new_warehouse, defect=good.defect, responsible_id=responsible_id,
				                           project_id=project_id)
				good_to.count += count
				good_to.save()
				good.count -= count
				good.save()
			except Good.DoesNotExist:
				Good.objects.create(count=count, unit_id=good.unit_id, location_id=new_warehouse, note=good.note,
				                    good_kind_id=good.good_kind_id, defect=good.defect, responsible_id=responsible_id,
				                    project_id=project_id)
				good.count -= count
				good.save()
		return ChangeWarehouse(result=True)


class Mutation(ObjectType):
	create_good = CreateGood.Field()
	create_good_kind = CreateGoodKind.Field()
	create_manufacturer = CreateManufacturer.Field()
	change_manufacturer = ChangeManufacturer.Field()
	delete_manufacturer = DeleteManufacturer.Field()
	rename_manufacturer = RenameManufacturer.Field()
	create_warehouse = CreateWarehouse.Field()

	update_good = UpdateGood.Field()
	update_good_kind = UpdateGoodKind.Field()
	update_good_kind_exsist_code = UpdateGoodKindExsistCode.Field()

	delete_good = DeleteGood.Field()
	delete_good_kind = DeleteGoodKind.Field()

	change_warehouse = ChangeWarehouse.Field()

	confirm_good_kind = ConfirmGoodKind.Field()
