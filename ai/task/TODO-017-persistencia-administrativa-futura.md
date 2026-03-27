# TODO-017 Persistencia administrativa futura

## Estado
TODO

## Prioridad
Baja

## Objetivo
Diseñar la incorporación futura de una base administrativa SQL como fuente de verdad documental.

## Alcance
- definir responsabilidades de `metadata_repository.py`
- definir esquema mínimo administrativo
- definir qué datos viven en SQL y cuáles en Weaviate
- definir estrategia de auditoría de carga y borrado

## Dependencias
- TODO-005
- TODO-009
- TODO-012

## No incluye
- implementación completa en esta fase

## Criterio de aceptación
- queda documento técnico o contrato de repositorio preparado para la evolución
- no se bloquea la implementación actual

## Pruebas mínimas
- no aplica en esta fase