import csv
import sys

from django.core.management.base import BaseCommand

from recipes.models import Ingredient, Unit


class Command(BaseCommand):
    help = 'Импорт данных из csv в модель Ingredient'

    def add_arguments(self, parser):
        parser.add_argument('--path', type=str, help='Путь к файлу')

    def handle(self, *args, **options):
        params_for_create = []

        try:
            file_path = options['path']
            with open(file_path, 'r', encoding='utf-8') as csv_file:
                reader = csv.reader(csv_file)
                for row in reader:
                    unit_obj, created = Unit.objects.get_or_create(name=row[1])
                    params = {
                        'name': row[0],
                        'measurement_unit_id': unit_obj.id,
                    }
                    params_for_create.append(params)

            Ingredient.objects.bulk_create(
                [Ingredient(**parameters) for parameters in params_for_create]
            )
        except Exception as error:
            self.stdout.write(
                self.style.ERROR(f'Error loading model {error}'),
            )
            sys.exit()

        self.stdout.write(
            self.style.SUCCESS(
                f'{len(params_for_create)}' ' Ingredient Objects Created'
            )
        )
