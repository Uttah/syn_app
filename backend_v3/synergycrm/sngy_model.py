import json
from datetime import datetime
from django.db.models import Model
from project_logging.models import Journal
from django_currentuser.middleware import get_current_user


def change_data_with_serialization_problem(kwargs):
	for k in kwargs:
		data = kwargs[k]
		value = None
		if isinstance(data, type(datetime.now().date())):
			value = '%02d.%02d.%d' % (data.day, data.month, data.year)
		if isinstance(data, type(datetime.now())):
			value = '%02d.%02d.%d %02d:%02d' % (data.day, data.month, data.year, data.hour, data.minute)
		if isinstance(data, type(datetime.now().time())):
			value = '%02d:%02d' % (data.hour, data.minute)
		if value:
			kwargs[k] = value
	return kwargs


class SngyModel(Model):
	class Meta:
		abstract = True

	def save(self, *args, **kwargs):
		model_name = str(type(self)).split("'")[1].split('.'); del model_name[1]; model_name = '.'.join(model_name)
		before = None
		if self.id:
			before = type(self).objects.get(id=self.id)
			before_values = type(self).objects.filter(id=self.id).values()[0]
			for f in before_values:
				if f.find('_id') != -1 and hasattr(getattr(before, f[0:-3]), 'DoesNotExist'):
					before_values[f] = '%s - %s' % (before_values[f], getattr(before, f[0:-3]).__str__())
			before = before_values
		Model.save(self, *args, **kwargs)
		after = type(self).objects.get(id=self.id)
		after_values = type(self).objects.filter(id=self.id).values()[0]
		for f in after_values:
			if f.find('_id') != -1 and hasattr(getattr(after, f[0:-3]), 'DoesNotExist'):
				after_values[f] = '%s - %s' % (after_values[f], getattr(after, f[0:-3]).__str__())
		after = after_values
		before_difference = {}
		after_difference = {}
		if before:
			for f in before:
				if before[f] != after[f]:
					before_difference[f] = before[f]
					after_difference[f] = after[f]
			before = json.dumps(change_data_with_serialization_problem(before_difference))
			after = json.dumps(change_data_with_serialization_problem(after_difference))
		else:
			after = None
		if not before or before_difference and after_difference:
			Journal.objects.create(model=model_name, instance_id=self.id, user=get_current_user(), before=before, after=after)

	def delete(self, *args, **kwargs):
		model_name = str(type(self)).split("'")[1].split('.'); del model_name[1]; model_name = '.'.join(model_name)
		before = type(self).objects.filter(id=self.id)[0]
		before_values = type(self).objects.filter(id=self.id).values()[0]
		for f in before_values:
			if f.find('_id') != -1 and hasattr(getattr(before, f[0:-3]), 'DoesNotExist'):
				before_values[f] = '%s - %s' % (before_values[f], getattr(before, f[0:-3]).__str__())
		before = json.dumps(change_data_with_serialization_problem(before_values))
		instance_id = self.id
		Model.delete(self, *args, **kwargs)
		Journal.objects.create(model=model_name, instance_id=instance_id, user=get_current_user(), before=before, after=None)

	@property
	def history_name(self):
		return str(self)

	@classmethod
	def history_related(cls):
		return None, None
