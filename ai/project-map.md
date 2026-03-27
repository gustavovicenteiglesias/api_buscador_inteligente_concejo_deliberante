# Mapa del proyecto

## Visión general
Sistema API para:
- indexación documental
- búsqueda semántica
- administración de documentos

## Capas

### API
Responsabilidad:
- endpoints HTTP
- validación
- respuesta JSON

Componentes:
- routes
- schemas
- error handler

### Services
Responsabilidad:
- lógica de negocio
- orquestación de procesos

Componentes:
- indexing_service
- search_service
- deletion_service
- document_service

### Repositories
Responsabilidad:
- acceso a datos
- queries y deletes

Componentes:
- vector_repository
- metadata_repository

### Clients
Responsabilidad:
- conexión a servicios externos

Componentes:
- azure_openai_client
- weaviate_client

### Core
Responsabilidad:
- configuración
- logging
- errores

Componentes:
- config
- logging
- constants
- errors

### Utils
Responsabilidad:
- procesamiento documental

Componentes:
- pdf_reader
- filename_parser
- chunking

## Entidades

### Documento
- id_documento
- nombre_archivo
- tipo
- anio
- mes
- fecha_indexacion

### Chunk
- id_chunk
- id_documento
- texto
- orden

### Metadata
- tipo
- anio
- mes

## Relaciones
- Documento → muchos Chunk
- Chunk → pertenece a Documento

## Flujos

### Indexación
1. API recibe archivo
2. parsing de metadata
3. lectura PDF
4. chunking
5. embeddings
6. persistencia

### Búsqueda
1. API recibe query
2. embedding de consulta
3. búsqueda vectorial
4. retorno de resultados

### Borrado por año
1. API recibe año
2. validación
3. batch delete

### Borrado por año/mes
1. API recibe año y mes
2. validación
3. batch delete

## Dependencias
- API → Services
- Services → Repositories + Clients + Utils
- Repositories → Clients

## Puntos de extensión
- base SQL administrativa
- nuevos filtros
- nuevos formatos documentales
- auditoría