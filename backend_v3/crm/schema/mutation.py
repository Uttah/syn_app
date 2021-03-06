import re
import graphene
from promise import Promise, is_thenable
from collections import OrderedDict


class SngyMutation(graphene.Mutation):
	class Meta:
		abstract = True

	@classmethod
	def __init_subclass_with_meta__(cls, output=None, input_fields=None, arguments=None, name=None, **options):
		input_class = getattr(cls, 'Input', None)
		base_name = re.sub('Payload$', '', name or cls.__name__)

		assert not output, "Can't specify any output"
		assert not arguments, "Can't specify any arguments"

		bases = (graphene.InputObjectType,)
		if input_class:
			bases += (input_class,)

		if not input_fields:
			input_fields = {}

		cls.Input = type('{}Input'.format(base_name), bases, OrderedDict(input_fields))

		arguments = OrderedDict(input=cls.Input(required=True))
		mutate_and_get_payload = getattr(cls, 'mutate_and_get_payload', None)
		if cls.mutate and cls.mutate.__func__ == SngyMutation.mutate.__func__:
			assert mutate_and_get_payload, (
				"{name}.mutate_and_get_payload method is required"
				" in a SngyMutation.").format(name=name or cls.__name__)

		if not name:
			name = '{}Payload'.format(base_name)

		super(SngyMutation, cls).__init_subclass_with_meta__(
			output=None, arguments=arguments, name=name, **options)

	# noinspection PyShadowingBuiltins
	@classmethod
	def mutate(cls, root, info, input):
		def on_resolve(payload):
			return payload

		result = cls.mutate_and_get_payload(root, info, **input)
		if is_thenable(result):
			return Promise.resolve(result).then(on_resolve)

		return on_resolve(result)
