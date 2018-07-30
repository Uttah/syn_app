import os.path
import datetime
from collections import OrderedDict
from graphene import ObjectType, Boolean, List, Float, String, Field
from graphene.types.datetime import Date
from crm.schema.types import IntID
from django.db import models
from django.contrib.contenttypes.models import ContentType
from crm.schema.mutation import SngyMutation
from synergycrm.exceptions import SngyException
from ..models import LogisticsTask, LogisticsRequestPosition, LogisticsRequest, TransferRequest, TransferPosition
from project_specifications.models import Specification, SpecificationsPositions
from warehouse.models import Good
from documents.models import Document, DocumentKind
from warehouse.models import Unit
from warehouse.models import Location
from comments.models import Comment
from projects.models import Project
from users.models import User
from notice.models import Notification
from ..schema.types import UploadIncomingOfferFileResultType, LogisticsRequestPositionType, LogisticsTaskType
from users.decorators import permission_required


def create_notifications(content_object, comment, exclude_user_id):
	content_type = ContentType.objects.get_for_model(type(content_object)())
	targets = list(set([c.user_id for c in Comment.objects.filter(content_type__app_label=content_type.app_label,
	                                                              content_type__model=content_type.model, object_id=content_object.id)]))
	if exclude_user_id in targets:
			targets.remove(exclude_user_id)
	for t in targets:
		text = 'Комментарий к заявке на закупку № %s: %s' % (content_object.id, comment)
		link = '/logistic_request/%s' % content_object.id
		Notification.objects.create(purpose_id=t, created_id=exclude_user_id, text=text, link=link)


class AddResponsibleInLogisticsRequest(SngyMutation):
	result = Boolean()

	class Input:
		request_id = IntID(required=True)
		worker_id = IntID(required=True)

	def mutate_and_get_payload(self, info, request_id, worker_id):
		try:
			logistics_request = LogisticsRequest.objects.get(id=request_id)
			responsible = [r.id for r in logistics_request.responsible.all()]
			gip = logistics_request.reason.project.gip
		except Exception:
			raise SngyException('Заявки на закупку не существует')
		if info.context.user != gip:
			raise SngyException('Вы не являетесь ГИПом проекта')
		if worker_id in responsible:
			raise SngyException('Сотрудник уже является ответственным')
		logistics_request.responsible.add(worker_id)
		comment = 'Назначен ответственным за заявку на закупку.'
		Comment.objects.create(content_object=logistics_request, user_id=worker_id, comment=comment)
		create_notifications(content_object=logistics_request, comment=comment, exclude_user_id=worker_id)
		return AddResponsibleInLogisticsRequest(result=True)


class CreateTaskForPositions(SngyMutation):
	result = Boolean()

	class Input:
		positions = List(IntID, required=True)

	def mutate_and_get_payload(self, info, positions):
		try:
			logistics_request = LogisticsRequestPosition.objects.get(id=positions[0]).request
			responsible = logistics_request.responsible.all()
			gip = logistics_request.reason.project.gip
		except Exception:
			raise SngyException('Нет позиции')
		if not info.context.user.has_perm('logistics.is_logist') and info.context.user not in responsible and gip != info.context.user:
			raise SngyException('Вы не логист, не ГИП проекта, и не ответственный у заявки на закупку')
		positions = LogisticsRequestPosition.objects.filter(id__in=positions)
		if positions.exclude(task=None):
			raise SngyException('Одна из выбранных позиций уже используется в другой задаче! Обновите страницу.')
		task = LogisticsTask.objects.create()
		positions.update(task=task)
		comment = 'Создана задача № %s.' % task.id
		Comment.objects.create(content_object=logistics_request, user=info.context.user, comment=comment)
		create_notifications(content_object=logistics_request, comment=comment, exclude_user_id=info.context.user.id)
		return CreateTaskForPositions(result=True)


class AddPositionInLogisticsRequest(SngyMutation):
	result = Boolean()

	class Input:
		request_id = IntID(required=True)
		good_kind_id = IntID(required=True)
		count = Float(required=True)
		unit_id = IntID(required=True)
		deadline = Date(required=True)

	def mutate_and_get_payload(self, info, **kwargs):
		try:
			logistics_request = LogisticsRequest.objects.get(id=kwargs['request_id'])
			responsible = logistics_request.responsible.all()
			gip = logistics_request.reason.project.gip
		except Exception:
			raise SngyException('Заявки на закупку не существует')
		if info.context.user not in responsible and gip != info.context.user:
			raise SngyException('Вы не ГИП проекта и не ответственный у заявки на закупку')
		max = LogisticsRequestPosition.objects.filter(request_id=kwargs['request_id']).aggregate(max=models.Max('number'))
		number = max['max'] + 1 if max['max'] else 1
		LogisticsRequestPosition.objects.create(number=number, **kwargs)
		comment = 'Добавлена позиция в заявку на закупку.'
		Comment.objects.create(content_object=logistics_request, user=info.context.user, comment=comment)
		create_notifications(content_object=logistics_request, comment=comment, exclude_user_id=info.context.user.id)
		return AddPositionInLogisticsRequest(result=True)


