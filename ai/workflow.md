# Workflow de trabajo

## Principio general
Toda modificación debe entrar por tarea explícita en `/ai/tasks/` y respetar el orden de prioridad técnica.

## Secuencia obligatoria por tarea
1. Leer:
   - `ai/context.md`
   - `ai/decisions.md`
   - `ai/project-map.md`
   - `ai/workflow.md`
   - tarea objetivo en `ai/tasks/`
2. Identificar dependencias declaradas en la tarea.
3. Verificar impacto en:
   - API
   - services
   - repositories
   - clients
   - utils
   - tests
4. Implementar solo el alcance definido.
5. Actualizar pruebas mínimas asociadas.
6. Cambiar estado de la tarea:
   - `TODO` -> `DOING`
   - `DOING` -> `DONE`

## Estados permitidos
- `TODO`
- `DOING`
- `BLOCKED`
- `DONE`

## Reglas de ejecución
- No implementar más de una tarea de alto impacto a la vez.
- No modificar contratos públicos sin actualizar esquemas y tests.
- No introducir dependencias nuevas sin necesidad técnica justificada.
- No mezclar refactor estructural con cambio funcional no planificado.
- No acoplar reglas de negocio al framework HTTP.
- No acceder al SDK del proveedor directamente desde rutas/controladores.
- No duplicar lógica de validación entre API y services.

## Regla para cambios de estructura
Antes de mover archivos o módulos:
- verificar imports afectados
- verificar punto de entrada
- verificar configuración
- verificar pruebas

## Regla para cambios de metadatos
Todo cambio en metadatos documentales debe reflejarse en:
- modelos
- parsing
- persistencia vectorial
- filtros de búsqueda/borrado
- tests

## Regla para cambios de borrado
Todo cambio en operaciones de borrado debe:
- validar filtros de entrada
- usar batch delete si el proveedor lo permite
- devolver respuesta consistente
- dejar trazabilidad mínima en logs

## Regla para pruebas
Cada tarea debe definir prueba mínima esperada:
- unit
- integration
- ambas

## Criterio de finalización de tarea
Una tarea se considera terminada solo si:
- el alcance definido fue implementado
- no deja imports rotos
- no rompe contratos existentes no declarados
- posee pruebas mínimas asociadas
- su estado fue actualizado a `DONE`

## Orden recomendado de ejecución
1. Base estructural
2. Configuración y logging
3. Manejo de errores
4. Parsing y metadatos
5. Repositorios y clients
6. Servicios
7. Endpoints nuevos
8. Pruebas
9. Persistencia administrativa futura