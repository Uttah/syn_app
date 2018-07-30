import graphene
from documents.models import Document

class Query(graphene.ObjectType):
	doc_test = graphene.Boolean()

	def resolve_doc_test(self, info):
		doc = Document.objects.get(id=2)
		return doc.approved()
