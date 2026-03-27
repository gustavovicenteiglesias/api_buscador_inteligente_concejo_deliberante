# TODO-009 Repositorio vectorial

## Estado
DONE

## Prioridad
Alta

## Objetivo
Crear una capa repositorio para encapsular persistencia y consultas en Weaviate.

## Alcance
- Crear `vector_repository.py`
- Encapsular alta de chunks/documentos
- Encapsular búsqueda semántica
- Encapsular borrado por filtro
- Encapsular batch delete

## Dependencias
- TODO-008
- TODO-005

## Criterio de aceptación
- services no dependen del SDK de Weaviate
- las operaciones vectoriales quedan centralizadas

## Pruebas mínimas
- unit tests con mock de cliente