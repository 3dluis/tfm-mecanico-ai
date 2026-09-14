# Git History Report

Informe final de la preparación del repositorio para el tribunal (13 y 14 de septiembre de
2026). Complementa `docs/git-history-audit.md` (auditoría previa), `docs/commit-plan.md` (plan)
y `docs/git-sha-mapping.md` (mapa completo de SHA).

## Estado inicial

| | |
|---|---|
| HEAD original | `3b001d4c210a696efb88fe73bfa54829d8065926` («Introduccion: anunciar el vacio, que solo vivia en el capitulo 3», 13-09-2026 17:35 -0400) |
| Branch | `main`, 170 commits lineales, un solo autor |
| Working tree | limpio; sin untracked, sin stash |
| Remote | `origin` = `https://github.com/3dluis/-mecanico-ai-exp.git`, vacío (nunca se ha hecho push) |
| Tags | ninguno |

## Backup

Referencia de recuperación: rama **`backup/pre-history-cleanup-20260913-1815`** → `3b001d4`.
Creada antes de cualquier otra operación y **conservada de forma permanente** como rama de
archivo del historial original, por decisión del autor. Al publicar, se publica junto a `main`.

## Cambios realizados

1. **Normalización del historial (opción A).** `git filter-repo --force --refs main
   --message-callback` retiró de 69 mensajes las dos líneas `Co-Authored-By: Claude Opus 5 (1M
   context) <noreply@anthropic.com>` y `Claude-Session: …`. Verificado commit a commit contra la
   rama de archivo: autor, correo, fecha de autor, committer, fecha de commit y árbol idénticos
   en los 170; mensaje idéntico salvo esas dos líneas, y salvo dos referencias internas a otros
   commits que `filter-repo` actualizó al SHA nuevo (`docs/git-sha-mapping.md`). Ningún fichero
   se editó para sustituir SHA antiguos.
2. **Limpiezas aprobadas** (bloque 2 del plan): `.idea/` fuera del índice; rutas
   `TFM/.claude/skills/…` escritas de forma neutra; rutas locales fuera de dos cuadernos;
   `.env.example` y el tipo de proveedores LLM alineados con la implementación;
   `results/RESULTADOS_TFM.md` marcado OBSOLETO conservando su texto; informe del tutor
   trasladado a `docs/audits/tutor_reports/`; `research/available-skills.md` retirado (queda en
   el historial).
3. **RERUN-A ejecutado** sin alterar el pre-registro: pasos B, D, F, G (13-09) e I (14-09).
   Registros canónicos en `experiments/`; los anteriores congelados en
   `experiments/pre_mixed_embedding_fix/` (incluidas copias nuevas de E13 y E13b). Resultado:
   decisiones idénticas (15/17), conjuntos recuperados distintos en 10/17 casos, líneas base
   invariantes reproducidas, E13 LoRA v2 17/17 sobre el conjunto ampliado. Interpretación fijada
   de antemano: sin efecto detectable con este instrumento (`docs/experiments/resultado-rerun-a.md`).
4. **Siete discrepancias documentales resueltas** con notas fechadas, sin armonizar cifras
   (`docs/experiment-index.md` §Discrepancias). La más relevante: el «9/9» de respeto al
   veredicto del modelo base y LoRA v1 era 7 de 7 evaluables; corregido en
   `docs/experiments/E13_agente_slm.md` y `docs/memoria/cap5_resultados.md`.
5. **Documentación para el tribunal**: `README.md`, `JURY_GUIDE.md`, `docs/experiment-index.md`,
   `docs/tfm-traceability.md`, `docs/reproducibility.md`, `docs/limitations.md`,
   `docs/git-sha-mapping.md`, `artifacts/` (12 figuras, 19 tablas, 1 métrica, con procedencia),
   `data/samples/` + `data/README.md`, `scripts/reproduce_baseline.sh`,
   `scripts/reproduce_main_results.sh`.

## Commits nuevos

Todos posteriores a la normalización, sin trailers de herramientas, en orden cronológico. El
commit de este informe se añade al final.

