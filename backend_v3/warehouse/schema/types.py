import graphene
from graphene_django import DjangoObjectType
from ..models import Good, GoodKind, Manufacturer, Unit, Location, GoodGroup
from projects.schema.types import ProjectType
from users.schema.types import UserType
from crm.schema.types import IntID


class UnitType(DjangoObjectType):
	class Meta:
		model = Unit
		exclude_fields = ('good_set',)


class ManufacturerType(DjangoObjectType):
	class Meta:
		model = Manufacturer
		exclude_fields = ('goodkind_set',)


class GoodKindType(DjangoObjectType):
	class Meta:
		model = GoodKind
		exclude_fields = ('good_set',)

	gosts = graphene.List(graphene.String)

	def resolve_gosts(self, info):
		return [g.name for g in self.gosts.all()]


class WarehouseType(DjangoObjectType):
	class Meta:
		model = Location
		exclude_fields = ('good_set',)


class GoodType(DjangoObjectType):
	class Meta:
		model = Good
		exclude_fields = ('goodkind_set',)


class GoodGroupType(DjangoObjectType):
	class Meta:
		model = GoodGroup


class GoodsFilter(graphene.InputObjectType):
	manufacturer = IntID()
	storage = IntID()
	responsible = IntID()
	project = IntID()
	quantity = graphene.Float()
	quantity_type = graphene.String()




class GoodSubRowsType(graphene.ObjectType):
	id = IntID()
	location = graphene.Field(WarehouseType)
	count = graphene.Float()
	unit = graphene.Field(UnitType)
	project = graphene.Field(ProjectType)
	responsible = graphene.Field(UserType)
	note = graphene.String()
	defect = graphene.Boolean()


class TableGoodType(graphene.ObjectType):
	good_kind = graphene.Field(GoodKindType)
	sub_rows = graphene.List(GoodSubRowsType)


class PagedGoodsType(graphene.ObjectType):
	goods = graphene.List(TableGoodType)
	total_count = graphene.Int()


class PagedManufacturersType(graphene.ObjectType):
	manufacturers = graphene.List(ManufacturerType)
	total_count = graphene.Int()


class PagedGoodKindsType(graphene.ObjectType):
	good_kinds = graphene.List(GoodKindType)
	total_count = graphene.Int()


class GoodKindsFilter(graphene.InputObjectType):
	only_new = graphene.Boolean()
	groups_id = graphene.List(IntID)
	manufacturer_id = graphene.List(IntID)
