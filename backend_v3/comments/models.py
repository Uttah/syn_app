from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class Comment(models.Model):
	content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
	object_id = models.PositiveIntegerField()
	content_object = GenericForeignKey('content_type', 'object_id')
	date = models.DateTimeField('Дата', auto_now_add=True)
	user = models.ForeignKey('users.User', on_delete=models.DO_NOTHING, verbose_name='Пользователь')
	comment = models.TextField('Комментарий')

	def __str__(self):
		return '%s: %s' % (self.user.short_name, self.comment)
