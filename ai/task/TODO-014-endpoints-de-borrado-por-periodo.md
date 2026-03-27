# TODO-014 Endpoints de borrado por período

## Estado
DONE

## Prioridad
Alta

## Objetivo
Exponer endpoints administrativos para borrado por año y año/mes.

## Alcance
- Implementar `DELETE /api/docs/anio/<int:anio>`
- Implementar `DELETE /api/docs/anio/<int:anio>/mes/<int:mes>`
- Delegar en `deletion_service`
- Responder con formato JSON consistente

## Dependencias
- TODO-012
- TODO-013
- TODO-004

## Criterio de aceptación
- ambos endpoints existen
- ambos validan parámetros
- ambos usan batch delete indirectamente

## Pruebas mínimas
- integration test por endpoint