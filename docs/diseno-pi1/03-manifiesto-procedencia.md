# 3. Manifiesto de procedencia por sesión (Fase B)

**La pregunta que este esquema tiene que poder responder, para cualquier serie del conjunto:** ¿con qué
configuración exacta se generó esta sesión?

Hoy no se puede. La ficha de `synthetic_v2` guarda `dataset_id`, `dataset_type`, la fuente, la fecha,
la versión, la frecuencia de muestreo, el simulador, una nota, la **semilla global**, el número de
sesiones y de muestras, las señales, los identificadores de fallo y los identificadores de sesión. Los
datos crudos guardan por muestra el régimen, el fallo y si está activo. **No queda registrada** la
semilla individual de cada sesión, ni su temperatura ambiente, ni su duración, ni el instante de
aparición del fallo, ni los parámetros con que se aplicó.

Con el plan equilibrado por omisión eso se puede reconstruir, porque el constructor del plan es
determinista y la semilla global lo fija. En cuanto se varíe un parámetro por sesión, no.

## 3.1 Esquema propuesto

Un fichero `data/raw/synthetic/synthetic_v4.provenance.json` junto a la ficha actual, que no se
sustituye.

```json
{
  "dataset_id": "synthetic_v4",
  "dataset_type": "synthetic",
  "created_at": "<ISO-8601 UTC>",
  "generator": {
    "module": "mecanico_ia_exp.obd.synthetic",
    "declared_version": "1.0.0",
    "commit": "<sha completo del repositorio al generar>",
    "dirty": false,
    "source_fingerprints_16": {
      "src/mecanico_ia_exp/obd/engine.py": "<sha256:16>",
      "src/mecanico_ia_exp/obd/synthetic.py": "<sha256:16>",
      "src/mecanico_ia_exp/obd/faults.py": "<sha256:16>",
      "src/mecanico_ia_exp/obd/regimes.py": "<sha256:16>",
      "src/mecanico_ia_exp/obd/signals.py": "<sha256:16>",
      "configs/calibracion_mazda3_bk.yaml": "<sha256:16>"
    },
    "why_fingerprints": "la constante declared_version no distinguio synthetic_v2 de synthetic_v3, que son fenomenos distintos"
  },
  "global_seed": 20260901,
  "sampling_rate_hz": 1.0,
  "n_sessions": 216,
  "sessions": [
    {
      "session_id": "F03_thermostat_stuck__warmup__07",
      "seed": 20260901073,
      "regime": "warmup",
      "duration_s": 600.0,
      "fault_id": "F03_thermostat_stuck",
      "fault_onset_s": 120.0,
      "ambient_temp_c": 21.4,
      "initial_coolant_c": null,
      "fault_params": {"temp_cap_c": 71.0},
      "severity": null,
      "n_samples": 600
    }
  ],
  "temporal_distribution": {
    "by_regime": {"idle": 36, "urban": 72, "highway": 54, "warmup": 54},
    "by_condition": {"F00_normal": 36, "F01_vacuum_leak": 36, "F02_maf_drift": 36,
                     "F03_thermostat_stuck": 36, "F04_o2_lag": 36, "F05_misfire": 36},
    "note": "los recuentos reales los escribe el generador; aqui figuran como ejemplo del esquema"
  },
  "artifact_fingerprints_16": {
    "data/raw/synthetic/synthetic_v4.parquet": "<sha256:16>",
    "data/processed/synthetic_v4_x.npy": "<sha256:16>",
    "data/processed/synthetic_v4_features.npy": "<sha256:16>",
    "data/processed/synthetic_v4_meta.parquet": "<sha256:16>",
    "data/processed/synthetic_v4_preprocess.json": "<sha256:16>"
  }
}
```

## 3.2 Decisiones del esquema, y su motivo

**`severity` existe aunque hoy sea nulo en la mayoría.** El catálogo de fallos parametriza la severidad
de forma distinta según la condición: `severity` en la fuga de vacío, `temp_cap_c` en el termostato,
`rate` y `rpm_drop` en el encendido. El campo `fault_params` recoge lo que de verdad se aplicó, y
`severity` queda para cuando el parámetro se llame así. **No se inventa un valor** cuando la condición
no lo tiene: se escribe nulo.

Los valores del ejemplo son los que el protocolo de `v4` fija: sesión de **600 s**, instante de
aparición del fallo en **120 s** —el 20 % de la duración, como hace el plan equilibrado— y temperatura
ambiente sorteada en el rango que el generador usa. Un ejemplo con otros valores describiría otro
experimento y no serviría como comprobación de reconstrucción.

**`initial_coolant_c` se registra incluso cuando es nulo**, porque nulo significa algo —«el motor
arranca a la temperatura ambiente»— y es exactamente la propiedad que hace indetectable el termostato
en las primeras ventanas de una sesión de calentamiento. Perderla sería perder la explicación del
hallazgo más interesante de PI.1.

**La semilla por sesión se registra aunque se derive de la global.** Si alguien varía un parámetro de
una sola sesión, la derivación deja de reconstruir nada, y es justo entonces cuando el campo hace
falta.

**Las huellas del código fuente del generador, y no solo su versión declarada.** Es la lección de
`v2` frente a `v3`: dos conjuntos con la misma versión declarada y distinta física.

**Y `engine.py` encabeza la lista, que es donde está la física.** Conviene no equivocarse aquí: el
fichero `configs/calibracion_mazda3_bk.yaml` **no lo lee ningún módulo**. Documenta de dónde sale cada
valor y con qué cita del manual, y eso tiene su propio valor para el jurado, pero los números que el
generador usa están **codificados como constantes** en `src/mecanico_ia_exp/obd/engine.py`:
`_IDLE_RPM = 690.0`, `_THERMOSTAT_C = 82.0`, los coeficientes del caudal, el avance base. La diferencia
entre `v2` y `v3` —690 frente a 820 rpm de ralentí— es un cambio en **ese** fichero.

De modo que la huella del YAML sirve para rastrear la **justificación** y la de `engine.py` para
identificar la **señal**. Las dos van, y si solo pudiera ir una, iría la del código.

**Y una columna nueva en los datos crudos, no en el manifiesto:** `fault_expressed`, que dice por muestra
si el fallo modificó esa muestra. La que ya existe, `fault_active`, dice solo que la función se aplicó, y
para el fallo de encendido vale cierto en ventanas sin ningún episodio. El manifiesto declara que la
columna está y con qué criterio la escribe cada fallo; el dato va con las muestras, que es donde se usa.

## 3.3 Cómo se comprueba que el manifiesto sirve

Una prueba automatizada que, para una sesión elegida del conjunto, reconstruya su `SessionSpec` desde
el manifiesto, la regenere con el generador y compruebe que las muestras resultantes son **idénticas**
a las del conjunto. Si eso pasa, el manifiesto responde a la pregunta; si no, le falta un campo.

Es la misma clase de comprobación que las del anclaje de E19: no se confía en que el fichero diga la
verdad, se verifica que reproduce.

## 3.4 Qué no hace este manifiesto

No convierte en reproducible a `synthetic_v2` ni a `synthetic_v3` retroactivamente. Para ellos la
procedencia sigue siendo la semilla global más el constructor determinista del plan, y eso hay que
declararlo como limitación en la reproducibilidad en lugar de regenerarlos, porque regenerarlos
cambiaría las cifras publicadas.