| SHA | Tipo | Descripción |
|-----|------|-------------|
| `1d21a23` | chore(ide) | chore(ide): dejar de versionar la configuración del IDE |
| `2fff828` | docs(revision) | docs(revision): escribir de forma neutra las rutas al directorio de skills |
| `5cef663` | docs | docs: actualizar las remisiones al informe del tutor tras su traslado |
| `8939900` | docs(research) | docs(research): retirar el inventario de herramientas de asistencia del repositorio |
| `b3b1544` | chore(notebooks) | chore(notebooks): retirar rutas locales de dos salidas guardadas |
| `d4cf640` | fix(config) | fix(config): documentar solo los proveedores LLM implementados |
| `aca345c` | docs(results) | docs(results): marcar como obsoleto el marcador de resultados del 1-09-2026 |
| `0cfaee0` | docs(git) | docs(git): auditar el historial, planificar la limpieza y registrar el mapa de SHA |
| `832a713` | docs(experiments) | docs(experiments): índice de experimentos con estado, evidencia y resultados negativos |
| `4ced1cf` | docs(tfm) | docs(tfm): matriz de trazabilidad pregunta → objetivo → experimento → evidencia → sección |
| `b597559` | docs(reproducibility) | docs(reproducibility): entorno verificado, versiones fijadas, semillas, comandos y riesgos |
| `9c85bec` | data(experiments) | data(experiments): congelar los registros de E13 y E13b previos a la corrección del espacio de embeddings |
| `e93dda9` | chore(gitignore) | chore(gitignore): excluir el contenido de .idea tras la reinclusión de directorios |
| `e8055aa` | eval(rerun-a) | eval(rerun-a): pasos B, D, F y G de la reejecución canónica pre-registrada |
| `487e98a` | docs(limitations) | docs(limitations): resumen para el tribunal del registro de limitaciones |
| `3cc8057` | eval(rerun-a) | eval(rerun-a): paso I (agente E13) y resultado de la reejecución canónica |
| `95b80b1` | docs(experiments) | docs(experiments): resolver las siete discrepancias documentales con notas fechadas |
| `6361205` | eval(artifacts) | eval(artifacts): versionar figuras, tablas y métricas usadas en la memoria, con procedencia |
| `94d46c7` | data(samples) | data(samples): muestra sintética redistribuible y README de datos |
| `0533abf` | build(scripts) | build(scripts): envoltorios de reproducción del bloque de telemetría y del bloque documental |
| `e002094` | docs | docs: README de investigación y guía de revisión para el tribunal |
| `ad30142` | docs | docs: actualizar índice, trazabilidad, reproducibilidad y limitaciones tras RERUN-A |

## Commits históricos modificados

99 commits recibieron SHA nuevo: 69 por eliminación de los trailers y 30 por descender de un
commit reescrito. Los 71 primeros (`3a2ce39` … `d0866ce`) no cambiaron. Tabla completa (copia
de `docs/git-sha-mapping.md`):

