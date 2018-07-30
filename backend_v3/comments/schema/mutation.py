import graphene
from django.contrib.contenttypes.models import ContentType
from crm.schema.mutation import SngyMutation
from synergycrm.exceptions import SngyException
from ..models import Comment
from notice.models import Notification
from users.models import User


class CreateComments(SngyMutation):
	result = graphene.Boolean()

	class Input:
		name = graphene.String(required=True)
		object_id = graphene.Int(required=True)
		comment = graphene.String(required=True)
		targets = graphene.List(of_type=graphene.Int)

	def mutate_and_get_payload(self, info, name, object_id, comment, targets):
		if not '.' in name:
			raise SngyException('Неправильное имя')
		app_label, model = name.lower().split('.')
		content_type = ContentType(app_label=app_label, model=model)
		content_object = content_type.get_object_for_this_type(id=object_id)
		Comment.objects.create(content_object=content_object, user=info.context.user, comment=comment)

		users_id = [u.id for u in User.objects.all()]
		if not targets:
			targets = list(set([c.user_id for c in Comment.objects.filter(content_type__app_label=app_label,
			                                                     content_type__model=model, object_id=object_id)]))
			if info.context.user.id in targets:
				targets.remove(info.context.user.id)
		for t in targets:
			if t in users_id:
				text = 'Комментарий: ' + comment
				Notification.objects.create(purpose_id=t, created=info.context.user, text=text)

		return CreateComments(result=True)


class Mutation(graphene.ObjectType):
	create_comments = CreateComments.Field()

