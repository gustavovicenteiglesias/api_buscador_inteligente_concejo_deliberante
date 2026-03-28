AGENTS.md
Antes de realizar cualquier acción, debes leer obligatoriamente:
ai/context.md
ai/decisions.md
ai/project-map.md
ai/workflow.md
ai/tasks/

Regla principal
NO empieces a codear directamente.

Gestión obligatoria de tareas (CRÍTICO)
La carpeta /ai/tasks/ es la única fuente válida de estado del trabajo.
Es OBLIGATORIO:
Identificar una tarea con estado TODO
Cambiar su estado a DOING
Explicar el plan de trabajo
Ejecutar únicamente esa tarea
Al finalizar:
cambiar estado a DONE, o
cambiar a BLOCKED si no puede continuar
PROHIBIDO
Trabajar sin tarea asignada
Ejecutar múltiples tareas en paralelo sin registrarlo
Realizar cambios sin actualizar el estado de la tarea
Continuar trabajando después de terminar una tarea sin seleccionar la siguiente

Control de ejecución (anti consumo de tokens)
La ejecución debe ser incremental y controlada.
NO realizar cambios grandes sin dividir en tareas
NO avanzar a otra tarea sin cerrar la actual
NO improvisar fuera del flujo definido en /ai/tasks/
Cada iteración debe:
empezar con una tarea clara
terminar con un estado actualizado

Alcance del proyecto
El alcance está definido en:
ai/context.md → objetivos y funcionalidad
ai/decisions.md → reglas técnicas
NO asumir alcance fuera de esos documentos.

Flujo obligatorio
Para cada tarea:
Leer contexto relevante
Validar decisiones técnicas
Ubicar archivos en project-map.md
Explicar plan
Ejecutar cambios
Actualizar estado de tarea

Consistencia del sistema
Si el proyecto tiene múltiples capas:
backend
frontend
base de datos
sincronización
APIs
TODO cambio debe evaluarse en todas las capas afectadas.

Cambios estructurales
Antes de modificar:
modelos de datos
persistencia
sincronización
contratos entre capas
Debes:
Explicar impacto
Validar compatibilidad
Definir transición si aplica

Uso de IA
La IA puede:
analizar
proponer
ejecutar tareas específicas
La IA NO puede:
ignorar el sistema de tareas
trabajar fuera de /ai/tasks/
modificar arquitectura sin justificación

Objetivo
Mantener un sistema:
trazable
controlado
reproducible
independiente de la herramienta
Cada cambio debe poder ser entendido y continuado por otro agente sin pérdida de contexto.