| SHA anterior | SHA nuevo | Motivo |
|--------------|-----------|--------|
| `a34bab25372f2467c36b4337f59c28407f216037` | `64288f97cc4cf1c07a4eb783dcc633705b43f81c` | trailers eliminados |
| `10ed541e2a122acb5d9ee099875bc698b85efd57` | `500dfbf623afa87aae1bc7c92e21e51e8e9060a0` | trailers eliminados |
| `478ebe09c9e79ee53217df41e16ba21b88a7cec5` | `ac92a030efe0a555185c3bfb4136f303cd005baa` | trailers eliminados |
| `1a58376f5a94ba4f763a7f84b54b6b7413456fea` | `7a91b473f753294f6ee17868484a5c5f05b309a9` | trailers eliminados |
| `f290263bd08d01437e4949453b315da748d5d4ea` | `b73241d6044272969c54137a1a4987048a090ab5` | trailers eliminados |
| `43f56dc7c944634bf4a83e53f3b20977b0bda39e` | `7f8ddc1001ff698abbe642e8a2a643d3760ad051` | trailers eliminados |
| `3b02cf88d7162d3773daa86d9c8f98da0cb97817` | `d0498e8d45f745ad8b549fd7de8f4e88d5ef5f4d` | trailers eliminados |
| `f34f625a898bfb9d3323d8bb7ab853f6e16db48c` | `e872538d3028aefa91991d535dda6a901147b441` | trailers eliminados |
| `c502f9a9a10efb5360ffa201e738b036450aaca0` | `edcad616861614e4810c3ff53ba57f45b61581a0` | trailers eliminados |
| `465563a16be51340258ac4aa088e3d694d469183` | `84d83ee2beda0822153dc4b2f0398baf1df7efac` | trailers eliminados |
| `9139dcdca04386f60cfe600f369b55b29d416ad3` | `02afef43c218119d278f6ce67f541b5d7ad628f2` | trailers eliminados |
| `4c17732055f96fe8322a518380446d23545634e9` | `bef8d0e34d1a26938c4cedfdc2ab661c3f848262` | trailers eliminados |
| `0292f72ea953d701d997b2cc3359de42ae21796b` | `8f61a67da7dcb4ce243a0ed6d3c86a8d25dc9cff` | trailers eliminados |
| `3964961acf089667490c657886bae0470edeb357` | `fed38d37c3823a648073af56d240bd1185f2b5a1` | trailers eliminados |
| `7a3ef513b8398894cfda7503b0303b02b4e1540a` | `0f9f3e6a89888a47e3b083f4caee2ffab7d2c81d` | trailers eliminados |
| `54071a212857cc55dbf385c820581f949c9f9e3d` | `a5cef8ae7bfec45f72070d6e035655726d2b15d3` | trailers eliminados |
| `c6a95be836832a9525c29f2b4d7cae961f198932` | `693df7fe1119911d0b7d1b8f750e3871ce10ec99` | trailers eliminados |
| `43e2e873e4dc8bff30f256d5c2ae1058b13b11f3` | `75607861704472e8af88d81a7bb92f7c5aa57c7c` | trailers eliminados |
| `6b5b92dbfff252b05f5236a683bbbb028fef2ca9` | `a0a0fe39f0a6919e88fc1765c75a8e20df50e676` | trailers eliminados |
| `3845c07b23a4366f3b458b6a77aff3d2e8ee2ae0` | `19adc297cf10802e792a5ad522eceeae276165f1` | trailers eliminados |
| `b79dfa78409cd3bf95fd12bb8888653d64b79ee3` | `5dc1450a6d1e283871a8a8752f68052b55a0623e` | trailers eliminados |
| `7ff9949d75997baeec0ebdf92ecb38072b6dd466` | `d2c7f552e689e1f2db40637bd4401b76229deeb5` | trailers eliminados |
| `df003f0dadc3db5f381e057307e7016f3a6acbfa` | `2b29b92201236cbaf8d146d6d7da8d3c148266f6` | trailers eliminados |
| `57b6c936ac0f0add17ad3a470869f45fa0e5b0ad` | `ac7eb62f65f77d4710410e411b579ce39b02151a` | trailers eliminados |
| `aed6fe26196794d1f9807c123cf8d0b38ecbf02f` | `cd38cafbe57a6e44919ef5b437d10d62cd557250` | trailers eliminados |
| `7d52627f622209a1fbf09028fa6867863e5fa078` | `2fce938c3a33332f5125fa0106abd8b1747e443e` | trailers eliminados |
| `9c388d9713df8afee329e9075bfdc40df825644a` | `4ee46dee6f8e72dbe196b94bd884652be40985cf` | descendiente de un commit reescrito |
| `1d6177206e46e484e2052b9604d12cb53fdece88` | `ceb38404cd7dd56f2aa1511496588286d78efa8b` | descendiente de un commit reescrito |
| `191bd84c461c7cb05a2f5143b6b12adf330b7e69` | `bf6e76b757eff9608420ca64f4b8110c6b00b8e8` | descendiente de un commit reescrito |
| `a80f14a148cdde9d2f752c71eebfe1bbeec42b83` | `10579c9dd8fe4ee4bbf586ebe11c87cc8bb06cfe` | descendiente de un commit reescrito |
| `77281a9cc5dbaa7399d7c81daeab49cc57806371` | `0dcdfd5af4532027e3fe7585a9470f0441348c08` | descendiente de un commit reescrito |
| `2550bc1b62a5e16cbb4d26145570e46ea2831136` | `f5cb5dd9f42b683d7a008c764bfd03ac711b0290` | descendiente de un commit reescrito |
| `e2151ca178d2edf7bb2e93f149dceadbfd83660c` | `c2ceec06f619383ba5628428fb6ba98fddff8922` | descendiente de un commit reescrito |
| `701f1c4377505dd61d56ae5e8baeb7dd4b561cae` | `2ff078d5f8eea704246fd47567648a67166d91b5` | descendiente de un commit reescrito |
| `d0866cebfdf5b6900807f9ff67d0645bfc24d506` | `c2e4123e31da01ea0037c86a567abf0a46938662` | descendiente de un commit reescrito |
| `6b6534504cdf3575a5c3724a450c4ded4b350b26` | `dac3399b7b3a86b402ade9af1741186d18468b73` | descendiente de un commit reescrito |
| `dc1296363d1b3b3775171491a8145cdafdd0cbcf` | `42f3d390b728773fc560eaa7be278201f158c066` | descendiente de un commit reescrito |
| `f210021a0c40f2150e0219af39c856f4f8da954e` | `32948a972bd19fa607b714c129a18596c841f2b7` | descendiente de un commit reescrito |
| `94a08e4d72ce9735f18ffb19c97360e78455de8c` | `476132fdee821ab26d8cec07f9ef1902bf1b9f09` | descendiente de un commit reescrito |
| `422350811147cf455cd149e86082f1d46b60b882` | `9d66b4f43d4fb9e3670618fba8739909b23ca82a` | descendiente de un commit reescrito |
| `4a87700fca417af25621ba18e08eb1f1cf0e1662` | `4343ccd00bd9b8ab8086395a9056a7e2a0c2893b` | descendiente de un commit reescrito |
| `ae9dfc39fc171fa28f38e2b348ff4bf5814ed83d` | `38cfb47e9e70fcb2c5658891edd456bb94d38ab5` | descendiente de un commit reescrito |
| `a0cc296acbbe5f3a5dd878d9e38aa24764bb6d9c` | `0eaba28aed0d57bc9c66cd15365d98eaf6796630` | descendiente de un commit reescrito |
| `0c519fe9d80affe90dfbc2077e365723c8f00145` | `0ad500ca76b0a26f639003d0cd200b020cbc9906` | descendiente de un commit reescrito |
| `2903ecbf7cc8c20c529773967ba43227b36e945a` | `331d438685c329c98ca6980f1c7bf6ff4f59470b` | descendiente de un commit reescrito |
| `5e87ae866837ec61f71f73ad5888933fb7448c45` | `f4d6a4f2950e76068a7edf217e6a5bf97b9b9423` | descendiente de un commit reescrito |
| `76e1046619b5afb25bec671655e1f885201cea4c` | `91c2826751e1b43d7aed1bcc8451a1a9c984cfca` | descendiente de un commit reescrito |
| `0f5e3b0e93ef54c7523323cf163d7f41ebd768f0` | `67755f03a5dbbab1b608822e63e2e79f5ced184b` | descendiente de un commit reescrito |
| `b5ca3b32754bd969eb90dbcd746caaae77c1baac` | `ab13b28f4a119ffa51ab3e374e83c2d6dd06ead2` | descendiente de un commit reescrito |
| `32c6a7d6c9e059319d6c6da541acf121a9cd11bd` | `100ce676c2ce6389f3be69a32f537540b20782b6` | descendiente de un commit reescrito |
| `b0e13e2a09bd78219e61208b52e663acdedff923` | `a03e499172a596fa66d583cb334e687d9f629529` | descendiente de un commit reescrito |
| `0400ed2e522257e2f61c09db25a6403e77b2d033` | `7fd33403373f97fecdc163ecbd2b1d337955d51c` | descendiente de un commit reescrito |
| `835a317f28873a47305993b17c569e7f804a83b6` | `05b6314d416e509e831722d576af58443961c2ed` | descendiente de un commit reescrito |
| `5a611943ccaabc629a07c778b9fc70f2d54d1b63` | `2b0e7881cf5908ede1158a1ca1f187b5723f886b` | descendiente de un commit reescrito |
| `615ebeb37662d5c9c2d1d4299a165b66431f1c98` | `7d492db6033b41bdf00bb4c55eff600afccd34e0` | descendiente de un commit reescrito |
| `4a0c6d81557aba97569c7d8cfb6a62e331c50999` | `169300a2e85660666b2e888800cd11febe20959e` | descendiente de un commit reescrito |
| `d0fa41279c09c9ea30029110bd4231368aa309b3` | `f919fe734ebdbf9f21e7a87d4ebcd0c4cbdd5861` | trailers eliminados |
| `cc7eefd0c2c3f4d364f1c4d8106afce3c7d658e5` | `7be182e11368930fef68159b2c7846a737a18f12` | trailers eliminados |
| `456e9a011a193655bb528051dad6cd6bb92b901b` | `3afab6e1fb12fc6a4ce266714444f2f0107519f1` | trailers eliminados |
| `1d368e07a4790e7c053cff93178fe76404f97ebf` | `fa8c09fc6a383528ee6bbe434c595293e29e248b` | trailers eliminados |
| `32e7c991201eda17a2c421552bd6476c073cf5de` | `4c0da2051ae18df4160d48cff7bd114913ca052e` | trailers eliminados |
| `038c20c1b4b05f0a504d2ae4cbd900e577a6c44c` | `b5fc6e2f9b9e98b9fd737bbc7ad3e481271b2fb2` | trailers eliminados |
| `6f0e21d0a7c201e4da3bc47bb89a630118b9e4e0` | `ad84a434fe27ed25b0d5bf5da9a655f0f2c9d101` | trailers eliminados |
| `12b665ad8abf2ea2967692bb4f5d89f4eeff43e2` | `b9b66cf4eaaa789f9d5954905339b4a3d2dc543e` | trailers eliminados |
| `d7bdaef93cfbee9ad75f7513a420edeb91fe4f0f` | `e147c317c7636c9f9e527276e1d813ac68a6d8dc` | trailers eliminados |
| `6515210bc5b2810256d4326f3192661713456785` | `2fe91f608005867d02a6e908ae603521afd26f6d` | trailers eliminados |
| `d3ddde8ee68930276df65f09f7438a23e0b4040c` | `419766b41c0e5f41bae7aa3887f2b97a456b1469` | trailers eliminados |
| `c39536880a8ff3b2b49d69b17d3ed31e51165b76` | `1724c9f73f24f8a020d38308546789bc36c499f2` | trailers eliminados |
| `43e1151eea39493a8cb83f355e495ee2390229e8` | `24219e9843cadd527b12c22edae2f8738b8dc39e` | trailers eliminados |
| `521123c3ae527f410fe879e7f302766fa0f3b124` | `74df3a2ee0ebc1263de5fb4e430c998d71409ec2` | trailers eliminados |
| `6f7ec0fbc3aa3fa2a4b3627d2273df9d6a1f8be3` | `ab8b66d122905469a1037686e4be066b4a2b8722` | trailers eliminados |
| `c617d14497bbd12899538e8116a7d2ee449d7d31` | `334859335fa6257556c63607d5c593c261fd46d8` | trailers eliminados |
| `5e7f95d02461761977f9ca022e604ec620d3f743` | `606779287adb695a1a44c0fb9767830efe7ef3a1` | trailers eliminados |
| `66198d98ebcb835892d1852aeb36de43c15e9107` | `57f0a6f90e4dc3f3e8a3dadb6bf5e5981220d32d` | trailers eliminados |
| `3d7ab90362dad2ea989932eec46011f1e7e27374` | `7c134db2920345980721d26fbcea87d278ca2c8f` | trailers eliminados |
| `e7aeb14651095911d775085f6049f34e38fe3f76` | `5de25ac650cb662ed17ba22a08fcc5fd18ab8d8f` | trailers eliminados |
| `95d4e7178568df8d500ad793a258091b39869c79` | `f92186efb2ab461e60b78346e207e12601a26666` | trailers eliminados |
| `6d95a25304a3b16b1ddacaa90891d884b1083920` | `6db791a03d041d165ec203f52347537dbab8160d` | trailers eliminados |
| `e4dfdf16b61efe5a3c652066572fa1184f813604` | `4627d5441dc6e76639325e7076075963d6f3800c` | trailers eliminados |
| `4cac4aefd081fbd2cb5dc1c04906c6a6c77fb70e` | `dd2440408c194b3c97573dc9a8a924ed7ae10bf4` | trailers eliminados |
| `cd52cdb9bd15c791995eeac518c96b52e3c0b6fe` | `83787e3f6fe559d92c1be2918d4c197f0fca4d81` | trailers eliminados |
| `37f1294d52d7e71f2c620b107ca4ed1b365079a3` | `a23cd5ab1eed4469c280120867901f8fd2ec4b1b` | trailers eliminados |
| `0b0864b38aaa79f67cfe1ffb18723cf0b36a7d60` | `768f229fcb55cfe2ac21ff3312fe3e68e120832b` | trailers eliminados |
| `8be7fc2cd67d616299a6e0a0762ab9fd40a764f6` | `8381ec66d6af051b5389e04db79d9bdb8dbb5cc2` | trailers eliminados |
| `4e9e4a6690941def4706700e31ce52142758e700` | `c75795f8a66b876ef241e8ac652b1ae88429b04f` | trailers eliminados |
| `daddffd9171dc9a88aa42406f5b54f2ff21f1a0e` | `d7f83077b6d49037818b73a80b038c928974c000` | trailers eliminados |
| `4a6358bbb907d7ef6c5e4203f71e79a96e7badf7` | `00ccb267e961e6703cfc57a033d8cfb9375c0ecb` | trailers eliminados |
| `9bb8c6cace025346ed59ef68bf461e532811aa6d` | `d9978bd47847af5c35ee2662a9654111ab6dd666` | trailers eliminados |
| `23208b0e8aaf8251d9b641a504356522d11b11cb` | `4a43ced4345c4953017287df4d803368e4903e82` | trailers eliminados |
| `e5242d00628b75b9d113592b02a794421ea60611` | `47f3beed0059f7f8026fa5d31244d1db76ef5211` | trailers eliminados |
| `822026153a6b5235a835e1a0b35c16806250d4ac` | `8d85d2705c8313a81826530e6635be6e573afb75` | trailers eliminados |
| `fad82f6e45f00de5deac1194780bdda8f8ecfb98` | `781f6e718472ece7d5667d0cd0690984d901edd0` | trailers eliminados |
| `03ab04fca6e289b6a2f5420cc2d3848866f663eb` | `2f8bc78dde5ca3cabcfe2c75f496f40e7435f6bc` | trailers eliminados |
| `0505a2b44fefb154d06b916250df199b1b3829e6` | `a21d7124fc79dba005cd242c959bc7e3478f4bd6` | trailers eliminados |
| `4cb4de5d27818f92b94929e5f791cab489dc1193` | `35a7b6fec34dfcae38163db6cf86915d7ac43fe2` | trailers eliminados |
| `089d48f7ca0c6c30859845766e15e79b22c7fe01` | `dc6345baac24e4fb9eb9aa696d6a8dd1284a0c73` | trailers eliminados |
| `636cf150b12eef0defddf8212ece819d640631ad` | `a2d390d4725794a6064b6bb6329a62fbc56cd76c` | trailers eliminados |
| `167e17e4202b5a9033621ed4a3eeb583ae46d794` | `575991c5f8f01734629080d55e47d97836a41f0f` | trailers eliminados |
| `3b001d4c210a696efb88fe73bfa54829d8065926` | `3bffe2c4aed88b1a8109b0c8d6078fe0b975beeb` | trailers eliminados |

