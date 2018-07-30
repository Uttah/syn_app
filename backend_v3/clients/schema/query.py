import graphene
from crm.schema.types import PagedInput
from clients.schema.types import PagedClients, PagedContacts, ClientKindType, ClientRelationType, OrganizationFormType, \
    ClientFilter, ContactFilter, ContactType, ClientType, PagedClientHistory, ClientHistoryFilter
from clients.models import Client, ClientKind, ClientRelation, Contact, ClientHistory, OrganizationForm
from crm.schema.types import IntID


class Query(graphene.ObjectType):
    paged_clients = graphene.Field(PagedClients, paged=PagedInput(required=True), filters=ClientFilter(),
                                   description="Постраничный вывод контрагентов")
    all_client_kinds = graphene.List(ClientKindType, description="Список всех типов контрагентов")
    all_client_relations = graphene.List(ClientRelationType, description="Список всех взаимоотношений")
    paged_contacts = graphene.Field(PagedContacts, paged=PagedInput(required=True), filters=ContactFilter(),
                                    description="Постраничный вывод контактов")
    all_contacts = graphene.List(ContactType, filters=IntID(), description="Список всех контактов")
    all_clients = graphene.List(ClientType, description="Список всех клиентов")
    all_own_clients = graphene.List(ClientType, description="Список клиентов с фильтрацией")
    paged_client_histories = graphene.Field(PagedClientHistory, paged=PagedInput(required=True),
                                            filters=ClientHistoryFilter(), description="Список всех взаимодействий")
    organization_forms = graphene.List(OrganizationFormType, description="Список организационно-правовых форм")

    def resolve_paged_client_histories(self, info, paged, **kwargs):
        client_histories, total_count = ClientHistory.objects.list_paged_client_histories(info, **paged, **kwargs)
        return PagedClientHistory(client_history=client_histories, total_count=total_count)

    def resolve_paged_clients(self, info, paged, **kwargs):
        clients, total_count = Client.objects.list_paged_clients(**paged, **kwargs)
        return PagedClients(clients=clients, total_count=total_count)

    def resolve_all_client_kinds(self, info):
        return ClientKind.objects.all()

    def resolve_all_client_relations(self, info):
        return ClientRelation.objects.all()

    def resolve_all_contacts(self, info, **kwargs):
        return Contact.objects.list_all_contacts(**kwargs)

    def resolve_all_clients(self, info):
        return Client.objects.all()

    def resolve_all_own_clients(self, info):
        return Client.objects.list_all_own_clients(info)

    def resolve_paged_contacts(self, info, paged, **kwargs):
        contacts, total_count = Contact.objects.list_paged_contacts(info, **paged, **kwargs)
        return PagedContacts(contacts=contacts, total_count=total_count)

    def resolve_organization_forms(self, info):
        return OrganizationForm.objects.all()