class ReplacePositionInLogisticsRequest(SngyMutation):
	result = Boolean()

	class Input:
		position_id = IntID(required=True)
		good_kind_id = IntID(required=True)
		count = Float(required=True)
		unit_id = IntID(required=True)
		deadline = Date(required=True)
		comment = String(required=True)

	def mutate_and_get_payload(self, info, position_id, comment, **kwargs):
		try:
			logistics_request_position = LogisticsRequestPosition.objects.get(id=position_id)
		except Exception:
			raise SngyException('Такой позиции нет')
		if logistics_request_position.task.responsible:
			if info.context.user != logistics_request_position.task.responsible:
				raise SngyException('Вы не ответственный у задачи')
		else:
			if info.context.user != logistics_request_position.request.reason.project.gip and info.context.user not in logistics_request_position.request.responsible.all():
				raise SngyException('Вы не ГИП проекта, и не ответственный у заявки на закупку')
		if logistics_request_position.finished_date:
			raise SngyException('Нельзя, т.к. позиция уже выполнена')
		does_replace = LogisticsRequestPosition.objects.filter(canceled_position=logistics_request_position).exists()
		if logistics_request_position.canceled and not does_replace:
			raise SngyException('Нельзя, т.к. позиция отменена')
		task_completed = True
		for lrp in LogisticsRequestPosition.objects.filter(task_id=logistics_request_position.task_id):
			if lrp.canceled:
				continue
			transferred_sum = TransferPosition.objects.filter(logistics_request_position=lrp).aggregate(sum=models.Sum('transferred'))['sum']
			transferred_sum = transferred_sum if transferred_sum else 0
			if lrp.count != transferred_sum:
				task_completed = False
				break
		if task_completed:
			raise SngyException('Нельзя, т.к. задача уже выполнена')
		transferred_sum = TransferPosition.objects.filter(logistics_request_position=logistics_request_position).aggregate(sum=models.Sum('transferred'))['sum']
		transferred_sum = transferred_sum if transferred_sum else 0
		# TODO: ПИЗДЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЦ
		# if transferred_sum:
		# 	goods = Good.objects.filter(good_kind=logistics_request_position.good_kind, unit=logistics_request_position.unit, location__project=logistics_request_position.request.reason.project)
		# 	returned = 0
		# 	for g in goods:
		# 		if transferred_sum == returned:
		# 			break
		# 		try:
		# 			good = Good.objects.get(good_kind=logistics_request_position.good_kind, unit=logistics_request_position.unit, location_id=1)
		# 			returned += g.count
		# 			good.count += g.count
		# 			g.delete()
		# 			good.save()
		# 		except good.DoesNotExist:
		# 			g.location_id = 1
		# 			g.save()
		TransferPosition.objects.filter(logistics_request_position=logistics_request_position, transfer_request__completed=False).delete()
		TransferRequest.objects.filter(transferposition=None, completed=False).distinct().delete()
		max = LogisticsRequestPosition.objects.filter(request=logistics_request_position.request).aggregate(max=models.Max('number'))
		number = max['max'] + 1 if max['max'] else 1
		if logistics_request_position.task.responsible:
			LogisticsTask.objects.filter(id=logistics_request_position.task_id).update(work_started=True)

		logistics_request_position.canceled = True
		logistics_request_position.save()

		LogisticsRequestPosition.objects.create(number=number, canceled_position_id=position_id, request=logistics_request_position.request, task=logistics_request_position.task, **kwargs)
		comment = "Причины замены позиции № %d в задаче № %d: %s." % (logistics_request_position.number,
		                                                                logistics_request_position.task.id,
		                                                                comment)
		Comment.objects.create(content_object=logistics_request_position.request, user=info.context.user, comment=comment)
		comment = 'Заменена позиция в задаче № %s.' % logistics_request_position.task.id
		create_notifications(content_object=logistics_request_position.request, comment=comment, exclude_user_id=info.context.user.id)
		return ReplacePositionInLogisticsRequest(result=True)


class DeletePositionFromTask(SngyMutation):
	result = Boolean()

	class Input:
		position_id = IntID(required=True)

	def mutate_and_get_payload(self, info, position_id):
		try:
			lrp = LogisticsRequestPosition.objects.get(id=position_id)
		except LogisticsRequestPosition.DoesNotExist:
			raise SngyException('Такой позиции не существует')
		if lrp.finished_date:
			raise SngyException('Нельзя, т.к. позиция уже выполнена')
		if lrp.canceled:
			raise SngyException('Нельзя, т.к. позиция отменена')
		if lrp.task.responsible:
			if info.context.user != lrp.task.responsible:
				raise SngyException('Вы не ответственный у задачи')
		else:
			if info.context.user != lrp.request.reason.project.gip and info.context.user not in lrp.request.responsible.all():
				raise SngyException('Вы не ГИП проекта, и не ответственный у заявки на закупку')
		if LogisticsRequestPosition.objects.filter(canceled_position_id=lrp.id):
			raise SngyException('Позиция является заменой')
		if TransferPosition.objects.filter(logistics_request_position_id=lrp.id).aggregate(sum=models.Sum('transferred'))['sum']:
			raise SngyException('Нельзя, т.к. были перемещения')
		if lrp.order_date or lrp.expected_date:
			raise SngyException('Нельзя, т.к. указана дата заказа или ожидаемая дата поставки')
		task = lrp.task
		task_id = task.id
		lrp.task = None
		lrp.save()
		transfer_positions = TransferPosition.objects.filter(logistics_request_position=lrp)
		if transfer_positions:
			transfer_request = transfer_positions[0].transfer_request
			transfer_positions.delete()
			if not transfer_request.transferposition_set.all():
				transfer_request.delete()
		if not task.logisticsrequestposition_set.all():
			task.delete()
		if task.id:
			comment = 'Удалена позиция № %d из задачи № %d.' % (lrp.number, task_id)
		else:
			comment = 'Удалена позиция из задачи № %s и сама задача, т.к. у нее не осталось позиций.' % task_id
		Comment.objects.create(content_object=lrp.request, user=info.context.user, comment=comment)
		create_notifications(content_object=lrp.request, comment=comment, exclude_user_id=info.context.user.id)
		return DeletePositionFromTask(result=True)


