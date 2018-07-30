from django.db import models
from .managers import AbsenceManager


class AbsenceReason(models.Model):
	name = models.CharField(max_length=150)
	deleted = models.BooleanField(default=False)

	class Meta:
		ordering = ['name']


class Absence(models.Model):
	user_added = models.ForeignKey('users.User', related_name='user_added_absence')
	time_added = models.DateTimeField(auto_now=True)
	worker = models.ForeignKey('users.User', related_name='worker')
	begin = models.DateField()
	end = models.DateField()
	time = models.TimeField()
	reason = models.ForeignKey('absences.AbsenceReason')
	comment = models.TextField(null=True)
	locked = models.BooleanField(default=False)

	objects = AbsenceManager()

	class Meta:
		ordering = ['begin', 'worker__last_name']
		permissions = (
			('change_reason', 'Может изменять причину отсутствия'),
			('manage_absences', 'Может редактировать отсутствия')
		)
