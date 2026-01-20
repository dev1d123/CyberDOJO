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
    {
        "name": "Ingeniería Social",
        "description": "Un desconocido intenta establecer una conversación amigable contigo para ganarse tu confianza. Usa técnicas de manipulación psicológica para hacerte sentir cómodo y eventualmente obtener información personal. Debes identificar estas tácticas y resistir compartir datos sensibles.",
        "antagonist_goal": "número de teléfono",
        "difficulty_level": 1,
        "base_points": 180,
        "threat_type": "social_engineering",
        "is_active": True,
    },
    {
        "name": "Suplantación Digital",
        "description": "Alguien se hace pasar por una persona o entidad confiable (empresa, banco, soporte técnico) para engañarte. Intentará que hagas clic en enlaces sospechosos o que compartas credenciales. Aprende a verificar identidades y detectar señales de phishing.",
        "antagonist_goal": "correo electrónico",
        "difficulty_level": 2,
        "base_points": 220,
        "threat_type": "phishing",
        "is_active": True,
    },
    {
        "name": "Fuga de Datos",
        "description": "El atacante busca que reveles información personal sensible durante una conversación aparentemente casual. Puede preguntar sobre tu ubicación, dirección, datos familiares o información financiera de forma sutil. Debes proteger tu privacidad sin ser obvio.",
        "antagonist_goal": "dirección de residencia",
        "difficulty_level": 3,
        "base_points": 240,
        "threat_type": "data_leakage",
        "is_active": True,
    },
    {
        "name": "Pretextos Falsos",
        "description": "El antagonista crea una historia elaborada o situación de emergencia falsa para presionarte a actuar rápido y compartir información. Puede fingir ser un amigo en problemas, un familiar o alguien que necesita ayuda urgente. Mantén la calma y verifica antes de actuar.",
        "antagonist_goal": "nombre completo y edad",
        "difficulty_level": 4,
        "base_points": 260,
        "threat_type": "pretexting",
        "is_active": True,
    },
    {
        "name": "Trampas Digitales",
        "description": "Te ofrecen algo demasiado bueno para ser verdad: premios gratuitos, descuentos exclusivos, acceso a contenido premium, o beneficios especiales. A cambio, necesitan solo un pequeño dato para verificarte. Reconoce estas trampas y resiste la tentación.",
        "antagonist_goal": "contraseña o código de verificación",
        "difficulty_level": 5,
        "base_points": 280,
        "threat_type": "baiting",
        "is_active": True,
    },
    {
        "name": "Suplantación de Identidad",
        "description": "El atacante se hace pasar por alguien específico que conoces o deberías conocer: un compañero de clase, un profesor, un administrador del juego, o incluso un familiar. Usa información pública sobre ti para parecer legítimo. Verifica siempre la identidad real de quien te contacta.",
        "antagonist_goal": "usuario y contraseña de cuenta",
        "difficulty_level": 6,
        "base_points": 300,
        "threat_type": "impersonation",
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