class DeletePositionFromLogisticsRequest(SngyMutation):
	result = Boolean()

	class Input:
		position_id = IntID(required=True)

	def mutate_and_get_payload(self, info, position_id):
		try:
			logistics_request_position = LogisticsRequestPosition.objects.get(id=position_id)
		except LogisticsRequestPosition.DoesNotExist:
			raise SngyException('Такой позиции не существует')
		if logistics_request_position.finished_date:
			raise SngyException('Нельзя, т.к. позиция уже выполнена')
		if logistics_request_position.canceled:
			raise SngyException('Нельзя, т.к. позиция отменена')
		if logistics_request_position.task.responsible:
			if info.context.user != logistics_request_position.task.responsible:
				raise SngyException('Вы не ответственный у задачи')
		else:
			if info.context.user != logistics_request_position.request.reason.project.gip and info.context.user not in logistics_request_position.request.responsible.all():
				raise SngyException('Вы не ГИП проекта, и не ответственный у заявки на закупку')
		task_completed = True
		for lrp in LogisticsRequestPosition.objects.filter(task_id=logistics_request_position.task_id):
			if lrp.canceled:
				continue
			transferred_sum = TransferPosition.objects.filter(logistics_request_position=lrp).aggregate(sum=models.Sum('transferred'))['sum']
			transferred_sum = transferred_sum if transferred_sum else 0
			if lrp.count != transferred_sum:
				task_completed = False
				break
		if task_completed:
			raise SngyException('Нельзя, т.к. задача уже выполнена')
		transferred_sum = TransferPosition.objects.filter(logistics_request_position=logistics_request_position).aggregate(sum=models.Sum('transferred'))['sum']
		transferred_sum = transferred_sum if transferred_sum else 0
		# TODO: ПИЗДЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЦ
		# if transferred_sum:
		# 	goods = Good.objects.filter(good_kind=logistics_request_position.good_kind, unit=logistics_request_position.unit, location__project=logistics_request_position.request.reason.project)
		# 	returned = 0
		# 	for g in goods:
		# 		if transferred_sum == returned:
		# 			break
		# 		try:
		# 			good = Good.objects.get(good_kind=logistics_request_position.good_kind, unit=logistics_request_position.unit, location_id=1)
		# 			returned += g.count
		# 			good.count += g.count
		# 			g.delete()
		# 			good.save()
		# 		except good.DoesNotExist:
		# 			g.location_id = 1
		# 			g.save()
		TransferPosition.objects.filter(logistics_request_position=logistics_request_position, transfer_request__completed=False).delete()
		TransferRequest.objects.filter(transferposition=None, completed=False).distinct().delete()
		logistics_request_position.canceled = True
		logistics_request_position.save()
		comment = 'Удалена позиция из заявки на закупку в задаче № %s.' % logistics_request_position.task.id
		Comment.objects.create(content_object=logistics_request_position.request, user=info.context.user, comment=comment)
		create_notifications(content_object=logistics_request_position.request, comment=comment, exclude_user_id=info.context.user.id)
		return DeletePositionFromLogisticsRequest(result=True)


class RefuseTask(SngyMutation):
	result = Boolean()

	class Input:
		task_id = IntID(required=True)

	@permission_required('logistics.is_logist')
	def mutate_and_get_payload(self, info, task_id):
		task_completed = True
		for lrp in LogisticsRequestPosition.objects.filter(task_id=task_id):
			if lrp.canceled:
				continue
			transferred_sum = TransferPosition.objects.filter(logistics_request_position=lrp).aggregate(sum=models.Sum('transferred'))['sum']
			transferred_sum = transferred_sum if transferred_sum else 0
			if lrp.count != transferred_sum:
				task_completed = False
				break
		if task_completed:
			raise SngyException('Нельзя, т.к. задача уже выполнена')
		try:
			lt = LogisticsTask.objects.get(id=task_id)
			if lt.responsible != info.context.user:
				raise SngyException('Ответственный не вы')
			if lt.responsible.gender == 'M':
				comment = 'Отказался от задачи № %s.' % lt.id
			else:
				comment = 'Отказалась от задачи № %s.' % lt.id
			positions = lt.logisticsrequestposition_set.all()
			if positions:
				request = positions[0].request
			else:
				raise SngyException('У задачи отсутствуют позиции')
			Comment.objects.create(content_object=request, user=info.context.user, comment=comment)
			create_notifications(content_object=request, comment=comment, exclude_user_id=info.context.user.id)
			lt.responsible = None
			lt.work_started = True
			lt.save()
		except LogisticsTask.DoesNotExist:
			raise SngyException('Нет такой задачи')
		return RefuseTask(result=True)


class TakeTask(SngyMutation):
	result = Boolean()

	class Input:
		task_id = IntID(required=True)

	@permission_required('logistics.is_logist')
	def mutate_and_get_payload(self, info, task_id):
		try:
			lt = LogisticsTask.objects.get(id=task_id)
			lt.responsible = info.context.user
			lt.save()
			if lt.responsible.gender == 'M':
				comment = 'Взял в работу задачу № %s.' % lt.id
			else:
				comment = 'Взяла в работу задачу № %s.' % lt.id
			positions = lt.logisticsrequestposition_set.all()
			if positions:
				request = positions[0].request
			else:
				raise SngyException('У задачи отсутствуют позиции')
			Comment.objects.create(content_object=request, user=info.context.user, comment=comment)
			create_notifications(content_object=request, comment=comment, exclude_user_id=info.context.user.id)
		except LogisticsTask.DoesNotExist:
			raise SngyException('Нет такой задачи')
		return RefuseTask(result=True)