## Metadatos eliminados

Exactamente 69 líneas `Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>` y
69 líneas `Claude-Session: https://claude.ai/code/session_…` (26 con
`session_01BxABErdF9ssaDxuxRUb1Dk`, del 4-09; 43 con `session_01J6War2vaULRmaHQZYtffHr`, del
10 al 13-09), más la línea en blanco que las precedía. Comprobación: `git log --format=%B main |
grep -c -E '^(Co-Authored-By|Claude-Session)'` devuelve 0.

Ningún comentario de código: no existía ninguno que eliminar (`docs/git-history-audit.md` §3.2).
En documentos: cuatro rutas `TFM/.claude/skills/…` (tres ficheros) sustituidas por una
descripción neutra; el inventario `research/available-skills.md` retirado del árbol.

## Cambios deliberadamente conservados

- `LLMProviderName` y `docs/setup/llm-providers.md` describen los proveedores de modelo de
  lenguaje del sistema (ahora solo los implementados: `echo`, `ollama`, `transformers`,
  `transformers-lora`). El rol `assistant` del protocolo de chat en `llm/agent.py` y
  `llm/training_data.py`. El título de la referencia REF-107.
- Los informes de revisión y auditoría (`docs/tfm/revision/`, `docs/audits/`, incluido el del
  tutor) declaran qué skills de revisión asistida los produjeron; son registro del proceso y
  los commits posteriores se remiten a ellos.
