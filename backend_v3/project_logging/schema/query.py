import json
from datetime import datetime
import graphene
from django.apps import apps
from ..models import Journal
from .types import JournalType, AllModelsType


def get_rus_field_value(data):
	value = str(data)
	if isinstance(data, bool):
		value = 'нет'
		if data:
			value = 'да'
	if isinstance(data, type(None)):
		value = 'неопределенно'
	if isinstance(data, type(datetime.now().date())):
		value = '%02d.%02d.%d' % (data.day, data.month, data.year)
	if isinstance(data, type(datetime.now())):
		value = '%02d.%02d.%d %02d:%02d' % (data.day, data.month, data.year, data.hour, data.minute)
	if isinstance(data, type(datetime.now().time())):
		value = '%02d:%02d' % (data.hour, data.minute)
	return value


def get_rus_string_from_dict(before, after, model):
	string = ''
	if before and after:
		for bf in before:
			for af in after:
				if bf == af:
					field = model._meta.get_field(bf).verbose_name
					before_value = get_rus_field_value(before[bf])
					after_value = get_rus_field_value(after[af])
					string += '%s: %s ➔ %s|=-=|' % (field, before_value, after_value)  # |=-=| - разделитель
	if before and not after:
		for bf in before:
			field = model._meta.get_field(bf).verbose_name
			before_value = get_rus_field_value(before[bf])
			string += '%s: %s ➔ |=-=|' % (field, before_value)

	if not before and after:
		for af in after:
			field = model._meta.get_field(af).verbose_name
			after_value = get_rus_field_value(after[af])
			string += '%s: ➔ %s|=-=|' % (field, after_value)
	return string[0:-5]


# noinspection PyMethodMayBeStatic,PyUnusedLocal
class Query(graphene.ObjectType):
	all_journal = graphene.List(JournalType, model_name=graphene.String(required=True), instance_id=graphene.Int())
	all_models = graphene.List(AllModelsType)

	def resolve_all_models(self, info):
		all_models = Journal.objects.filter().distinct('model').values('model')
		result = []
		for d in all_models:
			app, model = d['model'].split('.')
			model = apps.get_model(app, model)
			result.append(AllModelsType(id=d['model'], name=model._meta.verbose_name))
		return result

	def resolve_all_journal(self, info, model_name, **kwargs):
		instance_id = kwargs.get('instance_id', None)
		all_journal = Journal.objects.select_related('user').filter(model=model_name)
		if instance_id:
			all_journal = all_journal.filter(instance_id=instance_id)
		app, model = model_name.split('.')
		model = apps.get_model(app, model)
		result = []
		# Подготавливаем объекты для отображения их наименования
		ids = (o['instance_id'] for o in all_journal.distinct('instance_id').order_by('instance_id').values('instance_id'))
		select_rel, prefetch_rel = model.history_related()
		instances = model.objects
		if select_rel:
			instances = instances.select_related(*select_rel)
		if prefetch_rel:
			instances = instances.prefetch_related(*prefetch_rel)
		instances = instances.filter(id__in=ids)
		instances = {o.id: o.history_name for o in instances}
		# Запрашиваем журнал
		all_journal = all_journal.order_by('-date')
		for r in all_journal:
			before = ''
			after = ''
			if r.before:
				before = json.loads(r.before)
			if r.after:
				after = json.loads(r.after)
			change = get_rus_string_from_dict(before, after, model)
			result.append(JournalType(date=r.date, user=r.user, instance=instances[r.instance_id], change=change))
		return result
