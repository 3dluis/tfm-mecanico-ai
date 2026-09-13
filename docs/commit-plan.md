# Plan de commits

Estado: **propuesta, pendiente de aprobación del autor**. Nada de lo que sigue se ha ejecutado.
Contexto y evidencia en `docs/git-history-audit.md`.

## Principio

Los 170 commits existentes **son** la historia real del laboratorio y se conservan tal cual
(salvo, si se aprueba, la retirada de dos trailers automáticos en 69 de ellos). No se crean
commits retroactivos: no hay evidencia de trabajo sin confirmar anterior a hoy, y el working
tree estaba limpio al empezar. Lo único que se confirma como nuevo es (a) la documentación
producida por esta preparación para el tribunal y (b) limpiezas pequeñas y justificadas.

Cada commit: una sola intención, staging selectivo (`git add <ficheros>`), revisión con
`git diff --cached` antes de confirmar, mensaje `<tipo>(<ámbito>): <acción>` en español, sin
trailers de herramientas.

## Bloque 1 — Documentación para el tribunal (ficheros nuevos, ya redactados como borrador)

| # | Mensaje propuesto | Ficheros | Nota |
|--:|---|---|---|
| 01 | `docs(git): auditar el historial y planificar su limpieza` | `docs/git-history-audit.md`, `docs/commit-plan.md`, `docs/git-history-report.md` | Solo documentación. `git-history-report.md` se completa en un commit posterior tras la ejecución |
| 02 | `docs(experiments): índice de experimentos con estado y evidencia` | `docs/experiment-index.md` | Identificadores E-n existentes como clave; alias por familia solo como referencia cruzada |
| 03 | `docs(tfm): matriz de trazabilidad pregunta → experimento → evidencia → sección` | `docs/tfm-traceability.md` | Se apoya en las matrices ya versionadas (`research/traceability-matrix.md`, `docs/matriz_validacion_pi.md`) sin sustituirlas |
| 04 | `docs(reproducibility): entorno verificado, versiones fijadas, semillas y comandos` | `docs/reproducibility.md` | Complementa `research/reproducibility.md` (que se conserva) con las versiones de `uv.lock` y la ruta mínima para el tribunal |
| 05 | `docs: README y guía de revisión para el tribunal` | `README.md` (reemplaza al actual, tras aprobación del borrador `docs/drafts/README.draft.md`), `JURY_GUIDE.md` (desde `docs/drafts/JURY_GUIDE.draft.md`) | **Solo tras aprobación explícita del autor.** El README actual quedó en «Fase E1 cerrada» (1-09) y ya no describe el estado del laboratorio |

## Bloque 2 — Limpiezas pequeñas y justificables (cada una es opcional y se decide por separado)

| # | Mensaje propuesto | Cambio exacto | Justificación | Riesgo |
|--:|---|---|---|---|
| 06 | `chore(ide): dejar de versionar la configuración del IDE` | `git rm --cached -r .idea/` (6 ficheros). No se borra del disco | `.gitignore:15` ya excluye `.idea/`; los ficheros entraron antes de la regla. Configuración personal del editor, sin valor para el tribunal | Ninguno |
| 07 | `docs(revision): escribir de forma neutra las rutas al directorio de skills` | 4 líneas en `docs/tfm/cambio_pi_eliminacion_datos_reales.md:97`, `docs/audits/first_submission/FIRST_SUBMISSION_DIAGNOSTIC.md:15`, `tutor-reports/TUTOR-REPORT-20260903.md:8,287,298`: `TFM/.claude/skills/...` → «directorio de skills de revisión, fuera del repositorio» | Mismo criterio que aplicó el commit `af008f9` («rutas del entorno de trabajo escritas de forma neutra»). No se retira la mención a los skills ni su función | Ninguno; son informes, no registros experimentales |
| 08 | `chore(notebooks): retirar rutas locales de dos salidas guardadas` | `notebooks/00_environment_check.ipynb` (celda con `/Users/ldiaz/...`), `notebooks/08_rag_corpus.ipynb` (aviso de tqdm con ruta a `.venv`) | Rutas de la máquina del autor en outputs guardados. Se sustituye la ruta por `<repo>`; no se reejecuta nada | Bajo. Alternativa: dejarlas, son inocuas |
| 09 | `docs(results): sustituir el marcador obsoleto de resultados por una remisión al índice` | `results/RESULTADOS_TFM.md` dice «Estado: sin resultados… No se ha entrenado ningún modelo» (`:5-6`) frente a 23 registros en `experiments/` | Es un marcador del 1-09 que hoy induce a error al tribunal. Se reemplaza por dos líneas que remiten a `docs/experiment-index.md` y `experiments/` | Ninguno: no contiene cifras |
| 10 | `chore(config): corregir la plantilla de entorno` | `.env.example`: `EMBEDDING_DIM=768` → `384` (dimensión real: `migrations/versions/0003_embeddings.py`, `rag/embeddings.py:186-190`); retirar o marcar como no leídas `EMBEDDING_PROVIDER`, `EMBEDDING_MODEL`, `OLLAMA_BASE_URL` (ninguna se lee en `src/` ni `scripts/`) | Un revisor que siga la plantilla configuraría una dimensión incompatible con la migración | Bajo. Decidir si retirar las variables o solo comentarlas |
| 11 | `fix(config): alinear el tipo de proveedor LLM con los proveedores implementados` | `src/mecanico_ia_exp/config/settings.py:16`: `Literal["openai_compatible","anthropic","ollama","echo"]` frente a `get_llm()` (`llm/provider.py:270-286`) que implementa `echo`, `ollama`, `transformers`, `transformers-lora[@dir]` y **no** `openai_compatible` ni `anthropic`. Actualizar el `Literal` y `docs/setup/llm-providers.md` para que documenten lo que existe | Coherencia entre configuración, código y documentación. Es el único cambio de código propuesto | Bajo. `tests/test_settings.py` puede necesitar ajuste **solo si** comprueba los literales; se revisará antes, nunca se cambia un test para forzar verde |
| 12 | `chore(repo): mover el informe del tutor junto al resto de auditorías` | `git mv tutor-reports/TUTOR-REPORT-20260903.md docs/audits/tutor_reports/` y actualizar las 5 remisiones (`docs/tfm/revision/00_baseline.md`, `04_evidence_findings.md`, …) | Un directorio de nivel raíz con un solo fichero cuyo lugar natural es `docs/audits/` | Decisión del autor; ver auditoría §5.3 |

