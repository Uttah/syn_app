from graphene import ObjectType, Field, Boolean, String, List
from ..models import LogisticsRequest, TransferRequest, LogisticsRequestPosition, TransferPosition
from .types import PagedLogisticsRequestType, LogisticsRequestFilter, TransferRequestData, \
	PagedTransferRequestsType, TransferRequestsFilter, PagedLogisticsRequestPositionType, LogisticsRequestPositionFilter,\
	TransferRequestType, LogisticsRequestType, GoodLocationInfoType
from crm.schema.types import PagedInput, IntID
from warehouse.models import Good

class Query(ObjectType):
	paged_logistics_request = Field(PagedLogisticsRequestType, paged=PagedInput(required=True), filters=LogisticsRequestFilter())
	transfer_request = Field(TransferRequestData, requestId=IntID(required=True), sort_by=String(), desc=Boolean())
	get_logistics_request = Field(LogisticsRequestType, id=IntID())
	paged_transfer_requests = Field(PagedTransferRequestsType, paged=PagedInput(required=True), filters=TransferRequestsFilter())
	paged_logistics_request_position = Field(PagedLogisticsRequestPositionType, paged=PagedInput(required=True),
	                                         filters=LogisticsRequestPositionFilter())
	transfer_request_position_info = List(TransferRequestType, position_id=IntID(required=True))
	good_location_info = List(GoodLocationInfoType, position_id=IntID(required=True))
	get_logistics_request_id = IntID()
	get_logistics_request_project_id = IntID()

	def resolve_paged_logistics_request(self, info, paged, **kwargs):
		logistics_requests, total_count = LogisticsRequest.objects.list_paged_logistics_requests(info.context.user,
		                                                                                         **paged, **kwargs)
		return PagedLogisticsRequestType(logistics_requests=logistics_requests, total_count=total_count)

	def resolve_transfer_request(self, info, **kwargs):
		transfer_request, transfer_positions = TransferRequest.objects.transfer_request(info, **kwargs)
		return TransferRequestData(transfer_request=transfer_request, transfer_positions=transfer_positions)

	def resolve_get_logistics_request(self, info, id):
		return LogisticsRequest.objects.get(id=id)

	def resolve_paged_transfer_requests(self, info, paged, **kwargs):
		transfer_requests, total_count = TransferRequest.objects.list_paged_transfer_requests(info.context.user,
		                                                                                         **paged, **kwargs)
		return PagedTransferRequestsType(transfer_requests=transfer_requests, total_count=total_count)

	def resolve_paged_logistics_request_position(self, info, paged, **kwargs):
		logistics_request_positions, total_count = LogisticsRequestPosition.objects.list_paged_logistics_request_position(info.context.user,
		                                                                                      **paged, **kwargs)
		return PagedLogisticsRequestPositionType(logistics_request_positions=logistics_request_positions, total_count=total_count)

	def resolve_transfer_request_position_info(self, info, position_id):
		try:
			position = LogisticsRequestPosition.objects.get(id=position_id)
		except LogisticsRequestPosition.DoesNotExist:
			return []
		transfer_requests = []
		for tp in TransferPosition.objects.filter(good__good_kind=position.good_kind, good__unit=position.unit, transfer_request__completed=False).exclude(logistics_request_position=position):
			transfer_request = tp.transfer_request
			transfer_request.count = '%s %s' % (str(int(tp.count) if isinstance(tp.count, float) and tp.count.is_integer() else tp.count), tp.good.unit.short_name)
			transfer_requests.append(transfer_request)
		transfer_requests = list(set(transfer_requests))
		return transfer_requests

	def resolve_good_location_info(self, info, position_id):
		try:
			position = LogisticsRequestPosition.objects.get(id=position_id)
		except LogisticsRequestPosition.DoesNotExist:
			return []
		result = []
		for g in Good.objects.filter(good_kind=position.good_kind, unit=position.unit).exclude(location_id__in=(1, 646)):
			if (g.project and g.project.id == position.request.reason.project.id) or \
					(g.location.project and g.location.project.id == position.request.reason.project.id):
				continue
			result.append(GoodLocationInfoType(project=g.location.project, good=g))
		return result


	def resolve_get_logistics_request_id(self, info):
		lr = LogisticsRequest.objects.filter(logisticsrequestposition__transferposition__transfer_request__ready_to_go=False,
		                       logisticsrequestposition__transferposition__transfer_request__who_requested=info.context.user).distinct()
		if lr:
			lr = lr[0].id
			return lr
		else:
			return -1

	def resolve_get_logistics_request_project_id(self, info):
		proj = None
		tr = TransferRequest.objects.filter(ready_to_go=False, who_requested=info.context.user)
		if tr:
			tp = TransferPosition.objects.filter(transfer_request=tr[0]).select_related('logistics_request_position__request')
			proj = tp[0].logistics_request_position.request.reason.project

		if proj:
			proj = proj.id
			return proj
		else:
			return -1
