from graphene import ObjectType, List
from django.db.models import Q
from .types import TopMenuType, TopMenu


# noinspection PyUnusedLocal
class Query(ObjectType):
	menu = List(TopMenuType, description='Меню для залогиненного сотрудника')

	@staticmethod
	def resolve_menu(root, info):
		user = info.context.user
		user_positions = user.positions.values('id')
		user_positions = (pos['id'] for pos in user_positions)
		menu = TopMenu.objects.filter(Q(position_id__in=user_positions) | Q(position__isnull=True))
		menu = menu.prefetch_related('items__required_permissions__content_type').all()
		return menu
