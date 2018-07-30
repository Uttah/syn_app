import graphene
from graphene import ObjectType, Field, List, String, Boolean
from warehouse.schema.types import PagedGoodsType, PagedManufacturersType, UnitType, \
	ManufacturerType, GoodsFilter, GoodKindType, WarehouseType, PagedGoodKindsType, GoodGroupType, \
	GoodKindsFilter
from warehouse.models import Good, Unit, Manufacturer, GoodKind, Location, GoodGroup
from crm.schema.types import PagedInput, IntID


class Query(ObjectType):
	paged_goods = Field(PagedGoodsType, paged=PagedInput(required=True), filters=GoodsFilter())
	paged_good_kinds = Field(PagedGoodKindsType, paged=PagedInput(required=True), filters=GoodKindsFilter())
	all_units = List(UnitType)
	all_manufacturers = List(ManufacturerType)
	all_good_kinds = List(GoodKindType, search=String(), require=List(IntID), checked=Boolean())
	all_warehouses = List(WarehouseType, search=graphene.String(), require=List(IntID), project=IntID())
	paged_manufacturers = Field(PagedManufacturersType, paged=PagedInput(required=True))
	check_manufacturer = Boolean(filters=GoodsFilter(required=True))
	all_good_groups = List(GoodGroupType)

	def resolve_check_manufacturer(self, info, filters):
		return Good.objects.checking_manufacturer(filters=filters)

	def resolve_paged_goods(self, info, paged, filters):
		goods, total_count = Good.objects.list_paged_goods(info, **paged, filters=filters)
		return PagedGoodsType(goods=goods, total_count=total_count)

	def resolve_paged_manufacturers(self, info, paged):
		manufacturers, total_count = Manufacturer.objects.list_paged_manufacturer(**paged)
		return PagedManufacturersType(manufacturers=manufacturers, total_count=total_count)

	def resolve_paged_good_kinds(self, info, paged, **kwargs):
		good_kinds, total_count = GoodKind.objects.list_paged_goods_kinds(**paged, **kwargs)
		return PagedGoodKindsType(good_kinds=good_kinds, total_count=total_count)

	def resolve_all_units(self, info):
		return Unit.objects.all()

	def resolve_all_manufacturers(self, info):
		return Manufacturer.objects.all()

	def resolve_all_good_kinds(self, info, search='', require=[], checked=False):
		return GoodKind.objects.load_good_kind(search=search, require=require, checked=checked)

	def resolve_all_warehouses(self, info, search='', require=[], project=None):
		return Location.objects.load_warehouse(info, search=search, require=require, project=project)

	def resolve_all_good_groups(self, info):
		return GoodGroup.objects.all()


