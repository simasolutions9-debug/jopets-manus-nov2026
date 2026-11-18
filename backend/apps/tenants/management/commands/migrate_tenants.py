from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Ejecuta migraciones compartidas; el provisionamiento por plan se mantiene explícito."

    def handle(self, *args, **options):
        call_command("migrate", interactive=False)
        self.stdout.write(
            self.style.SUCCESS(
                "Migraciones compartidas aplicadas; revisar provisionamiento por tenant antes de producción."
            )
        )
