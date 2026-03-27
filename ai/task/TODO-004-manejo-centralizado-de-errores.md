# TODO-004 Manejo centralizado de errores

## Estado
DONE

## Prioridad
Alta

## Objetivo
Implementar respuesta JSON uniforme para errores controlados y no controlados.

## Alcance
- Crear `app/core/errors.py`
- Crear handler global en `app/api/handlers/error_handler.py`
- Definir errores de validación, integración y negocio
- Mapear excepciones a JSON uniforme

## Dependencias
- TODO-001
- TODO-002

## Criterio de aceptación
- los errores devuelven JSON consistente
- las rutas no contienen bloques repetitivos de manejo de error

## Pruebas mínimas
- integration test de error 400
- integration test de error 500 controlado