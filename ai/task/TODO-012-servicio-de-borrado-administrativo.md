# TODO-012 Servicio de borrado administrativo

## Estado
DONE

## Prioridad
Alta

## Objetivo
Crear un servicio dedicado a operaciones de borrado por filtros administrativos.

## Alcance
- Crear `deletion_service.py`
- Implementar borrado por año
- Implementar borrado por año y mes
- Validar filtros antes de delegar
- Usar batch delete vía repositorio

## Dependencias
- TODO-009
- TODO-005

## Criterio de aceptación
- no existe borrado objeto por objeto en capas superiores
- se soportan filtros por período

## Pruebas mínimas
- unit test de validación de filtros
- unit test de llamado a batch delete