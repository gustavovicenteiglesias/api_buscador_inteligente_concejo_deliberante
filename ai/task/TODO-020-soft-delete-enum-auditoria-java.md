# TODO-020 Soft Delete con Enum y Auditoría en Entidad Documento (Java)

## Estado
DONE

## Prioridad
Alta

## Contexto
Para garantizar el rollback distribuido del borrado de documentos (patrón Saga), la entidad `Documento` del backend Spring Boot necesita incorporar:
- Un campo enum `EstadoDocumento` que registre el estado del ciclo de vida del borrado.
- Campos de auditoría para trazabilidad de cuándo y quién inició el borrado.

Esta modificación es prerequisito para que el método `delete()` en `DocumentosService` pueda:
1. Marcar el documento como "ELIMINANDO" ANTES de llamar a la API Python (buscador).
2. Hacer Hard Delete o ROLLBACK a "ACTIVO" segun si Python respondió 200 o falló.

## Archivos a modificar

### Spring Boot (`hcdarecoback`)

- **[NEW]** `app/models/enums/EstadoDocumento.java`
  - Enum con los valores: `ACTIVO`, `ELIMINANDO`, `ELIMINADO`

- **[MODIFY]** `models/Documento.java`
  - Agregar campo: `EstadoDocumento estado` (default: `ACTIVO`)
  - Agregar campo de auditoría: `LocalDateTime fechaInicioEliminacion` (nullable)
  - Agregar campo de auditoría: `LocalDateTime fechaEliminacionConfirmada` (nullable)

- **[MODIFY]** `service/impl/DocumentosServiceImpl.java` — Método `delete(Integer id)`
  - **Paso 1:** `doc.setEstado(EstadoDocumento.ELIMINANDO)` + `doc.setFechaInicioEliminacion(LocalDateTime.now())` → `repo.save(doc)`.
  - **Paso 2:** Llamar a la API Python: `DELETE http://{buscador.url}/api/admin/documento/{filename}`.
  - **Paso 3a (éxito):** `repo.delete(doc)` (Hard Delete definitivo de MySQL).
  - **Paso 3b (error):** `doc.setEstado(EstadoDocumento.ACTIVO)` + limpiar auditoría → `repo.save(doc)`. Relanzar excepción para que el Controller devuelva 500.

- **[NEW]** `config/RestTemplateConfig.java` (si no existe)
  - Definir un `@Bean RestTemplate` con timeout de conexión (ej. 5 segundos) para no bloquear ante caídas de Python.

- **[MODIFY]** `application.properties` (o `.yml`)
  - Agregar variable: `buscador.api.url=http://IP_VPS:9000`

- **[MODIFY]** `repo/DocumentosRepository.java`
  - Agregar query para consultar documentos en estado `ELIMINANDO` (útil para reintentos futuros):
    ```java
    List<Documento> findAllByEstado(EstadoDocumento estado);
    ```

## Secuencia del flujo de rollback

```
DELETE /api/documentos/{id}
  → estado = ELIMINANDO      (MySQL)
  → llama Python DELETE       (HTTP)
     ├── 200 OK → Hard Delete  (MySQL definitivo)
     └── Error  → estado = ACTIVO + limpiar fecha (Rollback MySQL)
```

## Migración de base de datos
Se debe agregar la columna `estado` con valor default `ACTIVO` a la tabla `documentos`.
Si usás Flyway o Liquibase, crear el script de migración correspondiente.
Si usás `ddl-auto: update`, Hibernate lo creará automáticamente (solo para dev).

## Notas Adicionales
- El campo `estado` debe ser parte de los filtros en `DocumentosSpecifications.java` para que el frontend nunca vea documentos en estado `ELIMINANDO` o `ELIMINADO`.
- El frontend no necesita cambios visibles en esta etapa; la exclusión es transparente desde el backend.
- Los documentos que queden varados en estado `ELIMINANDO` (por caídas de red) son candidatos a una futura tarea de reintentos automáticos (cron job o Spring Scheduled).

## Checkpoints (marcar al completar)
- [x] Enum `EstadoDocumento` creado.
- [x] Campos `estado`, `fechaInicioEliminacion`, `fechaEliminacionConfirmada` añadidos en `Documento`.
- [x] `delete` en `DocumentosServiceImpl` implementa estado ELIMINANDO, llamada HTTP y rollback/hard delete.
- [x] `RestTemplate` con timeout configurado.
- [x] Propiedad `buscador.api.url=https://api.buscadorhcd.cfl401areco.edu.ar` añadida.
- [x] `spring.jpa.hibernate.ddl-auto=update` configurado.
- [x] `DocumentosRepository` expone `findAllByEstado`.
- [x] `DocumentosSpecifications` excluye ELIMINANDO/ELIMINADO.
path de proyecto java = C:\Users\Gustavo\OneDrive\Documentos\spring\hcdarecoback
