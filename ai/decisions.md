# Decisiones de arquitectura

## D-001 Separación por capas
Se separa la aplicación en capas:
- API/transport
- Services
- Repositories/adapters
- Core/config
- Utils/document-processing

Motivo:
Reducir acoplamiento y permitir pruebas unitarias sobre lógica de negocio sin servidor HTTP.

## D-002 main.py como punto de entrada mínimo
main.py solo debe:
- cargar configuración
- crear la app
- registrar rutas
- iniciar el servidor

Motivo:
Eliminar el rol de archivo monolítico y reducir impacto de cambios.

## D-003 Estructura base del proyecto
Estructura objetivo:

/
├── app/
│   ├── __init__.py
│   ├── core/
│   │   ├── config.py
│   │   ├── logging.py
│   │   ├── constants.py
│   │   └── errors.py
│   ├── api/
│   │   ├── routes/
│   │   │   ├── documents.py
│   │   │   └── search.py
│   │   ├── schemas/
│   │   │   ├── documents.py
│   │   │   └── search.py
│   │   └── handlers/
│   │       └── error_handler.py
│   ├── services/
│   │   ├── document_service.py
│   │   ├── indexing_service.py
│   │   ├── search_service.py
│   │   └── deletion_service.py
│   ├── repositories/
│   │   ├── vector_repository.py
│   │   └── metadata_repository.py
│   ├── clients/
│   │   ├── azure_openai_client.py
│   │   └── weaviate_client.py
│   ├── models/
│   │   ├── document.py
│   │   ├── chunk.py
│   │   └── metadata.py
│   └── utils/
│       ├── pdf_reader.py
│       ├── filename_parser.py
│       └── chunking.py
├── tests/
│   ├── unit/
│   └── integration/
├── .env
├── .env.example
├── requirements.txt
└── main.py

Motivo:
Escalabilidad controlada y responsabilidades explícitas.

## D-004 Validación de contratos de entrada
Las entradas HTTP deben validarse con esquemas explícitos.

Motivo:
- reducir validación manual
- mejorar documentación
- garantizar consistencia

## D-005 Manejo centralizado de errores
Todas las excepciones deben mapearse a respuesta JSON uniforme:

{
  "error": "mensaje",
  "code": "ERROR_CODE"
}

Motivo:
Consistencia y debugging.

## D-006 Logger centralizado
La configuración de logging se define en app/core/logging.py.

Motivo:
Unificar formato y comportamiento.

## D-007 Metadatos documentales obligatorios
Todo documento debe incluir:
- id_documento
- nombre_archivo
- tipo
- anio
- mes (opcional)
- fecha_indexacion
- origen

Motivo:
Permitir filtros administrativos.

## D-008 Parsing desacoplado
La extracción de metadatos se implementa en filename_parser.py.

Motivo:
Evitar mezclar reglas de negocio con transporte o indexación.

## D-009 Borrado masivo por filtro
El borrado por año o período se realiza mediante batch delete.

Motivo:
Evitar iteración objeto a objeto.

## D-010 Validación de filtros administrativos
Antes de borrar:
- año > 1900
- mes entre 1 y 12
- coherencia de parámetros

Motivo:
Evitar errores operativos.

## D-011 Endpoints de borrado
Se definen:
- DELETE /api/docs/anio/<anio>
- DELETE /api/docs/anio/<anio>/mes/<mes>

Motivo:
Soporte administrativo.

## D-012 Weaviate como índice
Weaviate se usa para búsqueda semántica, no como única fuente administrativa.

Motivo:
Separar búsqueda de gestión.

## D-013 Persistencia administrativa futura
Se prevé una base SQL para:
- catálogo documental
- auditoría
- trazabilidad

Motivo:
Gobernanza de datos.

## D-014 Servicios especializados
Separación en:
- indexing_service
- search_service
- deletion_service
- document_service

Motivo:
Claridad y mantenibilidad.

## D-015 Repositorios desacoplados
Los services no acceden directamente a SDKs externos.

Motivo:
Reducir dependencia de proveedores.

## D-016 Estrategia de pruebas
Se definen:
- unit tests
- integration tests

Motivo:
Soporte a refactorización.

## D-017 .env.example obligatorio
Debe existir archivo de ejemplo sin secretos.

Motivo:
Onboarding seguro.

## D-018 Sin sobreingeniería
No introducir complejidad innecesaria.

Motivo:
Mantener foco práctico.