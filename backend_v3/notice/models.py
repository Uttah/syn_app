from django.db import models
from users.models import User


class Notification(models.Model):
	NOTIFICATIONS_TYPE = (
		('N', 'Уведомление'),
		('S', 'Успешное'),
		('W', 'Предупреждение'),
		('C', 'Критическое'),
	)
	purpose = models.ForeignKey(User, related_name='notification_purpose_user', verbose_name='Цель')
	created = models.ForeignKey(User, related_name='notification_created_user', verbose_name='Создатель')
	date = models.DateTimeField('Дата создания', auto_now_add=True)
	text = models.CharField('Текст уведомления', max_length=500)
	confirmed = models.BooleanField('Подтверждено', default=False)
	type = models.CharField('Тип', max_length=1, choices=NOTIFICATIONS_TYPE, default='N')
	link = models.CharField('Ссылка', max_length=300, null=True, blank=True)

	class Meta:
		verbose_name = 'Уведомление'
		verbose_name_plural = 'Уведомления'

	def __str__(self):
		return str(self.id)
