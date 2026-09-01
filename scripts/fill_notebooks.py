"""Rellena los notebooks de las fases ejecutadas con su análisis.

Los notebooks son **capa de análisis sobre artefactos**, no re-ejecución del
pipeline. Cargan lo que los ejecutores produjeron --tablas, registros, base de
datos-- y muestran el hallazgo. Así son rápidos, no dependen de reentrenar nada y
no pueden contradecir a los informes: leen las mismas cifras.

La lógica científica vive en ``src/``. Aquí solo se lee y se muestra.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = ROOT / "notebooks"

PREAMBULO = """import sys
from pathlib import Path

RAIZ = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
sys.path.insert(0, str(RAIZ / "src"))

import pandas as pd

from mecanico_ia_exp.config import paths
"""

CONTENIDO: dict[str, list[tuple[str, str]]] = {
    "01_synthetic_obd_generation": [
        (
            "md",
            "## Las constantes del generador salen del manual\n\n"
            "Cada valor lleva su cita. Un generador con constantes inventadas es "
            "coherente consigo mismo y no corresponde a ningún vehículo.",
        ),
        (
            "code",
            "import yaml\n\n"
            "calib = yaml.safe_load((paths.CONFIGS / 'calibracion_mazda3_bk.yaml').read_text())\n"
            "for nombre, p in calib['parametros'].items():\n"
            "    fuente = p.get('fuente')\n"
            '    print(f"{nombre:<28} {str(fuente)[:44]}")',
        ),
        ("md", "## Comprobación: ¿el generador respeta la especificación?"),
        (
            "code",
            "from mecanico_ia_exp.obd.synthetic import SessionSpec, generate_session\n\n"
            "d = generate_session(SessionSpec(session_id='demo', regime='urban',\n"
            "                                 duration_s=900.0, seed=5))\n"
            "ral = d[d['vehicle_speed'] < 2.0]\n"
            "print(f\"ralentí        {ral['rpm'].min():.0f}-{ral['rpm'].max():.0f} rpm      \"\n"
            '      f"(manual: 640-740)")\n'
            "print(f\"caudal ralentí {ral['maf'].mean():.2f} g/s            (manual: 2,5)\")\n"
            "print(f\"refrigerante   {d['coolant_temperature'].max():.1f} °C           \"\n"
            '      f"(manual: apertura 80-84)")\n'
            "print(f\"avance ralentí {ral['ignition_timing'].mean():.1f} BTDC          \"\n"
            '      f"(manual: 9-11)")',
        ),
        ("md", "## Las cinco condiciones y su respaldo documental"),
        (
            "code",
            "from mecanico_ia_exp.obd.faults import FAULTS\n\n"
            "for fid, f in FAULTS.items():\n"
            '    print(f"{fid}")\n'
            "    print(f\"    señales : {', '.join(f.affected_signals)}\")\n"
            '    print(f"    patrón  : {f.temporal_pattern[:70]}")',
        ),
    ],
    "03_timeseries_eda": [
        (
            "md",
            "## Separabilidad por señal y condición\n\n"
            "Medida con el delta de Cliff, **por separado en nivel y en dispersión**. "
            "Dos condiciones no aparecen en las medias.",
        ),
        (
            "code",
            "sep = pd.read_csv(paths.TABLES / 'E4_separabilidad.csv')\n"
            "mejor = (sep.groupby('signal')['delta_max_abs'].max()\n"
            "            .sort_values(ascending=False).round(3))\n"
            "mejor.to_frame('delta máximo')",
        ),
        ("md", "### El hallazgo: la deriva del caudalímetro no se ve en el caudalímetro"),
        (
            "code",
            "f02 = sep[sep.fault_id == 'F02_maf_drift'].set_index('signal')\n"
            "f02.loc[['maf', 'stft_bank1', 'ltft_bank1'],\n"
            "        ['delta_level', 'delta_dispersion']].round(3)",
        ),
        ("md", "### Y la sonda lenta solo aparece en la dispersión"),
        (
            "code",
            "f04 = sep[sep.fault_id == 'F04_o2_lag'].set_index('signal')\n"
            "f04.loc[['oxygen_sensor'], ['delta_level', 'delta_dispersion']].round(3)",
        ),
    ],
    "04_preprocessing_features": [
        (
            "md",
            "## Estudio de longitud de ventana\n\n"
            "El criterio no fue el número más alto, sino la **concordancia con el "
            "mecanismo**: que el efecto caiga sobre una señal que la ficha del fallo declara.",
        ),
        (
            "code",
            "est = pd.read_csv(paths.TABLES / 'E5_estudio_ventana.csv')\n"
            "est[['length_s', 'fault_id', 'noise_floor_p90', 'best_delta',\n"
            "     'best_feature', 'feature_declared_by_fault', 'above_noise_floor']]",
        ),
        ("md", "### El suelo de ruido: por qué a 30 s el fallo de encendido era ruido"),
        (
            "code",
            "f05 = est[est.fault_id == 'F05_misfire'][\n"
            "    ['length_s', 'noise_floor_p90', 'best_delta',\n"
            "     'best_feature', 'above_noise_floor']]\n"
            "f05",
        ),
        ("md", "## El reparto no filtra información entre particiones"),
        (
            "code",
            "meta = pd.read_parquet(paths.DATA_PROCESSED / 'synthetic_v2_meta.parquet')\n"
            "por_part = meta.groupby('partition')['session_id'].nunique()\n"
            "solape = {}\n"
            "for a in ('train', 'validation', 'test'):\n"
            "    for b in ('train', 'validation', 'test'):\n"
            "        if a < b:\n"
            "            sa = set(meta.loc[meta.partition == a, 'session_id'])\n"
            "            sb = set(meta.loc[meta.partition == b, 'session_id'])\n"
            "            solape[f'{a}∩{b}'] = len(sa & sb)\n"
            "print('sesiones por partición:', por_part.to_dict())\n"
            "print('sesiones compartidas  :', solape)\n"
            "assert all(v == 0 for v in solape.values()), 'hay fuga entre particiones'",
        ),
    ],
    "05_model_training": [
        (
            "md",
            "## Baseline frente a modelo temporal\n\n"
            "Se leen los registros de las ejecuciones; no se reentrena nada.",
        ),
        (
            "code",
            "def cargar(nombre):\n"
            "    ruta = paths.EXPERIMENTS / nombre\n"
            "    return json.loads(ruta.read_text()) if ruta.is_file() else None\n\n"
            "import json\n"
            "filas = []\n"
            "for ds in ('synthetic_v2', 'synthetic_v3'):\n"
            "    b, t = cargar(f'E6_baseline_{ds}.json'), cargar(f'E7_temporal_{ds}.json')\n"
            "    if b and t:\n"
            "        filas.append({'dataset': ds, 'n_train': b['n_train'],\n"
            "                      'baseline': b['metrics']['macro_f1'],\n"
            "                      'temporal': t['metrics']['macro_f1'],\n"
            "                      'diferencia': round(t['metrics']['macro_f1']\n"
            "                                          - b['metrics']['macro_f1'], 3)})\n"
            "pd.DataFrame(filas)",
        ),
        (
            "md",
            "**El límite era el volumen de datos, no la arquitectura.** Con el triple "
            "de sesiones el orden se invierte.",
        ),
    ],
    "06_model_evaluation": [
        ("md", "## Rendimiento por clase y calibración"),
        (
            "code",
            "import json\n"
            "b = json.loads((paths.EXPERIMENTS / 'E6_baseline_synthetic_v2.json').read_text())\n"
            "pd.DataFrame(b['metrics']['per_class'])",
        ),
        (
            "code",
            "print('calibración sin corregir:', b['metrics']['calibration'])\n"
            "print()\n"
            "print('El bosque está INFRAconfiado: acierta más de lo que dice.')\n"
            "print('Un umbral sobre esta confianza se abstendría de más.')",
        ),
        (
            "md",
            "### Dónde falla: el límite físico del termostato\n\n"
            "Las ventanas que el modelo falla tienen el motor por debajo del techo que "
            "el fallo impone. Ahí la señal de un motor averiado es **idéntica** a la de "
            "uno sano.",
        ),
        (
            "code",
            "from IPython.display import Image\n"
            "Image(str(paths.FIGURES / 'FIG-E6-02_limite_evidencia_f03.png'))",
        ),
    ],
    "07_xai": [
        (
            "md",
            "## Atribución sobre el modelo especializado\n\n"
            "La función explicada se declara siempre. El fondo sale solo de entrenamiento.",
        ),
        (
            "code",
            "import json\n"
            "x = json.loads((paths.EXPERIMENTS / 'E9_xai_synthetic_v2.json').read_text())\n"
            "print('función explicada :', x['explained_function'])\n"
            "print('explainer         :', x['explainer'])\n"
            "print('fondo             :', x['background'])",
        ),
        ("md", "### El hallazgo: `maf` no contribuye a detectar su propio fallo"),
        (
            "code",
            "atr = pd.read_csv(paths.TABLES / 'E9_atribuciones_synthetic_v2.csv')\n"
            "f02 = atr[atr.predicted_class == 'F02_maf_drift']\n"
            "(f02.groupby('signal')['importance']\n"
            "    .apply(lambda s: s.abs().sum()).sort_values(ascending=False)\n"
            "    .round(4).to_frame('importancia acumulada'))",
        ),
        (
            "code",
            "from mecanico_ia_exp.obd.faults import FAULTS\n"
            "print('la ficha del fallo declara:', FAULTS['F02_maf_drift'].affected_signals)\n"
            "print()\n"
            "print('La atribución NO señala maf. Es el hallazgo de E4 por otra vía.')\n"
            "print('Una explicación que dijera «el caudal es bajo» sería falsa.')",
        ),
        (
            "md",
            "> **La atribución no es causalidad.** Dice de qué depende la salida del "
            "modelo, no qué le ocurre al vehículo.",
        ),
    ],
    "08_rag_corpus": [
        ("md", "## El corpus indexado"),
        (
            "code",
            "import sqlalchemy as sa\n"
            "from mecanico_ia_exp.config.settings import get_settings\n\n"
            "eng = sa.create_engine(get_settings().database.url)\n"
            "with eng.connect() as cx:\n"
            "    resumen = pd.read_sql(sa.text('''\n"
            "        SELECT count(*) AS fragmentos,\n"
            "               count(*) FILTER (WHERE cardinality(dtc_codes) > 0) AS con_dtc,\n"
            "               count(DISTINCT source_file) AS ficheros,\n"
            "               count(DISTINCT language) AS idiomas\n"
            "        FROM rag.document_chunk'''), cx)\n"
            "resumen",
        ),
        (
            "md",
            "### Procedencia completa de un fragmento\n\nNunca «según el manual» sin decir cuál.",
        ),
        (
            "code",
            "from mecanico_ia_exp.rag.embeddings import get_provider\n"
            "from mecanico_ia_exp.rag.store import PgVectorStore\n\n"
            "store, prov = PgVectorStore(), get_provider('multilingual')\n"
            "consulta = 'la sonda lambda responde con lentitud'\n"
            "res = store.search(prov.embed_one(consulta), vehicle_id='mazda-3-bk-2007',\n"
            "                   top_k=1, dtc_codes=('P0133',),\n"
            "                   embedding_model=prov.identity.model)\n"
            "for r in res:\n"
            "    print('consulta :', consulta)\n"
            "    print('cita     :', r.provenance())\n"
            "    print('DTC      :', r.dtc_codes, '· motores:', r.engine_codes)",
        ),
        ("md", "### Aislamiento entre vehículos"),
        (
            "code",
            "otro = store.search(prov.embed_one(consulta), vehicle_id='otro-vehiculo',\n"
            "                    top_k=5, embedding_model=prov.identity.model)\n"
            "print(f'resultados para otro vehículo: {len(otro)}')\n"
            "print('el vehículo es parámetro obligatorio: no hay búsqueda global')\n"
            "store.dispose()",
        ),
    ],
    "09_retrieval_evaluation": [
        ("md", "## Cinco estrategias sobre el mismo conjunto anotado"),
        (
            "code",
            "import json\n"
            "r = json.loads((paths.EXPERIMENTS / 'E12_retrieval.json').read_text())\n"
            "pd.DataFrame([{k: v for k, v in s.items() if k != 'cases'}\n"
            "              for s in r['strategies']])",
        ),
        (
            "md",
            "**La recuperación semántica nunca encuentra el procedimiento correcto.** "
            "Guiarla con el diagnóstico del modelo la lleva a encontrarlo siempre.\n\n"
            "Eso valida la arquitectura: si el LLM diagnosticara sobre OBD-II crudo, no "
            "habría diagnóstico previo que guiara la búsqueda.",
        ),
        ("md", "### El distractor: mismo código, otro motor"),
        (
            "code",
            "detalle = pd.read_csv(paths.TABLES / 'E12_retrieval_por_caso.csv')\n"
            "detalle[detalle.distractors_retrieved > 0][\n"
            "    ['strategy', 'case_id', 'distractors_retrieved',\n"
            "     'distractor_above_relevant']]",
        ),
    ],
    "11_evidence_sufficiency": [
        (
            "md",
            "## El criterio y sus señales\n\n"
            "Conjunción, no promedio: ningún factor es compensable.",
        ),
        (
            "code",
            "import json\n"
            "s = json.loads((paths.EXPERIMENTS / 'E15_suficiencia.json').read_text())\n"
            "print('umbrales:', json.dumps(s['thresholds'], indent=2, ensure_ascii=False))\n"
            "print('calibración:', s['calibration'])",
        ),
        (
            "code",
            "filas = [{'caso': c['case_id'], 'decisión': c['verdict']['decision'],\n"
            "          **{k: v for k, v in c['verdict']['signals'].items()\n"
            "             if k in ('confidence', 'n_documents_applicable',\n"
            "                      'n_distinct_sources', 'claim_coverage')},\n"
            "          'motivos': ', '.join(c['verdict']['reasons'])}\n"
            "         for c in s['cases']]\n"
            "pd.DataFrame(filas)",
        ),
        (
            "md",
            "### Citar no es sostener\n\n"
            "El verificador rechaza las citas que no hablan de la señal afirmada.",
        ),
        (
            "code",
            "checks = [ch for c in s['cases'] for ch in c['support_checks']]\n"
            "print(f'comprobaciones: {len(checks)} · aceptadas: '\n"
            "      f'{sum(1 for x in checks if x[\"supports\"])}')\n"
            "pd.Series([x['reason'] for x in checks if not x['supports']]).value_counts()",
        ),
    ],
    "12_abstention": [
        (
            "md",
            "## El experimento central\n\n"
            "Mismos datos, mismo modelo, misma atribución, **misma confianza**. "
            "Lo único que cambia es que se retira la evidencia del índice.",
        ),
        (
            "code",
            "import json\n"
            "s = json.loads((paths.EXPERIMENTS / 'E15_suficiencia.json').read_text())\n"
            "par = [c for c in s['cases'] if 'vacuum_leak' in c['case_id']]\n"
            "pd.DataFrame([{'caso': c['case_id'],\n"
            "               'variante': c.get('corpus_variant', 'FULL'),\n"
            "               'confianza': c['verdict']['signals']['confidence'],\n"
            "               'docs aplicables': c['verdict']['signals']['n_documents_applicable'],\n"
            "               'cobertura': c['verdict']['signals']['claim_coverage'],\n"
            "               'decisión': c['verdict']['decision']} for c in par])",
        ),
        ("md", "### Lo que el agente respondería en cada caso"),
        (
            "code",
            "for c in par:\n"
            "    v = c['verdict']\n"
            "    print(f\"--- {c['case_id']}\")\n"
            "    if v['decision'] == 'EXPLAIN':\n"
            "        for cl in c['bundle']['claims']:\n"
            "            print(f\"  [{cl['support_status']}] {cl['text'][:88]}\")\n"
            "            print(f\"      observación: {cl['observational_evidence']}\")\n"
            "            print(f\"      documento  : {cl['documentary_evidence']}\")\n"
            "    else:\n"
            "        print('  ABSTAIN — INSUFFICIENT_EVIDENCE')\n"
            "        for m in v['missing_evidence']:\n"
            "            print(f'      falta: {m}')\n"
            "    print()",
        ),
        (
            "md",
            "> La abstención **no es un fallo**. Es la respuesta correcta cuando la "
            "evidencia disponible no sostiene una explicación.",
        ),
    ],
    "15_tfm_demo": [
        (
            "md",
            "## Demostración\n\n"
            "La cadena completa sobre un caso, y el mismo caso sin su evidencia.",
        ),
        (
            "code",
            "import json\n"
            "s = json.loads((paths.EXPERIMENTS / 'E15_suficiencia.json').read_text())\n"
            "caso = next(c for c in s['cases'] if c['case_id'] == 'C05_vacuum_leak')\n"
            "b = caso['bundle']\n"
            "print(f\"vehículo   : {b['vehicle_id']}\")\n"
            "print(f\"diagnóstico: {b['predicted_class']}\")\n"
            "print(f\"confianza  : {b['calibrated_confidence']}\")\n"
            "print()\n"
            "print('EVIDENCIA OBSERVACIONAL')\n"
            "for o in b['observations'][:3]:\n"
            "    print(f\"  {o['observation_id']}: {o['signal']}.{o['statistic']} = \"\n"
            "          f\"{o['value']:.4g} ({o['direction']}) · ventana \"\n"
            "          f\"{o['window_start_s']:.0f}-{o['window_end_s']:.0f} s\")",
        ),
        (
            "code",
            "print('EVIDENCIA DOCUMENTAL')\n"
            "for d in b['documents'][:3]:\n"
            "    print(f\"  {d['chunk_id'][-10:]} · {d['section']}\")\n"
            "    print(f\"      {d['publisher']} · pág {d['page_start']} · \"\n"
            "          f\"DTC {d['dtc_codes']} · aplicabilidad {d['applicability']}\")",
        ),
        (
            "code",
            "print('DECISIÓN:', caso['verdict']['decision'])\n"
            "print()\n"
            "ausente = next(c for c in s['cases'] if 'retirada' in c['case_id'])\n"
            "print('Mismo caso, retirando la evidencia del índice:')\n"
            "print('  decisión:', ausente['verdict']['decision'])\n"
            "print('  motivos :', ausente['verdict']['reasons'])",
        ),
        (
            "md",
            "**Ésa es la respuesta a la pregunta de investigación**, sobre datos "
            "sintéticos calibrados: cuando la evidencia está, el agente explica "
            "trazando cada afirmación; cuando no está, se abstiene.",
        ),
    ],
}


def main() -> None:
    for nombre, celdas in CONTENIDO.items():
        ruta = NOTEBOOKS / f"{nombre}.ipynb"
        if not ruta.is_file():
            print(f"omitido (no existe): {nombre}")
            continue
        cuaderno = json.loads(ruta.read_text(encoding="utf-8"))
        # Se conservan la cabecera documental (celda 0), el preámbulo (1) y el
        # cierre (última): solo se sustituye el cuerpo.
        cabecera = cuaderno["cells"][0]
        cierre = cuaderno["cells"][-1]

        nuevas = [
            cabecera,
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": PREAMBULO.splitlines(keepends=True),
            },
        ]
        for tipo, texto in celdas:
            nuevas.append(
                {
                    "cell_type": "markdown" if tipo == "md" else "code",
                    "metadata": {},
                    **({} if tipo == "md" else {"execution_count": None, "outputs": []}),
                    "source": texto.splitlines(keepends=True),
                }
            )
        nuevas.append(cierre)
        cuaderno["cells"] = nuevas
        ruta.write_text(json.dumps(cuaderno, indent=1, ensure_ascii=False) + "\n")
        print(f"rellenado: {nombre} ({len(celdas)} celdas)")


if __name__ == "__main__":
    main()