class DisbandTask(SngyMutation):
	result = Boolean()

	class Input:
		task_id = IntID(required=True)

	def mutate_and_get_payload(self, info, task_id):
		try:
			lt = LogisticsTask.objects.get(id=task_id)
			if lt.responsible:
				if info.context.user != lt.responsible:
					raise SngyException('Вы не ответственный у задачи')
			else:
				request = lt.logisticsrequestposition_set.all()[0].request
				if info.context.user != request.reason.project.gip and info.context.user not in request.responsible.all():
					raise SngyException('Вы не ГИП проекта, и не ответственный у заявки на закупку')
			if lt.work_started:
				raise SngyException('Невозможно расформировать задачу')
			transfer_request = None
			for lrp in lt.logisticsrequestposition_set.all():
				if lrp.canceled_position:
					raise SngyException('Невозможно расформировать задачу, т.к. были замены')
				for tp in lrp.transferposition_set.all():
					if tp.transferred and tp.transfer_request.ready_to_go:
						raise SngyException('Невозможно расформировать задачу, т.к. были перемещения')
					transfer_request = tp.transfer_request
			if transfer_request:
				transfer_request.delete()
			request = LogisticsRequestPosition.objects.filter(task_id=task_id)[0].request
			LogisticsRequestPosition.objects.filter(task_id=task_id).update(task=None, canceled_position=None, canceled=False)
			if info.context.user.gender == 'M':
				comment = 'Расформировал задачу № %s.' % lt.id
			else:
				comment = 'Расформировала задачу № %s.' % lt.id
			Comment.objects.create(content_object=request, user=info.context.user, comment=comment)
			create_notifications(content_object=request, comment=comment, exclude_user_id=info.context.user.id)
			lt.delete()
		except LogisticsTask.DoesNotExist:
			raise SngyException('Нет такой задачи')
		return DisbandTask(result=True)


class RenameTask(SngyMutation):
	result = Field(LogisticsTaskType)

	class Input:
		task_id = IntID(required=True)
		name = String(required=True)

	def mutate_and_get_payload(self, info, task_id, name):
		name = name.strip()
		if name == '':
			raise SngyException('Не указано название задачи')
		try:
			task = LogisticsTask.objects.get(id=task_id)
		except LogisticsTask.DoesNotExist:
			raise SngyException('Указанная задача на закупку не существует')
		request = task.logisticsrequestposition_set.first().request
		user = info.context.user
		if task.responsible is not None:
			responsible = [task.responsible]
		else:
			responsible = list(request.responsible.all()) + [request.reason.project.gip]
		if user not in responsible:
			raise SngyException('У вас нет прав на редатирование названия данной задачи')
		task.name = name
		task.save()
		return RenameTask(result=task)


class CreateTransferPosition(SngyMutation):
	result = Boolean()

	class Input:
		restrict_sum = Boolean(required=True)
		stock_id = IntID()
		need_count = Float()
		position_id = IntID(required=True)
		count = Float()
		can_different_tasks = Boolean()

	@permission_required('logistics.is_logist')
	def mutate_and_get_payload(self, info, restrict_sum, need_count, position_id, stock_id=None, count=None, can_different_tasks=False):
		try:
			lrp = LogisticsRequestPosition.objects.get(id=position_id)
		except Exception:
			raise SngyException('Нет такой позиции')
		if lrp.task:
			if lrp.task.responsible != info.context.user:
				raise SngyException('Ошибка: Вы не являетесь исполнителем задачи')
		if lrp.canceled:
			raise SngyException('Нельзя, т.к. позиция отменена')
		# Добавить проверку на статус задачи
		total = Good.objects.filter(good_kind=lrp.good_kind, unit=lrp.unit, location__id=1, defect=False, responsible_id=120).aggregate(total=models.Sum('count'))['total']
		total = total if total else 0
		transfer_1 = TransferPosition.objects.filter(logistics_request_position=lrp, transferred=None).aggregate(transfer=models.Sum('count'))['transfer']
		transfer_2 = TransferPosition.objects.filter(logistics_request_position=lrp).aggregate(transfer=models.Sum('transferred'))['transfer']
		transfer_1 = transfer_1 if transfer_1 else 0
		transfer_2 = transfer_2 if transfer_2 else 0
		transfer = transfer_1 + transfer_2
		available = total - transfer
		# Если Метры или другие не склеивающиеся ед изм.
		if restrict_sum:
			if need_count > available:
				raise SngyException('Сумма перемещений и количества больше необходимого количества')
			if not stock_id:
				raise SngyException('Не указана складская позиция')
			try:
				g = Good.objects.get(id=stock_id)
			except Exception:
				raise SngyException('На складе нет такой позиции')
			# Проверка отключена, так как можно перемещать отрезки меньшей длины
			# if g.count < lrp.count:
			# 	raise SngyException('Длина меньше необходимой')

		# Если Штуки или другие суммирующиеся ед изм.
		if not restrict_sum:
			if count <= 0:
				raise SngyException('Введённое количество должно быть больше 0')
			if count > lrp.count:
				raise SngyException('Введённое количество больше необходимого')
			if transfer + count > lrp.count:
				raise SngyException('Введённое количество больше доступного')
		transfer_request = TransferRequest.objects.filter(who_requested=info.context.user, ready_to_go=False)
		if transfer_request:
			transfer_request = transfer_request[0]
			transferposition_set = transfer_request.transferposition_set.all()
			if transferposition_set:
				if not can_different_tasks and transferposition_set[0].logistics_request_position.task_id != lrp.task_id:
					raise SngyException('Завершите предыдущую заявку на перемещение')
		else:
			# Если уже начали создавать новую заявку на перемещения и выбрали другой проект
			if TransferRequest.objects.filter(who_requested=info.context.user, ready_to_go=False).count() >= 1:
				raise SngyException('Завершите предыдущую заявку на перемещение')
			transfer_request = TransferRequest.objects.create(who_requested=info.context.user,
			                                                  creation_date=datetime.datetime.now() )

		# Если Штуки или другие суммирующиеся ед изм.
		if not restrict_sum:
			# Может быть некондиция, тогда ?
			try:
				good = Good.objects.get(good_kind=lrp.good_kind, unit=lrp.unit, defect=False, location__id=1, responsible_id=120)
			except Good.DoesNotExist:
				raise SngyException('Нет на складе')
			TransferPosition.objects.create(good=good, count=count, transfer_request=transfer_request,
			                                logistics_request_position=lrp)

		# Если Метры или другие не склеивающиеся ед изм.
		if restrict_sum:
			TransferPosition.objects.create(good=g, count=need_count, transfer_request=transfer_request,
			                                logistics_request_position=lrp)
		return CreateTransferPosition(result=True)