- Todos los registros JSON anteriores a la corrección del 4-09 (`NON-CANONICAL`), los
  resultados negativos, las versiones v1 y v2 del verificador, la ejecución adversa por índice
  y el `results/RESULTADOS_TFM.md` original.
- Los 15 SHA antiguos citados en registros congelados, manifiestos y documentos de método:
  intactos, resolubles con el mapa o contra la rama de archivo.

## Validación

Ejecutada el 14-09-2026 sobre el árbol final, con los comandos que define el proyecto:

| Comando | Resultado |
|---|---|
| `uv sync --frozen --all-extras` | Audited 176 packages (lock en sincronía) |
| `uv run ruff check .` | All checks passed |
| `uv run ruff format --check src tests` | 94 files already formatted |
| `uv run mypy src` | Success: no issues found in 69 source files |
| `uv run pytest` | **400 passed, 0 failed, 0 skipped, 0 warnings** (los tests marcados `db` corrieron contra el PostgreSQL local) |
| `uv run mecanico-exp doctor` | Python 3.11.14 · Darwin 25.6.0 arm64 · torch 2.13.0 mps · PostgreSQL 14.15 · pgvector 0.8.0 |
| `bash scripts/reproduce_baseline.sh` | E2 → E5 → E6 → E15b sobre `synthetic_v2`: **E6 reproducido bit a bit** (métricas, matriz por clase, calibración y configuración idénticas al registro versionado); E15b idéntico salvo cabecera (`commit`, `executed_at`, `dirty`). Los registros versionados se restauraron; la reproducción no se confirmó como cambio |
| Flujo de demostración con `data/samples/` | `preprocess` + `train-baseline` sobre `synthetic_sample` completan sin error (49 ventanas de validación; cifras no comparables, como declara `data/README.md`) |
| RERUN-A (`scripts/reproduce_main_results.sh` equivalente) | Ejecutado paso a paso; resultados en `docs/experiments/resultado-rerun-a.md` |

