from graphene import Boolean, Field, String
from graphene.types.datetime import DateTime, Time

from crm.schema.mutation import SngyMutation
from crm.schema.types import IntID
from .types import AbsenceType, Absence
from users.decorators import permission_required
from users.models import User
from synergycrm.exceptions import SngyException


# noinspection PyUnusedLocal
class AddAbsence(SngyMutation):
	class Meta:
		description = 'Добавление отсутствия сотрудника'

	class Input:
		worker = IntID(required=True)
		begin = DateTime(required=True)
		end = DateTime(required=True)
		time = Time()
		reason = IntID(required=True)
		comment = String()

	absence = Field(AbsenceType, description='Созданное отсутствие')

	@staticmethod
	def mutate_and_get_payload(root, info, **kwargs):
		user = info.context.user
		worker = kwargs.pop('worker')
		reason = kwargs.pop('reason')
		# Причина: Отпросился
		if not info.context.user.has_perm('absences.change_reason'):
			reason = 7
		absence = None
		if info.context.user.has_perm('absences.add_absence') or User.objects.get(id=worker).head_id == user.id:
			absence = Absence(user_added=info.context.user, worker_id=worker, reason_id=reason, **kwargs)
			absence.save(force_insert=True)
		elif User.objects.get(id=worker).head_id != user.id:
			raise SngyException('Ошибка: Недостаточно прав')
		return AddAbsence(absence=absence)


# noinspection PyUnusedLocal
class DeleteAbsence(SngyMutation):
	class Meta:
		description = 'Удаление отсутствия сотрудника'

	class Input:
		absence_id = IntID(required=True, description='ID отсутствия для удаления')

	success = Field(Boolean, description='Успех операции')

	@staticmethod
	@permission_required('absences.delete_absence')
	def mutate_and_get_payload(root, info, **kwargs):
		absence = Absence.objects.get(id=kwargs.pop('absence_id'))
		if not absence.locked:
			absence.delete()
		else:
			raise SngyException('Невозможно удалить запись, учтенную в ЗП')
		return DeleteAbsence(success=True)


# noinspection PyUnusedLocal
class UpdateAbsence(SngyMutation):
	class Meta:
		description = 'Обновление данных отсутствия'

	class Input:
		id = IntID(required=True, description='ID отсутствия для изменения')
		worker = IntID(required=True)
		begin = DateTime(required=True)
		end = DateTime(required=True)
		time = Time()
		reason = IntID(required=True)
		comment = String()

	absence = Field(AbsenceType)

	@staticmethod
	def mutate_and_get_payload(root, info, id, **kwargs):
		user = info.context.user
		worker = kwargs.get('worker')
		# Если пользователь не может изменять причину отутствия, то убираем ее из запроса
		if not info.context.user.has_perm('absences.change_reason'):
			kwargs.pop('reason')
		if info.context.user.has_perm('absences.change_absence') or User.objects.get(id=worker).head_id == user.id:
			Absence.objects.filter(id=id).update(**kwargs)
		elif User.objects.get(id=worker).head_id != user.id:
			raise SngyException('Ошибка: Недостаточно прав')
		return UpdateAbsence(absence=Absence.objects.get(id=id))