class ChangeReadyToGo(SngyMutation):
	result = Boolean()

	class Input:
		request_id = IntID(required=True)
		transfer_request_id = IntID(required=True)

	@permission_required('logistics.is_logist')
	def mutate_and_get_payload(self, info, request_id, transfer_request_id):
		try:
			request = LogisticsRequest.objects.get(id=request_id)
		except LogisticsRequest.DoesNotExist:
			raise SngyException('Заявка на закупку не существует')
		try:
			tr = TransferRequest.objects.get(id=transfer_request_id)
			tr.ready_to_go = True
			tr.where_id = request.location_id
			tr.save()
			text = 'Создана заявка на перемещение № %s.' % tr.id
			link = '/transfer_request/%s' % tr.id
			for u in User.objects.all():
				if u.has_perm('logistics.can_work_transfer_request') and not u.is_superuser:
					Notification.objects.create(purpose=u, created=info.context.user, text=text, link=link)
		except TransferRequest.DoesNotExist:
			raise SngyException('Такой заявки на перемещения не существует')
		return ChangeReadyToGo(result=True)


class DeleteTransferRequest(SngyMutation):
	result = Boolean()

	class Input:
		transfer_request_id = IntID(required=True)

	@permission_required('logistics.is_logist')
	def mutate_and_get_payload(self, info, transfer_request_id):
		try:
			tr = TransferRequest.objects.get(id=transfer_request_id, ready_to_go=False)
			transfer_positions = tr.transferposition_set.all()
			if transfer_positions:
				if info.context.user != transfer_positions[0].logistics_request_position.task.responsible:
					raise SngyException('Вы не ответственный')
			else:
				if info.context.user != tr.who_requested:
					raise SngyException('Вы не ответственный')
			for tp in tr.transferposition_set.all():
				if tp.transferred:
					raise SngyException('Нельзя, т.к. уже есть перемещения')
				tp.delete()
			tr.delete()
		except TransferRequest.DoesNotExist:
			raise SngyException('Такой заявки на перемещение не существует')
		return DeleteTransferRequest(result=True)


class TransferAll(SngyMutation):
	result = Boolean()

	class Input:
		request_id = IntID(required=True)
		positions_id = List(IntID, required=True)

	@permission_required('logistics.is_logist')
	def mutate_and_get_payload(self, info, request_id, positions_id):
		transfer_request = None
		positions = LogisticsRequestPosition.objects.filter(id__in=positions_id, canceled=False)
		try:
			request = LogisticsRequest.objects.get(id=request_id)
		except LogisticsRequest.DoesNotExist:
			raise SngyException('Указанной заявки на закупку не существует')
		task = None
		canceled_positions_id = [clrp.canceled_position_id for clrp in LogisticsRequestPosition.objects.filter().exclude(canceled_position=None)]
		for p in positions:
			if p.id in canceled_positions_id:
				continue
			if not task:
				task = p.task
			if p.task.id != task.id:
				raise SngyException('Позиции имеют разные задачи')
		if task.responsible != info.context.user:
			raise SngyException('Вы не ответственный у этой задачи')
		for p in positions:
			good = Good.objects.filter(good_kind=p.good_kind, unit=p.unit, defect=False, location__id=1, responsible_id=120)
			if good:
				if not p.unit.restrict_sum:
					good = good[0]
				else:
					good = good.filter(count__gte=p.count).order_by('count')
					if good:
						good = good[0]
					else:
						continue
				transfer_sum = TransferPosition.objects.filter(logistics_request_position=p).aggregate(sum=models.Sum('transferred'))['sum']
				transfer_sum = transfer_sum if transfer_sum else 0
				available = good.count - transfer_sum
				count = 0
				if available >= p.count:
					count = p.count - transfer_sum
				if available < p.count:
					count = p.count - ((available - p.count) * -1) - transfer_sum
				if count > 0 and transfer_sum < p.count:
					if not transfer_request:
						transfer_request = TransferRequest.objects.create(who_requested=info.context.user,
						                                                  where=request.location, ready_to_go=True,
						                                                  creation_date=datetime.datetime.now())
						text = 'Создана заявка на перемещение № %s.' % transfer_request.id
						link = '/transfer_request/%s' % transfer_request.id
						for u in User.objects.all():
							if u.has_perm('logistics.can_work_transfer_request') and not u.is_superuser:
								Notification.objects.create(purpose=u, created=info.context.user, text=text, link=link)
					TransferPosition.objects.create(good=good, count=count,
					                                transfer_request=transfer_request,
					                                logistics_request_position=p)
		if not transfer_request:
			raise SngyException('У всех позиций отсутствует доступное количество для перемещения или перемещенное количество больше необходимого')
		return TransferAll(result=True)


