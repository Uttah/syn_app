import graphene
from crm.schema.mutation import SngyMutation
from crm.schema.types import IntID
from .types import CoefficientsType, Coefficients
from users.decorators import permission_required
from synergycrm.exceptions import SngyException


class UpdateCoefficients(SngyMutation):
	coefficients = graphene.Field(CoefficientsType)

	class Input:
		id = IntID(required=True)
		general = graphene.Float()
		welding = graphene.Float()
		experience = graphene.Float()
		etech = graphene.Float()
		schematic = graphene.Float()
		initiative = graphene.Float()
		discipline = graphene.Float()

	@permission_required('users.view_all_coefficients')
	def mutate_and_get_payload(self, info, id, **kwargs):
		fields = ['general', 'welding', 'experience', 'etech', 'schematic', 'initiative', 'discipline']
		for f in fields:
			v = kwargs.get(f, 0)
			if v < 0 or v > 1:
				raise SngyException('value < 0 or value > 1')
		Coefficients.objects.filter(id=id).update(**kwargs)
		return UpdateCoefficients(coefficients=Coefficients.objects.get(id=id))
