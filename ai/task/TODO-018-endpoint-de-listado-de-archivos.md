# TODO-018 Endpoint de listado de archivos

## Estado
DONE

## Prioridad
Media

## Objetivo
Implementar un endpoint para listar todos los documentos indexados con soporte para filtros y paginación.

## Alcance
- Extender `VectorRepository` con capacidad de listado y agrupamiento.
- Implementar filtros por año y tipo de documento.
- Implementar paginación básica (limit/offset).
- Crear el endpoint `GET /api/docs`.

## Dependencias
- TODO-009
- TODO-013
- TODO-014

## Criterio de aceptación
- El endpoint devuelve una lista única de documentos (no fragmentos).
- Soporta filtros por año y tipo.
- Soporta paginación.

## Pruebas mínimas
- Llamada al endpoint con filtros.
- Verificación de la estructura de respuesta.