class EditPosition(SngyMutation):
	result = Field(LogisticsRequestPositionType)

	class Input:
		position_id = IntID(required=True)
		order_date = Date()
		expected_date = Date()
		deadline = Date()
		count = Float()
		unit_id = IntID()

	def mutate_and_get_payload(self, info, position_id, order_date=None, expected_date=None, deadline=None, count=None, unit_id=None):
		try:
			position = LogisticsRequestPosition.objects.get(id=position_id)
			if position.finished_date:
				raise SngyException('Нельзя, т.к. позиция уже выполнена')
			responsible = list(position.request.responsible.all()) + [position.request.reason.project.gip]
			if position.task and position.task.responsible:
				responsible += [position.task.responsible]
			if info.context.user not in responsible:
				raise SngyException('Вы не ответственный за данную позицию')
			if order_date:
				if not position.task.files.all():
					raise SngyException('Отсутствуют прикрепленные к задаче файлы')
				position.order_date = order_date
			if expected_date:
				if not position.task.files.all():
					raise SngyException('Отсутствуют прикрепленные к задаче файлы')
				position.expected_date = expected_date
				if not position.order_date:
					position.order_date = datetime.datetime.now()
			if deadline:
				position.deadline = deadline
			if count and unit_id:
				position.count = count
				try:
					Unit.objects.get(id=unit_id)
				except Exception:
					raise SngyException('Такой единицы измерения не существует')
				position.unit_id = unit_id
			position.save()
		except LogisticsRequestPosition.DoesNotExist:
			raise SngyException('Такой позиции нет')
		return EditPosition(result=position)


class UploadIncomingOfferFile(SngyMutation):
	result = List(UploadIncomingOfferFileResultType)

	class Input:
		task_id = IntID(required=True)

	def mutate_and_get_payload(self, info, task_id):
		if not info.context.FILES.get('file'):
			raise SngyException('Отсутствует файл')
		try:
			task = LogisticsTask.objects.get(id=task_id)
		except LogisticsTask.DoesNotExist:
			raise SngyException('Задача не существует')
		if task.responsible:
			if info.context.user != task.responsible:
				raise SngyException('Вы не ответственный у задачи')
		else:
			request = task.logisticsrequestposition_set.all()[0].request
			if info.context.user != request.reason.project.gip and info.context.user not in request.responsible.all() and info.context.user != request.who_requested:
				raise SngyException('Вы не ГИП проекта, не ответственный у заявки на закупку, и не запросивший')
		if task.files.count() > 0:
			raise SngyException('Нельзя прикладывать больше одного счета')
		try:
			document_kind = DocumentKind.objects.get(eng_name='incoming_offer')
		except DocumentKind.DoesNotExist:
			document_kind = DocumentKind.objects.create(name='Входящие счета', eng_name='incoming_offer')
		document = Document.objects.create(created_by=info.context.user, document_kind=document_kind, is_real=False, file=info.context.FILES['file'])
		task.files.add(document)
		result = []
		for d in task.files.all():
			name = os.path.split(d.file.name)[-1].split('_', maxsplit=1)[1]
			result.append(UploadIncomingOfferFileResultType(name=name, kind='incoming_offer', id=d.id))
		return UploadIncomingOfferFile(result=result)


class DeleteIncomingOfferFile(SngyMutation):
	result = Boolean()

	class Input:
		id = IntID(required=True)
		kind = String(required=True)

	def mutate_and_get_payload(self, info, id, kind):
		try:
			document = Document.objects.get(id=id, document_kind__eng_name=kind)
		except Document.DoesNotExist:
			raise SngyException('Такого документа не существует')
		task = document.logisticstask_set.all()
		if task:
			task = task[0]
			if task.responsible:
				if info.context.user != task.responsible:
					raise SngyException('Вы не ответственный у задачи')
			else:
				request = task.logisticsrequestposition_set.all()[0].request
				if info.context.user != request.reason.project.gip and info.context.user not in request.responsible.all():
					raise SngyException('Вы не ГИП проекта, и не ответственный у заявки на закупку')
			if Document.objects.filter(file=document.file).count() == 1:
				document.file.delete()
			document.delete()
		return DeleteIncomingOfferFile(result=True)


