from django.db import models
from django.db.models import Q
import datetime


class LogisticsRequestManager(models.Manager):

	def list_paged_logistics_requests(self, user, offset, first, sort_by, desc=False, search='', filters=None):
		from logistics.models import LogisticsRequestPosition
		last = offset + first
		search = search.strip()
		not_finished_logistics_id = []
		logistics_requests = self
		# Ищем только НЕ выполненные заявки на закупку
		for lr in logistics_requests.all():
			for lrp in LogisticsRequestPosition.objects.filter(request_id=lr.id):
				if not lrp.canceled and lrp.finished_date is None:
					not_finished_logistics_id.append(lr.id)
					break
		logistics_requests = logistics_requests.filter(id__in=not_finished_logistics_id)
		# Для логистов отображаем только переданные в работу заявки
		if user.has_perm('logistics.is_logist') and not user.is_superuser:
			logistics_requests = logistics_requests.filter(ready_for_work=True)

		sort_field = None
		if sort_by == 'applicationDate' or sort_by is None:
			sort_field = models.F('when_requested')
		elif sort_by == 'number':
			sort_field = models.F('id')
		elif sort_by == 'project':
			sort_field = models.F('project_spec_reason__project__number')
		elif sort_by == 'deadline':
			sort_field = models.F('deadline')
		if desc:
			sort_field = sort_field.desc()

		if search != '':
			logistics_requests = logistics_requests.filter(id__icontains=search)
		else:
			if filters:
				if filters.get('show_completed'):
					logistics_requests = self
				if filters.get('projects'):
					logistics_requests = logistics_requests.filter(project_spec_reason__project_id__in=filters['projects'])
				if filters.get('requested'):
					logistics_requests = logistics_requests.filter(who_requested_id__in=filters['requested'])
				if filters.get('partic'):
					# Ответственные
					# Запросил
					# Исполнитель в какой-либо задаче
					logistics_requests = logistics_requests.filter(
						Q(who_requested_id=user.id) | Q(responsible__in=[user.id]) |
						Q(logisticsrequestposition__task__responsible=user.id)).distinct()

		test_data = logistics_requests.order_by(sort_field).values('id')
		test_data = [q['id'] for q in test_data[offset:last]]

		_q = (Q(logisticsrequestposition__task_id__isnull=True) | Q(logisticsrequestposition__task__responsible=None) |
		      (Q(logisticsrequestposition__task__responsible=user.id) &
		       Q(logisticsrequestposition__expected_date__lt=datetime.datetime.now().date()) &
		       Q(logisticsrequestposition__finished_date__isnull=True) &
		       Q(logisticsrequestposition__canceled=False)))

		# Возможно вместо self - logistics_requests
		logistics_requests = self.annotate(need_attention=models.Case(models.When(_q, then=models.Value(True)),
		                                                              default=models.Value(False),
		                                                              output_field=models.BooleanField())). \
			order_by('id', '-need_attention').distinct('id').filter(id__in=test_data)

		annotated = {r.id: r for r in logistics_requests}
		result = []
		for row in test_data:
			result.append(annotated[row])

		if first < 0:
			return [], 0

		logistics_requests = list(result)

		if filters.get('actions'):
			if user.has_perm('logistics.is_logist'):
				# в заявке есть позиции без задачи
				# в заявке есть задачи без исполнителя
				# есть позиции, которые должны были прибыть вчера или раньше
				logistics_requests = [q for q in logistics_requests if q.need_attention == True]

		tc = len(logistics_requests)
		return logistics_requests[offset:last], tc


