# TODO-011 Servicio de búsqueda semántica

## Estado
DONE

## Prioridad
Alta

## Objetivo
Construir un servicio dedicado a consultas semánticas.

## Alcance
- Crear `search_service.py`
- Recibir query y filtros
- Generar embedding de consulta
- Delegar búsqueda al repositorio vectorial
- Normalizar respuesta

## Dependencias
- TODO-008
- TODO-009

## Criterio de aceptación
- la búsqueda semántica no reside en rutas ni bootstrap
- existe contrato de entrada y salida claro

## Pruebas mínimas
- unit test del servicio con mocks