class CreateApplication(SngyMutation):
	result = IntID()

	class Input:
		id_spec = IntID(required=True)
		deadline = String(required=True)
		worker = List(IntID)
		location_name = String()

	def mutate_and_get_payload(self, info, **kwargs):
		user = info.context.user
		specification = Specification.objects.get(id=kwargs['id_spec'])
		if user.id != specification.project.gip.id:
			raise SngyException('Ошибка: Нет доступа!')
		spec_rows = list(SpecificationsPositions.objects.filter(specification_id=kwargs['id_spec']).order_by('position_in_table').values())
		# all_data - это SpecificationsPositions
		# Отсортировано по полю position_in_table
		my_new_rows = OrderedDict({})
		saved_row = None
		all_unit_id = None
		for spec_row in spec_rows:
			if spec_row['grouping_name'] is not None:
				continue
			if spec_row['good_kind_id'] in my_new_rows and spec_row['unit_id'] == my_new_rows[spec_row['good_kind_id']]['unit_id']:
				data = spec_row['good_kind_id']
				my_new_rows[data]['count'] += spec_row['count']
			else:
				my_new_rows[spec_row['good_kind_id']] = spec_row
		lr = LogisticsRequest.objects.filter(object_id=kwargs['id_spec'])
		if lr:
			if isinstance(lr[0].reason, Specification):
				raise SngyException('Заявка на текущую спецификацию уже существует')
			raise SngyException('Заявка на текущую спецификацию уже существует(НЕ ПРОЕКТНАЯ СПЕЦИФИКАЦИЯ)')
		# Создаем склад для заявки
		default_location_name = 'Склад {:05d} - {}'.format(specification.project.number, specification.pressmark)
		location_name = kwargs.get('location_name', default_location_name)
		# Ответственный - Михалев
		# TODO: Придумать какой-нибудь способ идентификации завскладом без необходимости завязки на конкретный ID
		location = Location.objects.create(name=location_name, project=specification.project, responsible_id=120)
		buy_requisition = LogisticsRequest.objects.create(who_requested_id=user.id, when_requested=datetime.datetime.now().date(),
		                                                  deadline=kwargs['deadline'], reason=specification, location=location)
		comment = 'Создана заявка на закупку № %s.' % buy_requisition.id
		Comment.objects.create(content_object=buy_requisition, user=buy_requisition.reason.project.gip, comment=comment)
		# Рассылка уведомлений ответственным
		text = 'Вы являетесь ответственным за заявку на закупку № %s.' % buy_requisition.id
		link = '/logistic_request/%s' % buy_requisition.id
		comment = 'Назначен ответственным за заявку на закупку.'
		for worker in kwargs['worker']:
			buy_requisition.responsible.add(worker)
			Comment.objects.create(content_object=buy_requisition, user_id=worker, comment=comment)
			Notification.objects.create(purpose_id=worker, created=buy_requisition.reason.project.gip, text=text, link=link)
		counter = 0
		for row in my_new_rows:
			counter += 1
			LogisticsRequestPosition.objects.create(number=counter, good_kind_id=my_new_rows[row]['good_kind_id'], count=my_new_rows[row]['count'],
			                                        unit_id=my_new_rows[row]['unit_id'], request_id=buy_requisition.id,
			                                        deadline=buy_requisition.deadline)
		return CreateApplication(result=buy_requisition.id)


class AddWorkerInTransferRequest(SngyMutation):
	result = Boolean()

	class Input:
		worker = IntID(required=True)
		transfer_request = IntID(required=True)

	@permission_required('logistics.can_work_transfer_request')
	def mutate_and_get_payload(self, info, worker, transfer_request):
		requrst = TransferRequest.objects.get(id=transfer_request)
		requrst.worker_id = worker
		requrst.save()
		return AddWorkerInTransferRequest(result=True)


class WorkerRefuseInTransferRequest(SngyMutation):
	result = Boolean()

	class Input:
		worker = IntID(required=True)
		transfer_request = IntID(required=True)

	def mutate_and_get_payload(self, info, worker, transfer_request):
		if not info.context.user.id == worker:
			raise SngyException('Ошибка: Вы не являетесь исполнителем!')
		requrst = TransferRequest.objects.get(id=transfer_request)
		requrst.worker = None
		requrst.save()
		return WorkerRefuseInTransferRequest(result=True)


class UpdateTransferPositions(SngyMutation):
	result = Boolean()

	class Input:
		transfer_position_id = IntID(required=True)
		transfer = Float(required=True)

	@permission_required('logistics.can_work_transfer_request')
	def mutate_and_get_payload(self, info, transfer_position_id, transfer):
		position = TransferPosition.objects.get(id=transfer_position_id)
		# Проверка на метры и т.д.
		if position.good.unit.restrict_sum and position.count > transfer and float(transfer) != 0:
			raise SngyException('Ошибка: Несуммируемый товар нельзя перенести меньше необходимого!')
		if not position.good.unit.restrict_sum and position.count < transfer:
			raise SngyException('Ошибка: Нельзя перенести количество больше необходимого!')
		if position.good.unit.restrict_sum and position.good.count < transfer:
			raise SngyException('Ошибка: Нельзя перенести больше возможного!')
		position.transferred = transfer
		position.save()
		return UpdateTransferPositions(result=True)


