"""
Examen de Nivel — Logoped-IA
Backend Flask con SQLite
Banco: 55 preguntas · Selección aleatoria: 25 por sesión (≥4 por bloque)
"""

from flask import Flask, jsonify, request, send_from_directory, Response
import json, os, random, io
from datetime import datetime
from functools import wraps
from db import get_db, init_db

app = Flask(__name__, static_folder="static")
APP_TITLE = "Examen de Aprendizaje — Logoped-IA"
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "").strip()
EXAM_MODE = os.getenv("EXAM_MODE", "completo").strip().lower()

# ─────────────────────────────────────────────
# BANCO DE PREGUNTAS
# ─────────────────────────────────────────────

BANCO = [

    # ══════════════════════════════════════════
    # BLOQUE A — CONOCIMIENTO BÁSICO IA
    # ══════════════════════════════════════════
    {
        "id": "A01", "bloque": "Conocimiento básico IA", "dificultad": "basico",
        "pregunta": "¿Qué significa la sigla LLM en inteligencia artificial?",
        "opciones": ["Large Language Model", "Limited Learning Machine", "Logical Language Module", "Linear Learning Method"],
        "correcta": 0,
        "explicacion": "LLM (Large Language Model) es el tipo de modelo de IA detrás de ChatGPT, Claude o Gemini. Están entrenados sobre enormes volúmenes de texto."
    },
    {
        "id": "A02", "bloque": "Conocimiento básico IA", "dificultad": "basico",
        "pregunta": "¿Cuál de estas herramientas es un modelo de lenguaje desarrollado por Anthropic?",
        "opciones": ["ChatGPT", "Gemini", "Claude", "Manus"],
        "correcta": 2,
        "explicacion": "Claude es el modelo de Anthropic. ChatGPT es de OpenAI, Gemini es de Google y Manus es una herramienta de automatización no-code."
    },
    {
        "id": "A03", "bloque": "Conocimiento básico IA", "dificultad": "basico",
        "pregunta": "¿Qué es un 'prompt' en IA generativa?",
        "opciones": [
            "Un archivo de audio para análisis vocal",
            "La instrucción o texto que le damos a la IA para obtener una respuesta",
            "Un programa de inteligencia artificial",
            "Un formato de exportación de informes"
        ],
        "correcta": 1,
        "explicacion": "El prompt es la entrada que le das al modelo. Su calidad determina directamente la calidad del resultado."
    },
    {
        "id": "A04", "bloque": "Conocimiento básico IA", "dificultad": "basico",
        "pregunta": "¿Qué es la 'alucinación' en un modelo de lenguaje?",
        "opciones": [
            "Un error de conexión del modelo",
            "Cuando el modelo genera información falsa o inventada con total seguridad",
            "Un modo de respuesta creativa activado por el usuario",
            "Un fallo de pronunciación en herramientas de voz"
        ],
        "correcta": 1,
        "explicacion": "Las alucinaciones son un riesgo crítico en contexto clínico: el modelo puede inventar referencias, diagnósticos o datos con plena confianza. Siempre hay que verificar."
    },
    {
        "id": "A05", "bloque": "Conocimiento básico IA", "dificultad": "basico",
        "pregunta": "¿Qué es el 'contexto' (context window) en un LLM?",
        "opciones": [
            "El idioma en el que está entrenado el modelo",
            "La cantidad máxima de texto que el modelo puede procesar en una conversación",
            "La velocidad de respuesta del modelo",
            "El número de idiomas que soporta el modelo"
        ],
        "correcta": 1,
        "explicacion": "La ventana de contexto define cuánto texto puede 'recordar' el modelo en una misma conversación. Modelos como Claude 3.5 tienen contextos de ~200.000 tokens, lo que equivale a libros enteros."
    },
    {
        "id": "A06", "bloque": "Conocimiento básico IA", "dificultad": "medio",
        "pregunta": "¿Qué es un modelo 'multimodal' de IA?",
        "opciones": [
            "Un modelo que solo procesa texto",
            "Un modelo que puede trabajar con texto, imágenes, audio y/o vídeo",
            "Un modelo con múltiples idiomas disponibles",
            "Un modelo que usa varias IAs simultáneamente"
        ],
        "correcta": 1,
        "explicacion": "Multimodal significa que el modelo entiende y genera distintos tipos de información: texto, imágenes, audio... GPT-4o y Gemini son ejemplos multimodales especialmente relevantes en logopedia."
    },
    {
        "id": "A07", "bloque": "Conocimiento básico IA", "dificultad": "medio",
        "pregunta": "¿Qué son los 'tokens' en el contexto de los LLMs?",
        "opciones": [
            "Contraseñas de acceso a los modelos de IA",
            "Unidades de texto (palabras o fragmentos de palabras) que el modelo procesa",
            "Los créditos de pago para usar la API",
            "Los archivos de configuración del modelo"
        ],
        "correcta": 1,
        "explicacion": "Los tokens son las unidades básicas de procesamiento. En español, una palabra suele equivaler a 1-2 tokens. Entender los tokens ayuda a gestionar el coste y la longitud de los prompts."
    },
    {
        "id": "A08", "bloque": "Conocimiento básico IA", "dificultad": "medio",
        "pregunta": "¿Qué es RAG (Retrieval Augmented Generation)?",
        "opciones": [
            "Un tipo de alucinación común en modelos de lenguaje",
            "Una técnica que combina búsqueda en documentos propios con generación de texto",
            "Un modelo de IA especializado en reconocimiento de voz",
            "Un formato de exportación de resultados clínicos"
        ],
        "correcta": 1,
        "explicacion": "RAG permite que el modelo consulte documentos propios (protocolos, artículos, historiales) antes de responder. NotebookLM usa este principio: la IA responde basándose en TUS documentos."
    },
    {
        "id": "A09", "bloque": "Conocimiento básico IA", "dificultad": "avanzado",
        "pregunta": "¿Qué es el 'fine-tuning' de un modelo de IA?",
        "opciones": [
            "Mejorar la velocidad de un modelo existente",
            "Ajustar y reentrenar un modelo base con datos específicos para un dominio concreto",
            "Cambiar el idioma de respuesta del modelo",
            "Actualizar el modelo a una versión más nueva"
        ],
        "correcta": 1,
        "explicacion": "El fine-tuning adapta un modelo genérico a un dominio específico (p.ej. logopedia) entrenándolo con ejemplos propios. Produce modelos más precisos pero requiere datos y coste computacional elevado."
    },
    {
        "id": "A10", "bloque": "Conocimiento básico IA", "dificultad": "avanzado",
        "pregunta": "¿Qué diferencia existe entre IA generativa e IA discriminativa?",
        "opciones": [
            "No hay diferencia, son lo mismo",
            "La generativa crea contenido nuevo; la discriminativa clasifica o predice a partir de datos existentes",
            "La generativa es más antigua que la discriminativa",
            "La discriminativa solo funciona con texto, la generativa con imágenes"
        ],
        "correcta": 1,
        "explicacion": "Los LLMs (ChatGPT, Claude) son generativos: crean texto. Los modelos discriminativos (diagnóstico por imagen, clasificación de patología) clasifican datos. En logopedia clínica, ambos tipos tienen aplicaciones distintas."
    },

    # ══════════════════════════════════════════
    # BLOQUE B — HERRAMIENTAS DE IA
    # ══════════════════════════════════════════
    {
        "id": "B01", "bloque": "Herramientas de IA", "dificultad": "basico",
        "pregunta": "¿Para qué sirve principalmente NotebookLM (Google)?",
        "opciones": [
            "Generar imágenes para materiales logopédicos",
            "Crear avatares parlantes",
            "Trabajar con documentos propios como fuentes y hacerles preguntas",
            "Transcribir audio de sesiones clínicas"
        ],
        "correcta": 2,
        "explicacion": "NotebookLM permite subir tus propios PDFs, artículos o apuntes y usarlos como base de conocimiento: hacer preguntas, crear resúmenes o generar podcasts de audio automáticamente."
    },
    {
        "id": "B02", "bloque": "Herramientas de IA", "dificultad": "basico",
        "pregunta": "¿Qué herramienta permite crear páginas web completas y presentaciones sin escribir código?",
        "opciones": ["Claude", "Manus", "Wispr Flow", "HeyGen"],
        "correcta": 1,
        "explicacion": "Manus es un agente no-code que puede crear webs, hacer búsquedas, generar presentaciones y rellenar formularios de forma autónoma."
    },
    {
        "id": "B03", "bloque": "Herramientas de IA", "dificultad": "basico",
        "pregunta": "¿Para qué sirve HeyGen?",
        "opciones": [
            "Generar pictogramas para SAAC",
            "Crear avatares parlantes con voz y movimiento labial sincronizados",
            "Transcribir conversaciones clínicas",
            "Analizar acústicamente la voz del paciente"
        ],
        "correcta": 1,
        "explicacion": "HeyGen genera vídeos con avatares realistas que sincronizan voz y movimientos labiales. Útil para crear materiales educativos o formaciones sin grabarse personalmente."
    },
    {
        "id": "B04", "bloque": "Herramientas de IA", "dificultad": "basico",
        "pregunta": "¿Qué hace Wispr Flow?",
        "opciones": [
            "Genera imágenes con texto integrado",
            "Crea podcasts automáticamente",
            "Permite dictar por voz en cualquier aplicación del sistema",
            "Analiza el perfil fonológico de un paciente"
        ],
        "correcta": 2,
        "explicacion": "Wispr Flow es dictado por voz universal: funciona en cualquier app (correo, documentos, chats). Ideal para logopedas que redactan mucho y quieren agilizar sin perder calidad."
    },
    {
        "id": "B05", "bloque": "Herramientas de IA", "dificultad": "medio",
        "pregunta": "¿Qué es un 'GPT Project' en ChatGPT?",
        "opciones": [
            "Un modelo de IA más potente que el estándar",
            "Un espacio personalizado con instrucciones, archivos y contexto propio persistente",
            "Una app móvil de pago de ChatGPT",
            "Un plugin para integrar ChatGPT en el navegador"
        ],
        "correcta": 1,
        "explicacion": "Los GPT Projects permiten configurar instrucciones personalizadas, subir archivos de referencia y mantener el contexto entre conversaciones. Muy útil para proyectos clínicos recurrentes como dislexia o voz."
    },
    {
        "id": "B06", "bloque": "Herramientas de IA", "dificultad": "medio",
        "pregunta": "¿Cuál de estas herramientas de Google genera imágenes con texto legible integrado para materiales logopédicos?",
        "opciones": [
            "Google Slides AI",
            "Google Workspace Gemini",
            "Gemini con generación de imágenes (Imagen 3)",
            "Google Forms IA"
        ],
        "correcta": 2,
        "explicacion": "Gemini Imagen 3 es el generador de imágenes de Google que resuelve el histórico problema del texto en imágenes generadas. Permite crear materiales logopédicos con texto legible integrado."
    },
    {
        "id": "B07", "bloque": "Herramientas de IA", "dificultad": "medio",
        "pregunta": "¿Para qué se usa principalmente ElevenLabs?",
        "opciones": [
            "Generar imágenes realistas",
            "Crear voces sintéticas realistas y clonar voces",
            "Hacer análisis acústico de patología vocal",
            "Transcribir automáticamente sesiones de terapia"
        ],
        "correcta": 1,
        "explicacion": "ElevenLabs genera voces sintéticas de alta calidad y permite clonar voces reales. En logopedia puede usarse para crear materiales de audición, pares mínimos o demos de pronunciación."
    },
    {
        "id": "B08", "bloque": "Herramientas de IA", "dificultad": "medio",
        "pregunta": "¿Qué es Perplexity y en qué se diferencia de ChatGPT?",
        "opciones": [
            "Es un editor de vídeo con IA",
            "Es un buscador con IA que cita fuentes verificables en tiempo real",
            "Es un generador de imágenes de OpenAI",
            "Es una app de transcripción de audio clínico"
        ],
        "correcta": 1,
        "explicacion": "Perplexity combina búsqueda web en tiempo real con generación de respuestas citadas. Ideal para buscar evidencia científica reciente en logopedia con fuentes verificables."
    },
    {
        "id": "B09", "bloque": "Herramientas de IA", "dificultad": "medio",
        "pregunta": "¿Qué hace Descript?",
        "opciones": [
            "Genera imágenes desde texto",
            "Permite editar vídeo y audio editando el texto de la transcripción",
            "Crea chatbots para atención al paciente",
            "Analiza fonemas en grabaciones de logopedia"
        ],
        "correcta": 1,
        "explicacion": "Descript transcribe vídeo/audio y permite editarlo modificando el texto transcrito. Cortar palabras del texto elimina esos fragmentos del vídeo. Muy útil para crear contenido formativo."
    },
    {
        "id": "B10", "bloque": "Herramientas de IA", "dificultad": "avanzado",
        "pregunta": "¿Qué es Cursor y para qué puede usarlo un logopeda con interés técnico?",
        "opciones": [
            "Un generador de pictogramas",
            "Un editor de código con IA integrada para crear herramientas y prototipos",
            "Una plataforma de videoconferencia con subtítulos automáticos",
            "Un sistema de reconocimiento de voz clínico"
        ],
        "correcta": 1,
        "explicacion": "Cursor es un editor de código donde la IA ayuda a escribir, depurar y crear software. Permite a profesionales con conocimientos básicos construir herramientas propias como generadores de materiales o chatbots."
    },
    {
        "id": "B11", "bloque": "Herramientas de IA", "dificultad": "avanzado",
        "pregunta": "¿Qué es Codex (OpenAI) y cómo puede beneficiar al logopeda?",
        "opciones": [
            "Un generador de imágenes médicas",
            "Un modelo especializado en código para crear herramientas o scripts personalizados",
            "Una plataforma de cursos de IA para sanitarios",
            "Un sistema de reconocimiento de voz clínico"
        ],
        "correcta": 1,
        "explicacion": "Codex es un modelo de OpenAI especializado en código. Permite crear herramientas personalizadas, automatizar tareas o construir prototipos incluso con conocimientos técnicos limitados."
    },
    {
        "id": "B12", "bloque": "Herramientas de IA", "dificultad": "avanzado",
        "pregunta": "¿Qué tipo de herramienta es Google AI Studio y quién debería usarla?",
        "opciones": [
            "Una plataforma de cursos online de Google sobre IA",
            "Un entorno de desarrollo para experimentar con los modelos Gemini vía API",
            "Una herramienta de creación de presentaciones con IA",
            "Una suite de análisis de datos para investigación"
        ],
        "correcta": 1,
        "explicacion": "Google AI Studio es el playground oficial de los modelos Gemini. Permite experimentar con prompts, ajustar parámetros y acceder a la API. Orientado a profesionales con perfil técnico que quieran construir herramientas."
    },

    # ══════════════════════════════════════════
    # BLOQUE C — INGENIERÍA DE PROMPTS
    # ══════════════════════════════════════════
    {
        "id": "C01", "bloque": "Ingeniería de prompts", "dificultad": "basico",
        "pregunta": "¿Cuál de estos elementos mejora más la calidad de un prompt clínico?",
        "opciones": [
            "Escribirlo siempre en inglés",
            "Usar el máximo número de palabras posible",
            "Dar contexto, asignar un rol, definir la tarea y especificar el formato de salida",
            "Hacer preguntas genéricas sin especificar el perfil del paciente"
        ],
        "correcta": 2,
        "explicacion": "Un buen prompt clínico tiene cuatro elementos: rol ('actúa como logopeda especialista en...'), contexto del paciente, tarea concreta y formato esperado. Esta estructura multiplica la utilidad del resultado."
    },
    {
        "id": "C02", "bloque": "Ingeniería de prompts", "dificultad": "basico",
        "pregunta": "Un prompt que empieza con 'Actúa como logopeda especialista en dislexia...' usa la técnica de:",
        "opciones": ["Chain of thought", "Few-shot prompting", "Asignación de rol (role prompting)", "Prompt negativo"],
        "correcta": 2,
        "explicacion": "La asignación de rol orienta al modelo a responder desde una perspectiva experta específica, mejorando la pertinencia clínica y el vocabulario técnico del resultado."
    },
    {
        "id": "C03", "bloque": "Ingeniería de prompts", "dificultad": "basico",
        "pregunta": "¿Qué información clave debe incluir un prompt para generar materiales de discriminación auditiva?",
        "opciones": [
            "Solo el nivel educativo del paciente",
            "El nombre completo del paciente",
            "El par fonológico objetivo, el nivel del paciente y el tipo de actividad",
            "El modelo de IA que se va a usar"
        ],
        "correcta": 2,
        "explicacion": "Para discriminación auditiva, el prompt necesita: los fonemas o pares mínimos objetivo (p/b, d/t...), el nivel del paciente y el tipo de actividad (identificación, producción, discriminación)."
    },
    {
        "id": "C04", "bloque": "Ingeniería de prompts", "dificultad": "medio",
        "pregunta": "¿Qué significa hacer 'iteraciones' con un prompt?",
        "opciones": [
            "Copiar el mismo prompt en varios modelos a la vez",
            "Refinar y ajustar el prompt progresivamente hasta obtener el resultado deseado",
            "Traducir el prompt para mejorar los resultados",
            "Guardar los prompts en una base de datos"
        ],
        "correcta": 1,
        "explicacion": "Iterar significa ajustar el prompt en varias rondas: añades contexto, corriges el tono, especificas el formato... hasta que el resultado se ajusta a lo que necesitas clínicamente."
    },
    {
        "id": "C05", "bloque": "Ingeniería de prompts", "dificultad": "medio",
        "pregunta": "¿Qué es el 'few-shot prompting'?",
        "opciones": [
            "Usar prompts muy cortos para ahorrar tokens",
            "Incluir ejemplos del resultado esperado dentro del propio prompt",
            "Hacer múltiples preguntas seguidas al modelo",
            "Limitar el número de respuestas que puede generar el modelo"
        ],
        "correcta": 1,
        "explicacion": "Few-shot prompting consiste en incluir 2-3 ejemplos del output deseado dentro del prompt. Es muy eficaz para conseguir materiales con un formato o estructura muy específica (fichas, actividades, informes)."
    },
    {
        "id": "C06", "bloque": "Ingeniería de prompts", "dificultad": "medio",
        "pregunta": "¿Qué es el 'chain of thought' (cadena de pensamiento) en prompting?",
        "opciones": [
            "Usar varios modelos encadenados para obtener la respuesta",
            "Pedir al modelo que razone paso a paso antes de dar la respuesta final",
            "Un prompt muy largo que incluye todo el contexto posible",
            "Conectar varias conversaciones del mismo modelo"
        ],
        "correcta": 1,
        "explicacion": "Chain of thought pide al modelo que 'piense en voz alta' paso a paso antes de responder. Mejora notablemente la calidad en tareas complejas como planificaciones terapéuticas o análisis de casos."
    },
    {
        "id": "C07", "bloque": "Ingeniería de prompts", "dificultad": "medio",
        "pregunta": "¿Qué es el 'system prompt' en un modelo de IA?",
        "opciones": [
            "El mensaje de error que da el modelo cuando falla",
            "Instrucciones previas que configuran el comportamiento del modelo antes de la conversación",
            "El resumen automático que hace el modelo de la conversación",
            "El prompt predeterminado de la interfaz del modelo"
        ],
        "correcta": 1,
        "explicacion": "El system prompt configura el rol, tono, restricciones y comportamiento del modelo antes de empezar. Es lo que define cómo actúa un GPT personalizado o un chatbot clínico."
    },
    {
        "id": "C08", "bloque": "Ingeniería de prompts", "dificultad": "avanzado",
        "pregunta": "¿Cuándo conviene usar una 'temperatura' alta en un modelo de IA?",
        "opciones": [
            "Para obtener respuestas técnicas precisas y reproducibles",
            "Para tareas creativas donde se busca variedad y originalidad",
            "Para traducciones o cálculos exactos",
            "Para reducir las alucinaciones del modelo"
        ],
        "correcta": 1,
        "explicacion": "La temperatura controla la 'creatividad' del modelo. Alta temperatura (0.8-1.0) → respuestas más variadas y creativas. Baja temperatura (0.1-0.3) → respuestas más precisas y repetibles. Para informes clínicos: baja. Para generar ideas de materiales: alta."
    },
    {
        "id": "C09", "bloque": "Ingeniería de prompts", "dificultad": "avanzado",
        "pregunta": "En el workflow de Claude para logopedia del canal, ¿cuál es el orden correcto?",
        "opciones": [
            "Material → Prompt → Actividad interactiva",
            "Prompt clínico → IA genera material → Logopeda revisa → Actividad interactiva",
            "IA genera → Logopeda publica directamente",
            "Actividad → Material → Prompt de refinado"
        ],
        "correcta": 1,
        "explicacion": "El workflow del canal siempre incluye la revisión profesional entre la generación del material y su uso clínico. La IA genera, el logopeda valida. Nunca se salta ese paso."
    },
    {
        "id": "C10", "bloque": "Ingeniería de prompts", "dificultad": "avanzado",
        "pregunta": "¿Cuál es la principal ventaja de tener una biblioteca personal de prompts clínicos validados?",
        "opciones": [
            "Reducir el coste de las suscripciones a modelos de IA",
            "Garantizar resultados consistentes y ahorra tiempo en la creación de materiales",
            "Evitar que la IA genere alucinaciones",
            "Permite usar modelos de IA sin conexión a internet"
        ],
        "correcta": 1,
        "explicacion": "Una biblioteca de prompts validados es uno de los activos más valiosos para un logopeda que usa IA: produce materiales consistentes, reproduce resultados que ya funcionaron y agiliza el trabajo repetitivo."
    },

    # ══════════════════════════════════════════
    # BLOQUE D — APLICACIONES CLÍNICAS
    # ══════════════════════════════════════════
    {
        "id": "D01", "bloque": "Aplicaciones clínicas", "dificultad": "basico",
        "pregunta": "¿Cuál de estos es un par mínimo fonológico?",
        "opciones": ["casa / mesa", "pato / bato", "gato / perro", "silla / mesa"],
        "correcta": 1,
        "explicacion": "Un par mínimo son dos palabras que solo se diferencian en un fonema (pato/bato, pelo/belo). Se usan en discriminación auditiva y en terapia fonológica para contrastar rasgos distintivos."
    },
    {
        "id": "D02", "bloque": "Aplicaciones clínicas", "dificultad": "basico",
        "pregunta": "¿Para qué área logopédica resulta más inmediatamente útil usar IA generativa?",
        "opciones": [
            "Diagnóstico diferencial de afasias",
            "Creación de materiales terapéuticos personalizados",
            "Evaluación estandarizada de lenguaje",
            "Análisis acústico de voz"
        ],
        "correcta": 1,
        "explicacion": "La creación de materiales personalizados (fichas, actividades, textos adaptados) es el uso más inmediato y seguro de la IA en logopedia. No requiere validación clínica del diagnóstico."
    },
    {
        "id": "D03", "bloque": "Aplicaciones clínicas", "dificultad": "medio",
        "pregunta": "¿En qué área logopédica se centra el 'Visualizador Narrativo Simbólico' del canal?",
        "opciones": [
            "Dislexia y lectoescritura infantil",
            "Daño cerebral adquirido y demencias",
            "Deglución atípica",
            "Lenguaje infantil temprano"
        ],
        "correcta": 1,
        "explicacion": "El Visualizador Narrativo Simbólico genera imágenes simbólicas a partir de relatos autobiográficos, para personas con daño adquirido o demencias. Ayuda a trabajar la narrativa personal y la identidad."
    },
    {
        "id": "D04", "bloque": "Aplicaciones clínicas", "dificultad": "medio",
        "pregunta": "¿Para qué sirve CliniCost?",
        "opciones": [
            "Software de historia clínica digital",
            "Calculadora del coste real por sesión/paciente con y sin IA",
            "Generador automático de informes logopédicos",
            "App de gestión de agenda"
        ],
        "correcta": 1,
        "explicacion": "CliniCost calcula el coste real por sesión y paciente considerando tiempo de preparación, materiales y el ahorro (o no) de la IA. Muy útil para tomar decisiones informadas sobre herramientas."
    },
    {
        "id": "D05", "bloque": "Aplicaciones clínicas", "dificultad": "medio",
        "pregunta": "¿Para qué sirve el chatbot de anamnesis desarrollado en el canal?",
        "opciones": [
            "Hacer diagnóstico automático de trastornos del lenguaje",
            "Recoger información inicial del paciente antes de la primera consulta",
            "Transcribir y analizar las sesiones de logopedia",
            "Gestionar la facturación del gabinete"
        ],
        "correcta": 1,
        "explicacion": "El chatbot de anamnesis hace preguntas estructuradas al paciente (o familia) antes de la primera sesión: motivo de consulta, historial y preocupaciones. Ahorra tiempo al logopeda sin reemplazar la entrevista clínica."
    },
    {
        "id": "D06", "bloque": "Aplicaciones clínicas", "dificultad": "medio",
        "pregunta": "¿Cómo puede ayudar la IA en el trabajo con dislexia específicamente?",
        "opciones": [
            "Diagnosticando la dislexia automáticamente desde una muestra de escritura",
            "Generando materiales de lectoescritura adaptados al nivel y las dificultades del alumno",
            "Evaluando la velocidad lectora con mayor precisión que los tests estándar",
            "Corrigiendo automáticamente los errores de lectura del alumno en tiempo real"
        ],
        "correcta": 1,
        "explicacion": "La IA destaca en generar materiales personalizados para dislexia: textos en el nivel exacto, actividades de consciencia fonológica, ejercicios de pares mínimos o materiales con tipografías específicas."
    },
    {
        "id": "D07", "bloque": "Aplicaciones clínicas", "dificultad": "medio",
        "pregunta": "¿Qué es un SAAC y cómo puede intervenir la IA en su desarrollo?",
        "opciones": [
            "Un test de evaluación del lenguaje; la IA lo aplica automáticamente",
            "Un Sistema Aumentativo y Alternativo de Comunicación; la IA puede generar pictogramas personalizados",
            "Un software de análisis acústico; la IA interpreta los resultados",
            "Una técnica de intervención en afasia; la IA la aplica de forma autónoma"
        ],
        "correcta": 1,
        "explicacion": "Los SAAC son sistemas de comunicación para personas con dificultades severas de habla. La IA permite crear pictogramas personalizados para contextos y necesidades específicas que no existen en bases estándar como ARASAAC."
    },
    {
        "id": "D08", "bloque": "Aplicaciones clínicas", "dificultad": "medio",
        "pregunta": "¿Cuál es la principal limitación de usar IA para evaluar la fluencia del habla?",
        "opciones": [
            "Los modelos de IA no procesan audio en español",
            "La IA no puede acceder a grabaciones de audio",
            "La IA no detecta con fiabilidad las disfluencias sutiles ni el contexto comunicativo del paciente",
            "La legislación prohíbe usar IA para analizar voz humana"
        ],
        "correcta": 2,
        "explicacion": "La evaluación de la fluencia requiere detectar disfluencias sutiles, valorar el contexto y el impacto comunicativo, lo que los modelos actuales no hacen con la fiabilidad necesaria para la práctica clínica."
    },
    {
        "id": "D09", "bloque": "Aplicaciones clínicas", "dificultad": "avanzado",
        "pregunta": "¿Cuál es la diferencia clave entre buscar pictogramas en ARASAAC y generarlos con IA?",
        "opciones": [
            "No hay diferencia real",
            "Generar con IA permite crear pictogramas para conceptos no existentes en bases estándar",
            "ARASAAC tiene mejor resolución que los pictogramas generados con IA",
            "Generar con IA siempre es más rápido pero de menor calidad"
        ],
        "correcta": 1,
        "explicacion": "La generación con IA permite crear pictogramas para conceptos muy específicos, contextos culturales propios o necesidades individuales que no existen en bases como ARASAAC. Es la transición de 'buscar' a 'crear'."
    },
    {
        "id": "D10", "bloque": "Aplicaciones clínicas", "dificultad": "avanzado",
        "pregunta": "¿Para qué puede usarse un LLM en la redacción de informes logopédicos?",
        "opciones": [
            "Para redactar el diagnóstico completo de forma autónoma",
            "Para estructurar, ampliar o mejorar el estilo de un borrador redactado por el logopeda",
            "Para sustituir la observación clínica y los tests",
            "Para firmar digitalmente los informes"
        ],
        "correcta": 1,
        "explicacion": "El uso más seguro de la IA en informes es como asistente de redacción: el logopeda aporta los datos y observaciones clínicas, la IA ayuda con la estructura, el estilo o la adaptación del lenguaje. El juicio clínico es siempre del profesional."
    },

    # ══════════════════════════════════════════
    # BLOQUE E — ÉTICA Y CRITERIO PROFESIONAL
    # ══════════════════════════════════════════
    {
        "id": "E01", "bloque": "Ética y criterio profesional", "dificultad": "medio",
        "pregunta": "Según la filosofía del canal Logoped-IA, ¿cuál es el papel correcto de la IA en logopedia?",
        "opciones": [
            "Sustituto del logopeda en tareas rutinarias",
            "Herramienta de apoyo al criterio clínico del profesional, sin reemplazarlo",
            "Sistema de diagnóstico automatizado para agilizar listas de espera",
            "Reemplazo de los tests estandarizados en evaluación"
        ],
        "correcta": 1,
        "explicacion": "El principio central del canal es claro: la IA acelera la creación de materiales y apoya el trabajo, pero el criterio clínico es siempre del logopeda. La IA no diagnostica ni interviene sola."
    },
    {
        "id": "E02", "bloque": "Ética y criterio profesional", "dificultad": "medio",
        "pregunta": "¿Por qué es imprescindible verificar la información que genera la IA en contexto clínico?",
        "opciones": [
            "Porque los modelos solo funcionan bien en inglés",
            "Porque los modelos pueden generar información incorrecta o inventada con total seguridad",
            "Porque la IA no puede procesar terminología logopédica",
            "Porque el uso de IA en salud viola automáticamente la LOPD"
        ],
        "correcta": 1,
        "explicacion": "Las alucinaciones, los sesgos y la desactualización son riesgos reales. En contexto clínico, un error puede tener consecuencias para el paciente. La revisión profesional es obligatoria siempre."
    },
    {
        "id": "E03", "bloque": "Ética y criterio profesional", "dificultad": "medio",
        "pregunta": "Al crear materiales con IA para pacientes con afasia, ¿qué consideración es más importante?",
        "opciones": [
            "Que el material esté en el idioma del modelo de IA",
            "Que sea visualmente atractivo",
            "Que sea revisado y adaptado por el logopeda al perfil específico del paciente",
            "Que sea generado con el modelo más potente disponible"
        ],
        "correcta": 2,
        "explicacion": "La afasia es altamente heterogénea. Lo que funciona para un paciente puede ser contraproducente para otro. La IA genera un punto de partida, pero la adaptación al perfil individual es responsabilidad del logopeda."
    },
    {
        "id": "E04", "bloque": "Ética y criterio profesional", "dificultad": "medio",
        "pregunta": "¿Cuál es el principal riesgo ético de usar IA directamente para diagnóstico logopédico?",
        "opciones": [
            "Que el modelo no conozca el DSM-5",
            "Que el modelo genere un diagnóstico sin haber observado ni evaluado al paciente real",
            "Que el diagnóstico salga en inglés",
            "Que el modelo tarde demasiado en responder"
        ],
        "correcta": 1,
        "explicacion": "El diagnóstico clínico requiere observación directa, evaluación estandarizada y juicio profesional. Un modelo que solo lee texto nunca puede sustituir esa evaluación. Usarlo directamente para diagnosticar es clínicamente irresponsable."
    },
    {
        "id": "E05", "bloque": "Ética y criterio profesional", "dificultad": "avanzado",
        "pregunta": "¿Qué implica la LOPD (Ley Orgánica de Protección de Datos) respecto al uso de IA en logopedia?",
        "opciones": [
            "Prohíbe completamente el uso de IA con datos de pacientes",
            "Obliga a tratar los datos de los pacientes con la misma confidencialidad y seguridad que cualquier dato clínico",
            "Solo aplica a hospitales públicos, no a gabinetes privados",
            "Permite compartir datos con modelos de IA sin restricciones si es para fines clínicos"
        ],
        "correcta": 1,
        "explicacion": "La LOPD no prohíbe el uso de IA, pero exige que los datos del paciente se traten con las mismas garantías que cualquier dato clínico. Subir datos identificativos a modelos externos sin anonimizar es una infracción."
    },
    {
        "id": "E06", "bloque": "Ética y criterio profesional", "dificultad": "avanzado",
        "pregunta": "¿Cuándo NO debería usarse IA generativa en logopedia clínica?",
        "opciones": [
            "Nunca, la IA siempre aporta valor en cualquier contexto",
            "Para crear materiales visuales de apoyo",
            "Para tomar decisiones clínicas sin supervisión humana experta",
            "Para redactar borradores de informes que el logopeda revisará"
        ],
        "correcta": 2,
        "explicacion": "La IA no debe tomar decisiones clínicas sin supervisión. En logopedia, cualquier decisión que afecte al paciente (diagnóstico, plan de intervención, alta) requiere el juicio experto del profesional. La IA apoya, no decide."
    },
    {
        "id": "E07", "bloque": "Ética y criterio profesional", "dificultad": "avanzado",
        "pregunta": "¿Qué significa 'pensamiento crítico aplicado a la IA' en el contexto del canal Logoped-IA?",
        "opciones": [
            "Rechazar la IA por completo por sus riesgos",
            "Adoptar toda herramienta nueva lo antes posible",
            "Evaluar cada herramienta según si resuelve problemas reales en consulta, sin hype",
            "Usar solo herramientas avaladas por publicaciones científicas"
        ],
        "correcta": 2,
        "explicacion": "La filosofía del canal propone: innovación con criterio. Cada herramienta se evalúa por si resuelve un problema real en la consulta o el aula. El hype y la adopción ciega son tan problemáticos como el rechazo total."
    },

    # ══════════════════════════════════════════
    # BLOQUE F — NIVEL AVANZADO
    # ══════════════════════════════════════════
    {
        "id": "F01", "bloque": "Nivel avanzado", "dificultad": "avanzado",
        "pregunta": "¿Qué es un 'agente de IA'?",
        "opciones": [
            "Un modelo de IA con licencia comercial",
            "Un sistema de IA que puede ejecutar tareas de forma autónoma tomando decisiones secuenciales",
            "Un asistente virtual de voz como Siri",
            "Un modelo de IA especializado en un único dominio"
        ],
        "correcta": 1,
        "explicacion": "Un agente de IA percibe el entorno, planifica y ejecuta tareas de forma autónoma (navegar webs, escribir código, hacer búsquedas). Manus y Cursor son ejemplos. Representan el siguiente salto tras los chatbots."
    },
    {
        "id": "F02", "bloque": "Nivel avanzado", "dificultad": "avanzado",
        "pregunta": "¿Cuál fue el resultado más destacado de la encuesta sobre uso de IA en logopedia del canal?",
        "opciones": [
            "Diagnóstico automatizado y videoconferencia son los usos más comunes",
            "Creación de materiales, redacción de informes y búsqueda de información son los usos principales",
            "La mayoría de logopedas no usa ninguna herramienta de IA",
            "El análisis acústico es el uso más extendido"
        ],
        "correcta": 1,
        "explicacion": "La comunidad usa principalmente la IA para crear materiales, redactar informes más rápido y buscar/contrastar información. Los usos clínicos directos (diagnóstico, análisis vocal) son minoritarios aún."
    },
    {
        "id": "F03", "bloque": "Nivel avanzado", "dificultad": "avanzado",
        "pregunta": "¿Qué es 'automatización no-code' en el contexto de la IA aplicada a logopedia?",
        "opciones": [
            "Usar IA sin conexión a internet",
            "Crear flujos de trabajo y herramientas automáticas sin necesidad de programar",
            "Aplicar IA solo a tareas no clínicas",
            "Usar modelos de código abierto sin licencia"
        ],
        "correcta": 1,
        "explicacion": "No-code permite crear automatizaciones, formularios inteligentes o chatbots sin saber programar. Manus, Make o Zapier son ejemplos. Un logopeda puede automatizar la anamnesis, recordatorios o generación de materiales sin escribir una línea de código."
    },
    {
        "id": "F04", "bloque": "Nivel avanzado", "dificultad": "avanzado",
        "pregunta": "¿Qué ventaja tiene el RadarClínico Digital presentado en el canal?",
        "opciones": [
            "Evalúa automáticamente el nivel de lenguaje de un paciente",
            "Permite al logopeda autoevaluar su propio nivel de preparación y uso de IA",
            "Genera informes clínicos automatizados",
            "Conecta al logopeda con otros profesionales para supervisión de casos"
        ],
        "correcta": 1,
        "explicacion": "El RadarClínico es una herramienta de autoevaluación para que el logopeda identifique en qué áreas de su práctica la IA podría aportarle más valor y cuál es su nivel actual de implementación."
    },
    {
        "id": "F05", "bloque": "Nivel avanzado", "dificultad": "avanzado",
        "pregunta": "¿Qué representa el dispositivo físico para la vibrante /r/ que aparece en el canal?",
        "opciones": [
            "Un producto comercial ya en venta",
            "Un prototipo en iteración que combina logopedia con diseño y fabricación",
            "Una app de reconocimiento de fonemas",
            "Un test de evaluación de la /r/ vibrante"
        ],
        "correcta": 1,
        "explicacion": "El dispositivo para la /r/ es un prototipo que muestra el enfoque del canal: usar IA y tecnología para resolver problemas clínicos reales, en este caso facilitar la adquisición de uno de los fonemas más difíciles del español."
    },
    {
        "id": "F06", "bloque": "Nivel avanzado", "dificultad": "avanzado",
        "pregunta": "Cuando el canal compara herramientas de IA, ¿cuál es el criterio principal de evaluación?",
        "opciones": [
            "El precio de la suscripción mensual",
            "El número de usuarios activos de la herramienta",
            "Si resuelve un problema clínico o de trabajo real en logopedia",
            "La empresa que hay detrás de la herramienta"
        ],
        "correcta": 2,
        "explicacion": "El filtro del canal es siempre la utilidad práctica real: ¿resuelve esto un problema en consulta o aula? El hype, el precio o la popularidad son secundarios frente a la utilidad clínica demostrable."
    },
]

