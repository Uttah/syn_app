import sys
import graphene
import companies.api
import users.schema
import menu.schema
import reports.schema
import absences.schema
import projects.schema
import warehouse.schema
import salary.schema
import help.schema
import tasks.schema
import documents.schema
import clients.schema
import notice.schema
import logistics.schema
import project_specifications.schema
import comments.schema
import project_specifications.excel_gen.app
import project_logging.schema
from django.core.exceptions import PermissionDenied
from graphene.utils.str_converters import to_snake_case
from graphql.error.located_error import GraphQLLocatedError
from graphql.execution.executor import logger
from synergycrm.exceptions import SngyException

permission_denied_string = '401::Необходимо осуществить вход в систему'


# noinspection PyMethodMayBeStatic,PyShadowingBuiltins
class AuthorizationMiddleware(object):
	def resolve(self, next, root, info, **args):
		field_name = to_snake_case(info.field_name)
		if hasattr(info.parent_type, 'graphene_type'):
			field = getattr(info.parent_type.graphene_type, field_name, None)
			if field:
				allow_unauthorized = getattr(field, 'allow_unauthorized', False)
				if (not allow_unauthorized and info.context.user.is_authenticated) or allow_unauthorized:
					return next(root, info, **args)
				else:
					raise PermissionDenied(permission_denied_string)
		return next(root, info, **args)


# noinspection PyMethodMayBeStatic,PyUnusedLocal
class Query(reports.schema.Query, projects.schema.Query, warehouse.schema.Query, users.schema.Query, help.schema.Query,
            companies.api.Query, absences.schema.Query, menu.schema.Query, salary.schema.Query, tasks.schema.Query,
            documents.schema.Query, clients.schema.Query, notice.schema.Query, project_specifications.schema.Query,
            comments.schema.Query, project_logging.schema.Query, logistics.schema.Query):
	pass


class Mutation(reports.schema.Mutation, projects.schema.Mutation, warehouse.schema.Mutation, users.schema.Mutation,
               absences.schema.Mutation, salary.schema.Mutation, tasks.schema.Mutation, clients.schema.Mutation,
               notice.schema.Mutation, project_specifications.schema.Mutation, project_specifications.excel_gen.app.Mutation,
               comments.schema.Mutation, logistics.schema.Mutation):
	pass


# Фильтр, который не допускает вывод PermissionDenied в логи
def graphql_exception_filter(record):
	ignored_types = (PermissionDenied, SngyException)
	if record.exc_info:
		if len(record.exc_info) >= 2:
			exc_type = record.exc_info[0]
			exc = record.exc_info[1]
			if len(exc.args) > 0:
				exc_msg = exc.args[0]
			else:
				exc_msg = ''
			if (exc_type in ignored_types) or (exc_type is GraphQLLocatedError) and exc_msg == permission_denied_string:
				return False
			# Отслеживаем предыдущую ошибку
			if exc_type is GraphQLLocatedError and type(exc.original_error) in ignored_types:
				return False
	return True


# Переопределяем sys.excepthook
def custom_except_hook(exc_type, value, traceback):
	logger.exception('', exc_info=(exc_type, value, traceback))


# Подключаем переопределение и фильтры
sys.excepthook = custom_except_hook
logger.addFilter(graphql_exception_filter)

schema = graphene.Schema(query=Query, mutation=Mutation)
