import os
from django.core.management.base import BaseCommand
from synergycrm.settings import PROJECTS_DIR
from projects.models import Project
from projects.schema.mutation import format_project_folder


class Command(BaseCommand):
	def handle(self, *args, **options):
		folders = os.listdir(PROJECTS_DIR)
		for f in folders:
			if not f.startswith('SNGY'):
				continue
			number = f[4:10]
			try:
				int(number)
			except ValueError:
				continue
			project = Project.objects.get(number=int(number))
			if project.number > 1300:
				path = PROJECTS_DIR + format_project_folder(project)
				old_path = PROJECTS_DIR + f
				try:
					if old_path != path:
						os.rename(old_path, path)
				except PermissionError:
					print('PermissionError')
