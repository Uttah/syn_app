import pickle
from copy import deepcopy
from django.db.models import F, Q
from django.db import transaction
import graphene
from datetime import datetime
from graphene.types.datetime import Date
from crm.schema.mutation import SngyMutation
from crm.schema.types import IntID
from ..models import Order, SalaryArchive, CoefficientsArchive, GradeCoefficient, SalaryPayment
from .types import OrderType
from .query import calculation_all_salary_in_month, get_last_salary_month, get_salary_limits
from users.decorators import permission_required
from reports.models import Report
from users.models import Bonus, GlobalCoefficient
from absences.models import Absence
from synergycrm.exceptions import SngyException


class CreateOrder(SngyMutation):
	order = graphene.Field(OrderType)

	class Input:
		project_id = IntID(required=True)
		responsible_id = IntID(required=True)
		date = Date(required=True)

	@permission_required('users.add_order')
	def mutate_and_get_payload(self, info, **kwargs):
		order = Order.objects.create(**kwargs)
		return CreateOrder(order=order)


class DeleteOrder(SngyMutation):
	result = graphene.Boolean()

	class Input:
		id = IntID(required=True)

	@permission_required('users.delete_order')
	def mutate_and_get_payload(self, info, id):
		order = Order.objects.get(id=id)
		order.delete()
		return DeleteOrder(result=True)


class UpdateOrder(SngyMutation):
	order = graphene.Field(OrderType)

	class Input:
		id = IntID(required=True)
		project_id = IntID()
		responsible_id = IntID()
		date = Date()

	@permission_required('users.change_order')
	def mutate_and_get_payload(self, info, id, **kwargs):
		order = Order.objects.get(id=id)
		[setattr(order, f, kwargs.get(f)) for f in kwargs.keys()]
		order.save()
		return UpdateOrder(order=order)


class CloseSalary(graphene.Mutation):
	result = graphene.Boolean()

	@permission_required('users.can_close_salary')
	def mutate(self, info):
		if info.context.user.id != 27:
			raise SngyException('Недостаточно прав')
		last_salary_month = get_last_salary_month()
		limits = get_salary_limits(last_salary_month)
		end_limit = limits[1].date()
		today = datetime.today().date()
		allow_close_date = end_limit.replace(day=20)
		if end_limit > today and today < allow_close_date:
			raise SngyException('Нельзя закрыть текущий месяц раньше {:%d.%m.%Y}'.format(allow_close_date))
		with transaction.atomic():
			users = calculation_all_salary_in_month()['users']
			# Общий фильтр закрываемых записей
			gen_filter = Q(report_date__lte=limits[1]) & Q(checked_by__isnull=False) & Q(deleted=False)
			selected = Report.objects.select_for_update().filter(gen_filter)
			# Помечаем проверенные записи как record_counted = 1
			selected.filter(record_counted=0).update(record_counted=1)
			# Ночные смены
			selected.filter(night_shift=True, checked_hr=True, night_shifts_paid=False).update(night_shifts_paid=True)
			# Оценки
			selected.filter(quality_grade__isnull=False, time_grade__isnull=False, record_counted__lt=2).update(
				record_counted=2)
			# Ответственность
			selected.filter(projects__order__isnull=False, projects__order__responsible_id=F('worker'),
			                projects__order__date__lte=F('report_date'), func_role__kind='R', responsible_work_paid=False). \
				update(responsible_work_paid=True)
			# Закрываем бонусы и отсутствия
			Bonus.objects.select_for_update().filter(counted=False, cash=False).update(month=limits[1], counted=True)
			bonuses = Bonus.objects.select_for_update().filter(month=limits[1], counted=True, installments__gt=1, cash=False)
			for b in bonuses:
				new_b = deepcopy(b)
				new_b.id = None
				new_b.amount = new_b.amount - (new_b.amount / new_b.installments)
				new_b.installments -= 1
				new_b.month = None
				new_b.counted = False
				new_b.save()

				b.amount = b.amount / b.installments
				b.save()

			Absence.objects.select_for_update().filter(begin__lte=limits[1]).update(locked=True)

			for u in users:
				SalaryArchive.objects.create(date=limits[0], worker_id=u, object=pickle.dumps(users[u]))

			global_coefficients = pickle.dumps(list(GlobalCoefficient.objects.all().values()))
			grade_coefficients = pickle.dumps(list(GradeCoefficient.objects.all().values()))
			CoefficientsArchive.objects.create(date=limits[0], global_coefficients=global_coefficients,
			                                   grade_coefficients=grade_coefficients)
			return CloseSalary(result=True)


class CreateSalaryPayment(SngyMutation):
	result = graphene.Boolean()

	class Input:
		user_id = IntID(required=True)
		amount = graphene.Int(required=True)
		advance = graphene.Int(required=True)
		company_id = IntID(required=True)

	@permission_required('salary.add_salarypayment')
	def mutate_and_get_payload(self, info, **kwargs):
		if kwargs['amount'] < 0:
			raise SngyException('Сумма выплаты меньше нуля')
		if kwargs['advance'] < 0:
			raise SngyException('Аванс меньше нуля')
		SalaryPayment.objects.create(**kwargs)
		return CreateSalaryPayment(result=True)


class UpdateSalaryPayment(SngyMutation):
	result = graphene.Boolean()

	class Input:
		id = IntID(required=True)
		user_id = IntID(required=True)
		amount = graphene.Int(required=True)
		advance = graphene.Int(required=True)
		company_id = IntID(required=True)

	@permission_required('salary.change_salarypayment')
	def mutate_and_get_payload(self, info, id, **kwargs):
		if kwargs['amount'] < 0:
			raise SngyException('Сумма выплаты меньше нуля')
		if kwargs['advance'] < 0:
			raise SngyException('Аванс меньше нуля')
		SalaryPayment.objects.filter(id=id).update(**kwargs)
		return UpdateSalaryPayment(result=True)


class DeleteSalaryPayment(SngyMutation):
	result = graphene.Boolean()

	class Input:
		id = IntID(required=True)

	@permission_required('salary.delete_salarypayment')
	def mutate_and_get_payload(self, info, id, **kwargs):
		try:
			SalaryPayment.objects.get(id=id).delete()
			return DeleteSalaryPayment(result=True)
		except SalaryPayment.DoesNotExist:
			raise SngyException('Такой записи не существует')


class Mutation(graphene.ObjectType):
	create_order = CreateOrder.Field()
	delete_order = DeleteOrder.Field()
	update_order = UpdateOrder.Field()
	close_salary = CloseSalary.Field()
	create_salary_payment = CreateSalaryPayment.Field()
	update_salary_payment = UpdateSalaryPayment.Field()
	delete_salary_payment = DeleteSalaryPayment.Field()
