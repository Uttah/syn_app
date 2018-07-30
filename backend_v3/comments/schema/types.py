from graphene_django import DjangoObjectType
from ..models import Comment


class CommentType(DjangoObjectType):
	class Meta:
		model = Comment


