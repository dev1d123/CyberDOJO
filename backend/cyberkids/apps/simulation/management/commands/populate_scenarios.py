from django.core.management.base import BaseCommand

from ...models import Scenario

SCENARIOS = [
    {
        "name": "Falso Soporte Técnico",
        "description": "El antagonista finge ser soporte técnico del banco y solicita información para 'verificar la cuenta'.",
        "antagonist_goal": "Obtener credenciales bancarias o datos sensibles",
        "difficulty_level": 2,
        "base_points": 100,
        "threat_type": "phishing",
        "is_active": True,
    },
    {
        "name": "Oferta de Empleo Fraude",
        "description": "El antagonista contacta ofreciendo un trabajo fácil y solicita datos personales y un pago inicial.",
        "antagonist_goal": "Conseguir transferencia o datos personales",
        "difficulty_level": 3,
        "base_points": 150,
        "threat_type": "social_engineering",
        "is_active": True,
    },
    {
        "name": "Encuesta con Recompensa",
        "description": "Se ofrece recompensa por completar una encuesta que requiere datos personales sensibles.",
        "antagonist_goal": "Recopilar PII útil para suplantación",
        "difficulty_level": 1,
        "base_points": 75,
        "threat_type": "data_collection",
        "is_active": True,
    },
    {
        "name": "Mensaje de Compañero de Trabajo",
        "description": "Un mensaje urgente de un supuesto compañero pidiendo ayuda y envío de un archivo/contraseña.",
        "antagonist_goal": "Obtener acceso a recursos internos o credenciales",
        "difficulty_level": 4,
        "base_points": 200,
        "threat_type": "impersonation",
        "is_active": True,
    },
    {
        "name": "Prueba: Solicitud de Contraseña",
        "description": "Escenario de prueba que representa una petición directa de contraseña/credenciales para verificar si los patrones peligrosos son detectados.",
        "antagonist_goal": "Provocar la divulgación de credenciales (contraseña, PIN, número de cuenta)",
        "difficulty_level": 1,
        "base_points": 50,
        "threat_type": "test_sensitive_pattern",
        "is_active": True,
    },
]


class Command(BaseCommand):
    help = "Popula la tabla Scenario con datos iniciales"

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Eliminar escenarios existentes antes de insertar",
        )

    def handle(self, *args, **options):
        if options.get("flush"):
            Scenario.objects.all().delete()
            self.stdout.write(self.style.WARNING("Eliminados escenarios existentes."))

        created = 0
        updated = 0
        for s in SCENARIOS:
            obj, created_flag = Scenario.objects.update_or_create(
                name=s["name"],
                defaults={
                    "description": s.get("description"),
                    "antagonist_goal": s.get("antagonist_goal"),
                    "difficulty_level": s.get("difficulty_level", 1),
                    "base_points": s.get("base_points", 100),
                    "threat_type": s.get("threat_type"),
                    "is_active": s.get("is_active", True),
                },
            )
            if created_flag:
                created += 1
            else:
                updated += 1

        self.stdout.write(self.style.SUCCESS(f"Escenarios creados: {created}, actualizados: {updated}"))
