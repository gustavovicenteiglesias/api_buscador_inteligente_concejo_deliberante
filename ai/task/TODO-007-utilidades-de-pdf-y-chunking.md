# TODO-007 Utilidades de PDF y chunking

## Estado
DONE

## Prioridad
Media

## Objetivo
Separar lectura de PDF y chunking en módulos reutilizables.

## Alcance
- Crear `pdf_reader.py`
- Crear `chunking.py`
- Extraer funciones puras o casi puras desde el archivo actual

## Dependencias
- TODO-001

## Criterio de aceptación
- lectura de PDF y chunking quedan fuera de rutas y bootstrap
- services pueden consumir ambos módulos

## Pruebas mínimas
- unit test de chunking
- smoke test de extracción de texto con fixture pequeño