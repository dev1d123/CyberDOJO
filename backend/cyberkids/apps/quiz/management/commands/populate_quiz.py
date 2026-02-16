"""
Script para poblar todas las tablas del app quiz con escenarios pedagogicos.
Uso: python manage.py populate_quiz
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.quiz.models import (
    AudienceSegment,
    RiskCategory,
    Quiz,
    QuizQuestion,
    QuizAlternative,
    QuizHint,
)
from apps.quiz.rewards_config import get_expected_questions, get_points_reward


SEGMENTS = {
    "junior": {
        "name": "Junior 7-10",
        "description": "Contenido basico para ninos (7-10)",
        "min_age": 7,
        "max_age": 10,
        "display_order": 1,
    },
    "middle": {
        "name": "Middle 11-14",
        "description": "Contenido intermedio para preadolescentes (11-14)",
        "min_age": 11,
        "max_age": 14,
        "display_order": 2,
    },
    "senior": {
        "name": "Senior 15+",
        "description": "Contenido avanzado para adolescentes (15+)",
        "min_age": 15,
        "max_age": 150,
        "display_order": 3,
    },
}

CATEGORIES = [
    {"name": "Privacidad", "description": "Proteccion de datos personales", "icon": "🔒", "display_order": 1},
    {"name": "Contrasenas", "description": "Seguridad de contrasenas", "icon": "🔑", "display_order": 2},
    {"name": "Phishing", "description": "Enganos para robar informacion", "icon": "🎣", "display_order": 3},
    {"name": "Ciberacoso", "description": "Acoso en linea", "icon": "💬", "display_order": 4},
    {"name": "Descargas", "description": "Instalaciones seguras", "icon": "📥", "display_order": 5},
    {"name": "Redes Sociales", "description": "Seguridad en redes", "icon": "📱", "display_order": 6},
    {"name": "Estafas", "description": "Fraudes y ofertas falsas", "icon": "💸", "display_order": 7},
    {"name": "Banca", "description": "Seguridad bancaria", "icon": "🏦", "display_order": 8},
    {"name": "Malware", "description": "Software malicioso", "icon": "🧪", "display_order": 9},
    {"name": "Autenticacion", "description": "2FA y verificacion", "icon": "✅", "display_order": 10},
    {"name": "WiFi Publica", "description": "Riesgos de redes abiertas", "icon": "📶", "display_order": 11},
]

QUIZZES = [
    # JUNIOR (7-10) - 3 Quizzes por dificultad
    {
        "segment": "junior",
        "difficulty": "baja",  # difficulty_level: 1
        "category": "Privacidad",
        "title": "Protege tu Privacidad - Basico",
        "description": "Aprende los fundamentos basicos de privacidad digital",
        "questions": [
            {
                "content": "Tu prima quiere usar tu tablet y pide el PIN. Que haces?",
                "hint": "Los secretos se cuidan incluso con familia.",
                "alternatives": [
                    {"content": "Dar el PIN para que juegue.", "is_correct": False, "feedback": "No es seguro: el PIN protege tu cuenta."},
                    {"content": "Decirle que pregunte a un adulto.", "is_correct": True, "feedback": "Correcto: un adulto protege tu cuenta."},
                    {"content": "Dejar el PIN anotado.", "is_correct": False, "feedback": "Cualquiera podria verlo."},
                    {"content": "Cambiar el PIN a 1234.", "is_correct": False, "feedback": "Un PIN facil se adivina rapido."},
                ]
            },
            {
                "content": "Ves una foto donde aparece el numero de tu casa. Que haces?",
                "hint": "En fotos, cuida lo que se ve detras.",
                "alternatives": [
                    {"content": "Subirla igual.", "is_correct": False, "feedback": "Muestra tu direccion."},
                    {"content": "Recortar para ocultar el numero.", "is_correct": True, "feedback": "Correcto: proteges tu direccion."},
                    {"content": "Mandarla a un chat publico.", "is_correct": False, "feedback": "Mas personas verian tu casa."},
                    {"content": "Poner la direccion en comentario.", "is_correct": False, "feedback": "Compartir datos personales es riesgoso."},
                ]
            },
            {
                "content": "Un desconocido te pide tu edad y ciudad. Que haces?",
                "hint": "No todos en internet son quienes dicen ser.",
                "alternatives": [
                    {"content": "Dar los datos para caerle bien.", "is_correct": False, "feedback": "No es seguro compartir datos personales."},
                    {"content": "Bloquear y reportar.", "is_correct": True, "feedback": "Correcto: proteges tu privacidad."},
                    {"content": "Dar solo la edad.", "is_correct": False, "feedback": "Sigue siendo un dato personal."},
                    {"content": "Mandar tu usuario real.", "is_correct": False, "feedback": "Pueden buscarte fuera del juego."},
                ]
            },
            {
                "content": "Terminas de jugar y dejas tu cuenta abierta. Que haces?",
                "hint": "Cerrar sesion es como cerrar una puerta.",
                "alternatives": [
                    {"content": "Dejarla abierta porque es casa.", "is_correct": False, "feedback": "Cualquiera puede entrar a tu cuenta."},
                    {"content": "Cerrar sesion siempre.", "is_correct": True, "feedback": "Correcto: proteges tu cuenta."},
                    {"content": "Cambiar clave a algo facil.", "is_correct": False, "feedback": "Claves faciles se adivinan rapido."},
                    {"content": "Decir el PIN a todos.", "is_correct": False, "feedback": "Pierdes control de tu cuenta."},
                ]
            },
            {
                "content": "Te llega un link que dice ganaste una skin gratis. Que haces?",
                "hint": "Si no participaste, no ganaste.",
                "alternatives": [
                    {"content": "Hacer clic rapido.", "is_correct": False, "feedback": "Puede ser una pagina falsa."},
                    {"content": "Borrarlo y avisar a un adulto.", "is_correct": True, "feedback": "Correcto: evitas el engaño."},
                    {"content": "Mandarlo a amigos.", "is_correct": False, "feedback": "Contagias el engaño."},
                    {"content": "Poner datos para ver premio.", "is_correct": False, "feedback": "Podrias perder tu cuenta."},
                ]
            },
            {
                "content": "Una amiga te pide compartir el PIN de tu juego. Que haces?",
                "hint": "Tus secretos solo son tuyos.",
                "alternatives": [
                    {"content": "Compartirlo solo por hoy.", "is_correct": False, "feedback": "Riesgoso una vez que lo sabe."},
                    {"content": "No compartir y hablar con adulto.", "is_correct": True, "feedback": "Correcto: proteges tu cuenta."},
                    {"content": "Cambiar PIN a algo facil.", "is_correct": False, "feedback": "Sera facil de adivinar."},
                    {"content": "Decirle en voz alta.", "is_correct": False, "feedback": "Otros pueden escuchar."},
                ]
            }
        ]
    },
    {
        "segment": "junior",
        "difficulty": "media",  # difficulty_level: 2
        "category": "Contrasenas",
        "title": "Contrasenas Fuertes - Intermedio",
        "description": "Aprende a crear y proteger contrasenas fuertes",
        "questions": [
            {
                "content": "Un amigo te ofrece Robux si pasas tu contrasena. Que haces?",
                "hint": "Las cosas gratis suelen ser trampas.",
                "alternatives": [
                    {"content": "Pasarla porque es amigo.", "is_correct": False, "feedback": "Podria robar tu cuenta."},
                    {"content": "No compartirla y avisar adulto.", "is_correct": True, "feedback": "Correcto: proteges tu cuenta."},
                    {"content": "Pasarla solo por hoy.", "is_correct": False, "feedback": "Riesgoso una vez que la sabe."},
                    {"content": "Mandar captura de pantalla.", "is_correct": False, "feedback": "Revela datos privados."},
                ]
            },
            {
                "content": "Necesitas crear contrasena fuerte. Cual escoges?",
                "hint": "Mezcla numeros, letras y simbolos.",
                "alternatives": [
                    {"content": "Ana2010", "is_correct": False, "feedback": "Datos personales se adivinan facil."},
                    {"content": "123456", "is_correct": False, "feedback": "Numeros seguidos se adivinan."},
                    {"content": "K9@mP2x!", "is_correct": True, "feedback": "Correcto: mezcla letras mayusculas, numeros y simbolos."},
                    {"content": "Password", "is_correct": False, "feedback": "Palabras comunes son debiles."},
                ]
            },
            {
                "content": "Compartiste clave con un amigo. Que es urgente?",
                "hint": "Las claves cambian si se comprometen.",
                "alternatives": [
                    {"content": "Nada, fue solo una vez.", "is_correct": False, "feedback": "El riesgo persiste."},
                    {"content": "Cambiar la clave inmediatamente.", "is_correct": True, "feedback": "Correcto: recuperas control de la cuenta."},
                    {"content": "Esperar tres dias.", "is_correct": False, "feedback": "Demasiado tiempo para un riesgo."},
                    {"content": "Decirle al amigo que la elimine.", "is_correct": False, "feedback": "No controlas lo que otros hacen."},
                ]
            },
            {
                "content": "Olvidas tu contrasena. Cual es el paso seguro?",
                "hint": "Usa las opciones oficiales.",
                "alternatives": [
                    {"content": "Pedirle a un amigo.", "is_correct": False, "feedback": "Los amigos no tienen la clave."},
                    {"content": "Usar la recuperacion oficial.", "is_correct": True, "feedback": "Correcto: la plataforma puede verificarte."},
                    {"content": "Hacer clic en recuperar en un link extraño.", "is_correct": False, "feedback": "Podria ser phishing."},
                    {"content": "Usar una clave similar.", "is_correct": False, "feedback": "No suelve el problema de olvidar."},
                ]
            },
            {
                "content": "Sospechas que robaron tu clave. Que haces primero?",
                "hint": "Actua rapido ante compromiso.",
                "alternatives": [
                    {"content": "Cambiar la clave inmediatamente.", "is_correct": True, "feedback": "Correcto: impides acceso no autorizado."},
                    {"content": "Esperar a ver si roban.", "is_correct": False, "feedback": "Demasiado lento para actuar."},
                    {"content": "Contar a amigos.", "is_correct": False, "feedback": "No soluciona el problema."},
                    {"content": "Ignorar la sospecha.", "is_correct": False, "feedback": "El riesgo persiste."},
                ]
            },
            {
                "content": "Van a cambiar clave. Donde la escribes?",
                "hint": "La memoria es mas segura que papel.",
                "alternatives": [
                    {"content": "En una nota en el escritorio.", "is_correct": False, "feedback": "Cualquiera puede verla."},
                    {"content": "En el navegador.", "is_correct": False, "feedback": "Si roban la compu pierdes acceso."},
                    {"content": "Memorizarla.", "is_correct": True, "feedback": "Correcto: es mas seguro que papel."},
                    {"content": "Mandarla por WhatsApp.", "is_correct": False, "feedback": "Terceros pueden verla."},
                ]
            },
            {
                "content": "Usas la misma clave en varios sitios. Que riesgo hay?",
                "hint": "Si uno se compromete, todos caen.",
                "alternatives": [
                    {"content": "Es mas facil de recordar.", "is_correct": False, "feedback": "No vale el riesgo."},
                    {"content": "Si roban una, roban todas.", "is_correct": True, "feedback": "Correcto: usa claves unicas por sitio."},
                    {"content": "Los sitios se protegen entre si.", "is_correct": False, "feedback": "Cada sitio es independiente."},
                    {"content": "No hay riesgo. Confia en ti.", "is_correct": False, "feedback": "El riesgo es real."},
                ]
            },
            {
                "content": "Te piden la clave por correo. Que haces?",
                "hint": "Sitios legales nunca piden claves.",
                "alternatives": [
                    {"content": "Darla si el correo parece oficial.", "is_correct": False, "feedback": "Es phishing."},
                    {"content": "Ignorar y entrar a la pagina directa.", "is_correct": True, "feedback": "Correcto: nunca des claves por correo."},
                    {"content": "Llamar al numero del correo.", "is_correct": False, "feedback": "El numero podria ser falso."},
                    {"content": "Dar solo la mitad.", "is_correct": False, "feedback": "Sigue siendo inseguro."},
                ]
            },
            {
                "content": "Cambias clave cada mes. Cual es el beneficio?",
                "hint": "Limita el tiempo de acceso no autorizado.",
                "alternatives": [
                    {"content": "Ningun beneficio especial.", "is_correct": False, "feedback": "Hay beneficios reales."},
                    {"content": "Limita robo de acceso anterior.", "is_correct": True, "feedback": "Correcto: si se compromete, solo durante un mes."},
                    {"content": "Hace la clave mas fuerte.", "is_correct": False, "feedback": "Cambia fortaleza, no frecuencia."},
                    {"content": "Es una regla sin motivo.", "is_correct": False, "feedback": "Hay razon de seguridad."},
                ]
            },
            {
                "content": "La clave tiene tu nombre/fecha nacimiento. Es segura?",
                "hint": "Datos personales se adivinan.",
                "alternatives": [
                    {"content": "Si, porque solo tu sabes.", "is_correct": False, "feedback": "Tu informacion es publica."},
                    {"content": "No, es facil de adivinar.", "is_correct": True, "feedback": "Correcto: evita datos personales."},
                    {"content": "Depende del idioma.", "is_correct": False, "feedback": "No importa el idioma."},
                    {"content": "Si agrego un numero es segura.", "is_correct": False, "feedback": "Sigue siendo debil en base."},
                ]
            }
        ]
    },
    {
        "segment": "junior",
        "difficulty": "alta",  # difficulty_level: 3
        "category": "Phishing",
        "title": "Detecta Phishing - Avanzado",
        "description": "Identifica intentos de engaño y protege tus datos",
        "questions": [
            {
                "content": "Un DM de Instagram dice tu cuenta sera bloqueada. Que haces?",
                "hint": "Instagram no avisa por mensajes privados.",
                "alternatives": [
                    {"content": "Hacer clic en el link.", "is_correct": False, "feedback": "Es phishing."},
                    {"content": "Revisar en la app oficial.", "is_correct": True, "feedback": "Correcto: verifica desde app oficial."},
                    {"content": "Reenviar a amigos.", "is_correct": False, "feedback": "Contagias el engaño."},
                    {"content": "Responder con correo.", "is_correct": False, "feedback": "Das datos a desconocido."},
                ]
            },
            {
                "content": "Correo dice cuenta bloqueada, pide ingresar datos. Analiza:",
                "hint": "Busca senal de phishing.",
                "alternatives": [
                    {"content": "Confiar porque parece oficial.", "is_correct": False, "feedback": "El diseno puede ser copiado."},
                    {"content": "Llamar a soporte oficial.", "is_correct": True, "feedback": "Correcto: verifica por canal oficial."},
                    {"content": "Poner datos para recuperar.", "is_correct": False, "feedback": "Pierdes acceso a la cuenta."},
                    {"content": "Ignorar permanentemente.", "is_correct": False, "feedback": "Si era real pierdes cuenta."},
                ]
            },
            {
                "content": "Link te llevaria a ingresar usuario/clave, pero la URL es rara. Que significa?",
                "hint": "URL real vs URL falsa.",
                "alternatives": [
                    {"content": "Es un sitio de espejo (mirror).", "is_correct": False, "feedback": "No existen espejos legales."},
                    {"content": "Es phishing, no hagas clic.", "is_correct": True, "feedback": "Correcto: URL extraña es senal de phishing."},
                    {"content": "Solo ingresar si te sientes comodo.", "is_correct": False, "feedback": "El riesgo siempre existe."},
                    {"content": "Usa VPN para entrar seguro.", "is_correct": False, "feedback": "VPN no protege de phishing."},
                ]
            },
            {
                "content": "Recibes correo: 'Verify your account or it closes!'? Que haces?",
                "hint": "Presion y prisa son senales.",
                "alternatives": [
                    {"content": "Hacer clic inmediatamente.", "is_correct": False, "feedback": "La prisa es tactica de phishing."},
                    {"content": "Entrar a la pagina oficialmente.", "is_correct": True, "feedback": "Correcto: ignora la prisa."},
                    {"content": "Llamar a numero en el correo.", "is_correct": False, "feedback": "Numero podria ser falso."},
                    {"content": "Preguntar en group de WhatsApp.", "is_correct": False, "feedback": "No es el lugar para verificar."},
                ]
            },
            {
                "content": "Correo de un 'banco' para 'actualizar datos'. Riesgo real?",
                "hint": "Bancos no piden datos por correo.",
                "alternatives": [
                    {"content": "No, es comunicacion normal.", "is_correct": False, "feedback": "Es sospechoso."},
                    {"content": "Si, muy probable phishing.", "is_correct": True, "feedback": "Correcto: bancos usan canales seguros."},
                    {"content": "Depende del banco.", "is_correct": False, "feedback": "Ninguno lo hace."},
                    {"content": "Solo si pides datos de tarjeta.", "is_correct": False, "feedback": "Cualquier dato bancario es riesgoso."},
                ]
            },
            {
                "content": "Link en email muestra bit.ly/xyz pero es realmente otro sitio. Que es?",
                "hint": "Las URLs acortadas ocultan destino real.",
                "alternatives": [
                    {"content": "Tecnica segura de Google.", "is_correct": False, "feedback": "No es segura, oculta destino."},
                    {"content": "Podria ocultar phishing.", "is_correct": True, "feedback": "Correcto: no uses links acortados."},
                    {"content": "Solo problema con navegador antiguo.", "is_correct": False, "feedback": "Afecta todos los navegadores."},
                    {"content": "Seguro si el correo es legit.", "is_correct": False, "feedback": "Correos pueden ser falsificados."},
                ]
            },
            {
                "content": "Archivos adjuntos en correo de amigo. Riesgo?",
                "hint": "Cuenta de amigo podria estar hackeada.",
                "alternatives": [
                    {"content": "Ningun riesgo, confio en amigo.", "is_correct": False, "feedback": "La cuenta podria estar comprometida."},
                    {"content": "Verificar con amigo antes de abrir.", "is_correct": True, "feedback": "Correcto: confirma que amigo lo envio."},
                    {"content": "Abrir si archivo parece seguro.", "is_correct": False, "feedback": "La apariencia puede engañar."},
                    {"content": "Usar antivirus logrará seguridad.", "is_correct": False, "feedback": "Antivirus no previene phishing."},
                ]
            },
            {
                "content": "Correo muy profesional y urgente pidiendo verificacion. Que haces?",
                "hint": "Profesionalismo no garantiza legitimidad.",
                "alternatives": [
                    {"content": "Confiar y verificar datos.", "is_correct": False, "feedback": "Phishing pode parecer profesional."},
                    {"content": "Contactar directamente a empresa.", "is_correct": True, "feedback": "Correcto: verifica por canal oficial."},
                    {"content": "Buscar el numero en el email.", "is_correct": False, "feedback": "Numero puede ser falso."},
                    {"content": "Ignorar si no recuerdas problemas.", "is_correct": False, "feedback": "Podria perder acceso importante."},
                ]
            },
            {
                "content": "Correo dice 'confirma identidad en 5 minutos'. Que significa?",
                "hint": "Presion de tiempo es tactica comun.",
                "alternatives": [
                    {"content": "Es urgencia legitima.", "is_correct": False, "feedback": "Es parte de la estrategia."},
                    {"content": "Es phishing con presion.", "is_correct": True, "feedback": "Correcto: la prisa evita reflexion."},
                    {"content": "Solo si viene de tu banco.", "is_correct": False, "feedback": "Aun bancos legit dan mas tiempo."},
                    {"content": "Verifica pero sin prisa.", "is_correct": False, "feedback": "Mejor no haga clic en link."},
                ]
            },
            {
                "content": "Te piden 'confirmar' informacion por link en email. Resultado mas probable?",
                "hint": "La palabra 'confirmar' es tactica.",
                "alternatives": [
                    {"content": "Legit, confirmas tus propios datos.", "is_correct": False, "feedback": "Es phishing."},
                    {"content": "Roban datos al hacer clic.", "is_correct": True, "feedback": "Correcto: el link lleva a sitio falso."},
                    {"content": "Es solo para verificar navegador.", "is_correct": False, "feedback": "El objetivo es robar datos."},
                    {"content": "Seguro si tienes antivirus.", "is_correct": False, "feedback": "Antivirus no ayuda aca."},
                ]
            },
            {
                "content": "Observas email de Paypal. URL dice paypa1.com vs paypal.com. Riesgo?",
                "hint": "Una letra diferente cambia todo.",
                "alternatives": [
                    {"content": "Ningun riesgo, es casi igual.", "is_correct": False, "feedback": "Una letra diferente es phishing."},
                    {"content": "Alto riesgo, URL es falsa.", "is_correct": True, "feedback": "Correcto: letra '1' en lugar de 'l'."},
                    {"content": "Phishing solo en mayusculas.", "is_correct": False, "feedback": "Puede ser cualquier variacion."},
                    {"content": "Entrar lentamente para revisar.", "is_correct": False, "feedback": "No hagas clic en links falsos."},
                ]
            },
            {
                "content": "Correo de Amazon con gramatica pobre/errores. Que sugiere?",
                "hint": "Empresas grandes cuidan detalles.",
                "alternatives": [
                    {"content": "Podria ser error de redactor.", "is_correct": False, "feedback": "Empresas profesionales revisan."},
                    {"content": "Sospecha fuerte de phishing.", "is_correct": True, "feedback": "Correcto: errores sugieren falsificacion."},
                    {"content": "Solo problema en algunos idiomas.", "is_correct": False, "feedback": "Amazon cuida en todos."},
                    {"content": "Confiar si logo se ve correcto.", "is_correct": False, "feedback": "Logo puede ser copiado."},
                ]
            }
        ]
    },
    # MIDDLE (11-14) - 3 Quizzes por dificultad
    {
        "segment": "middle",
        "difficulty": "baja",
        "category": "Redes Sociales",
        "title": "Redes Seguras - Basico",
        "description": "Protege tu identidad en redes sociales",
        "questions": [
            {
                "content": "Un desconocido solicita amistad en Instagram. Que haces?",
                "hint": "No todos son quienes dicen ser.",
                "alternatives": [
                    {"content": "Aceptar para tener mas amigos.", "is_correct": False, "feedback": "Podria ser un depredador."},
                    {"content": "Revisar perfil e ignorar si es extraño.", "is_correct": True, "feedback": "Correcto: verifica antes de aceptar."},
                    {"content": "Aceptar y bloquearlo despues.", "is_correct": False, "feedback": "Pierde tiempo y es riesgoso."},
                    {"content": "Aceptar si tiene muchos followers.", "is_correct": False, "feedback": "Followers no prueban legitimidad."},
                ]
            },
            {
                "content": "Subes foto en bikini/short. Que debes saber?",
                "hint": "Lo que subes puede usarse mal.",
                "alternatives": [
                    {"content": "Es tu cuerpo, publicalo.", "is_correct": False, "feedback": "Otros pueden guardar/compartir."},
                    {"content": "Considerar que podria ser replicada.", "is_correct": True, "feedback": "Correcto: una vez online nunca se elimina."},
                    {"content": "Borrar despues lo protege.", "is_correct": False, "feedback": "Ya fue capturada."},
                    {"content": "Solo amigos cercanos?", "is_correct": False, "feedback": "Amigos tambien pueden compartir."},
                ]
            },
            {
                "content": "Un bot te sigue y te manda DM raro. Que haces?",
                "hint": "Los bots buscan dejar links.",
                "alternatives": [
                    {"content": "Responder para saber que es.", "is_correct": False, "feedback": "Confirma que tu cuenta es activa."},
                    {"content": "Bloquear y reportar.", "is_correct": True, "feedback": "Correcto: elimina el problema."},
                    {"content": "Ignorar, que se vaya solo.", "is_correct": False, "feedback": "Persisten si ven actividad."},
                    {"content": "Seguir de vuelta.", "is_correct": False, "feedback": "No ayuda."},
                ]
            },
            {
                "content": "Publicas ubicacion exacta en historias de TikTok. Que riesgo?",
                "hint": "Los predadores rastrean ubicaciones.",
                "alternatives": [
                    {"content": "Ningun riesgo, es solo TikTok.", "is_correct": False, "feedback": "El riesgo es real."},
                    {"content": "Podria revelar donde vives.", "is_correct": True, "feedback": "Correcto: evita ubicaciones exactas."},
                    {"content": "Solo riesgo si eres famoso.", "is_correct": False, "feedback": "Aplica a todos."},
                    {"content": "TikTok lo elimina automatico.", "is_correct": False, "feedback": "No lo hace."},
                ]
            },
            {
                "content": "Cuentas verificadas te piden numero para sorteo. Que es?",
                "hint": "Cuentas falsas copian nombres.",
                "alternatives": [
                    {"content": "Especie de sorteo real.", "is_correct": False, "feedback": "Es phishing."},
                    {"content": "Probablemente cuenta falsa.", "is_correct": True, "feedback": "Correcto: verifica si es oficial."},
                    {"content": "Seguro si tiene badge azul.", "is_correct": False, "feedback": "Badges pueden ser falsificados."},
                    {"content": "Dar numero falso para estar seguro.", "is_correct": False, "feedback": "Mejor no participar."},
                ]
            },
            {
                "content": "Amiga sube video donde te ves mal. Suplicale que lo borre?",
                "hint": "Tu dignidad revela importancia.",
                "alternatives": [
                    {"content": "No, porque es su video.", "is_correct": False, "feedback": "Tu imagen importa."},
                    {"content": "Si, es derecho tuyo.", "is_correct": True, "feedback": "Correcto: puedes pedir remoci­on."},
                    {"content": "Bloquearla if no obedece.", "is_correct": False, "feedback": "Extremo pero comienza conversacion."},
                    {"content": "Reportar a Instagram.", "is_correct": False, "feedback": "Primero habla con amiga."},
                ]
            }
        ]
    },
    {
        "segment": "middle",
        "difficulty": "media",
        "category": "Descargas",
        "title": "Descargas Seguras - Intermedio",
        "description": "Evita malware y virus al descargar",
        "questions": [
            {
                "content": "Video promete mod gratis con link raro. Que haces?",
                "hint": "Mods seguros vienen de fuentes autorizadas.",
                "alternatives": [
                    {"content": "Descargar e instalar.", "is_correct": False, "feedback": "Podria traer malware."},
                    {"content": "Buscar en pagina oficial.", "is_correct": True, "feedback": "Correcto: fuente confiable protege."},
                    {"content": "Desactivar antivirus para instalar.", "is_correct": False, "feedback": "Muy peligroso."},
                    {"content": "Descargar en PC sin internet.", "is_correct": False, "feedback": "Igual se ejecuta."},
                ]
            },
            {
                "content": "Descarga tiene tamano muy pequeno para lo que promete. Sospecha?",
                "hint": "Archivos completos son mas grandes.",
                "alternatives": [
                    {"content": "No, puede estar comprimido.", "is_correct": False, "feedback": "Hay limites de compresion."},
                    {"content": "Si, podria ser falso o incompleto.", "is_correct": True, "feedback": "Correcto: tamano anormal es sospechoso."},
                    {"content": "Solo si es menos de 1MB.", "is_correct": False, "feedback": "Tamano es relativo a contenido."},
                    {"content": "Descargar igual, no importa.", "is_correct": False, "feedback": "Importa para seguridad."},
                ]
            },
            {
                "content": "Instalador pide acceso a galeria y contactos. Que significa?",
                "hint": "Permisos excesivos son banderas rojas.",
                "alternatives": [
                    {"content": "Es normal para cualquier app.", "is_correct": False, "feedback": "La mayoria no los necesita."},
                    {"content": "Sospechoso, podria robarte datos.", "is_correct": True, "feedback": "Correcto: rechaza permisos innecesarios."},
                    {"content": "Solo problema si es Android.", "is_correct": False, "feedback": "iOS tambien tiene riesgos."},
                    {"content": "Dale permiso y desinstala si pasa algo.", "is_correct": False, "feedback": "Demasiado tarde para recuperar."},
                ]
            },
            {
                "content": "Descargas programa que promete acelerar tu compu. Que riesgo?",
                "hint": "Optimizadores falsos son comunes.",
                "alternatives": [
                    {"content": "Ningun riesgo si viene de web.", "is_correct": False, "feedback": "Webs falsas existen."},
                    {"content": "Podria traer adware o spyware.", "is_correct": True, "feedback": "Correcto: solo usa Windows official."},
                    {"content": "Solo problema si es antiguo.", "is_correct": False, "feedback": "La edad no importa aca."},
                    {"content": "Antivirus lo atrapara.", "is_correct": False, "feedback": "No siempre, especialmente cepas nuevas."},
                ]
            },
            {
                "content": "Descargas archivo de un repositorio desconocido. Como verificas?",
                "hint": "Checksum y hash verifican integridad.",
                "alternatives": [
                    {"content": "Confiar en el tamano del archivo.", "is_correct": False, "feedback": "Tamano no prueba seguridad."},
                    {"content": "Verificar hash SHA si lo proporciona.", "is_correct": True, "feedback": "Correcto: hash confirma que no fue alterado."},
                    {"content": "Escanar con multiples antivirus.", "is_correct": False, "feedback": "Es bueno pero insuficient."},
                    {"content": "Descargar en VM aislada.", "is_correct": False, "feedback": "Buena practica pero lenta."},
                ]
            },
            {
                "content": "Instalador bien conocido pide ejecutar como administrador. Es seguro?",
                "hint": "Admin access permite cambios profundos.",
                "alternatives": [
                    {"content": "Si, es programa conocido.", "is_correct": False, "feedback": "Conocido no garantiza seguridad."},
                    {"content": "Verifica realmente lo necesita.", "is_correct": True, "feedback": "Correcto: algunos piden permisos innecesarios."},
                    {"content": "Nunca de admin a nada.", "is_correct": False, "feedback": "Algunos programas genuinos lo necesitan."},
                    {"content": "Dar permiso y monitorear despues.", "is_correct": False, "feedback": "Demasiado tarde si es malicioso."},
                ]
            },
            {
                "content": "El archivo .exe tiene icono raro o nombre extraño. Que haces?",
                "hint": "Nombres normales pueden engañar.",
                "alternatives": [
                    {"content": "Ejecutar igual.", "is_correct": False, "feedback": "Icono raro es bandera roja."},
                    {"content": "No ejecutar. Investigar antes.", "is_correct": True, "feedback": "Correcto: confía en tu instinto."},
                    {"content": "Renombrar e intentar de nuevo.", "is_correct": False, "feedback": "No cambia lo que hace."},
                    {"content": "Ejecutar en modo ventana.", "is_correct": False, "feedback": "No cambia riesgos."},
                ]
            },
            {
                "content": "Post en forum dice 'Click aqui para version completa gratis'. Que es?",
                "hint": "Las cosas gratis no son siempre gratis.",
                "alternatives": [
                    {"content": "Alguien siendo generoso.", "is_correct": False, "feedback": "No en internet."},
                    {"content": "Probablemente malware o estafa.", "is_correct": True, "feedback": "Correcto: evita links de forums."},
                    {"content": "Seguro si tiene muchos likes.", "is_correct": False, "feedback": "Likes pueden ser falsos."},
                    {"content": "Usar VPN para protegerse.", "is_correct": False, "feedback": "VPN no previene malware."},
                ]
            },
            {
                "content": "Descargas app que solicita permisos de SMS/llamadas. Normal?",
                "hint": "Que app de juego necesita acceso a tel?",
                "alternatives": [
                    {"content": "Si, muchas apps lo piden.", "is_correct": False, "feedback": "Pocas deberien pedirlo."},
                    {"content": "No, es muy sospechoso. Desinstala.", "is_correct": True, "feedback": "Correcto: protege tus mensajes."},
                    {"content": "Solo si es app de mensajeria.", "is_correct": False, "feedback": "Pero incluso entonces es riesgo."},
                    {"content": "Dale el permiso pero borra app.", "is_correct": False, "feedback": "Demasiado tiempo danando."},
                ]
            },
            {
                "content": "Descarga gigante promete ser juego. Extension es .exe pero tamaño 5GB. Sospecha?",
                "hint": "Los juegos se distribuyen en platforms.",
                "alternatives": [
                    {"content": "Podria ser un juego legit.", "is_correct": False, "feedback": "Juegos vienen de Steam, Epic, etc."},
                    {"content": "Si, muy probablemente scam. Evita.", "is_correct": True, "feedback": "Correcto: distribuidores oficiales evitan .exe grande."},
                    {"content": "Descargalo en maquina virtual.", "is_correct": False, "feedback": "Mejor evitar completamente."},
                    {"content": "Usa bloqueador de ads antes.", "is_correct": False, "feedback": "Blockeador no ayuda aca."},
                ]
            }
        ]
    },
    {
        "segment": "middle",
        "difficulty": "alta",
        "category": "Ciberacoso",
        "title": "Frente al Ciberacoso - Avanzado",
        "description": "Identifica y responde al acoso online",
        "questions": [
            {
                "content": "En grupo burlan a compañero. Piden memes. Que haces?",
                "hint": "Participar normaliza el acoso.",
                "alternatives": [
                    {"content": "Mandar memes para encajar.", "is_correct": False, "feedback": "Aumentas el daño."},
                    {"content": "No participar y avisar adulto.", "is_correct": True, "feedback": "Correcto: proteges al compañero."},
                    {"content": "Mirar pero no comentar.", "is_correct": False, "feedback": "El silencio perpetúa."},
                    {"content": "Defender solo si te conoce bien.", "is_correct": False, "feedback": "Defender siempre es lo correcto."},
                ]
            },
            {
                "content": "Alguien te hace memes agraviantes y los comparte. Que sientes y haces?",
                "hint": "Tu reaccion emocional es valida.",
                "alternatives": [
                    {"content": "Ignorar completamente.", "is_correct": False, "feedback": "El dolor es valido. Actua."},
                    {"content": "Reportar y hablar con adulto.", "is_correct": True, "feedback": "Correcto: busca apoyo."},
                    {"content": "Vengarte con memes peores.", "is_correct": False, "feedback": "Escala el conflicto."},
                    {"content": "Dejar de ir a la escuela.", "is_correct": False, "feedback": "No resuelve, empeora."},
                ]
            },
            {
                "content": "En video de TikTok todos comentan burlas sobre ti. Paso a paso?",
                "hint": "Hay multiples etapas de respuesta.",
                "alternatives": [
                    {"content": "Entrtar en los comentarios y pelear.", "is_correct": False, "feedback": "Escala y empeora."},
                    {"content": "Reportar video, bloquear, avisar adulto.", "is_correct": True, "feedback": "Correcto: documen ta y obtén apoyo."},
                    {"content": "Borrar tu TikTok para evitar.", "is_correct": False, "feedback": "Excesivo. Hay mejores opciones."},
                    {"content": "Hablar solo con amigos cercanos.", "is_correct": False, "feedback": "Necesitas autoridades."},
                ]
            },
            {
                "content": "Hackers publicaron info privada tuya (doxxing). Que prioritario?",
                "hint": "La accion rapida limita danio.",
                "alternatives": [
                    {"content": "Contactar abogado primero.", "is_correct": False, "feedback": "Bueno pero no prioritario."},
                    {"content": "Reportar a plataforma e informar autoridades.", "is_correct": True, "feedback": "Correcto: documentacion y ayuda oficial."},
                    {"content": "Ignorar y cambiar clave.", "is_correct": False, "feedback": "Insuficiente. Necesitas ayuda."},
                    {"content": "Postear pruebas de que es falso.", "is_correct": False, "feedback": "Amplifica la distribucion."},
                ]
            },
            {
                "content": "Alguien susustra tu foto y te hace parecer en situacion compromedora. Que es?",
                "hint": "Es una forma grave de acoso.",
                "alternatives": [
                    {"content": "Solo una broma sin importancia.", "is_correct": False, "feedback": "Es explotacion sexual."},
                    {"content": "Deepfake o suplantacion. Muy grave. Reporta.", "is_correct": True, "feedback": "Correcto: es crimen en muchos lugares."},
                    {"content": "Ignorar porque no es real.", "is_correct": False, "feedback": "El danio psicologico es real."},
                    {"content": "Pedir que lo borre por DM.", "is_correct": False, "feedback": "Necesitas ayuda oficial."},
                ]
            },
            {
                "content": "Ciberbullies crean chat grupal solo para burlarte. Que señales de crisis?",
                "hint": "Tu bienestar mental cuenta.",
                "alternatives": [
                    {"content": "Nada, es solo internet.", "is_correct": False, "feedback": "Afecta la salud mental real."},
                    {"content": "Aislamiento, depresion, ideacion suicida. Busca ayuda urgente.", "is_correct": True, "feedback": "Correcto: busca profesionales de salud mental."},
                    {"content": "Solo ignorar como 'parte de crecer'.", "is_correct": False, "feedback": "No deberia ser 'normal'."},
                    {"content": "Intentar problemas academicos como castigo.", "is_correct": False, "feedback": "Te castigas a ti mismo."},
                ]
            },
            {
                "content": "Compañero crea cuenta falsa suplantandote. Como responder?",
                "hint": "Suplantacion es delito.",
                "alternatives": [
                    {"content": "Crear cuenta fake tuyo de venganza.", "is_correct": False, "feedback": "Escalas el problema."},
                    {"content": "Reportar a plataforma y avisar autoridades.", "is_correct": True, "feedback": "Correcto: es suplantacion. Delito."},
                    {"content": "Ignorar y esperar que se canse.", "is_correct": False, "feedback": "Podria continuar u empeorar."},
                    {"content": "Decirle en persona que pare.", "is_correct": False, "feedback": "Probablemente no funcione."},
                ]
            },
            {
                "content": "Acosador amenaza revelar secreto tuyo si no envias fotos. Que haces?",
                "hint": "Es extorsion sexual (sextortion).",
                "alternatives": [
                    {"content": "Enviar las fotos para evitar amenaza.", "is_correct": False, "feedback": "El ciclo nunca para."},
                    {"content": "No envies NADA. Reporta inmediatamente. Busca ayuda.", "is_correct": True, "feedback": "Correcto: es extorsion criminal."},
                    {"content": "Contactar al acosador e intentar razonar.", "is_correct": False, "feedback": "No funciona. Necesitas autoridades."},
                    {"content": "Cambiar password y esperar.", "is_correct": False, "feedback": "Insuficiente. Necesitas accion."},
                ]
            },
            {
                "content": "El acoso viene de cuenta privada de alguien que no conoces. Paso a paso?",
                "hint": "El rastreo y documentacion son claves.",
                "alternatives": [
                    {"content": "Hablar de vuelta con la cuenta.", "is_correct": False, "feedback": "No reconoce al acosador."},
                    {"content": "Bloquear, reportar a plataforma, guardar evidencia, avisar adulto.", "is_correct": True, "feedback": "Correcto: multiples capas de proteccion."},
                    {"content": "Ignorar y bloqueador automatico.", "is_correct": False, "feedback": "Podria volver en nueva cuenta."},
                    {"content": "Desactivar redes completamente.", "is_correct": False, "feedback": "Muy extremo. Hay mejores opciones."},
                ]
            },
            {
                "content": "Varios compañeros coordinan rechazarte en grupo. Como se llama?",
                "hint": "Es exclusion sistematica.",
                "alternatives": [
                    {"content": "Juego normal de ninos.", "is_correct": False, "feedback": "No, es exclusion deliberada."},
                    {"content": "Ostracismo o bullying grupal. Advisa a guia o psicolo.", "is_correct": True, "feedback": "Correcto: tiene impacto pasicologico serio."},
                    {"content": "Nada, los ignora a todos.", "is_correct": False, "feedback": "El danio existe incluso sin atender."},
                    {"content": "Forzar tu forma con ellos.", "is_correct": False, "feedback": "Agrava la tension."},
                ]
            }
        ]
    },
    # SENIOR (15+) - 3 Quizzes por dificultad
    {
        "segment": "senior",
        "difficulty": "baja",
        "category": "Banca",
        "title": "Seguridad Bancaria - Basico",
        "description": "Protege tus cuentas y transacciones financieras",
        "questions": [
            {
                "content": "Tu banco te envia alerta de login desde geo desconocida. Que haces?",
                "hint": "Los bancos AlertAn de actividad anormal.",
                "alternatives": [
                    {"content": "Ignorar, sera error.", "is_correct": False, "feedback": "Podria ser compromiso real."},
                    {"content": "Contactar al banco por number oficial.", "is_correct": True, "feedback": "Correcto: verifica por canal seguro."},
                    {"content": "Entrar a link del email alerta.", "is_correct": False, "feedback": "Podria ser phishing."},
                    {"content": "Cambiar PIN de inmediato desde ATM.", "is_correct": False, "feedback": "PIN no es para login web."},
                ]
            },
            {
                "content": "Email dice tu banco bloqueara cuenta. Enlace en el email. Que haces?",
                "hint": "Bancos no piden datos por email.",
                "alternatives": [
                    {"content": "Hacer clic para resolver.", "is_correct": False, "feedback": "Es phishing."},
                    {"content": "Contactar al banco directamente. Ignorar link.", "is_correct": True, "feedback": "Correcto: skip email. Contacta banco."},
                    {"content": "Verificar en app del banco.", "is_correct": False, "feedback": "Mas lento que llamar."},
                    {"content": "Enviar numero de tarjeta por reply.", "is_correct": False, "feedback": "NUNCA hagas esto."},
                ]
            },
            {
                "content": "Ves cargo no autorizado en tu cuenta. Primeros pasos?",
                "hint": "Tiempo es dinero en fraude.",
                "alternatives": [
                    {"content": "Esperar cuenta para ver si se revierte.", "is_correct": False, "feedback": "Demasiado lento."},
                    {"content": "Reportar inmediatamente al banco. Disputa la transaccion.", "is_correct": True, "feedback": "Correcto: actua rapido. Window limitado."},
                    {"content": "Cambiar solo la contrasena online.", "is_correct": False, "feedback": "Insuficiente. Necesitas ayuda banco."},
                    {"content": "Dejar de usar la tarjeta.", "is_correct": False, "feedback": "Bueno pero no suficiente."},
                ]
            },
            {
                "content": "Banco te ofrece 'verificacion en 2 pasos'. Que recomendacion?",
                "hint": "2FA reduce significativamente fraude.",
                "alternatives": [
                    {"content": "Rechazar, es muy molesto.", "is_correct": False, "feedback": "Vale la molestia."},
                    {"content": "Activar, preferible app autenticadora.", "is_correct": True, "feedback": "Correcto: es la mejor opcion."},
                    {"content": "Usar SMS si es opcion.", "is_correct": False, "feedback": "App autenticadora es mas segura."},
                    {"content": "Usar preguntas de seguridad solo.", "is_correct": False, "feedback": "Menos seguro que autenticador."},
                ]
            },
            {
                "content": "Recibles oferta 'gana cashback' pero requiere link. Sospecha?",
                "hint": "Cashback legit viene del banco oficial.",
                "alternatives": [
                    {"content": "No, muchos bancos lo ofrecen.", "is_correct": False, "feedback": "Verdadero pero verifica origen."},
                    {"content": "Si. Consulta con banco primero.", "is_correct": True, "feedback": "Correcto: verifica programas en pagina oficial."},
                    {"content": "Hacer clic si el email parece profesional.", "is_correct": False, "feedback": "Phishing puede parecer pro."},
                    {"content": "Dar datos bancarios para verificar.", "is_correct": False, "feedback": "NUNCA lo hagas."},
                ]
            },
            {
                "content": "Necesitas pagar en sitio de e-commerce desconocido. Como protegeras datos?",
                "hint": "El protocolo HTTPS y reputacion importan.",
                "alternatives": [
                    {"content": "Dar numero completo y CVV directo.", "is_correct": False, "feedback": "Muy riesgoso."},
                    {"content": "Usar PayPal/billetera digital o tarjeta virtual.", "is_correct": True, "feedback": "Correcto: agrega capa de proteccion."},
                    {"content": "Solo si hay logo de candado.", "is_correct": False, "feedback": "Bueno pero insuficiente."},
                    {"content": "Transferencia bancaria sin verificacion.", "is_correct": False, "feedback": "No es reversible en fraude."},
                ]
            }
        ]
    },
    {
        "segment": "senior",
        "difficulty": "media",
        "category": "Autenticacion",
        "title": "2FA y Autenticacion - Intermedio",
        "description": "Implementa autenticacion multifactor efectiva",
        "questions": [
            {
                "content": "Preguntas: '¿Mascota favorita?' '¿Primer auto?' Para recuperacion. Problema?",
                "hint": "La info personal es publica.",
                "alternatives": [
                    {"content": "Es seguro. Nadie sabe respuestas.", "is_correct": False, "feedback": "Personas cercanas podrian."},
                    {"content": "Si. Info personal se puede investigar. Elige no-conectadas a tu vida.", "is_correct": True, "feedback": "Correcto: evita hechos investigables."},
                    {"content": "Usar mismo codigo PIN.", "is_correct": False, "feedback": "Aun menos seguro."},
                    {"content": "Cambiar preguntas cada semana.", "is_correct": False, "feedback": "Inpractico."},
                ]
            },
            {
                "content": "App autenticadora genera codigos 30-seg. TV Show da codigo tuyo. Riesgo?",
                "hint": "Codigos temporales expiran pronto.",
                "alternatives": [
                    {"content": "Alto riesgo. Ya expiro. Sacame un codigo nuevo.", "is_correct": True, "feedback": "Correcto: el codigo viejo no funciona."},
                    {"content": "Bajo riesgo porque codigos rotan.", "is_correct": False, "feedback": "Pero alguien vio el codigo."},
                    {"content": "Cambiar toda la app.", "is_correct": False, "feedback": "Tomar mas precauciones pero no necesario."},
                    {"content": "Usar SMS 2FA en lugar de app.", "is_correct": False, "feedback": "SMS es menos seguro."},
                ]
            },
            {
                "content": "OneDrive te pide codigo 2FA. Alguien mas recibe el SMS. Que paso?",
                "hint": "SMS 2FA puede ser interceptado.",
                "alternatives": [
                    {"content": "Nada importante. Es solo un codigo.", "is_correct": False, "feedback": "Comprometio tu cuenta."},
                    {"content": "Alguien intenta acceder. Cambiar clave inmediatamente. Activar app-2FA.", "is_correct": True, "feedback": "Correcto: indica intento de acceso no autorizado."},
                    {"content": "Cambiar numero de telefono.", "is_correct": False, "feedback": "Bueno pero no suficiente."},
                    {"content": "Desactivar 2FA para simplificar.", "is_correct": False, "feedback": "Empeoras seguridad."},
                ]
            },
            {
                "content": "Banco ofrece huella dactilar como 2FA. Es seguro vs app autenticadora?",
                "hint": "Biomet­rico vs app tiene trade-offs.",
                "alternatives": [
                    {"content": "Si, biometria es mas segura.", "is_correct": False, "feedback": "Ambos tienen riesgos."},
                    {"content": "App autenticadora mas portable. Biometria menos portable. Elige segun contexto.", "is_correct": True, "feedback": "Correcto: considera acceso en devices multiples."},
                    {"content": "Biometria es peligrosa. Usa solo contrasena.", "is_correct": False, "feedback": "Biometria add seguridad."},
                    {"content": "Mismo nivel. Elige cualquiera.", "is_correct": False, "feedback": "Tienen diferencias importantes."},
                ]
            },
            {
                "content": "Tienes 2FA pero hacker cambia numero de cel recuperacion. Como paso?",
                "hint": "El account recovery es objetivo.",
                "alternatives": [
                    {"content": "Fallo de 2FA. Completamente comprometido.", "is_correct": False, "feedback": "No si actuaste rapido."},
                    {"content": "Contacta soporte urgente. 2FA salvo la mayoriac. Recupera control.", "is_correct": True, "feedback": "Correcto: auditoria y cambio de claves."},
                    {"content": "Cambiar numero telefonico nuevamente.", "is_correct": False, "feedback": "Insuficiente."},
                    {"content": "Desactivar 2FA.", "is_correct": False, "feedback": "Empeoras la situacion."},
                ]
            },
            {
                "content": "App autenticadora usa 'cloud backup' con 2FA. Pero cloud cuenta hacked?",
                "hint": "Backups en cloud son trade-off.",
                "alternatives": [
                    {"content": "2FA completamente comprometida.", "is_correct": False, "feedback": "Depende de situacion."},
                    {"content": "Si cloud hacked, 2FA en riesgo. Considera backup local o diversificacion.", "is_correct": True, "feedback": "Correcto: no confies en un vector."},
                    {"content": "Cloud nos es seguro. No usar autenticador.", "is_correct": False, "feedback": "Auticador sigue siendo bueno."},
                    {"content": "Activar mas 2FAs adicionales.", "is_correct": False, "feedback": "Buena idea pero no resuelve problema."},
                ]
            },
            {
                "content": "Google permite recuperacion con otros autenticadores como backup. Valor?",
                "hint": "Redundancia en seguridad es fuerte.",
                "alternatives": [
                    {"content": "No hay valor. Un 2FA es suficiente.", "is_correct": False, "feedback": "Redund­ancia es positiva."},
                    {"content": "Alto valor. Si pierdes un dispositivo, otro te recupera.", "is_correct": True, "feedback": "Correcto: redundancia = resilencia."},
                    {"content": "Solo util para personas paranoides.", "is_correct": False, "feedback": "Es buena practica general."},
                    {"content": "Significativamente menos seguro.", "is_correct": False, "feedback": "Mas bien lo contrario."},
                ]
            },
            {
                "content": "Alguien obtiene tus codigos de emergency 2FA y los usa. Que paso?",
                "hint": "Emergency codes son ultimo recurso.",
                "alternatives": [
                    {"content": "2FA fallo. Cuenta completamente hacked.", "is_correct": False, "feedback": "Importante pero no es fin del mundo."},
                    {"content": "Cuenta probablemente comprometida. Audita. Restablece. Genera nuevos codigos.", "is_correct": True, "feedback": "Correcto: actua rapido. Revoca todos tokens."},
                    {"content": "No importa. Emergency codes no hacen nada.", "is_correct": False, "feedback": "Los usan para recuperarse sin dispositivo."},
                    {"content": "Cambiar email y numero.", "is_correct": False, "feedback": "Pasos adicionales pero haz mas primero."},
                ]
            },
            {
                "content": "Navegador no recuerda tu dispositivo. Que implicacion para 2FA?",
                "hint": "Menos riesgo de loss-of-device.",
                "alternatives": [
                    {"content": "Pedira codigo cada login. Molesto pero mas seguro.", "is_correct": True, "feedback": "Correcto: cada login = mayor friccion = mas seguridad."},
                    {"content": "Es vulnerabilidad. Menos seguro.", "is_correct": False, "feedback": "Es lo opuesto."},
                    {"content": "Depende del navegador.", "is_correct": False, "feedback": "Es beneficio general."},
                    {"content": "Desactiva 2FA en ese dispositivo.", "is_correct": False, "feedback": "Empeora seguridad."},
                ]
            },
            {
                "content": "2FA basada SMS se puede interceptar con SIM swap. Como protegerse?",
                "hint": "Usar app autenticadora es un escudo.",
                "alternatives": [
                    {"content": "No hay proteccion. SMS 2FA es debil.", "is_correct": False, "feedback": "Hay protecciones."},
                    {"content": "Usar app autenticadora ademas de SMS. Contactar proveedor de celular.", "is_correct": True, "feedback": "Correcto: diversifica 2FA. Protege numero."},
                    {"content": "Cambiar de proveedor de celular.", "is_correct": False, "feedback": "No Necessarily resuelve."},
                    {"content": "Desactivar SMS 2FA completamente.", "is_correct": False, "feedback": "Bueno pero no es la unica solucion."},
                ]
            }
        ]
    },
    {
        "segment": "senior",
        "difficulty": "alta",
        "category": "Estafas",
        "title": "Fraude Avanzado - Alto",
        "description": "Identifica y evita estafas complejas",
        "questions": [
            {
                "content": "Startup promete 50% de retorno anual. Inversioncriptobajo. Que es?",
                "hint": "Retornos rapidos son clasico de Ponzi.",
                "alternatives": [
                    {"content": "Oportunidad real de riqueza.", "is_correct": False, "feedback": "Es esquema Ponzi clasico."},
                    {"content": "Alta probabilidad de estafa. Invierte solo lo que pierdes.", "is_correct": True, "feedback": "Correcto: si suena como milagro, lo es."},
                    {"content": "Seguro si es regulado localmente.", "is_correct": False, "feedback": "Las regulaciones varrian."},
                    {"content": "Comparar con S&P 500 performance.", "is_correct": False, "feedback": "S&P da 10%, no 50%."},
                ]
            },
            {
                "content": "Influencer te DM privado sobre oportunidad exclusive invertir. Red flags?",
                "hint": "Privados de inflenciador es raro.",
                "alternatives": [
                    {"content": "Es exclusive para ti. Apurate.", "is_correct": False, "feedback": "Red flag clasica."},
                    {"content": "Probable inauthenticidad. Influencers no DMean a randos. Sospecha = scam.", "is_correct": True, "feedback": "Correcto: 99% es cuenta falsa o hacked."},
                    {"content": "Si tiene muchos followers es legit.", "is_correct": False, "feedback": "Followers pueden ser bots."},
                    {"content": "Verificar perfil y seguir.", "is_correct": False, "feedback": "Podria ser clone perfecto."},
                ]
            },
            {
                "content": "Correo de 'herencia' de tio muerto lejano. Piden datisosbancarios. Situacion?",
                "hint": "Herencias no funcionan asi.",
                "alternatives": [
                    {"content": "Reclamo la herencia immediate.", "is_correct": False, "feedback": "Es avance-fee scam."},
                    {"content": "100% estafa. Nunca herencias por email. Bloquea.", "is_correct": True, "feedback": "Correcto: herencias van por abogado oficial."},
                    {"content": "Hablar con familcia lejana primero.", "is_correct": False, "feedback": "Es scam directo."},
                    {"content": "Pedir mas info del abogado por email.", "is_correct": False, "feedback": "El abogado es fake."},
                ]
            },
            {
                "content": "Pagina de 'impuestos' con diseno official pide TIN. Como verificas?",
                "hint": "Government sites tienen patrones.",
                "alternatives": [
                    {"content": "Si logo se ve official, confiar.", "is_correct": False, "feedback": "Logos pueden copiar."},
                    {"content": "Ir directamente a sitio official del gobierno (com**/)", "is_correct": True, "feedback": "Correcto: no hagas clic de enlace externo."},
                    {"content": "Llamar numero en la pagina.", "is_correct": False, "feedback": "El numero podria ser fake."},
                    {"content": "Enviar TIN a email del sitio.", "is_correct": False, "feedback": "Es phishing."},
                ]
            },
            {
                "content": "App de citas genera profile con fotos profesionales y stories ricas. Tipo?",
                "hint": "Romance scams usan fotos robadas.",
                "alternatives": [
                    {"content": "Es persona legit buscando.relacion.", "is_correct": False, "feedback": "Probablemente catfish."},
                    {"content": "Very sospechoso. Fotos profesionales + historias ricas = profile falso. Evita.", "is_correct": True, "feedback": "Correcto: reverse image search para verificar."},
                    {"content": "Si responde rapido es legit.", "is_correct": False, "feedback": "Bots responden rapido."},
                    {"content": "Pedir WhatsApp fuera de app.", "is_correct": False, "feedback": "Tactica comun de scammer."},
                ]
            },
            {
                "content": "Persona de citas te pide 'dinero para emergencia'. Como procedes?",
                "hint": "Es el giro final del romance scam.",
                "alternatives": [
                    {"content": "Enviar dinero si la amas.", "is_correct": False, "feedback": "Es romance scam setup."},
                    {"content": "NUNCA envies dinero a conocidos online. Corta contacto. Es scam.", "is_correct": True, "feedback": "Correcto: es esquema classico."},
                    {"content": "Pedir que pida a familia.", "is_correct": False, "feedback": "Seguira pidiendo a ti."},
                    {"content": "Prestar poco como 'prueba de amor'.", "is_correct": False, "feedback": "Es inicio del sangrado."},
                ]
            },
            {
                "content": "Job posting promete trabajo remote con salario alto pero pide 'signing fee'. Red flags?",
                "hint": "Job scams piden dinero upfront.",
                "alternatives": [
                    {"content": "Oportunidad rara. Pagar fee para trabajar.", "is_correct": False, "feedback": "Es estafa de empleos."},
                    {"content": "Gigantesca red flag. Ningun job real pide dinero. Rechaza.", "is_correct": True, "feedback": "Correcto: empleadores PAGAN, no cobran."},
                    {"content": "Tarifas pequenas son normales.", "is_correct": False, "feedback": "NO, nunca son normales."},
                    {"content": "Negocia la tarifa.", "is_correct": False, "feedback": "Es scam, no negociable."},
                ]
            },
            {
                "content": "Broker promete 'garantizeado stop loss' si inviertes EUR50k. Signal?",
                "hint": "No hay perdida garantizada cero.",
                "alternatives": [
                    {"content": "Es broker confiable ofreciendo certeza.", "is_correct": False, "feedback": "No existe certeza en mercados."},
                    {"content": "Breach basico de finanza. Stop loss NO son garantia. Es FRAUDULENT broker.", "is_correct": True, "feedback": "Correcto: promesas de ganancia = scam."},
                    {"content": "Leer terminos y condiciones.", "is_correct": False, "feedback": "Los terminos admitiran fine print."},
                    {"content": "Transferir fondo pequeño para probar.", "is_correct": False, "feedback": "Perdera dinero y mas pediran."},
                ]
            },
            {
                "content": "Seller en Marketplace pide transferencia bancaria antes de enviar. Nivel riesgo?",
                "hint": "Transferencias bancarias son irreversibles..",
                "alternatives": [
                    {"content": "Bajo. Los seller piden proteccion tambien.", "is_correct": False, "feedback": "Alto riesgo para comprador."},
                    {"content": "ALTO. Transf. Bancaria es irreversible si es scam. Usa escrow o plataforma.", "is_correct": True, "feedback": "Correcto: manejo de disputa=importante."},
                    {"content": "Medium. Depende de seller reputation.", "is_correct": False, "feedback": "Reputacion puede fakearse."},
                    {"content": "Enviar dinero en etapas pequenas.", "is_correct": False, "feedback": "Aun irreversible."},
                ]
            },
            {
                "content": "NFT promete 'blockchain profit sharing'. Creator unknown, hype alto. Que es?",
                "hint": "Muchos NFTs son esquemas de bombeo.",
                "alternatives": [
                    {"content": "Oportunidad legitima de riqueza.", "is_correct": False, "feedback": "Es pump-and-dump."},
                    {"content": "Probable esquema Ponzi NFT. Creator anon + hype + profit promesa = dump inminente.", "is_correct": True, "feedback": "Correcto: evita cuando creator es desconocido."},
                    {"content": "Invertir muy poco como diversificacion.", "is_correct": False, "feedback": "Incluso poco puede perderse."},
                    {"content": "Entrar temprano es ventaja.", "is_correct": False, "feedback": "Eres probablemente tarde."},
                ]
            }
        ]
    }
]


class Command(BaseCommand):
    help = "Popula todas las tablas del quiz con escenarios pedagogicos"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Iniciando poblacion de tablas quiz..."))
        with transaction.atomic():
            self._create_audience_segments()
            self._create_risk_categories()
            self._create_quizzes_and_content()
        self.stdout.write(self.style.SUCCESS("\n✓ Quiz poblado correctamente"))

    def _create_audience_segments(self):
        self.stdout.write("Creando Audience Segments...")
        for segment in SEGMENTS.values():
            obj, created = AudienceSegment.objects.update_or_create(
                name=segment["name"],
                defaults={
                    "description": segment["description"],
                    "min_age": segment["min_age"],
                    "max_age": segment["max_age"],
                    "display_order": segment["display_order"],
                    "is_active": True,
                },
            )
            self.stdout.write(f"  {'✓' if created else '•'} {obj}")
        self.stdout.write(self.style.SUCCESS(f"  Total: {AudienceSegment.objects.count()} segmentos\n"))

    def _create_risk_categories(self):
        self.stdout.write("Creando Risk Categories...")
        for cat in CATEGORIES:
            obj, created = RiskCategory.objects.update_or_create(
                name=cat["name"],
                defaults={
                    "description": cat.get("description", ""),
                    "icon": cat.get("icon"),
                    "display_order": cat.get("display_order", 0),
                    "is_active": True,
                },
            )
            self.stdout.write(f"  {'✓' if created else '•'} {obj}")
        self.stdout.write(self.style.SUCCESS(f"  Total: {RiskCategory.objects.count()} categorias\n"))

    def _create_quizzes_and_content(self):
        self.stdout.write("Creando Quizzes y contenido...")

        for quiz_data in QUIZZES:
            segment_name = SEGMENTS[quiz_data["segment"]]["name"]
            segment = AudienceSegment.objects.get(name=segment_name)
            category = RiskCategory.objects.get(name=quiz_data["category"])

            # Mapear dificultad (baja, media, alta) a difficulty_level (1, 2, 3)
            difficulty_map = {"baja": 1, "media": 2, "alta": 3}
            difficulty = difficulty_map[quiz_data["difficulty"]]
            
            # Contar questions por dificultad (baja=6, media=10, alta=12)
            question_count = len(quiz_data["questions"])
            base_points = get_points_reward(difficulty) * question_count
            time_limit_seconds = question_count * 60

            quiz, created = Quiz.objects.update_or_create(
                title=quiz_data["title"],
                segment=segment,
                category=category,
                defaults={
                    "description": quiz_data["description"],
                    "difficulty_level": difficulty,
                    "base_points": base_points,
                    "time_limit_seconds": time_limit_seconds,
                    "is_active": True,
                },
            )

            self.stdout.write(f"  {'✓' if created else '•'} {quiz.title} ({segment.name}) - {question_count} preguntas")

            # Eliminar preguntas anteriores
            quiz.questions.all().delete()

            # Crear preguntas para este quiz
            for q_idx, q_data in enumerate(quiz_data["questions"], start=1):
                question, _ = QuizQuestion.objects.update_or_create(
                    quiz=quiz,
                    display_order=q_idx,
                    defaults={
                        "content": q_data["content"],
                        "explanation": f"Revisa el feedback detallado en cada alternativa. Pista: {q_data['hint']}",
                        "points": get_points_reward(difficulty),
                        "image_url": None,
                    },
                )

                # Eliminar alternativas y pistas anteriores
                question.alternatives.all().delete()
                question.hints.all().delete()

                # Crear alternativas
                for alt_idx, alt in enumerate(q_data["alternatives"], start=1):
                    QuizAlternative.objects.create(
                        question=question,
                        display_order=alt_idx,
                        content=alt["content"],
                        is_correct=alt["is_correct"],
                        feedback=alt["feedback"],
                    )

                # Crear hint
                QuizHint.objects.create(
                    question=question,
                    display_order=1,
                    content=q_data["hint"],
                    cost_points=5,
                )

        self.stdout.write(self.style.SUCCESS("  Contenido de quizzes actualizado"))
