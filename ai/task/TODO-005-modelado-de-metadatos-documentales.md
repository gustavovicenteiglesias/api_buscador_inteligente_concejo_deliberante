# TODO-005 Modelado de metadatos documentales

## Estado
DONE

## Prioridad
Alta

## Objetivo
Definir el modelo mínimo de metadatos administrativos requeridos para indexación y borrado.

## Alcance
- Crear modelos de `Documento`, `Chunk` y `MetadataDocumento`
- Definir campos obligatorios y opcionales
- Incorporar `anio` y `mes` como metadatos soportados

## Dependencias
- TODO-001
- TODO-002

## Criterio de aceptación
- los modelos documentan claramente los metadatos requeridos
- `mes` queda previsto como opcional

## Pruebas mínimas
- unit tests de creación/validación de modelos