# TODO-006 Parser de nombre de archivo

## Estado
DONE

## Prioridad
Alta

## Objetivo
Encapsular la extracción de metadatos desde nombre de archivo.

## Alcance
- Crear `app/utils/filename_parser.py`
- Extraer `tipo`
- Extraer `anio`
- Extraer `mes` cuando sea posible
- Definir comportamiento ante ausencia de metadatos

## Dependencias
- TODO-005

## No incluye
- OCR
- lectura del contenido del PDF para inferencia avanzada

## Criterio de aceptación
- la lógica de parsing sale del archivo principal
- el parser es reutilizable y testeable

## Pruebas mínimas
- unit tests con nombres válidos e inválidos
- unit tests para año y mes