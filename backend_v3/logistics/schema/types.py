import os.path
import graphene
import random
from graphene.types.datetime import Date as GrapheneDate
from graphene_django import DjangoObjectType
from django.db import models
from ..models import LogisticsRequest, TransferRequest, LogisticsRequestPosition, LogisticsTask, TransferPosition
from warehouse.models import Good
from crm.schema.types import IntID
from users.schema.types import UserType
from projects.schema.types import ProjectType
from warehouse.schema.types import WarehouseType, GoodKindType, GoodType, UnitType
from project_specifications.schema.types import Specification
from reports.schema.types import DateRangeType
from salary.models import DayOff
from datetime import datetime
from calendar import monthrange
from django.db.models import Q


class LogisticsGoal(graphene.ObjectType):
	id = graphene.Int()
	project = graphene.Field(ProjectType)
	name = graphene.String()


class InStockType(graphene.ObjectType):
	id = IntID()
	count = graphene.Float()
	unit = graphene.Field(UnitType)
	available = graphene.Float()


class LogisticsRequestPositionType(DjangoObjectType):
	in_stock = graphene.List(InStockType)
	transferred = graphene.Float()
	sum_transfer = graphene.Float()
	real_in_stock = graphene.Int()
	can_transfer = graphene.Boolean()
	calculated_expected = GrapheneDate()

	class Meta:
		model = LogisticsRequestPosition
		exclude_fields = ('logisticsrequestposition_set',)

	def resolve_real_in_stock(self, info, **kwargs):
		if isinstance(self.request.reason, Specification):
			return Good.objects.filter(good_kind=self.good_kind, project=self.request.reason.project).aggregate(sum=models.Sum('count'))['sum']
		else:
			return None

	def resolve_sum_transfer(self, info, **kwargs):
		result = 0
		positions = TransferPosition.objects.filter(logistics_request_position_id=self.id, transfer_request__completed=True)
		if positions:
			for position in positions:
				if position.transferred is None:
					result += position.count
					continue
				result += position.transferred

		return result

	def resolve_in_stock(self, info, **kwargs):
		transfer_sum_for_self_position = TransferPosition.objects.filter(logistics_request_position=self.id,
		                                                                 transfer_request__completed=False).aggregate(sum=models.Sum('count'))['sum']
		transfer_sum_for_self_position = transfer_sum_for_self_position if transfer_sum_for_self_position else 0
		result = []
		# Если у Михалева будет проект, то ?
		for g in Good.objects.filter(good_kind=self.good_kind, defect=False, location__id=1, responsible_id=120):
			value = False
			for r in result:
				if r.unit.id == g.unit.id and not g.unit.restrict_sum:
					value = True
					r.count += g.count
					r.available += g.count
			if not value:
				transfer_sum = TransferPosition.objects.filter(good__id=g.id, transfer_request__completed=False
				                                               ).aggregate(sum=models.Sum('count'))['sum']
				transfer_sum = transfer_sum if transfer_sum else 0
				available = g.count - transfer_sum
				if transfer_sum_for_self_position and g.unit == self.unit and not g.unit.restrict_sum:
					g.count = g.count - transfer_sum_for_self_position
				_id = int(str(g.id) + str(int(random.randint(100, 999))))
				result.append(InStockType(id=_id, count=g.count, unit=g.unit, available=available))
		push_in_result = []
		for g in Good.objects.filter(good_kind=self.good_kind, defect=False).exclude(location__id=1, responsible_id=120).exclude(location__id=646):
			if (g.project and g.project.id == self.request.reason.project.id) or \
				(g.location.project and g.location.project.id == self.request.reason.project.id):
				continue
			for r in result:
				if r.unit.id == g.unit.id and not g.unit.restrict_sum:
					r.count += g.count
			if g.unit.restrict_sum:
				_id = int(str(g.id) + str(int(random.randint(100, 999))))
				push_in_result.append(InStockType(id=_id, count=g.count, unit=g.unit, available=0))
		result = result + push_in_result
		return result

	def resolve_transferred(self, info, **kwargs):
		transferred = TransferPosition.objects.filter(logistics_request_position_id=self.id).aggregate(sum=models.Sum('transferred'))['sum']
		transferred = transferred if transferred else 0
		return transferred

	def resolve_can_transfer(self, info, **kwargs):
		sum = 0
		for tp in TransferPosition.objects.filter(logistics_request_position_id=self.id):
			if tp.transferred:
				sum += tp.transferred
			else:
				sum += tp.count
		return sum < self.count

	def resolve_calculated_expected(self, info, **kwargs):
		if self.order_date:
			return DayOff.objects.calculate_end_date(self.order_date, self.delivery_days, False)
		else:
			return DayOff.objects.calculate_end_date(datetime.today().date(), self.delivery_days, False)


