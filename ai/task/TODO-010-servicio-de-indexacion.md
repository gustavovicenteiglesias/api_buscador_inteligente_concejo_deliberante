# TODO-010 Servicio de indexación

## Estado
DONE

## Prioridad
Alta

## Objetivo
Construir un servicio dedicado a la indexación documental.

## Alcance
- Crear `indexing_service.py`
- Orquestar parsing, lectura de PDF, chunking, embeddings y persistencia
- Devolver resultado estructurado de indexación

## Dependencias
- TODO-006
- TODO-007
- TODO-008
- TODO-009

## Criterio de aceptación
- la indexación no se ejecuta desde rutas ni bootstrap
- el flujo de indexación está centralizado

## Pruebas mínimas
- unit test del flujo con mocks