# Mapa de SHA: historial original → historial normalizado

El 13-09-2026 se normalizó el historial de `main` para retirar de 69 mensajes de commit dos
trailers automáticos de la herramienta de desarrollo (`Co-Authored-By: Claude …` y
`Claude-Session: …`). Se usó `git filter-repo --refs main --message-callback`. **No cambió
nada más**: se verificó commit a commit que autor, correo, fecha de autor, committer, fecha de
commit y árbol (contenido) son idénticos, y que el mensaje resultante es el original sin esas
dos líneas. Auditoría y justificación en `docs/git-history-audit.md`.

## Rama de archivo del historial original

El historial completo anterior a la normalización se conserva **de forma permanente** en la rama
`backup/pre-history-cleanup-20260913-1815` (HEAD `3b001d4c210a696efb88fe73bfa54829d8065926`).
Todo SHA citado en un registro experimental, manifiesto o documento anterior a esa fecha sigue
siendo verificable:

```
git show <sha-antiguo>                         # funciona mientras exista la rama de archivo
git diff <sha-antiguo> <sha-nuevo> --stat      # vacío: mismo contenido
git log --oneline backup/pre-history-cleanup-20260913-1815
```

Los registros JSON de `experiments/`, `configs/manifest_rerun_a.json` y los documentos de
método que citan SHA antiguos **no se han editado**: conservan el puntero original, que se
resuelve con esta tabla o directamente contra la rama de archivo.

## Dos mensajes con referencias internas actualizadas

`git filter-repo` reescribe por defecto los SHA de commit que aparecen dentro de los mensajes
para que sigan apuntando al commit correcto. Ocurrió en dos mensajes, y se declara:

| Commit (nuevo) | Texto original | Texto tras la normalización |
|---|---|---|
| `476132f` («Marco teorico: corregir una atribucion que contradecia a sus dos fuentes») | «desde el commit 77281a9» | «desde el commit 0dcdfd5» |
| `35a7b6f` («ADR-004: la pregunta canonica es la acotada…») | «el commit anterior, 0505a2b» | «el commit anterior, a21d712» |

Ambos pares figuran en la tabla siguiente. Fuera de esos dos casos y de los trailers, la
verificación commit a commit no encontró ninguna otra diferencia de mensaje.

## Tabla

Los 71 primeros commits (`3a2ce39` … `d0866ce`) no cambiaron de SHA y no aparecen. A partir de
la posición 72 todos los SHA cambian: 69 por eliminación de trailers y 30 por ser descendientes
de un commit reescrito (Git recalcula el identificador del hijo cuando cambia el padre).

