# TODO-008 Encapsular clientes externos

## Estado
DONE

## Prioridad
Alta

## Objetivo
Encapsular inicialización y acceso a Azure OpenAI y Weaviate.

## Alcance
- Crear `azure_openai_client.py`
- Crear `weaviate_client.py`
- Mover inicialización y configuración de SDKs

## Dependencias
- TODO-002

## Criterio de aceptación
- los services no inicializan SDKs directamente
- la configuración de clientes depende de `config.py`

## Pruebas mínimas
- smoke test de construcción de clientes con configuración mockeada