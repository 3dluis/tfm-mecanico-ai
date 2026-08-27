# Línea B — Detección de anomalías en series temporales y SLMs en edge

> **⚠ Nota de vigencia (2026-08-27).** Bajo la PI v4 esta línea es **antecedente
> instrumental**: sostiene el contexto diagnóstico (pasos 1–3) y el criterio transversal edge,
> no la contribución científica. Se conserva íntegra.

> Fichas de trabajo del primer barrido (Fase 1, 2026-08-12). Referencias verificadas en la fecha
> del barrido; releer texto completo antes de citar en la memoria.

## Detección de anomalías: trabajos verificados

### B1. Zamanzadeh Darban et al. (2024). *Deep Learning for Time Series Anomaly Detection: A Survey*
- **Venue:** ACM Computing Surveys 57(1), art. 15. **DOI:** [10.1145/3691338](https://doi.org/10.1145/3691338)
- Taxonomía canónica: métodos por predicción, por reconstrucción, por representación e híbridos; por arquitectura (LSTM/CNN/Transformer/VAE/GAN/GNN). Mapa para justificar el autoencoder (reconstrucción) como representante deep.

### B2. Schmidl, Wenig & Papenbrock (2022). *Anomaly Detection in Time Series: A Comprehensive Evaluation*
- **Venue:** PVLDB 15(9):1779–1797. **DOI:** [10.14778/3538598.3538602](https://dl.acm.org/doi/10.14778/3538598.3538602) · [PDF](http://vldb.org/pvldb/vol15/p1779-wenig.pdf)
- 71 algoritmos × 976 series: **los métodos clásicos son competitivos con deep learning a mucho menor coste; no hay ganador universal.** Justificación empírica central de nuestra comparación clásico-vs-deep en edge.

### B3. Wu & Keogh (2021/2023). *Current Time Series Anomaly Detection Benchmarks are Flawed…*
- **Venue:** IEEE TKDE 35(3):2421–2429. [arXiv:2009.13807](https://arxiv.org/abs/2009.13807)
- Los benchmarks clásicos (Yahoo, Numenta, NASA) sufren trivialidad, ground truth erróneo, run-to-failure bias. → No basar conclusiones del TFM en esos benchmarks; datos propios + inyección controlada.

### B4. Kim et al. (2022). *Towards a Rigorous Evaluation of Time-Series Anomaly Detection*
- **Venue:** AAAI 36(7):7194–7201. **DOI:** [10.1609/aaai.v36i7.20680](https://ojs.aaai.org/index.php/AAAI/article/view/20680)
- El protocolo *point adjustment* infla el F1 (hasta puntuaciones aleatorias parecen SOTA). → Nuestro protocolo: F1 por eventos / point-wise sin PA, declarado a priori (E3).

### B5. Hariri, Carrasco Kind & Brunner (2021). *Extended Isolation Forest*
- **Venue:** IEEE TKDE 33(4):1479–1489. **DOI:** [10.1109/TKDE.2019.2947676](https://experts.illinois.edu/en/publications/extended-isolation-forest-2) · [código](https://github.com/sahandha/eif)
- iForest con hiperplanos oblicuos; elimina artefactos del score con coste similar. Variante moderna citable de la familia iForest para el candidato "clásico".

### B6. Xu et al. (2023). *Deep Isolation Forest for Anomaly Detection*
- **Venue:** IEEE TKDE. **DOI:** [10.1109/TKDE.2023.3270293](https://dl.acm.org/doi/abs/10.1109/TKDE.2023.3270293) · [arXiv:2206.06602](https://arxiv.org/abs/2206.06602)
- Representaciones aleatorias + aislamiento; soporta series temporales (DeepOD). Tercer candidato opcional/baseline adicional.

### B7. Audibert et al. (2020). *USAD: UnSupervised Anomaly Detection on Multivariate Time Series*
- **Venue:** KDD 2020:3395–3404. **DOI:** [10.1145/3394486.3403392](https://dl.acm.org/doi/pdf/10.1145/3394486.3403392) · [código](https://github.com/manigalati/usad)
- Autoencoder adversario ligero (capas densas sobre ventanas) diseñado para producción (Orange). Patrón de referencia para nuestro autoencoder exportable a ONNX.

## SLMs en Raspberry Pi: evidencia verificada

**Fuente formal principal:** T. Nguyen (2025), *An Evaluation of LLMs Inference on Popular Single-board Computers*, [arXiv:2511.07425](https://arxiv.org/abs/2511.07425) — 25 LLMs Q4_K_M con Ollama/Llamafile en RPi 4/5 y Orange Pi 5 Pro. En **RPi 5**: ≤360M → >20 t/s; ≤1.5B → 5–15 t/s; ~3B → 2–5 t/s. Llamafile hasta 4× throughput y −30/40 % energía vs Ollama. "Punto dulce" de fiabilidad: ≤1.5B.

| Modelo (Q4) | t/s RPi 5 | RAM | Fuente |
|---|---|---|---|
| TinyLlama 1.1B | 18,4 | 0,7 GB | LocalAiMaster — **informal** |
| Llama 3.2 1B | 17,2 | 0,9 GB | LocalAiMaster — **informal** |
| Gemma 2 2B | 11,3 | 1,6 GB | LocalAiMaster — **informal** |
| Llama 3.2 3B | 8,8 | 2,1 GB | LocalAiMaster — **informal** |
| Qwen2.5 3B | 8,2 | 2,0 GB | LocalAiMaster — **informal** |
| Phi-3.5-mini 3.8B | 7,4 | 2,4 GB | LocalAiMaster — **informal** |
| Qwen2.5 1.5B | ~5 (Ollama) | baja | Stratosphere Lab — **informal** |
| Rango 3B | 2–5 | — | arXiv 2511.07425 — **formal** |
| Rango ≤1.5B | 5–15 | — | arXiv 2511.07425 — **formal** |

Notas: cifras informales coherentes con los rangos formales pero sensibles a configuración (refrigeración, hilos); discrepancia 8 t/s vs 2–5 t/s en 3B → **medir en nuestro perfil de recursos** (Fase 2, smoke test). Tamaños oficiales Ollama: llama3.2 1B = 1,3 GB; 3B = 2,0 GB. Sin cifras fiables de Phi-4-mini / Gemma 3 4B en RPi 5 al cierre del barrido.

## TinyML / ONNX en ARM

- **MLPerf Tiny Benchmark** (Banbury et al., NeurIPS 2021 D&B, [arXiv:2106.07597](https://arxiv.org/abs/2106.07597)): benchmark estándar; una de sus 4 tareas es detección de anomalías con autoencoder en microcontroladores → un AE de anomalías corre en hardware muy inferior a RPi 5.
- **Sai Charan (2022)**, SAE 2022-28-0406 ([DOI:10.4271/2022-28-0406](https://saemobilus.sae.org/articles/auto-encoder-based-tinyml-approach-real-time-anomaly-detection-2022-28-0406)): AE de 7,5 KB en Cortex-M4 para vibraciones (John Deere), ~80 % precisión. Antecedente automotriz directo.
- **Suryanarayanan & Gajula (2026)**, Future Internet 18(6):286 ([DOI:10.3390/fi18060286](https://www.mdpi.com/1999-5903/18/6/286)): CNN-AE 1.393 parámetros; INT8 con <1 punto de F1 perdido. *Solo simulación en CPU — citar con esa limitación.*
- **ONNX Runtime en ARM/RPi:** [tutorial oficial](https://onnxruntime.ai/docs/tutorials/iot-edge/rasp-pi-cv.html) y [Arm Learning Path](https://learn.arm.com/learning-paths/mobile-graphics-and-gaming/onnx/). [linkedin/isolation-forest](https://github.com/linkedin/isolation-forest) exporta iForest a ONNX → un solo runtime para ambas técnicas.

## Recomendación preliminar (para ratificar al inicio de Fase 2)

**Detección:** (a) **Isolation Forest** (scikit-learn; EIF/DIF citables) vs (b) **autoencoder por reconstrucción tipo USAD** (denso, ventanas deslizantes, ONNX INT8), más baseline z-score robusto. B2 justifica exactamente este emparejamiento; B3+B4 fijan el protocolo de evaluación honesto.
**LLMs candidatos:** Qwen2.5 3B (equilibrio calidad/multilingüe), Llama 3.2 3B (alternativa directa), Gemma 2 2B o Llama 3.2 1B como opción rápida/fallback. Phi-3.5-mini como cota superior (2,4 GB deja poco margen si AE + captura corren en paralelo). Todas las cifras se re-medirán en nuestro perfil de recursos.