Ningún test se modificó. La misma suite daba 400 aprobados antes de empezar.

## Estado final

`git status --short`:

```
(vacío: working tree limpio)
```

`git log --graph --decorate --oneline` (primeros 45; el resto sigue lineal hasta `3a2ce39`):

```
* ad30142 (HEAD -> main) docs: actualizar índice, trazabilidad, reproducibilidad y limitaciones tras RERUN-A
* e002094 docs: README de investigación y guía de revisión para el tribunal
* 0533abf build(scripts): envoltorios de reproducción del bloque de telemetría y del bloque documental
* 94d46c7 data(samples): muestra sintética redistribuible y README de datos
* 6361205 eval(artifacts): versionar figuras, tablas y métricas usadas en la memoria, con procedencia
* 95b80b1 docs(experiments): resolver las siete discrepancias documentales con notas fechadas
* 3cc8057 eval(rerun-a): paso I (agente E13) y resultado de la reejecución canónica
* 487e98a docs(limitations): resumen para el tribunal del registro de limitaciones
* e8055aa eval(rerun-a): pasos B, D, F y G de la reejecución canónica pre-registrada
* e93dda9 chore(gitignore): excluir el contenido de .idea tras la reinclusión de directorios
* 9c85bec data(experiments): congelar los registros de E13 y E13b previos a la corrección del espacio de embeddings
* b597559 docs(reproducibility): entorno verificado, versiones fijadas, semillas, comandos y riesgos
* 4ced1cf docs(tfm): matriz de trazabilidad pregunta → objetivo → experimento → evidencia → sección
* 832a713 docs(experiments): índice de experimentos con estado, evidencia y resultados negativos
* 0cfaee0 docs(git): auditar el historial, planificar la limpieza y registrar el mapa de SHA
* aca345c docs(results): marcar como obsoleto el marcador de resultados del 1-09-2026
* d4cf640 fix(config): documentar solo los proveedores LLM implementados
* b3b1544 chore(notebooks): retirar rutas locales de dos salidas guardadas
* 8939900 docs(research): retirar el inventario de herramientas de asistencia del repositorio
* 5cef663 docs: actualizar las remisiones al informe del tutor tras su traslado
* 2fff828 docs(revision): escribir de forma neutra las rutas al directorio de skills
* 1d21a23 chore(ide): dejar de versionar la configuración del IDE
* 3bffe2c Introduccion: anunciar el vacio, que solo vivia en el capitulo 3
* 575991c Registro denso en los dos apartados que quedaban
* a2d390d Retirar las marcas de trabajo del capitulo 4 y documentar las del 5
* dc6345b Cerrar el feedback del tutor tambien fuera de la memoria
* 35a7b6f ADR-004: la pregunta canonica es la acotada, decidido por la direccion
* a21d712 Observaciones del tutor: lo que no depende de la decision sobre la pregunta
* 2f8bc78 Marco teorico: registro denso en todo el capitulo
* 781f6e7 Marco teorico: devolver al proposito y procedimiento su registro denso
* 8d85d27 Fijar el criterio de escritura del TFM
* 47f3bee Marco teorico: moderar el vaiven del proposito y procedimiento
* 4a43ced Marco teorico: aplicar la voz de referencia a todo el capitulo
* d9978bd Fijar la voz de referencia del TFM y aplicarla donde mas se desviaba
* 00ccb26 Marco teorico: reescribir el proposito y procedimiento de la revision
* d7f8307 Separar prospectiva de trabajo pendiente dentro del TFM
* c75795f Conclusiones: ritmo y ultimo conector de apertura
* 8381ec6 Conclusiones provisionales para la primera entrega
* 768f229 Introduccion: deshacer un eco entre parrafos contiguos
* a23cd5a Conclusiones: alineadas con la pregunta, y sin el exceso de forma
* 83787e3 Marco teorico: romper la enumeracion formulaica de las cinco situaciones
* dd24404 Modelo de analisis: analisis, no resultados previstos
* 4627d54 Reproducibilidad: separada del control de calidad, y la huella dice sobre que se calcula
* 6db791a Fases del agente: diseno en el capitulo 4, incidentes en el 5
* f92186e Fase de recuperacion: informacion documental, no evidencia todavia
* 5de25ac Muestra: caracterizacion legible, y las doce senales con su propia tabla
* 7c134db Memoria: un parrafo, una linea
* 57f0a6f Objetivos alcanzan la pregunta, y se disena lo que falta para ejecutarlos
* 6067792 Primera entrega: diagnostico, informe de preparacion y niveles de agregacion
* 3348593 Poblacion y muestra: prosa academica, y el resultado de ventana fuera del metodo
…
```

Ramas: `main` (historial normalizado + commits de preparación) y
`backup/pre-history-cleanup-20260913-1815` (historial original, permanente). Remote `origin`
configurado y vacío: **no se ha hecho push**. Cuando el autor publique, deben subirse ambas
ramas: `git push origin main backup/pre-history-cleanup-20260913-1815`.

## Rollback

Para volver exactamente al estado anterior a toda la intervención:

```
cd mecanico-ia-exp
git checkout main
git reset --hard backup/pre-history-cleanup-20260913-1815      # main vuelve a 3b001d4 con los 69 trailers
git remote -v                                                   # origin sigue configurado; añadir si faltara:
# git remote add origin https://github.com/3dluis/-mecanico-ai-exp.git
```

Efectos: desaparecen de `main` los commits de preparación (documentación, limpiezas,
artefactos, muestra, scripts) y los registros de RERUN-A vuelven a los del 4-09. Los ficheros
generados en disco por RERUN-A (`tables/`, `figures/`, `data/`, `results/rag_ingestion/`) no
están versionados y no se ven afectados; la base de datos tampoco se tocó. Para conservar el
trabajo nuevo y solo recuperar el historial antiguo, crear antes una rama:
`git branch preparacion-tribunal main`.
