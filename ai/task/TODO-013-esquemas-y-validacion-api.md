# TODO-013 Esquemas y validación de API

## Estado
DONE

## Prioridad
Alta

## Objetivo
Formalizar los contratos HTTP de entrada y salida.

## Alcance
- Crear esquemas de requests/responses
- Validar búsqueda, carga y borrado
- Documentar errores de validación
- Mejorar especificación Swagger

## Dependencias
- TODO-005
- TODO-010
- TODO-011
- TODO-012

## Criterio de aceptación
- requests inválidos fallan antes de entrar a la lógica de negocio
- Swagger refleja contratos reales

## Pruebas mínimas
- integration tests de validación