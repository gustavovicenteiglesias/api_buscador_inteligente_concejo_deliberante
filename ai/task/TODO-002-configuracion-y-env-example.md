# TODO-002 Configuración central y contrato de entorno

## Estado
DONE

## Prioridad
Alta

## Objetivo
Centralizar la configuración y formalizar el contrato de variables de entorno.

## Alcance
- Crear `app/core/config.py`
- Centralizar lecturas de variables de entorno
- Eliminar valores hardcodeados inseguros en defaults
- Crear `.env.example` con claves vacías o placeholders seguros

## Entradas afectadas
- lecturas directas de `os.getenv`
- configuración dispersa

## Salidas esperadas
- configuración única reutilizable
- `.env.example` documentado

## Dependencias
- TODO-001

## No incluye
- rotación de secretos
- integración con vault externo

## Criterio de aceptación
- todas las variables críticas salen de `config.py`
- existe `.env.example`
- no quedan secretos hardcodeados

## Pruebas mínimas
- test unitario de carga de configuración mínima