**No se propone** (aunque se detectó): sustituir los 100 `print(` de 14 módulos por `logging`
(refactor transversal, no cosmético pero fuera del alcance «cambios pequeños»); reorganizar
físicamente `figures/`, `tables/`, `results/` bajo `artifacts/` (movimiento masivo; se propone
solo el mapa conceptual en `docs/drafts/estructura-para-jurado.md`); renombrar los
`experiment_id` de los 23 registros JSON a un esquema `EXP-XXX-nnn` (rompería la
correspondencia con la memoria y con los registros congelados); tocar los cuadernos sin
outputs (`02`, `13`, `14`, `TFM_EXPERIMENTO_COMPLETO`), que documentan fases no ejecutadas.

## Bloque 3 — Historial existente (opción A de la auditoría, §5.3)

| # | Paso | Detalle |
|--:|---|---|
| 13 | Conservar el backup como rama de archivo permanente | `backup/pre-history-cleanup-20260913-1815` se mantiene con ese nombre, se publica junto a `main` y mantiene vivos los 15 SHA citados en registros (decisión del autor, 13-09-2026) |
| 14 | Reescritura de mensajes | `uvx --from git-filter-repo git-filter-repo --force --refs main --message-callback '<quitar las dos líneas de trailer y la línea en blanco previa>'`. Solo `main`; la rama de archivo no se toca |
| 15 | Comprobaciones | `git diff archive/history-before-trailer-cleanup main` vacío (mismos árboles); `git log --format=%B main \| grep -c -E 'Co-Authored-By\|Claude-Session'` = 0; `git rev-list --count main` = 170 + commits del bloque 1–2; autor y fechas iguales commit a commit (`git log --format='%an %ai %ci'` comparado entre ambas ramas) |
| 16 | Restaurar el remote que filter-repo elimina | `git remote add origin https://github.com/3dluis/-mecanico-ai-exp.git` |
| 17 | `docs(git): informe final de la limpieza del historial` | Completar `docs/git-history-report.md` con el mapa `SHA anterior → SHA nuevo` (99 filas), los SHA de los commits nuevos, la validación y el rollback |
| — | **Sin push.** Ni normal ni forzado, hasta orden explícita del autor | El remoto está vacío, así que no hay clones ajenos que invalidar |

Orden recomendado: bloque 1 y 2 **antes** de la reescritura (así el mapa final los incluye y
la reescritura se hace una sola vez), o bien la reescritura primero y los commits nuevos
después (el mapa tendría exactamente 99 filas). Ambas son válidas; la segunda es más simple
de auditar.

## Fase 8 — Validación prevista

Comandos definidos por el proyecto (`docs/EXPERIMENTO_PASO_A_PASO.md:452`,
`docs/setup/macos-local.md:80-83`), en este orden, antes y después de los commits:

```
uv sync --all-extras
uv run ruff check .
uv run ruff format --check src tests
uv run mypy src
uv run pytest
```

Se registrará comando, resultado, aprobados, fallidos y omitidos. Los tests marcados `db` y
`llm` pueden omitirse si el entorno no tiene PostgreSQL o el modelo local; se dirá cuáles.