# Bloques y cuántas preguntas seleccionar de cada uno
BLOQUES_CONFIG = {
    "Conocimiento básico IA":    4,
    "Herramientas de IA":        4,
    "Ingeniería de prompts":     4,
    "Aplicaciones clínicas":     5,
    "Ética y criterio profesional": 4,
    "Nivel avanzado":            4,
}

NIVELES = [
    {"min": 0,  "max": 39,  "nivel": "Iniciando el camino",     "emoji": "🌱", "descripcion": "Estás comenzando a explorar la IA aplicada a logopedia. El canal tiene todo lo que necesitas para dar los primeros pasos sólidos."},
    {"min": 40, "max": 59,  "nivel": "Explorando herramientas", "emoji": "🔍", "descripcion": "Tienes bases sólidas pero hay muchas herramientas y aplicaciones por descubrir. Sigue el canal regularmente para avanzar."},
    {"min": 60, "max": 79,  "nivel": "Profesional aplicado",    "emoji": "⚡", "descripcion": "Buen nivel. Conoces herramientas clave, sabes escribir prompts y estás aprovechando bien la IA en tu práctica."},
    {"min": 80, "max": 94,  "nivel": "Experto en IA clínica",   "emoji": "🎯", "descripcion": "Nivel muy alto. Dominas herramientas avanzadas, prompts complejos y tienes criterio clínico sobre el uso de la IA."},
    {"min": 95, "max": 100, "nivel": "Pionero Logoped-IA",      "emoji": "🚀", "descripcion": "¡Excelencia! Dominas el ecosistema completo. Eres exactamente el perfil que la academia Logoped-IA necesita como referente."},
]


