# Notebooks históricos de fase

**No forman parte de la evidencia del trabajo y no hace falta abrirlos.**

Son los cuadernos de trabajo que se usaron durante cada fase del laboratorio (E1 a E20). Se
generaron con una plantilla común (`scripts/gen_notebooks.py`) y algunos se rellenaron después
(`scripts/fill_notebooks.py`), pero varios conservan sin redactar el cierre de la plantilla
(Resultados, Interpretación, Limitaciones y Conclusión experimental) y cuatro no pasaron de
la cabecera. Se conservan para que el recorrido se pueda seguir, no como resultado.

Lo que sí se entrega son **los siete notebooks de `notebooks/`**, que recogen el contenido válido de
estos cuadernos con su análisis, sus limitaciones y sus conclusiones redactados. Se ejecutan
con `bash scripts/ejecutar_notebooks.sh`.

Estos cuadernos **no se ejecutan desde esta carpeta**: su preámbulo busca `src/` un nivel por
encima del directorio `notebooks/`.

| Cuaderno histórico | Fase | Dónde está hoy su contenido |
|---|---|---|
| `00_environment_check` | E1 | `scripts/instalar.sh` y la sección de entorno de cada notebook |
| `01_synthetic_obd_generation` | E2 | `01_exploracion_obd` |
| `02_real_obd_ingestion` | E3 | sin contenido: no se usaron datos OBD-II reales (ADR-003) |
| `03_timeseries_eda` | E4 | `01_exploracion_obd` |
| `04_preprocessing_features` | E5 | `01_exploracion_obd` |
| `05_model_training` | E6–E7 | `02_comparacion_modelos` |
| `06_model_evaluation` | E8 | `02_comparacion_modelos` y `06_expresion_del_fallo` |
| `07_xai` | E9 | `04_explicabilidad` |
| `08_rag_corpus` | E10–E11 | `05_suficiencia_y_abstencion` (el corpus no se distribuye) |
| `09_retrieval_evaluation` | E12 | `05_suficiencia_y_abstencion` |
| `10_llm_agent` | E13 | `05_suficiencia_y_abstencion` |
| `11_evidence_sufficiency` | E15 | `05_suficiencia_y_abstencion` |
| `12_abstention` | E16 | `05_suficiencia_y_abstencion` |
| `13_integrated_experiment` | E17 | sin contenido; el recorrido completo está en `00_introduccion` |
| `14_final_evaluation` | E19 | `03_analisis_e19` |
| `15_tfm_demo` | E20 | `05_suficiencia_y_abstencion` (el caso con y sin evidencia) |
| `TFM_EXPERIMENTO_COMPLETO` | E20 | sin contenido; el recorrido completo está en `00_introduccion` |