class LogisticsRequestType(DjangoObjectType):
	purpose = graphene.String()
	project = graphene.String()
	goal = graphene.Field(LogisticsGoal)
	need_attention = graphene.Boolean()
	gip_id = IntID()
	reason_id = IntID()
	request_completed = graphene.Boolean()

	class Meta:
		model = LogisticsRequest

	def resolve_purpose(self, info, **kwargs):
		return 'Спец-ия %s' % self.reason.pressmark

	def resolve_project(self, info, **kwargs):
		return '%05d - %s' % (self.reason.project.number, self.reason.project.description)

	def resolve_goal(self, info, **kwargs):
		if isinstance(self.reason, Specification):
			return LogisticsGoal(id=self.reason.id, project=self.reason.project, name=self.reason.pressmark)
		else:
			return None

	def resolve_gip_id(self, info, **kwargs):
		return self.reason.project.gip.id

	def resolve_reason_id(self, info, **kwargs):
		return self.reason.id

	def resolve_request_completed(self, info, **kwargs):
		lrp = LogisticsRequestPosition.objects.filter(request_id=self.id)
		competed = True
		# array = []

		# for position in lrp:
		# 	array.append(position)

		# for position in lrp:
		# 	if position.canceled_position:
		# 		array.remove(position.canceled_position)

		for position in lrp:
			if not position.task:
				competed = False
				break
			if not position.canceled and not position.finished_date:
				competed = False
				break
		return competed


class PagedLogisticsRequestType(graphene.ObjectType):
	logistics_requests = graphene.List(LogisticsRequestType)
	total_count = graphene.Int()


class LogisticsRequestFilter(graphene.InputObjectType):
	projects = graphene.List(IntID)
	requested = graphene.List(IntID)
	actions = graphene.Boolean()
	partic = graphene.Boolean()
	show_completed = graphene.Boolean()


class TransferPositionSubRowsType(graphene.ObjectType):
	id = IntID()
	number = IntID()
	serial_number = IntID()
	location = graphene.Field(WarehouseType)
	project = graphene.Field(ProjectType)
	count = graphene.Float()
	transfer = graphene.Float()
	unit = graphene.Field(UnitType)
	all_count = graphene.Float()


class TransferPositionDataType(graphene.ObjectType):
	good_kind = graphene.Field(GoodKindType)
	sub_rows = graphene.List(TransferPositionSubRowsType)


class TransferRequestType(DjangoObjectType):
	need_attention = graphene.Boolean()
	status = graphene.String()
	count = graphene.String()

	class Meta:
		model = TransferRequest


class TransferRequestData(graphene.ObjectType):
	transfer_request = graphene.Field(TransferRequestType)
	transfer_positions = graphene.List(TransferPositionDataType)


class TransferPositionType(DjangoObjectType):
	class Meta:
		model = TransferPosition


class UploadIncomingOfferFileResultType(graphene.ObjectType):
	name = graphene.String()
	id = graphene.Int()
	kind = graphene.String()