class TransferRequestManager(models.Manager):

	def transfer_request(self, info, requestId=None, sort_by=None, desc=False):
		from logistics.models import TransferPosition
		from .schema.types import TransferPositionSubRowsType
		from .schema.types import TransferPositionDataType
		user = info.context.user

		sort_field = None
		if sort_by == 'goodGroup' or sort_by is None:
			sort_field = models.F('good__good_kind__good_group')
		elif sort_by == 'article':
			sort_field = models.F('good__good_kind__code')
		elif sort_by == 'name':
			sort_field = models.F('good__good_kind__name')
		elif sort_by == 'manufacturer':
			sort_field = models.F('good__good_kind__manufacturer')
		if desc:
			sort_field = sort_field.desc()

		request = self.get(id=requestId)
		positions = TransferPosition.objects.filter(transfer_request_id=requestId).order_by(sort_field)

		rows = []
		sub_rows = []
		number = 0
		# По факту при правильном коде эта ошибка не должна вызваться.
		if not positions:
			raise Exception('Ошибка: Нет позиций перемещения!')
		current_good_kind = positions[0].good.good_kind

		for position in positions:
			number += 1
			if position.good.good_kind != current_good_kind:
				position_type = TransferPositionDataType(good_kind=current_good_kind, sub_rows=sub_rows)
				rows.append(position_type)
				current_good_kind = position.good.good_kind
				sub_rows = []
			position_sub = TransferPositionSubRowsType(
				id=position.id,
				number=number,
				serial_number=position.logistics_request_position.number,
				location=position.good.location,
				project=position.good.project,
				count=position.count,
				transfer=position.transferred,
				unit=position.good.unit,
				all_count=position.good.count)
			sub_rows.append(position_sub)
		position_type = TransferPositionDataType(good_kind=current_good_kind, sub_rows=sub_rows)
		rows.append(position_type)
		return request, rows

	def list_paged_transfer_requests(self, user, offset, first, sort_by, desc=False, search='', filters=None):
		last = offset + first
		search = search.strip()
		transfer_requests = self.filter(ready_to_go=True)
		sort_field = None
		if sort_by == 'number' or sort_by is None:
			sort_field = models.F('id')
		elif sort_by == 'creationDate':
			sort_field = models.F('creation_date')
		elif sort_by == 'where':
			sort_field = models.F('where')
		if desc:
			sort_field = sort_field.desc()

		if search != '':
			transfer_requests = transfer_requests.filter(id__icontains=search)

		if filters:
			if filters.get('projects'):
				transfer_requests = transfer_requests.filter(where__project_id__in=filters['projects'])
			if filters.get('warehouses'):
				transfer_requests = transfer_requests.filter(where_id__in=filters['warehouses'])
			if filters.get('creators'):
				transfer_requests = transfer_requests.filter(who_requested_id__in=filters['creators'])
			if filters.get('date_range'):
				transfer_requests = filters.get('date_range').get_range(transfer_requests, 'creation_date')
			# Добавить фильтр по датам
			if filters.get('partic'):
				# Запросил  (who_requested)
				# Исполнитель (Исполнитель worker)
				transfer_requests = transfer_requests.filter(
					Q(who_requested_id=user.id) | Q(worker_id=user.id)).distinct()
		test_data = transfer_requests.order_by(sort_field).values('id')
		test_data = [q['id'] for q in test_data[offset:last]]
		# Условия: (Пользователь - исполнитель И заявка ещё не выполнена) ИЛИ (Есть разрешение И у заявки нет исполнителя)
		_q = Q(worker_id=user.id) & Q(completed=False)
		if user.has_perm('logistics.can_work_transfer_request'):
			_q |= Q(worker__isnull=True)

		_q_status_created = Q(ready_to_go=True) & Q(worker__isnull=True)
		_q_status_in_work = Q(ready_to_go=True) & Q(worker__isnull=False) & Q(completed=False)
		_q_status_completed = Q(completed=True)

		# Добавляем всем результатам поле need_attention и сортируем по тем которые показываются на этой странице
		transfer_requests = self.annotate(need_attention=models.Case(models.When(_q, then=models.Value(True)),
	                                                              default=models.Value(False),
	                                                              output_field=models.BooleanField())). \
			annotate(status=models.Case(models.When(_q_status_created, then=models.Value('Создана')),
		                                models.When(_q_status_in_work, then=models.Value('Выполняется')),
		                                models.When(_q_status_completed, then=models.Value('Выполнена')),
		                                         default=models.Value('Неизвестный статус'),
		                                         output_field=models.CharField())).\
			order_by('id', '-need_attention').distinct('id').filter(id__in=test_data)
		annotated = {r.id: r for r in transfer_requests}
		result = []
		for row in test_data:
			result.append(annotated[row])

		if first < 0:
			return [], 0

		transfer_requests = list(result)

		if filters:
			if filters.get('actions'):
				transfer_requests = [q for q in transfer_requests if q.need_attention == True]
			if filters.get('status'):
				# Вычислять статус
				filter_status_data = []
				for request in transfer_requests:
					if (request.status == filters['status']):
						filter_status_data.append(request)
				transfer_requests = filter_status_data
		tc = len(transfer_requests)
		return transfer_requests[offset:last], tc


