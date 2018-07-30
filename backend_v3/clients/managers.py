from django.db import models
from django.db.models import Q


class ClientManager(models.Manager):
    def list_paged_clients(self, offset, first, sort_by, desc=False, search='', filters=None):
        last = offset + first
        search = search.strip()
        clients = self.filter()
        sort_field = None
        if sort_by == 'name':
            sort_field = models.F('name')
        elif sort_by == 'kind':
            sort_field = models.F('kind__name')
        elif sort_by == 'relation':
            sort_field = models.F('relation__name')
        elif sort_by == 'manager':
            sort_field = models.F('manager')
        if desc:
            sort_field = sort_field.desc()
        if filters:
            if filters.get('client_kind'):
                clients = clients.filter(kind__in=filters['client_kind'])
            if filters.get('client_relation'):
                clients = clients.filter(relation__in=filters['client_relation'])
        if first < 0:
            return [], 0
        if search:
            clients = clients.filter(name__icontains=search)
        tc = clients.count()
        if sort_field:
            clients = clients.order_by(sort_field, '-id')
        return clients[offset:last], tc

    def list_all_own_clients(self, info):
        clients = self.filter()
        if not info.context.user.has_perm('clients.view_clients'):
            clients = clients.filter(manager_id=info.context.user)
        return clients


class ContactManager(models.Manager):
    def list_paged_contacts(self, info, offset, first, sort_by, desc=False, search='', filters=None):
        last = offset + first
        search = search.strip()
        contacts = self.filter()
        if not info.context.user.has_perm('clients.view_clients'):
            contacts = contacts.filter(client__manager_id=info.context.user)
        sort_field = None
        if sort_by:
            if sort_by == 'name':
                sort_field = models.F('last_name')
            elif sort_by == 'last_name':
                sort_field = models.F('last_name')
            elif sort_by == 'client':
                sort_field = models.F('client_id')
            if desc:
                sort_field = sort_field.desc()
        if filters:
            if filters.get('client_id'):
                contacts = contacts.filter(client_id__in=filters['client_id'])

        if first < 0:
            return [], 0
        if search:
            _filters = Q(last_name__icontains=search)
            _filters |= Q(first_name__icontains=search)
            _filters |= Q(patronum__icontains=search)
            contacts = contacts.filter(_filters)
        tc = contacts.count()
        if sort_field:
            contacts = contacts.order_by(sort_field, '-id')
        return contacts[offset:last], tc

    def list_all_contacts(self, filters=None):
        if filters:
            contacts = self.filter(client_id=filters)
        else:
            contacts = []
        return contacts


class ClientHistoryManager(models.Manager):
    def list_paged_client_histories(self, info, offset, first, sort_by, desc=False, search='', filters=None):
        last = offset + first
        search = search.strip()
        client_histories = self.filter()
        if not info.context.user.has_perm('clients.view_clients'):
            client_histories = client_histories.filter(client__manager_id=info.context.user)
        sort_field = None
        if sort_by == 'client':
            sort_field = models.F('client')
        elif sort_by == 'date':
            sort_field = models.F('date')
        elif sort_by == 'nextStepDate':
            sort_field = models.F('next_step_date')
        elif sort_by == 'nextStep':
            sort_field = models.F('next_step')
        if desc:
            sort_field = sort_field.desc()
        if filters:
            if filters.get('client_id'):
                client_histories = client_histories.filter(client_id__in=filters['client_id'])
        if first < 0:
            return [], 0
        if search:
            _search = Q(client__name__icontains=search)
            _search |= Q(interaction__icontains=search)
            _search |= Q(next_step__icontains=search)
            client_histories = client_histories.filter(_search)
        tc = client_histories.count()
        if sort_field:
            client_histories = client_histories.order_by(sort_field, '-id')
        return client_histories[offset:last], tc
