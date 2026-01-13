from django.core.management.base import BaseCommand

from ...models import Country

COUNTRIES = [
    {"name": "España", "iso_code": "ES", "language": "es"},
    {"name": "México", "iso_code": "MX", "language": "es"},
    {"name": "Argentina", "iso_code": "AR", "language": "es"},
    {"name": "Colombia", "iso_code": "CO", "language": "es"},
    {"name": "Chile", "iso_code": "CL", "language": "es"},
    {"name": "Perú", "iso_code": "PE", "language": "es"},
    {"name": "Estados Unidos", "iso_code": "US", "language": "en"},
    {"name": "Reino Unido", "iso_code": "GB", "language": "en"},
    {"name": "Francia", "iso_code": "FR", "language": "fr"},
    {"name": "Alemania", "iso_code": "DE", "language": "de"},
]


class Command(BaseCommand):
    help = "Popula la tabla Country con datos iniciales"

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Eliminar países existentes antes de insertar",
        )

    def handle(self, *args, **options):
        if options.get("flush"):
            Country.objects.all().delete()
            self.stdout.write(self.style.WARNING("Eliminados países existentes."))

        created = 0
        updated = 0
        for c in COUNTRIES:
            obj, created_flag = Country.objects.update_or_create(
                iso_code=c["iso_code"],
                defaults={
                    "name": c["name"],
                    "language": c["language"],
                    "is_active": True,
                },
            )
            if created_flag:
                created += 1
            else:
                updated += 1

        self.stdout.write(self.style.SUCCESS(f"Países creados: {created}, actualizados: {updated}"))
