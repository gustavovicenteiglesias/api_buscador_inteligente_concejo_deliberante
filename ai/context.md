# Contexto del proyecto

## Objetivo
Construir y evolucionar un buscador inteligente para el HCD con foco en indexación documental, búsqueda semántica y administración del repositorio documental mediante API.

## Estado actual
El sistema actual concentra responsabilidades de infraestructura, lógica de negocio, procesamiento documental y exposición HTTP en un único archivo principal. Esto genera alta fricción para mantener, probar y escalar.

## Problemas detectados
- La lógica HTTP está acoplada con la lógica de búsqueda semántica.
- La inicialización de clientes externos y la configuración están mezcladas con reglas de negocio.
- El procesamiento documental y el chunking no están encapsulados.
- El borrado documental actual es ineficiente para grandes volúmenes.
- No existe una estructura explícita para pruebas.
- No hay una separación clara entre configuración, servicios, rutas y utilidades.
- No existe una fuente administrativa de verdad aparte de la base vectorial.
- La validación de entradas y el manejo de errores no están centralizados.
- La gestión de secretos depende de `.env`, pero falta un contrato de configuración compartible.

## Alcance funcional identificado
- Carga e indexación de documentos PDF.
- Extracción de metadatos desde nombre de archivo y/o contenido.
- Chunking de texto para embeddings.
- Persistencia vectorial en Weaviate.
- Consulta semántica sobre documentos indexados.
- Exposición de endpoints HTTP documentados con Swagger.
- Eliminación de documentos por archivo.
- Nueva necesidad de eliminación por año.
- Nueva necesidad de eliminación por año y mes.

## Restricciones técnicas
- Mantener bajo acoplamiento entre transporte HTTP y lógica de negocio.
- Preparar la arquitectura para crecimiento sin sobreingeniería.
- Evitar dependencia directa de detalles de proveedor en las capas superiores.
- Permitir futura migración de framework HTTP o motor vectorial con impacto controlado.
- Mantener la solución apta para operación incremental.

## Suposiciones operativas
- Azure OpenAI se utiliza para embeddings y/o capacidades de IA.
- Weaviate se utiliza como motor vectorial principal.
- Los documentos requieren metadatos mínimos para filtrado administrativo.
- El nombre del archivo puede ser fuente parcial de metadatos.
- El borrado masivo debe resolverse con operaciones por lote y no por iteración objeto a objeto.

## Entidades principales
- Documento
- Chunk
- MetadataDocumento
- Embedding
- SolicitudBusqueda
- ResultadoBusqueda
- SolicitudBorrado
- ConfiguracionAplicacion

## Relaciones principales
- Un Documento tiene muchos Chunk.
- Un Chunk pertenece a un Documento.
- Un Documento posee MetadataDocumento.
- Un Chunk puede tener un Embedding asociado.
- Una SolicitudBusqueda consulta sobre Chunk y/o Documento.
- Una SolicitudBorrado filtra Documentos por criterios administrativos.
- La ConfiguracionAplicacion abastece a todas las capas.

## Riesgos actuales
- Cambios simples pueden romper múltiples áreas por acoplamiento.
- Baja observabilidad de errores.
- Riesgo de inconsistencias al inferir metadatos sin validación formal.
- Riesgo de costos y tiempos altos en borrados masivos mal implementados.
- Riesgo de dependencia excesiva de la base vectorial para funciones administrativas.

## Resultado esperado de la reorganización
- Código organizado por responsabilidades.
- Endpoints delgados.
- Servicios testeables.
- Configuración explícita y segura.
- Metadatos documentales aptos para filtros.
- Borrado eficiente por filtros administrativos.
- Base preparada para sumar persistencia administrativa sin romper la búsqueda semántica.