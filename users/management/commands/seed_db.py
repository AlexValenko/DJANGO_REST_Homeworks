from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Загружает данные из fixtures/homework.json."

    def handle(self, *args, **options):
        fixture_path = settings.BASE_DIR / "fixtures" / "homework.json"
        if not fixture_path.is_file():
            self.stdout.write("Нет данных для заполнения: файл fixtures/homework.json не найден.")
            return

        call_command("loaddata", str(fixture_path), verbosity=options["verbosity"], stdout=self.stdout)
