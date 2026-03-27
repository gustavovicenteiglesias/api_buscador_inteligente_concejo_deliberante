# TODO-015 Refactor de rutas existentes

## Estado
DONE

## Prioridad
Media

## Objetivo
Reducir las rutas/controladores a orquestadores delgados.

## Alcance
- mover lógica pesada existente a services
- dejar rutas con validación, delegación y respuesta
- eliminar dependencia directa de SDKs desde la capa API

## Dependencias
- TODO-010
- TODO-011
- TODO-012
- TODO-013

## Criterio de aceptación
- las rutas no contienen lógica de chunking, embeddings ni acceso directo a Weaviate
- la capa API es delgada y consistente

## Pruebas mínimas
- regression smoke test de endpoints existentes