---
name: linkedin-content
description: >-
  Use this skill when the user wants to draft, edit, review, schedule, or approve LinkedIn posts,
  manage the editorial calendar (Tuesdays for Projects/Building, Fridays for Applied Knowledge),
  or run local software repositories live to capture clean screenshots and transform them into LinkedIn content.
---

# Skill: Gestor de Publicaciones, Capturas en Vivo y Calendario Editorial (`linkedin-content`)

Este skill define el procedimiento exacto para planificar, investigar, ejecutar proyectos en vivo para obtener capturas limpias, redactar, validar y gestionar el ciclo de vida de las publicaciones de LinkedIn del usuario.

---

## 1. Contexto Obligatorio Antes de Redactar

Antes de escribir una sola línea de una publicación, **DEBES** leer:
1. `knowledge/professional-identity.md` (para alinear el enfoque con la identidad, propuesta de valor y pilares profesionales del usuario).
2. `knowledge/writing-style.md` (para aplicar sus reglas de estructura, tono, formato escaneable y prohibición de clichés).
3. La ficha específica del proyecto en `knowledge/projects/<proyecto>.md` (y, si hace falta mayor detalle técnico, inspeccionar el repositorio correspondiente en la ruta `LOCAL_REPOS_DIR` definida en `.env`).
4. `content/editorial-calendar.md` (para verificar el código correlativo `LI-XXX` y el pilar correspondiente).

---

## 2. Flujo Paso a Paso para Crear un Borrador

### Paso 1: Selección de Ángulo y Pilar
Determina qué tipo de publicación corresponde según el calendario del usuario:
- **Martes (Proyectos y Construcción - "El Builder"):**
  - *Objetivo:* Mostrar un sistema, dashboard o proyecto real construido por el usuario resolviendo un problema tangible de negocio, ciencia o ingeniería.
  - *Ángulo ejecutivo/práctico:* No enumeres librerías como una lista de compras. Explica **qué problema resuelve**, **cómo funciona su diseño** y **qué aprendizaje deja**.
- **Viernes (Conocimiento Aplicado - "El Estratega"):**
  - *Objetivo:* Compartir un aprendizaje técnico, metodológico o de dominio aplicable por otros profesionales.

### Paso 2: Estructura de la Publicación (Anatomía de Alto Impacto)
1. **El Gancho (Líneas 1 a 2 - Antes del "...ver más"):**
   - Máximo 180-210 caracteres en las primeras dos líneas.
   - Debe plantear una tensión real de negocio/ingeniería o un contraste directo.
2. **El Contexto / Problema (Párrafo corto):**
   - Por qué ocurre este problema en la práctica profesional o el desarrollo de soluciones.
3. **La Solución / Lo Construido (El Núcleo):**
   - Usa de 3 a 4 viñetas limpias (`•` o `→`) explicando los mecanismos clave del proyecto con lenguaje claro y sin saturar de estadísticas innecesarias.
4. **El Insight / Aprendizaje Profesional:**
   - Una reflexión breve que conecte la técnica con la toma de decisiones reales.
5. **Llamada a la Conversación (CTA Sobrio) + Enlace:**
   - Una pregunta específica para abrir debate profesional y mención al repositorio o demo cuando aplique.
6. **Hashtags (3 a 5 máximo):**
   - Ubicados al final, específicos al tema.

### Paso 3: Ejecución en Vivo del Repositorio y Capturas Limpias (Obligatorio)
Para hablar con propiedad de un proyecto y obtener las mejores imágenes posibles, **el agente siempre debe entrar al repositorio del usuario, correr el programa en vivo y ver lo que tiene**:

1. **Levantar y Ejecutar el Proyecto Real:**
   - Corre el código del repositorio objetivo en su propio entorno virtual y levanta su interfaz web (`Streamlit`, `Dash`, `React/Vite`, `FastAPI`, etc.).
2. **Guardar Solo Capturas Limpias (Sin Texto ni Marcos Superpuestos):**
   - Utiliza el script de captura limpia en vivo:
     [capture_live_app.py](./scripts/capture_live_app.py)
   - Ejemplos de ejecución:
     ```powershell
     # Capturar un proyecto pasándole su ruta o nombre en LOCAL_REPOS_DIR y el ID del post:
     .\.venv\Scripts\python.exe .\.agents\skills\linkedin-content\scripts\capture_live_app.py --post-id LI-001 --app-dir "nombre-del-repo"
     ```
   - Este script abre el programa corriendo en Chromium (`1680x1120`, `device_scale_factor=2`), recorre sus pestañas y almacena únicamente las **capturas de pantalla puras** como imágenes PNG en `content/assets/LI-XXX/`.
   - **Prohibido saturar las imágenes:** No agregues cabeceras, píldoras de texto ni bordes oscuros alrededor de las capturas de pantalla.
   - **Cuándo usar Carrusel PDF:** Reserva los carruseles PDF exclusivamente para eventos, congresos o resúmenes conceptuales donde no exista una interfaz de software que mostrar, y mantenlos siempre visuales y con el mínimo texto posible.
3. **No Saturar el Post de Cifras:**
   - Correr el programa sirve para que el agente vea cómo luce y qué hace realmente cada vista, no para volcar todas las estadísticas de la base de datos dentro del post.

### Paso 4: Verificación Anti-Humo (Checklist de Calidad)
Antes de guardar el borrador, comprueba:
- [ ] ¿Todas las funciones mencionadas existen realmente en el repositorio del proyecto?
- [ ] ¿La longitud total es inferior a 3.000 caracteres (idealmente entre 900 y 1.500 caracteres)?
- [ ] ¿Los párrafos tienen de 1 a 3 oraciones con líneas en blanco para lectura cómoda?
- [ ] ¿Está libre de frases hechas de IA (*"En el vertiginoso mundo actual..."*, *"¡Revolucionando la industria!"*)?

### Paso 5: Guardado y Registro
1. Guarda el borrador en `content/drafts/LI-XXX-slug-del-tema.md`.
2. Actualiza el estado en `content/editorial-calendar.md` a `📝 En Borrador (LI-XXX)`.
3. Presenta el borrador al usuario usando la plantilla del **Approval Gateway** definida en `AGENTS.md`.

---

## 3. Protocolo de Aprobación y Publicación

1. **Cuando el usuario pide cambios:**
   - Edita el archivo en `content/drafts/LI-XXX-....md` y vuelve a mostrar la versión actualizada manteniendo el estado `Pendiente de Aprobación`.
2. **Cuando el usuario aprueba explícitamente (`"Apruebo publicar LI-XXX"`):**
   - Mueve o copia el archivo validado a `content/approved/LI-XXX-....md` añadiendo en su cabecera la fecha y hora de aprobación.
   - Si el conector MCP de LinkedIn (`create_post`) está activo (Fase 2), invócalo con el texto exacto aprobado.
   - Una vez publicado, mueve el registro a `content/published/LI-XXX-....md` con el URN/ID de la publicación y añade una fila inicial en `analytics/performance-history.csv`.
