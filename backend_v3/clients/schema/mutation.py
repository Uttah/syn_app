import graphene
from crm.schema.mutation import SngyMutation
from clients.schema.types import ClientType
from clients.models import Client, Contact, ClientHistory, ClientHistoryContact
from crm.schema.types import IntID
from users.decorators import permission_required


class AddClient(SngyMutation):
	client = graphene.Field(ClientType, description='Созданный контрагент')

	class Input:
		name = graphene.String(required=True)
		kind_id = IntID()
		relation_id = IntID()
		full_name = graphene.String()
		INN = graphene.String()
		KPP = graphene.String()
		OKPO = graphene.String()
		OGRN = graphene.String()
		legal_address = graphene.String()
		street_address = graphene.String()
		phone_number = graphene.String()
		manager_id = IntID()
		other = graphene.String()

	def mutate_and_get_payload(self, info, **kwargs):
		client = Client.objects.create(**kwargs)
		return AddClient(client=client)


class DeleteClient(SngyMutation):
	result = graphene.Boolean()

	class Input:
		id_client = IntID(required=True)

	@permission_required('clients.delete_client')
	def mutate_and_get_payload(self, info, id_client):
		Client.objects.get(id=id_client).delete()
		return DeleteClient(result=True)


class EditClient(SngyMutation):
	result = graphene.Boolean()

	class Input:
		id_client = IntID(required=True)
		name = graphene.String(required=True)
		kind = IntID()
		relation = IntID()
		full_name = graphene.String()
		INN = graphene.String()
		KPP = graphene.String()
		OKPO = graphene.String()
		OGRN = graphene.String()
		legal_address = graphene.String()
		street_address = graphene.String()
		phone_number = graphene.String()
		manager = IntID()
		other = graphene.String()

	def mutate_and_get_payload(self, info, id_client, **kwargs):
		client = Client.objects.get(id=id_client)
		if not info.context.user.has_perm('clients.edit_client') and not info.context.user == client.manager:
			raise Exception('Ошибка: Недостаточно прав')
		Client.objects.filter(id=id_client).update(**kwargs)
		return EditClient(result=True)


class AddContact(SngyMutation):
	result = graphene.Boolean()

	class Input:
		last_name = graphene.String(required=True)
		first_name = graphene.String(required=True)
		patronum = graphene.String()
		position = graphene.String()
		phone_number = graphene.String()
		client_id = IntID(required=True)

	def mutate_and_get_payload(self, info, **kwargs):
		client = Client.objects.get(id=kwargs['client_id'])
		if not info.context.user.has_perm('clients.add_contact') and not info.context.user == client.manager:
			raise Exception('Ошибка: Недостаточно прав')
		Contact.objects.create(**kwargs)
		return AddContact(result=True)


class EditContact(SngyMutation):
	result = graphene.Boolean()

	class Input:
		id = IntID(required=True)
		last_name = graphene.String(required=True)
		first_name = graphene.String(required=True)
		patronum = graphene.String()
		position = graphene.String()
		phone_number = graphene.String()
		client_id = IntID(required=True)

	def mutate_and_get_payload(self, info, **kwargs):
		contact = Contact.objects.get(id=kwargs['id'])
		if not info.context.user.has_perm('clients.edit_contact') and not info.context.user == contact.client.manager:
			raise Exception('Ошибка: Недостаточно прав')
		Contact.objects.filter(id=kwargs['id']).update(**kwargs)
		return EditContact(result=True)


class DeleteContact(SngyMutation):
	result = graphene.Boolean()

	class Input:
		id = IntID(required=True)

	def mutate_and_get_payload(self, info, id):
		contact = Contact.objects.get(id=id)
		if not info.context.user.has_perm('clients.delete_contact') and not info.context.user == contact.client.manager:
			raise Exception('Ошибка: Недостаточно прав')
		Contact.objects.get(id=id).delete()
		return DeleteContact(result=True)


class AddClientHistory(SngyMutation):
	result = graphene.Boolean()

	class Input:
		client_id = IntID(required=True)
		contacts = graphene.List(IntID)
		date = graphene.String()
		interaction = graphene.String()
		result = graphene.String()
		next_step_date = graphene.String()
		next_step = graphene.String()

	def mutate_and_get_payload(self, info, **kwargs):
		client = Client.objects.get(id=kwargs['client_id'])
		if not info.context.user.has_perm('clients.add_clienthistory') and not info.context.user == client.manager:
			raise Exception('Ошибка: Недостаточно прав')
		contacts = kwargs.pop('contacts')
		client_history = ClientHistory.objects.create(**kwargs)
		for item in contacts:
			contact = Contact.objects.get(id=item)
			ClientHistoryContact.objects.create(contact=contact, client_history=client_history)
		return AddClientHistory(result=True)


class DeleteClientHistory(SngyMutation):
	result = graphene.Boolean()

	class Input:
		id = IntID(required=True)

	def mutate_and_get_payload(self, info, id):
		client_history = ClientHistory.objects.get(id=id)
		if not info.context.user.has_perm('clients.delete_clienthistory') and \
				not info.context.user == client_history.client.manager:
			raise Exception('Ошибка: Недостаточно прав')
		client_history = ClientHistory.objects.get(id=id)
		client_history.was_deleted = True
		client_history.save()
		return DeleteClientHistory(result=True)


class EditClientHistory(SngyMutation):
	result = graphene.Boolean()

	class Input:
		id = IntID(required=True)
		client_id = IntID()
		contacts = graphene.List(IntID)
		date = graphene.String()
		interaction = graphene.String()
		result = graphene.String()
		next_step_date = graphene.String()
		next_step = graphene.String()

	def mutate_and_get_payload(self, info, **kwargs):
		client_history = ClientHistory.objects.get(id=kwargs['id'])
		if not info.context.user.has_perm('clients.edit_clienthistory') and \
				not info.context.user == client_history.client.manager:
			raise Exception('Ошибка: Недостаточно прав')
		contacts = kwargs['contacts']
		kwargs.pop('contacts')
		ClientHistory.objects.filter(id=kwargs['id']).update(**kwargs)
		ClientHistoryContact.objects.filter(client_history_id=kwargs['id']).delete()
		for item in contacts:
			contact = Contact.objects.get(id=item)
			ClientHistoryContact.objects.create(contact=contact, client_history_id=kwargs['id'])
		return EditClientHistory(result=True)


class Mutation(graphene.ObjectType):
	add_client = AddClient.Field()
	delete_client = DeleteClient.Field()
	edit_client = EditClient.Field()
	add_contact = AddContact.Field()
	edit_contact = EditContact.Field()
	delete_contact = DeleteContact.Field()
	add_client_history = AddClientHistory.Field()
	delete_client_history = DeleteClientHistory.Field()
	edit_client_history = EditClientHistory.Field()