| # | SHA original | SHA nuevo | Motivo |
|--:|---|---|---|
| 72 | `a34bab25372f2467c36b4337f59c28407f216037` | `64288f97cc4cf1c07a4eb783dcc633705b43f81c` | trailers eliminados |
| 73 | `10ed541e2a122acb5d9ee099875bc698b85efd57` | `500dfbf623afa87aae1bc7c92e21e51e8e9060a0` | trailers eliminados |
| 74 | `478ebe09c9e79ee53217df41e16ba21b88a7cec5` | `ac92a030efe0a555185c3bfb4136f303cd005baa` | trailers eliminados |
| 75 | `1a58376f5a94ba4f763a7f84b54b6b7413456fea` | `7a91b473f753294f6ee17868484a5c5f05b309a9` | trailers eliminados |
| 76 | `f290263bd08d01437e4949453b315da748d5d4ea` | `b73241d6044272969c54137a1a4987048a090ab5` | trailers eliminados |
| 77 | `43f56dc7c944634bf4a83e53f3b20977b0bda39e` | `7f8ddc1001ff698abbe642e8a2a643d3760ad051` | trailers eliminados |
| 78 | `3b02cf88d7162d3773daa86d9c8f98da0cb97817` | `d0498e8d45f745ad8b549fd7de8f4e88d5ef5f4d` | trailers eliminados |
| 79 | `f34f625a898bfb9d3323d8bb7ab853f6e16db48c` | `e872538d3028aefa91991d535dda6a901147b441` | trailers eliminados |
| 80 | `c502f9a9a10efb5360ffa201e738b036450aaca0` | `edcad616861614e4810c3ff53ba57f45b61581a0` | trailers eliminados |
| 81 | `465563a16be51340258ac4aa088e3d694d469183` | `84d83ee2beda0822153dc4b2f0398baf1df7efac` | trailers eliminados |
| 82 | `9139dcdca04386f60cfe600f369b55b29d416ad3` | `02afef43c218119d278f6ce67f541b5d7ad628f2` | trailers eliminados |
| 83 | `4c17732055f96fe8322a518380446d23545634e9` | `bef8d0e34d1a26938c4cedfdc2ab661c3f848262` | trailers eliminados |
| 84 | `0292f72ea953d701d997b2cc3359de42ae21796b` | `8f61a67da7dcb4ce243a0ed6d3c86a8d25dc9cff` | trailers eliminados |
| 85 | `3964961acf089667490c657886bae0470edeb357` | `fed38d37c3823a648073af56d240bd1185f2b5a1` | trailers eliminados |
| 86 | `7a3ef513b8398894cfda7503b0303b02b4e1540a` | `0f9f3e6a89888a47e3b083f4caee2ffab7d2c81d` | trailers eliminados |
| 87 | `54071a212857cc55dbf385c820581f949c9f9e3d` | `a5cef8ae7bfec45f72070d6e035655726d2b15d3` | trailers eliminados |
| 88 | `c6a95be836832a9525c29f2b4d7cae961f198932` | `693df7fe1119911d0b7d1b8f750e3871ce10ec99` | trailers eliminados |
| 89 | `43e2e873e4dc8bff30f256d5c2ae1058b13b11f3` | `75607861704472e8af88d81a7bb92f7c5aa57c7c` | trailers eliminados |
| 90 | `6b5b92dbfff252b05f5236a683bbbb028fef2ca9` | `a0a0fe39f0a6919e88fc1765c75a8e20df50e676` | trailers eliminados |
| 91 | `3845c07b23a4366f3b458b6a77aff3d2e8ee2ae0` | `19adc297cf10802e792a5ad522eceeae276165f1` | trailers eliminados |
| 92 | `b79dfa78409cd3bf95fd12bb8888653d64b79ee3` | `5dc1450a6d1e283871a8a8752f68052b55a0623e` | trailers eliminados |
| 93 | `7ff9949d75997baeec0ebdf92ecb38072b6dd466` | `d2c7f552e689e1f2db40637bd4401b76229deeb5` | trailers eliminados |
| 94 | `df003f0dadc3db5f381e057307e7016f3a6acbfa` | `2b29b92201236cbaf8d146d6d7da8d3c148266f6` | trailers eliminados |
| 95 | `57b6c936ac0f0add17ad3a470869f45fa0e5b0ad` | `ac7eb62f65f77d4710410e411b579ce39b02151a` | trailers eliminados |
| 96 | `aed6fe26196794d1f9807c123cf8d0b38ecbf02f` | `cd38cafbe57a6e44919ef5b437d10d62cd557250` | trailers eliminados |
| 97 | `7d52627f622209a1fbf09028fa6867863e5fa078` | `2fce938c3a33332f5125fa0106abd8b1747e443e` | trailers eliminados |
| 98 | `9c388d9713df8afee329e9075bfdc40df825644a` | `4ee46dee6f8e72dbe196b94bd884652be40985cf` | descendiente de un commit reescrito |
| 99 | `1d6177206e46e484e2052b9604d12cb53fdece88` | `ceb38404cd7dd56f2aa1511496588286d78efa8b` | descendiente de un commit reescrito |
| 100 | `191bd84c461c7cb05a2f5143b6b12adf330b7e69` | `bf6e76b757eff9608420ca64f4b8110c6b00b8e8` | descendiente de un commit reescrito |
| 101 | `a80f14a148cdde9d2f752c71eebfe1bbeec42b83` | `10579c9dd8fe4ee4bbf586ebe11c87cc8bb06cfe` | descendiente de un commit reescrito |
| 102 | `77281a9cc5dbaa7399d7c81daeab49cc57806371` | `0dcdfd5af4532027e3fe7585a9470f0441348c08` | descendiente de un commit reescrito |
| 103 | `2550bc1b62a5e16cbb4d26145570e46ea2831136` | `f5cb5dd9f42b683d7a008c764bfd03ac711b0290` | descendiente de un commit reescrito |
| 104 | `e2151ca178d2edf7bb2e93f149dceadbfd83660c` | `c2ceec06f619383ba5628428fb6ba98fddff8922` | descendiente de un commit reescrito |
| 105 | `701f1c4377505dd61d56ae5e8baeb7dd4b561cae` | `2ff078d5f8eea704246fd47567648a67166d91b5` | descendiente de un commit reescrito |
| 106 | `d0866cebfdf5b6900807f9ff67d0645bfc24d506` | `c2e4123e31da01ea0037c86a567abf0a46938662` | descendiente de un commit reescrito |
| 107 | `6b6534504cdf3575a5c3724a450c4ded4b350b26` | `dac3399b7b3a86b402ade9af1741186d18468b73` | descendiente de un commit reescrito |
| 108 | `dc1296363d1b3b3775171491a8145cdafdd0cbcf` | `42f3d390b728773fc560eaa7be278201f158c066` | descendiente de un commit reescrito |
| 109 | `f210021a0c40f2150e0219af39c856f4f8da954e` | `32948a972bd19fa607b714c129a18596c841f2b7` | descendiente de un commit reescrito |
| 110 | `94a08e4d72ce9735f18ffb19c97360e78455de8c` | `476132fdee821ab26d8cec07f9ef1902bf1b9f09` | descendiente de un commit reescrito |
| 111 | `422350811147cf455cd149e86082f1d46b60b882` | `9d66b4f43d4fb9e3670618fba8739909b23ca82a` | descendiente de un commit reescrito |
| 112 | `4a87700fca417af25621ba18e08eb1f1cf0e1662` | `4343ccd00bd9b8ab8086395a9056a7e2a0c2893b` | descendiente de un commit reescrito |
| 113 | `ae9dfc39fc171fa28f38e2b348ff4bf5814ed83d` | `38cfb47e9e70fcb2c5658891edd456bb94d38ab5` | descendiente de un commit reescrito |
| 114 | `a0cc296acbbe5f3a5dd878d9e38aa24764bb6d9c` | `0eaba28aed0d57bc9c66cd15365d98eaf6796630` | descendiente de un commit reescrito |
| 115 | `0c519fe9d80affe90dfbc2077e365723c8f00145` | `0ad500ca76b0a26f639003d0cd200b020cbc9906` | descendiente de un commit reescrito |
| 116 | `2903ecbf7cc8c20c529773967ba43227b36e945a` | `331d438685c329c98ca6980f1c7bf6ff4f59470b` | descendiente de un commit reescrito |
| 117 | `5e87ae866837ec61f71f73ad5888933fb7448c45` | `f4d6a4f2950e76068a7edf217e6a5bf97b9b9423` | descendiente de un commit reescrito |
| 118 | `76e1046619b5afb25bec671655e1f885201cea4c` | `91c2826751e1b43d7aed1bcc8451a1a9c984cfca` | descendiente de un commit reescrito |
| 119 | `0f5e3b0e93ef54c7523323cf163d7f41ebd768f0` | `67755f03a5dbbab1b608822e63e2e79f5ced184b` | descendiente de un commit reescrito |
| 120 | `b5ca3b32754bd969eb90dbcd746caaae77c1baac` | `ab13b28f4a119ffa51ab3e374e83c2d6dd06ead2` | descendiente de un commit reescrito |
| 121 | `32c6a7d6c9e059319d6c6da541acf121a9cd11bd` | `100ce676c2ce6389f3be69a32f537540b20782b6` | descendiente de un commit reescrito |
| 122 | `b0e13e2a09bd78219e61208b52e663acdedff923` | `a03e499172a596fa66d583cb334e687d9f629529` | descendiente de un commit reescrito |
| 123 | `0400ed2e522257e2f61c09db25a6403e77b2d033` | `7fd33403373f97fecdc163ecbd2b1d337955d51c` | descendiente de un commit reescrito |
| 124 | `835a317f28873a47305993b17c569e7f804a83b6` | `05b6314d416e509e831722d576af58443961c2ed` | descendiente de un commit reescrito |
| 125 | `5a611943ccaabc629a07c778b9fc70f2d54d1b63` | `2b0e7881cf5908ede1158a1ca1f187b5723f886b` | descendiente de un commit reescrito |
| 126 | `615ebeb37662d5c9c2d1d4299a165b66431f1c98` | `7d492db6033b41bdf00bb4c55eff600afccd34e0` | descendiente de un commit reescrito |
| 127 | `4a0c6d81557aba97569c7d8cfb6a62e331c50999` | `169300a2e85660666b2e888800cd11febe20959e` | descendiente de un commit reescrito |
| 128 | `d0fa41279c09c9ea30029110bd4231368aa309b3` | `f919fe734ebdbf9f21e7a87d4ebcd0c4cbdd5861` | trailers eliminados |
| 129 | `cc7eefd0c2c3f4d364f1c4d8106afce3c7d658e5` | `7be182e11368930fef68159b2c7846a737a18f12` | trailers eliminados |
| 130 | `456e9a011a193655bb528051dad6cd6bb92b901b` | `3afab6e1fb12fc6a4ce266714444f2f0107519f1` | trailers eliminados |
| 131 | `1d368e07a4790e7c053cff93178fe76404f97ebf` | `fa8c09fc6a383528ee6bbe434c595293e29e248b` | trailers eliminados |
| 132 | `32e7c991201eda17a2c421552bd6476c073cf5de` | `4c0da2051ae18df4160d48cff7bd114913ca052e` | trailers eliminados |
| 133 | `038c20c1b4b05f0a504d2ae4cbd900e577a6c44c` | `b5fc6e2f9b9e98b9fd737bbc7ad3e481271b2fb2` | trailers eliminados |
| 134 | `6f0e21d0a7c201e4da3bc47bb89a630118b9e4e0` | `ad84a434fe27ed25b0d5bf5da9a655f0f2c9d101` | trailers eliminados |
| 135 | `12b665ad8abf2ea2967692bb4f5d89f4eeff43e2` | `b9b66cf4eaaa789f9d5954905339b4a3d2dc543e` | trailers eliminados |
| 136 | `d7bdaef93cfbee9ad75f7513a420edeb91fe4f0f` | `e147c317c7636c9f9e527276e1d813ac68a6d8dc` | trailers eliminados |
| 137 | `6515210bc5b2810256d4326f3192661713456785` | `2fe91f608005867d02a6e908ae603521afd26f6d` | trailers eliminados |
| 138 | `d3ddde8ee68930276df65f09f7438a23e0b4040c` | `419766b41c0e5f41bae7aa3887f2b97a456b1469` | trailers eliminados |
| 139 | `c39536880a8ff3b2b49d69b17d3ed31e51165b76` | `1724c9f73f24f8a020d38308546789bc36c499f2` | trailers eliminados |
| 140 | `43e1151eea39493a8cb83f355e495ee2390229e8` | `24219e9843cadd527b12c22edae2f8738b8dc39e` | trailers eliminados |
| 141 | `521123c3ae527f410fe879e7f302766fa0f3b124` | `74df3a2ee0ebc1263de5fb4e430c998d71409ec2` | trailers eliminados |
| 142 | `6f7ec0fbc3aa3fa2a4b3627d2273df9d6a1f8be3` | `ab8b66d122905469a1037686e4be066b4a2b8722` | trailers eliminados |
| 143 | `c617d14497bbd12899538e8116a7d2ee449d7d31` | `334859335fa6257556c63607d5c593c261fd46d8` | trailers eliminados |
| 144 | `5e7f95d02461761977f9ca022e604ec620d3f743` | `606779287adb695a1a44c0fb9767830efe7ef3a1` | trailers eliminados |
| 145 | `66198d98ebcb835892d1852aeb36de43c15e9107` | `57f0a6f90e4dc3f3e8a3dadb6bf5e5981220d32d` | trailers eliminados |
| 146 | `3d7ab90362dad2ea989932eec46011f1e7e27374` | `7c134db2920345980721d26fbcea87d278ca2c8f` | trailers eliminados |
| 147 | `e7aeb14651095911d775085f6049f34e38fe3f76` | `5de25ac650cb662ed17ba22a08fcc5fd18ab8d8f` | trailers eliminados |
| 148 | `95d4e7178568df8d500ad793a258091b39869c79` | `f92186efb2ab461e60b78346e207e12601a26666` | trailers eliminados |
| 149 | `6d95a25304a3b16b1ddacaa90891d884b1083920` | `6db791a03d041d165ec203f52347537dbab8160d` | trailers eliminados |
| 150 | `e4dfdf16b61efe5a3c652066572fa1184f813604` | `4627d5441dc6e76639325e7076075963d6f3800c` | trailers eliminados |
| 151 | `4cac4aefd081fbd2cb5dc1c04906c6a6c77fb70e` | `dd2440408c194b3c97573dc9a8a924ed7ae10bf4` | trailers eliminados |
| 152 | `cd52cdb9bd15c791995eeac518c96b52e3c0b6fe` | `83787e3f6fe559d92c1be2918d4c197f0fca4d81` | trailers eliminados |
| 153 | `37f1294d52d7e71f2c620b107ca4ed1b365079a3` | `a23cd5ab1eed4469c280120867901f8fd2ec4b1b` | trailers eliminados |
| 154 | `0b0864b38aaa79f67cfe1ffb18723cf0b36a7d60` | `768f229fcb55cfe2ac21ff3312fe3e68e120832b` | trailers eliminados |
| 155 | `8be7fc2cd67d616299a6e0a0762ab9fd40a764f6` | `8381ec66d6af051b5389e04db79d9bdb8dbb5cc2` | trailers eliminados |
| 156 | `4e9e4a6690941def4706700e31ce52142758e700` | `c75795f8a66b876ef241e8ac652b1ae88429b04f` | trailers eliminados |
| 157 | `daddffd9171dc9a88aa42406f5b54f2ff21f1a0e` | `d7f83077b6d49037818b73a80b038c928974c000` | trailers eliminados |
| 158 | `4a6358bbb907d7ef6c5e4203f71e79a96e7badf7` | `00ccb267e961e6703cfc57a033d8cfb9375c0ecb` | trailers eliminados |
| 159 | `9bb8c6cace025346ed59ef68bf461e532811aa6d` | `d9978bd47847af5c35ee2662a9654111ab6dd666` | trailers eliminados |
| 160 | `23208b0e8aaf8251d9b641a504356522d11b11cb` | `4a43ced4345c4953017287df4d803368e4903e82` | trailers eliminados |
| 161 | `e5242d00628b75b9d113592b02a794421ea60611` | `47f3beed0059f7f8026fa5d31244d1db76ef5211` | trailers eliminados |
| 162 | `822026153a6b5235a835e1a0b35c16806250d4ac` | `8d85d2705c8313a81826530e6635be6e573afb75` | trailers eliminados |
| 163 | `fad82f6e45f00de5deac1194780bdda8f8ecfb98` | `781f6e718472ece7d5667d0cd0690984d901edd0` | trailers eliminados |
| 164 | `03ab04fca6e289b6a2f5420cc2d3848866f663eb` | `2f8bc78dde5ca3cabcfe2c75f496f40e7435f6bc` | trailers eliminados |
| 165 | `0505a2b44fefb154d06b916250df199b1b3829e6` | `a21d7124fc79dba005cd242c959bc7e3478f4bd6` | trailers eliminados |
| 166 | `4cb4de5d27818f92b94929e5f791cab489dc1193` | `35a7b6fec34dfcae38163db6cf86915d7ac43fe2` | trailers eliminados |
| 167 | `089d48f7ca0c6c30859845766e15e79b22c7fe01` | `dc6345baac24e4fb9eb9aa696d6a8dd1284a0c73` | trailers eliminados |
| 168 | `636cf150b12eef0defddf8212ece819d640631ad` | `a2d390d4725794a6064b6bb6329a62fbc56cd76c` | trailers eliminados |
| 169 | `167e17e4202b5a9033621ed4a3eeb583ae46d794` | `575991c5f8f01734629080d55e47d97836a41f0f` | trailers eliminados |
| 170 | `3b001d4c210a696efb88fe73bfa54829d8065926` | `3bffe2c4aed88b1a8109b0c8d6078fe0b975beeb` | trailers eliminados |

