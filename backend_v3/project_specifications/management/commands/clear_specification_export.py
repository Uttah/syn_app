from django.core.management.base import BaseCommand
from os.path import join, isfile
from os import listdir, unlink
from synergycrm import settings


class Command(BaseCommand):
	def handle(self, *args, **options):
		spec_path = 'specifications/'
		save_path = join(settings.MEDIA_ROOT, spec_path)
		for the_file in listdir(save_path):
			file_path = join(save_path, the_file)
			try:
				if isfile(file_path):
					unlink(file_path)
			except OSError:
				pass