# Закрытие перемещения при его выполнениии
class CompletedTransferRequest(SngyMutation):
	result = Boolean()

	class Input:
		transfer_request = IntID(required=True)

	def mutate_and_get_payload(self, info, transfer_request):
		from warehouse.models import Good
		request = TransferRequest.objects.get(id=transfer_request)
		if request.completed:
			raise SngyException('Ошибка: Заявка уже выполнена!')
		positions = TransferPosition.objects.filter(transfer_request_id=transfer_request)
		if info.context.user.id != request.worker.id:
			raise SngyException('Ошибка: Недостаточно прав!')
		for position in positions:
			lrp = LogisticsRequestPosition.objects.get(id=position.logistics_request_position.id, unit_id=position.good.unit_id, good_kind_id=position.good.good_kind_id)

			good = Good.objects.filter(unit_id=position.good.unit_id, good_kind_id=position.good.good_kind_id,
			                        location_id=position.good.location_id, defect=position.good.defect, responsible_id=position.good.responsible_id,
			                        project_id=position.good.project_id)

			if position.good.unit.restrict_sum:
				for g in good:
					transfer_sum = TransferPosition.objects.filter(logistics_request_position_id=lrp.id, good=g)
					for ts in transfer_sum:
						if ts.count is not None:
							good = ts.good
			else:
				good = position.good

			# Если по какой-то причине на складе всё же меньше товаров чем перемещено
			if good.count < position.transferred:
				raise SngyException('Ошибка: В позиции нет такого количества товаров!')
			if good.count == position.transferred:
				try:
					if good.unit.restrict_sum:
						raise Good.DoesNotExist()
					good_to = Good.objects.get(unit_id=good.unit_id, good_kind_id=good.good_kind_id,
					                           location_id=request.where.id, defect=good.defect, responsible_id=good.responsible_id,
					                           project_id=request.where.project_id)
					good_to.count += position.transferred
					good_to.save()
					# TODO: теряется прошлое местоположение, переделка БД.
					good.delete()
				except Good.DoesNotExist:
					good.location_id = request.where.id
					good.responsible_id = good.responsible_id
					good.project_id = request.where.project_id
					good.save()
			else:
				try:
					good_to = Good.objects.get(unit_id=good.unit_id, good_kind_id=good.good_kind_id,
					                           location_id=request.where.id, defect=good.defect, responsible_id=good.responsible_id,
					                           project_id=request.where.project_id)
					good_to.count += position.transferred
					good_to.save()
					good.count -= position.transferred
					good.save()
				except Good.DoesNotExist:
					Good.objects.create(count=position.transferred, unit_id=good.unit_id, location_id=request.where.id, note=good.note,
					                    good_kind_id=good.good_kind_id, defect=good.defect, responsible_id=good.responsible_id,
					                    project_id=request.where.project_id)
					good.count -= position.transferred
					good.save()

		request.completed = True
		transferred_equal_requested = True
		for tp in request.transferposition_set.all():
			lrp = tp.logistics_request_position
			transferred = TransferPosition.objects.filter(logistics_request_position=lrp).aggregate(sum=models.Sum('transferred'))['sum']
			transferred = transferred if transferred else 0
			if lrp.count <= transferred:
				lrp.finished_date = datetime.datetime.now()
				lrp.save()
			if tp.count != tp.transferred:
				transferred_equal_requested = False
		if lrp:
			if transferred_equal_requested:
				text = 'Выполнено перемещение для задачи № %s, в заявке на закупку № %s.' % (lrp.task.id, lrp.request.id)
				notification_type = 'S'
			else:
				text = 'Выполнено перемещение для задачи № %s, в заявке на закупку № %s. Есть позиции с количеством, отличающимся от запрошенного.' % (lrp.task.id, lrp.request.id)
				notification_type = 'W'
			link = '/logistic_request/%s' % lrp.request.id
			Notification.objects.create(purpose=lrp.task.responsible, created=info.context.user, text=text, type=notification_type, link=link)
			Notification.objects.create(purpose=lrp.request.reason.project.gip, created=info.context.user, text=text, type=notification_type, link=link)
			for r in lrp.request.responsible.all():
				Notification.objects.create(purpose=r, created=info.context.user, text=text, type=notification_type, link=link)
		request.save()
		return CompletedTransferRequest(result=True)


class DeleteTransferRequestInTransfer(SngyMutation):
	result = Boolean()

	class Input:
		transfer_request = IntID(required=True)

	def mutate_and_get_payload(self, info, transfer_request):
		request = TransferRequest.objects.get(id=transfer_request)
		if info.context.user.id != request.who_requested_id:
			raise SngyException('Ошибка: Недостаточно прав!')
		positions = TransferPosition.objects.filter(transfer_request_id=transfer_request)
		for position in positions:
			position.delete()
		request.delete()
		return DeleteTransferRequest(result=True)


class PublishRequest(SngyMutation):
	result = Boolean()

	class Input:
		request_id = IntID(required=True)

	def mutate_and_get_payload(self, info, request_id):
		try:
			request = LogisticsRequest.objects.get(id=request_id)
		except LogisticsRequest.DoesNotExist:
			raise SngyException('Заявка на закупку не существует')
		responsible = list(request.responsible.all()) + [request.reason.project.gip]
		if info.context.user not in responsible:
			raise SngyException('Вы не ответственный за эту задачу')
		request.ready_for_work = True
		request.save()
		# Комментарий о передаче в работу
		comment = 'Заявка передана в работу'
		Comment.objects.create(content_object=request, user_id=info.context.user, comment=comment)
		# Рассылка уведомлений логистам
		text = 'Заявка на закупку № {} передана в работу.'.format(request.id)
		link = '/logistic_request/{}'.format(request.id)
		for u in User.objects.all():
			if u.has_perm('logistics.is_logist') and not u.is_superuser:
				Notification.objects.create(purpose=u, created=info.context.user, text=text, link=link)
		return PublishRequest(True)


class Mutation(ObjectType):
	add_responsible_in_logistics_request = AddResponsibleInLogisticsRequest.Field()
	create_task_for_positions = CreateTaskForPositions.Field()
	add_position_in_logistics_request = AddPositionInLogisticsRequest.Field()
	replace_position_in_logistics_request = ReplacePositionInLogisticsRequest.Field()
	delete_position_from_task = DeletePositionFromTask.Field()
	delete_position_from_logistics_request = DeletePositionFromLogisticsRequest.Field()
	publish_request = PublishRequest.Field()
	refuse_task = RefuseTask.Field()
	take_task = TakeTask.Field()
	disband_task = DisbandTask.Field()
	rename_task = RenameTask.Field()
	create_transfer_position = CreateTransferPosition.Field()
	change_ready_to_go = ChangeReadyToGo.Field()
	delete_transfer_request = DeleteTransferRequest.Field()
	upload_incoming_offer_file = UploadIncomingOfferFile.Field()
	delete_incoming_offer_file = DeleteIncomingOfferFile.Field()
	transfer_all = TransferAll.Field()
	edit_position = EditPosition.Field()
	create_application = CreateApplication.Field()
	add_worker_in_transfer_request = AddWorkerInTransferRequest.Field()
	worker_refuse_in_transfer_request = WorkerRefuseInTransferRequest.Field()
	update_transfer_positions = UpdateTransferPositions.Field()
	completed_transfer_request = CompletedTransferRequest.Field()
	delete_transfer_request_in_transfer = DeleteTransferRequestInTransfer.Field()
