from django.db import models


class Company(models.Model):
	client = models.ForeignKey('clients.Client', verbose_name='Контрагент', on_delete=models.PROTECT)
	short_name = models.CharField(max_length=5, verbose_name='Сокращенное название (аббревиатура)', null=True)
	minimize_salary = models.BooleanField(verbose_name='Минимизировать ЗП', default=False)
	rest_as_gray = models.BooleanField(verbose_name='Остальное - наличными', default=False)

	class Meta:
		verbose_name = 'компания'
		verbose_name_plural = 'компании'
		ordering = ('client__name',)

	def __str__(self):
		return self.client.name
