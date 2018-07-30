from django.db import models
from django.contrib.postgres.fields import JSONField


class Journal(models.Model):
	model = models.CharField('Название модели', max_length=30)
	instance_id = models.IntegerField('id экземпляра')
	date = models.DateTimeField('Дата и время', auto_now_add=True)
	user = models.ForeignKey('users.User', on_delete=models.DO_NOTHING, verbose_name='Пользователь')
	before = JSONField('До', null=True, blank=True)
	after = JSONField('После', null=True, blank=True)

	class Meta:
		indexes = [
			models.Index(fields=['model']),
			models.Index(fields=['instance_id'])
		]
