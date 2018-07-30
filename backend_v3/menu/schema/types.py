from graphene_django import DjangoObjectType
from graphene import List
from ..models import MenuItem, TopMenu


class MenuItemType(DjangoObjectType):
	class Meta:
		model = MenuItem
		only_fields = ('link', 'text')


class TopMenuType(DjangoObjectType):
	items = List(MenuItemType)

	class Meta:
		model = TopMenu
		only_fields = ('text', 'items')

	def resolve_items(self, info):
		user_permissions = set(info.context.user.get_all_permissions())
		items = []
		for menu_item in self.items.all():
			permissions = set()
			for permission in menu_item.required_permissions.all():
				permission_name = '{}.{}'.format(permission.content_type.app_label, permission.codename)
				permissions.add(permission_name)
			if len(permissions - user_permissions) == 0:
				items.append(menu_item)
		return items
