# TODO-019 Endpoint de Borrado Individual de Documentos

## Estado
DONE

## Contexto
El usuario necesita que la aplicación principal (Spring Boot con MySQL) pueda orquestar el borrado total de un documento de todos los sistemas distribuidos (disco local en VPS y Base de Datos Vectorial Weaviate).

## Objetivo
Implementar un endpoint REST `DELETE /api/admin/documento/<filename>` que funcione como compensador (Saga pattern) para eliminar todo el rastro de un PDF en los servicios Python sin afectar la fuente de verdad (Java).

## Tareas

1. **Esquemas de Respuesta**
   - Definir `DeleteResponse` en `app/schemas/admin_schemas.py` para normalizar la confirmación a la API principal, devolviendo `status`, `filename` y cantidad de chunks borrados de Weaviate.

2. **Lógica de Weaviate (`document_service.py`)**
   - Importar `weaviate_client`.
   - Implementar la función `delete_document_by_filename(filename)`.
   - Efectuar borrado nativo filtrado: `client.batch.delete_objects(class_name, where={"path":["title"], "operator":"Equal", "valueString":filename})`.

3. **Lógica de Sistema de Archivos**
   - En la nueva ruta, tomar el filename enviado por Path Variable y resolver `config.UPLOAD_DIR / filename`.
   - Chequear la existencia del archivo físico; si existe, forzar `os.remove()`. 
   - Atrapar errores en caso de que el archivo ya no exista físicamente (ignorar este error, o enviar Warning, para garantizar idempotencia en la comunicación).

4. **Integración HTTP (`admin.py`)**
   - Agregar el endpoint al Blueprint `admin_bp`.
   - Ligar validación del path y de Pydantic con retorno de estado JSON unificado.

## Notas Adicionales
- Se deberá evitar path traversal (asegurarse de hacer `secure_filename()` o `.replace("../", "")` sobre el filename).
- Si el documento no existe en Weaviate ni en Disco, el endpoint DEBE devolver `200 OK` (borrado exitoso por indemnidad) para prevenir que la API Java quede atascada en un estado "intentando borrar".
