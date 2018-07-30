import graphene
from crm.schema.types import IntID
from graphene_django import DjangoObjectType
from clients.models import Client, ClientKind, ClientRelation, Contact, ClientHistory, OrganizationForm


class ClientKindType(DjangoObjectType):
    class Meta:
        model = ClientKind


class ClientRelationType(DjangoObjectType):
    class Meta:
        model = ClientRelation


class ContactType(DjangoObjectType):
    class Meta:
        model = Contact


class ClientHistoryType(DjangoObjectType):
    class Meta:
        model = ClientHistory


class OrganizationFormType(DjangoObjectType):
    class Meta:
        model = OrganizationForm


class ClientType(DjangoObjectType):
    class Meta:
        model = Client


class PagedClients(graphene.ObjectType):
    clients = graphene.List(ClientType)
    total_count = graphene.Int()


class ClientFilter(graphene.InputObjectType):
    client_kind = graphene.List(IntID)
    client_relation = graphene.List(IntID)


class PagedContacts(graphene.ObjectType):
    contacts = graphene.List(ContactType)
    total_count = graphene.Int()


class ContactFilter(graphene.InputObjectType):
    client_id = graphene.List(IntID)


class ClientHistoryFilter(graphene.InputObjectType):
    client_id = graphene.List(IntID)


class PagedClientHistory(graphene.ObjectType):
    client_history = graphene.List(ClientHistoryType)
    total_count = graphene.Int()