class LogisticsRequestPositionManager(models.Manager):

	def list_paged_logistics_request_position(self, user, offset, first, sort_by, desc=False, search='', filters=None):
		from .schema.types import LogisticsRequestPositionDataType
		from .models import TransferPosition
		from warehouse.models import Good
		last = offset + first
		request_positions = self.filter()

		# Не отображаем Отмененные, Выполненые Заявочные позиции и с неуказанной датой заказа
		request_positions = request_positions.exclude(Q(canceled=True) | Q(finished_date__isnull=False) | Q(order_date__isnull=True))
		# Не отображаем Отмененные позиции
		for position in request_positions:
			if position.canceled_position:
				request_positions = request_positions.exclude(id=position.canceled_position.id)
		# Не отображаем если Необходимое количество больше или равно сумме количества позиций перемещения
		for position in request_positions:
			count = 0
			for transfer_position in position.transferposition_set.all().exclude(transfer_request__ready_to_go=False):
				if transfer_position.transferred is not None and transfer_position.transferred != transfer_position.count:
					count += transfer_position.transferred
				else:
					count += transfer_position.count
			if position.count <= count:
				request_positions = request_positions.exclude(id=position.id)

		request_positions = request_positions.annotate(none_date=models.Case(models.When(expected_date__isnull=True,
		                                                                                 then=models.Value(True)),
		                                                                     default=models.Value(False),
		                                                                     output_field=models.BooleanField()))

		if search != '':
			request_positions = request_positions.filter(Q(id__icontains=search) | Q(task__id__icontains=search) |
			                                             Q(transferposition__transfer_request__id__icontains=search) |
			                                             Q(good_kind__code__icontains=search) | Q(good_kind__name__icontains=search)).distinct()

		if filters:
			# Опоздала поставка
			if filters.get('late_delivery'):
				request_positions = request_positions.filter(Q(expected_date__lt=datetime.datetime.now().date()) | Q(expected_date__isnull=True))
			# Просроченные
			if filters.get('overdue'):
				request_positions = request_positions.filter(Q(deadline__lt=datetime.datetime.now().date()))

			if filters.get('row_status'):
				if filters['row_status'] == 'Готовые к перемещению':
					request_success_list = []
					for req in request_positions:
						goods_count = Good.objects.filter(good_kind=req.good_kind, location__id=1, unit=req.unit, defect=False).aggregate(sum=models.Sum('count'))['sum']
						transfer_count = TransferPosition.objects.filter(good__good_kind=req.good_kind,
						                                       good__unit=req.unit).aggregate(sum=models.Sum('transferred'))['sum']
						if goods_count is not None and transfer_count is not None:
							goods_count += transfer_count
						if goods_count is not None:
							if req.count <= goods_count:
								request_success_list.append(req.id)

					request_positions = request_positions.filter(id__in=request_success_list)

				if filters['row_status'] == 'Ожидающие моих действий':
					request_success_list = []
					for req in request_positions:
						goods_count = Good.objects.filter(good_kind=req.good_kind, location__id=1, unit=req.unit, defect=False).aggregate(sum=models.Sum('count'))['sum']

						transfer_count = TransferPosition.objects.filter(good__good_kind=req.good_kind,
						                                                 good__unit=req.unit).aggregate(sum=models.Sum('transferred'))['sum']
						if goods_count is not None and transfer_count is not None:
							goods_count += transfer_count
						if goods_count is not None:
							if req.count <= goods_count:
								request_success_list.append(req.id)
					request_positions = request_positions.filter(id__in=request_success_list, task__responsible=user)

				# С моим участием
				if filters['row_status'] == 'С моим участием':
					request_positions = request_positions.filter(Q(request__responsible=user) | Q(task__responsible_id=user.id)).distinct()

			# Ожидаемая дата
			if filters.get('expected_date'):
				if filters.get('expected_date').date_start:
					request_positions = request_positions.filter(expected_date__gte=filters['expected_date'].date_start)
				if filters.get('expected_date').date_end:
					request_positions = request_positions.filter(expected_date__lte=filters['expected_date'].date_end)
			# Необходимая дата
			if filters.get('deadline'):
				if filters.get('deadline').date_start:
					request_positions = request_positions.filter(deadline__gte=filters['deadline'].date_start)
				if filters.get('deadline').date_end:
					request_positions = request_positions.filter(deadline__lte=filters['deadline'].date_end)
			# Дата заказа
			if filters.get('order_date'):
				if filters.get('order_date').date_start:
					request_positions = request_positions.filter(order_date__gte=filters['order_date'].date_start)
				if filters.get('order_date').date_end:
					request_positions = request_positions.filter(order_date__lte=filters['order_date'].date_end)

			# Проекты
			if filters.get('projects'):
				request_positions = request_positions.filter(request__project_spec_reason__project_id__in=filters['projects'])
			# Ответственные
			if filters.get('responsible'):
				request_positions = request_positions.filter(request__responsible__in=filters['responsible'])
			# Исполнитель задачи
			if filters.get('worker'):
				request_positions = request_positions.filter(task__responsible=filters['worker'])
			# Переместивший
			if filters.get('moved'):
				request_positions = request_positions.filter(transferposition__transfer_request__worker=filters['moved']).distinct()
			# Количество на складе
			if filters.get('count_in_stock'):
				request_success_list = []
				for req in request_positions:
					goods_count = Good.objects.filter(good_kind=req.good_kind, defect=False, location__id=1, unit=req.unit, responsible_id=120).aggregate(sum=models.Sum('count'))['sum']
					if goods_count is not None and filters['count_in_stock'] is not None:
						if filters['status_in_stock'] == 'Меньше или равно':
							if float(goods_count) <= float(filters['count_in_stock']):
								request_success_list.append(req.id)
						if filters['status_in_stock'] == 'Равно':
							if float(goods_count) == float(filters['count_in_stock']):
								request_success_list.append(req.id)
						if filters['status_in_stock'] == 'Больше или равно':
							if float(goods_count) >= float(filters['count_in_stock']):
								request_success_list.append(req.id)
				request_positions = request_positions.filter(id__in=request_success_list)

		sort_field = None
		if sort_by == 'expectedDate' or sort_by is None:
			sort_field = models.F('expected_date')

		if sort_by == 'deadline':
			sort_field = models.F('deadline')
		elif sort_by == 'orderDate':
			sort_field = models.F('order_date')
		elif sort_by == 'manufacturer':
			sort_field = models.F('good_kind__manufacturer')
		if desc:
			sort_field = sort_field.desc()

		rows = []
		sub_rows = []

		if sort_by != 'expectedDate' and sort_by is not None:
			request_positions = request_positions.order_by(sort_field, models.F('good_kind'))
			if len(request_positions):
				current_good_kind = request_positions[0].good_kind

				for position in request_positions:
					if position.good_kind != current_good_kind:
						position_type = LogisticsRequestPositionDataType(good_kind=current_good_kind, sub_rows=sub_rows)
						rows.append(position_type)
						current_good_kind = position.good_kind
						sub_rows = []
					# Группируем по good_kind для неразрыности строк
					rows_good_kind = request_positions.filter(good_kind=current_good_kind)
					request_positions = request_positions.exclude(good_kind=current_good_kind)

					for row in rows_good_kind:
						sub_rows.append(row)

				position_type = LogisticsRequestPositionDataType(good_kind=current_good_kind, sub_rows=sub_rows)
				rows.append(position_type)

		if sort_by == 'expectedDate' or sort_by is None:
			request_positions = request_positions.order_by(models.F('none_date').desc(), sort_field, models.F('good_kind'))
			if len(request_positions):
				current_good_kind = request_positions[0].good_kind

				for position in request_positions:
					if position.good_kind != current_good_kind:
						position_type = LogisticsRequestPositionDataType(good_kind=current_good_kind, sub_rows=sub_rows)
						rows.append(position_type)
						current_good_kind = position.good_kind
						sub_rows = []
					# Группируем по good_kind для неразрыности строк
					rows_good_kind = request_positions.filter(good_kind=current_good_kind)
					request_positions = request_positions.exclude(good_kind=current_good_kind)

					# Сортировка по отсутствию даты(без даты вверху)
					sorted_by_none_date = []
					for row in rows_good_kind:
						if row.none_date:
							sorted_by_none_date.append(row)
					for row in rows_good_kind:
						if not row.none_date:
							sorted_by_none_date.append(row)

					for row in sorted_by_none_date:
						sub_rows.append(row)

				position_type = LogisticsRequestPositionDataType(good_kind=current_good_kind, sub_rows=sub_rows)
				rows.append(position_type)
		tc = len(rows)
		return rows[offset:last], tc
