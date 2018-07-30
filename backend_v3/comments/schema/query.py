import graphene
from .types import CommentType
from comments.models import Comment
from synergycrm.exceptions import SngyException


# noinspection PyMethodMayBeStatic,PyUnusedLocal
class Query(graphene.ObjectType):
	comments = graphene.List(CommentType, name=graphene.String(required=True), object_id=graphene.Int(required=True))

	def resolve_comments(self, info, name, object_id):
		if not '.' in name:
			raise SngyException('Неправильное имя')
		app_label, model = name.lower().split('.')
		return Comment.objects.filter(content_type__app_label=app_label, content_type__model=model, object_id=object_id)