class LogisticsTaskType(DjangoObjectType):
	transfer_request = graphene.Field(TransferRequestType)
	files = graphene.List(UploadIncomingOfferFileResultType)
	transferred = graphene.Boolean()
	transferred_with_ready_to_go_false = graphene.Boolean()
	replacement = graphene.Boolean()
	task_completed = graphene.Boolean()

	class Meta:
		model = LogisticsTask

	def resolve_transfer_request(self, info, **kwargs):
		for lrp in LogisticsRequestPosition.objects.filter(task_id=self.id):
			transferposition_set = lrp.transferposition_set.all()
			if transferposition_set:
				for tp in transferposition_set:
					if tp.transfer_request.completed or tp.transfer_request.ready_to_go:
						continue
					return tp.transfer_request

	def resolve_files(self, info, **kwargs):
		result = []
		for d in self.files.all():
			if not d.file:
				continue
			name = os.path.split(d.file.name)[-1].split('_', maxsplit=1)[1]
			result.append(UploadIncomingOfferFileResultType(name=name, kind='incoming_offer', id=d.id))
		return result

	def resolve_transferred(self, info, **kwargs):
		transferred = False
		for lrp in LogisticsRequestPosition.objects.filter(task_id=self.id):
			for tp in lrp.transferposition_set.all():
				if tp.transferred and tp.transfer_request.ready_to_go:
					transferred = True
		return transferred

	def resolve_transferred_with_ready_to_go_false(self, info, **kwargs):
		result = False
		for lrp in LogisticsRequestPosition.objects.filter(task_id=self.id):
			for tp in lrp.transferposition_set.all():
				if tp.transfer_request.ready_to_go == False:
					result = True
		return result

	def resolve_replacement(self, info, **kwargs):
		replacement = False
		for lrp in LogisticsRequestPosition.objects.filter(task_id=self.id):
			if lrp.canceled_position:
				replacement = True
		return replacement

	def resolve_task_completed(self, info, **kwargs):
		task_completed = True
		for lrp in LogisticsRequestPosition.objects.filter(task_id=self.id):
			if lrp.canceled:
				continue
			transferred_sum = TransferPosition.objects.filter(logistics_request_position=lrp).aggregate(sum=models.Sum('transferred'))['sum']
			transferred_sum = transferred_sum if transferred_sum else 0
			if lrp.count != transferred_sum:
				task_completed = False
				break
		return task_completed


class PagedTransferRequestsType(graphene.ObjectType):
	transfer_requests = graphene.List(TransferRequestType)
	total_count = graphene.Int()


class TransferRequestsFilter(graphene.InputObjectType):
	projects = graphene.List(IntID)
	warehouses = graphene.List(IntID)
	creators = graphene.List(IntID)
	date_range = DateRangeType()
	status = graphene.String()
	actions = graphene.Boolean()
	partic = graphene.Boolean()


class TransferCountType(graphene.ObjectType):
	count = graphene.Float()
	unit = graphene.String()
	completed = graphene.Boolean()


class LogisticsRequestPositionSubRowsType(graphene.ObjectType):
	id = IntID()
	expected_date = graphene.String()
	deadline = graphene.String()
	order_date = graphene.String()
	count = graphene.Float()
	available_in_stock = graphene.Float()
	count_in_stock = graphene.Float()
	unit = graphene.String()
	# transfer - колонка "Задачи на перемещение"
	transfer = graphene.List(TransferCountType)
	logistic_request_id = IntID()
	logistic_task_id = IntID()
	number = IntID()
	project = graphene.Field(ProjectType)
	responsible = graphene.List(UserType)
	worker = graphene.Field(UserType)


class LogisticsRequestPositionDataType(graphene.ObjectType):
	good_kind = graphene.Field(GoodKindType)
	sub_rows = graphene.List(LogisticsRequestPositionType)


class PagedLogisticsRequestPositionType(graphene.ObjectType):
	logistics_request_positions = graphene.List(LogisticsRequestPositionDataType)
	total_count = graphene.Int()


class DateDayRangeType(graphene.InputObjectType):
	date_start = graphene.String()
	date_end = graphene.String()


class LogisticsRequestPositionFilter(graphene.InputObjectType):
	late_delivery = graphene.Boolean()
	overdue = graphene.Boolean()
	row_status = graphene.String()
	expected_date = DateDayRangeType()
	deadline = DateDayRangeType()
	order_date = DateDayRangeType()
	projects = graphene.List(IntID)
	responsible = graphene.List(IntID)
	worker = IntID()
	moved = IntID()
	count_in_stock = graphene.Float()
	status_in_stock = graphene.String()


class GoodLocationInfoType(graphene.ObjectType):
	project = graphene.Field(ProjectType)
	good = graphene.Field(GoodType)