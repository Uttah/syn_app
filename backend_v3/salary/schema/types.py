from graphene import ObjectType, List, Field, ID
from graphene.types import Int, String, Float
from graphene_django import DjangoObjectType
from salary.models import Order, GradeCoefficient, SalaryPayment
from users.schema.types import FullUserType


class OrderType(DjangoObjectType):
	class Meta:
		model = Order


class GradeCoefficientType(DjangoObjectType):
	class Meta:
		model = GradeCoefficient


class TotalsType(ObjectType):
	work_hours = Float()
	overtime = Float()
	home = Float()
	welding = Float()
	healthy_day = Int()
	transport_office = Int()
	night = Float()
	positive_grade = Float()
	negative_grade = Float()
	ideal_grade = Float()
	order = Float()
	sick = Float()

	work_hours_money = Int()
	overtime_money = Int()
	home_money = Int()
	welding_money = Int()
	healthy_day_money = Int()
	night_money = Int()
	positive_grade_money = Int()
	negative_grade_money = Int()
	ideal_grade_money = Int()
	transport_money = Int()
	private_car = Int()
	duty_car = Int()
	transport_office_money = Int()
	order_money = Int()
	vacation_money = Int()
	sick_money = Int()


class MonthType(ObjectType):
	month = String()
	totals = Field(TotalsType)


class UserMonthsType(ObjectType):
	user = Field(FullUserType)
	months = List(MonthType)
	totals = Field(TotalsType)
	bonus = Int()
	advance = Int()


class UsersMonthsType(ObjectType):
	users = List(UserMonthsType)
	totals = Field(TotalsType)


class UserSalaryInfoType(ObjectType):
	salary = Int()
	base = Int()
	cost_hour = Float()
	work_hours_in_month = Int()
	advance = Int()

	general = Float()
	welding = Float()
	experience = Float()
	etech = Float()
	schematic = Float()
	initiative = Float()
	discipline = Float()

	my_general = Float()
	my_welding = Float()
	my_experience = Float()
	my_etech = Float()
	my_schematic = Float()
	my_initiative = Float()
	my_discipline = Float()

	avg = Float()
	base_cost_hour = Float()


class SalaryPaymentType(DjangoObjectType):
	class Meta:
		model = SalaryPayment


class PagedSalaryPayments(ObjectType):
	salary_payments = List(SalaryPaymentType)
	total_count = Int()


class AccrualType(ObjectType):
	user = String()
	auto = Int()
	other = Int()
	bonus = Int()
	advance = Int()
	main_part = Int()


class CompanyAccrualType(ObjectType):
	id = ID()
	name = String()
	accruals = List(AccrualType)


class SumAvgYearType(ObjectType):
	sum_year = Float()
	avg_year = Float()

