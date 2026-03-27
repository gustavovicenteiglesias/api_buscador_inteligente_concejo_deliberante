# TODO-003 Logging centralizado

## Estado
DONE

## Prioridad
Alta

## Objetivo
Unificar la configuración de logging para toda la aplicación.

## Alcance
- Crear `app/core/logging.py`
- Definir formato común de logs
- Reemplazar configuraciones dispersas
- Asegurar que services y routes usen el logger central

## Dependencias
- TODO-001
- TODO-002

## Criterio de aceptación
- existe una única configuración de logging
- los módulos principales usan el logger común

## Pruebas mínimas
- smoke test de emisión de log desde app y service