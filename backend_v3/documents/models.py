import os.path
from hashlib import sha1
from django.db import models
from synergycrm.settings import MEDIA_ROOT


class DocumentKind(models.Model):
	name = models.CharField(max_length=250, verbose_name='Название')
	eng_name = models.CharField(max_length=250, verbose_name='Название на английском')

	class Meta:
		verbose_name = "Вид документа"
		verbose_name_plural = "Виды документов"

	def __str__(self):
		return self.name


def file_directory_path(instance, filename):
	instance.file.open()
	contents = instance.file.read()
	hasher = sha1()
	hasher.update(contents)
	path = 'documents/{}/{}_{}'.format(instance.document_kind.eng_name, hasher.hexdigest(), filename)
	if os.path.exists(MEDIA_ROOT + path):
		os.remove(MEDIA_ROOT + path)
	try:
		old_instance = Document.objects.get(id=instance.id)
		old_instance.file.delete()
	except Document.DoesNotExist:
		pass
	return path


class Document(models.Model):
	number = models.CharField('Номер документа', max_length=100, default='Null')
	document_kind = models.ForeignKey('documents.DocumentKind', verbose_name='Вид документа', null=True)
	created_by = models.ForeignKey('users.User', related_name='created_by', verbose_name='Создатель')
	creation_date = models.DateTimeField(verbose_name='Время создания', auto_now_add=True)
	is_real = models.BooleanField(verbose_name='Документ физический')
	file = models.FileField(verbose_name='Файл', upload_to=file_directory_path, null=True, blank=True)

	class Meta:
		verbose_name = "Документ"
		verbose_name_plural = "Документы"
		ordering = ['number']

	def __str__(self):
		return self.number

	def approved(self):
		approvals = Approval.objects.filter(document=self)
		for approval in approvals:
			if not approval.approved():
				return False
		return True


class Approval(models.Model):
	name = models.CharField('Наименование', max_length=100)
	document = models.ForeignKey('documents.Document', related_name='document', verbose_name='Документ')
	need_one = models.BooleanField(verbose_name='Достаточно одного', default=False)

	class Meta:
		verbose_name = "Этап утверждения"
		verbose_name_plural = "Этапы утверждения"
		ordering = ['id']

	def __str__(self):
		return self.document

	def approved(self):
		approval_users = ApprovalUsers.objects.filter(approval=self)
		result = False
		if self.need_one == True:
			result = False
			for user in approval_users:
				if user.decision == True:
					result = True
		if self.need_one == False:
			result = True
			for user in approval_users:
				if user.decision != True:
					return False
		if result == False:
			return False
		return result


class ApprovalUsers(models.Model):
	user = models.ForeignKey('users.User', related_name='user', verbose_name='Утвердители')
	approval = models.ForeignKey('documents.Approval', related_name='approval', verbose_name='Утверждение')
	when = models.DateTimeField(verbose_name='Дата утверждения')
	decision = models.NullBooleanField(verbose_name='Решение', default=None)

	class Meta:
		verbose_name = "Утвердитель"
		verbose_name_plural = "Утвердители"
		ordering = ['id']

	def __str__(self):
		return self.approval