## Citas de SHA antiguos que siguen vigentes en ficheros versionados

| SHA original | SHA nuevo | Dónde se cita |
|---|---|---|
| `a34bab2` | `64288f9` | `docs/experiments/resultado-verificador-v2-1.md`; `experiments/E15_suficiencia_verifier_v2_1.json` (+ copia en `pre_mixed_embedding_fix/`) |
| `1a58376` | `7a91b47` | `docs/methodology/politica-evaluacion-no-oracular.md` |
| `f290263` | `b73241d` | `docs/methodology/politica-evaluacion-no-oracular-enmienda-01.md` |
| `43f56dc` | `7f8ddc1` | `experiments/E15_suficiencia.json`, `experiments/E15_suficiencia_non_oracle.json` (+ copias) |
| `3b02cf8` | `d0498e8` | `docs/methodology/politica-evaluacion-no-oracular-enmienda-01.md`; `experiments/E15_suficiencia_adverse_seleccion_por_indice.json` (+ copia) |
| `c502f9a` | `edcad61` | `experiments/E15_suficiencia_adverse.json` (+ copia) |
| `54071a2` | `a5cef8a` | `docs/methodology/plan-reejecucion-canonica.md` |
| `c6a95be` | `693df7f` | `docs/methodology/plan-reejecucion-canonica.md` |
| `43e2e87` | `7560786` | `docs/methodology/plan-reejecucion-canonica.md` |
| `aed6fe2` | `cd38caf` | `configs/manifest_rerun_a.json` (`frozen_at_commit`) |
| `9c388d9` | `4ee46de` | `docs/memoria/LEEME.md` |
| `b0e13e2` | `a03e499` | `docs/audits/full_memory_review/11_BLOCKERS_AND_DECISIONS.md`, `12_CORRECTION_LOG.md` |
| `835a317` | `05b6314` | `docs/audits/full_memory_review/00_INVENTORY.md` |
| `5a61194` | `2b0e788` | `docs/audits/full_memory_review/01_PI_TRACEABILITY_MATRIX.md` |
| `d0fa412` | `f919fe7` | `docs/audits/full_memory_review/12_CORRECTION_LOG.md` |
