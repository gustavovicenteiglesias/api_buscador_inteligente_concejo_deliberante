# TODO-021 Soft Delete Persistente en Documento (Java)

## Estado
TODO

## Prioridad
Alta

## Contexto
Actualmente `DocumentosServiceImpl.delete` marca `ELIMINANDO`, llama al buscador Python, y si la llamada es exitosa hace hard delete en MySQL. Se necesita conservar la fila con trazabilidad de borrado (soft delete final), ya que el borrado físico ya ocurre en el buscador y en disco.

## Objetivo
- Mantener el registro en MySQL tras un borrado exitoso dejando `estado = ELIMINADO` y registrando `fechaEliminacionConfirmada`.
- Garantizar que los listados API sigan mostrando solo documentos activos.

## Alcance y archivos a modificar
- `service/impl/DocumentosServiceImpl.java`
  - Paso de éxito: reemplazar `repo.delete(db)` por `db.setEstado(ELIMINADO)` + `db.setFechaEliminacionConfirmada(now)` + `repo.save(db)`.
  - Mantener rollback a `ACTIVO` si falla la llamada al buscador.
- `specs/DocumentosSpecifications.java`
  - Verificar/asegurar que filtra `estado=ACTIVO` para `/api/documentos`.
- (Opcional) `repo/DocumentosRepository.java`
  - Si se requiere, agregar helpers para contar/listar eliminados.
- (Opcional) Endpoint admin futuro para listar `ELIMINADO`/`ELIMINANDO` (fuera de este alcance).

## Checkpoints
- [ ] DELETE deja estado `ELIMINADO` y fecha de confirmación en MySQL (sin hard delete).
- [ ] Falla en llamada externa sigue haciendo rollback a `ACTIVO`.
- [ ] `/api/documentos` sigue retornando solo `ACTIVO`.
- [ ] Logs reflejan transición ACTIVO → ELIMINANDO → ELIMINADO.

## Notas
- No tocar hoy código ya modificado; implementar en próxima sesión.
- Validar con un caso real que también borre en Weaviate y disco (ya funciona).  
