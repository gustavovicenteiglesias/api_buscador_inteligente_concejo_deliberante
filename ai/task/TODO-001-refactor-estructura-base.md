# TODO-001 Refactor estructura base del proyecto

## Estado
DONE

## Prioridad
Alta

## Objetivo
Crear la estructura modular base del proyecto y convertir `main.py` en punto de entrada mínimo.

## Alcance
- Crear carpetas y módulos base definidos en `project-map.md`
- Mover configuración y creación de app fuera de `main.py`
- Dejar `main.py` solo como bootstrap
- Mantener comportamiento existente sin agregar funcionalidad nueva

## Entradas afectadas
- `main.py`

## Salidas esperadas
- `app/` creada con submódulos mínimos
- imports resueltos
- app inicializable desde el nuevo punto de entrada

## Dependencias
- Ninguna

## No incluye
- Cambios funcionales en endpoints
- Nuevos endpoints
- Persistencia SQL
- Reescritura completa de lógica de negocio

## Criterio de aceptación
- La aplicación levanta con la nueva estructura
- `main.py` no contiene lógica de negocio
- No se rompe la inicialización actual

## Pruebas mínimas
- smoke test de arranque de aplicación