def get_total_preguntas():
    if EXAM_MODE == "aleatorio":
        return sum(BLOQUES_CONFIG.values())
    return len(BANCO)


# ─────────────────────────────────────────────
# BASE DE DATOS — importada desde db.py
# (soporta SQLite local y PostgreSQL en nube)
# ─────────────────────────────────────────────


def seleccionar_preguntas():
    """Selecciona preguntas para la sesión actual."""
    if EXAM_MODE != "aleatorio":
        return sorted(BANCO, key=lambda p: (p["bloque"], p["id"]))

    por_bloque = {}
    for p in BANCO:
        b = p["bloque"]
        por_bloque.setdefault(b, []).append(p)

    seleccion = []
    for bloque, cantidad in BLOQUES_CONFIG.items():
        disponibles = por_bloque.get(bloque, [])
        elegidas = random.sample(disponibles, min(cantidad, len(disponibles)))
        seleccion.extend(elegidas)

    random.shuffle(seleccion)
    return seleccion


def require_admin(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not ADMIN_TOKEN:
            return view_func(*args, **kwargs)

        bearer = request.headers.get("Authorization", "")
        header_token = request.headers.get("X-Admin-Token", "").strip()
        query_token = request.args.get("token", "").strip()
        bearer_token = bearer.replace("Bearer ", "", 1).strip() if bearer.startswith("Bearer ") else ""
        token = header_token or bearer_token or query_token
        if token != ADMIN_TOKEN:
            return jsonify({"error": "No autorizado"}), 401
        return view_func(*args, **kwargs)

    return wrapped


# ─────────────────────────────────────────────
# RUTAS API
# ─────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/api/preguntas")
def get_preguntas():
    """Devuelve una selección aleatoria de preguntas sin revelar la respuesta correcta."""
    seleccion = seleccionar_preguntas()
    return jsonify({
        "titulo": APP_TITLE,
        "modo": EXAM_MODE,
        "total": len(seleccion),
        "bloques": sorted({p["bloque"] for p in seleccion}),
        "preguntas": [{
            "id": p["id"],
            "bloque": p["bloque"],
            "dificultad": p["dificultad"],
            "pregunta": p["pregunta"],
            "opciones": p["opciones"]
        } for p in seleccion]
    })


@app.route("/api/check", methods=["POST"])
def check_respuesta():
    """Valida una sola respuesta y devuelve el índice correcto + explicación."""
    data = request.get_json()
    pid = data.get("pregunta_id")
    respuesta = data.get("respuesta")
    pregunta = next((p for p in BANCO if p["id"] == pid), None)
    if not pregunta:
        return jsonify({"error": "Pregunta no encontrada"}), 404
    return jsonify({
        "correcta_idx": pregunta["correcta"],
        "es_correcta": respuesta == pregunta["correcta"],
        "explicacion": pregunta["explicacion"]
    })


@app.route("/api/submit", methods=["POST"])
def submit_examen():
    """Recibe las respuestas, calcula el resultado y lo guarda."""
    data = request.get_json()
    nombre = (data.get("nombre") or "Anónimo").strip()
    email = (data.get("email") or "").strip()
    profesion = (data.get("profesion") or "").strip()
    respuestas_usuario = data.get("respuestas", {})  # {id_str: indice}
    tiempo_segundos = data.get("tiempo_segundos", 0)
    preguntas_sesion = data.get("preguntas_sesion", [])  # ids de las preguntas del examen

    # Corregir solo las preguntas que se presentaron
    ids_presentados = set(preguntas_sesion) if preguntas_sesion else set(respuestas_usuario.keys())
    preguntas_map = {p["id"]: p for p in BANCO}

    detalle = []
    correctas = 0
    for pid in ids_presentados:
        p = preguntas_map.get(pid)
        if not p:
            continue
        respuesta_dada = respuestas_usuario.get(pid)
        es_correcta = respuesta_dada == p["correcta"]
        if es_correcta:
            correctas += 1
        detalle.append({
            "id": p["id"],
            "bloque": p["bloque"],
            "dificultad": p["dificultad"],
            "pregunta": p["pregunta"],
            "opcion_dada": respuesta_dada,
            "opcion_correcta": p["correcta"],
            "texto_opcion_dada": p["opciones"][respuesta_dada] if respuesta_dada is not None else "Sin respuesta",
            "texto_opcion_correcta": p["opciones"][p["correcta"]],
            "correcta": es_correcta,
            "explicacion": p["explicacion"]
        })

    total = len(detalle) or get_total_preguntas()
    porcentaje = round((correctas / total) * 100, 1)

    nivel_info = NIVELES[0]
    for n in NIVELES:
        if n["min"] <= porcentaje <= n["max"]:
            nivel_info = n
            break

    bloques = {}
    for item in detalle:
        b = item["bloque"]
        if b not in bloques:
            bloques[b] = {"total": 0, "correctas": 0}
        bloques[b]["total"] += 1
        if item["correcta"]:
            bloques[b]["correctas"] += 1

    conn = get_db()
    conn.execute("""
        INSERT INTO resultados (nombre, email, profesion, fecha, puntuacion, porcentaje, nivel, respuestas, tiempo_segundos)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (nombre, email, profesion, datetime.now().isoformat(),
          correctas, porcentaje, nivel_info["nivel"],
          json.dumps(detalle, ensure_ascii=False), tiempo_segundos))
    conn.commit()
    conn.close()

    return jsonify({
        "nombre": nombre,
        "puntuacion": correctas,
        "total": total,
        "porcentaje": porcentaje,
        "nivel": nivel_info["nivel"],
        "emoji": nivel_info["emoji"],
        "descripcion": nivel_info["descripcion"],
        "detalle": detalle,
        "bloques": bloques
    })


@app.route("/admin")
def admin():
    return send_from_directory("static", "admin.html")


@app.route("/api/admin/resultados")
@require_admin
def get_resultados():
    conn = get_db()
    rows = conn.execute(
        "SELECT id, nombre, email, profesion, fecha, puntuacion, porcentaje, nivel, tiempo_segundos FROM resultados ORDER BY fecha DESC"
    ).fetchall()
    participantes = [dict(r) for r in rows]

    stats = conn.execute("""
        SELECT COUNT(*) as total_participantes,
               ROUND(AVG(porcentaje), 1) as media_porcentaje,
               MAX(porcentaje) as max_porcentaje,
               MIN(porcentaje) as min_porcentaje
        FROM resultados
    """).fetchone()

    niveles_dist = conn.execute(
        "SELECT nivel, COUNT(*) as cantidad FROM resultados GROUP BY nivel ORDER BY cantidad DESC"
    ).fetchall()

    profesiones_dist = conn.execute(
        "SELECT profesion, COUNT(*) as cantidad FROM resultados WHERE profesion != '' GROUP BY profesion ORDER BY cantidad DESC"
    ).fetchall()

    todas = conn.execute("SELECT respuestas FROM resultados").fetchall()
    pregunta_stats = {}
    for row in todas:
        for item in json.loads(row["respuestas"]):
            pid = item["id"]
            if pid not in pregunta_stats:
                pregunta_stats[pid] = {"total": 0, "correctas": 0, "pregunta": item["pregunta"], "bloque": item["bloque"]}
            pregunta_stats[pid]["total"] += 1
            if item["correcta"]:
                pregunta_stats[pid]["correctas"] += 1
    for pid in pregunta_stats:
        t = pregunta_stats[pid]["total"]
        c = pregunta_stats[pid]["correctas"]
        pregunta_stats[pid]["tasa_acierto"] = round((c / t * 100), 1) if t > 0 else 0

    conn.close()
    stats_dict = dict(stats) if stats else {}
    stats_dict["total_preguntas_sesion"] = get_total_preguntas()
    return jsonify({
        "participantes": participantes,
        "stats": stats_dict,
        "niveles_distribucion": [dict(r) for r in niveles_dist],
        "profesiones_distribucion": [dict(r) for r in profesiones_dist],
        "pregunta_stats": list(pregunta_stats.values())
    })


@app.route("/api/admin/exportar")
@require_admin
def exportar_csv():
    conn = get_db()
    rows = conn.execute(
        "SELECT nombre, email, profesion, fecha, puntuacion, porcentaje, nivel, tiempo_segundos FROM resultados ORDER BY fecha DESC"
    ).fetchall()
    conn.close()
    output = io.StringIO()
    output.write("Nombre,Email,Profesion,Fecha,Puntuacion,Porcentaje,Nivel,Tiempo(s)\n")
    for r in rows:
        output.write(f"{r['nombre']},{r['email']},{r['profesion']},{r['fecha']},{r['puntuacion']},{r['porcentaje']},{r['nivel']},{r['tiempo_segundos']}\n")
    return Response(output.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment;filename=resultados_logoped_ia.csv"})


@app.route("/api/admin/status")
@require_admin
def admin_status():
    return jsonify({
        "ok": True,
        "protegido": bool(ADMIN_TOKEN),
        "modo_examen": EXAM_MODE,
        "total_preguntas": get_total_preguntas()
    })


@app.route("/healthz")
def healthcheck():
    return jsonify({"ok": True, "app": APP_TITLE})


# Inicializar BD al arrancar (local y gunicorn/nube)
init_db()

if __name__ == "__main__":
    print(f"\n🎓 {APP_TITLE}")
    print(f"   Banco: {len(BANCO)} preguntas · {get_total_preguntas()} por sesión ({EXAM_MODE})")
    print("   Servidor: http://localhost:5050")
    print("   Admin:    http://localhost:5050/admin\n")
    app.run(debug=True, port=5050, host="0.0.0.0")
