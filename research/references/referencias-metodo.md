# Referencias de método — verificadas el 2 de septiembre de 2026

La lista maestra (`references.md`, 144 entradas) procede del barrido de agosto y cubre el
dominio: OBD-II, diagnóstico vehicular, explicabilidad aplicada, RAG sobre documentación
técnica. **No contiene las referencias de los métodos que el laboratorio usa** (bosque
aleatorio, GRU, SHAP, calibración, predicción selectiva, RAG, LoRA, embeddings de frases,
fusión de rangos, Design Science Research). Sin ellas, los capítulos 3 y 4 citarían de memoria.

Cada entrada de abajo se comprobó el 2 de septiembre de 2026 contra **Crossref** (DOI) o el
**API de arXiv** (identificador), que son las mismas vías con las que se verificaron 110 de las
144 de la lista maestra. Se anota qué se comprobó. **No se han incorporado a la lista maestra**
para no alterar sus recuentos, que están pendientes de reconciliación (144 frente a 153
declaradas); la incorporación se hará en esa reconciliación.

| ID | Referencia (APA) | Identificador | Verificación |
|---|---|---|---|
| MET-01 | Breiman, L. (2001). Random forests. *Machine Learning, 45*(1), 5–32. | doi:10.1023/a:1010933404324 | Crossref: título, autor, revista, año |
| MET-02 | Cho, K., van Merriënboer, B., Gulcehre, C., Bahdanau, D., Bougares, F., Schwenk, H., & Bengio, Y. (2014). Learning phrase representations using RNN encoder–decoder for statistical machine translation. *Proceedings of EMNLP 2014*. | doi:10.3115/v1/d14-1179 | Crossref: título, autores, año |
| MET-03 | Lundberg, S. M., & Lee, S.-I. (2017). A unified approach to interpreting model predictions. *Advances in Neural Information Processing Systems, 30*. | arXiv:1705.07874 | arXiv: título, autores, año. Sin DOI en Crossref (NeurIPS) |
| MET-04 | Guo, C., Pleiss, G., Sun, Y., & Weinberger, K. Q. (2017). On calibration of modern neural networks. *Proceedings of ICML 2017*. | arXiv:1706.04599 | arXiv: título, autores, año. Sin DOI en Crossref (PMLR) |
| MET-05 | Zadrozny, B., & Elkan, C. (2002). Transforming classifier scores into accurate multiclass probability estimates. *Proceedings of KDD 2002*. | doi:10.1145/775047.775151 | Crossref: título, autores, año |
| MET-06 | Niculescu-Mizil, A., & Caruana, R. (2005). Predicting good probabilities with supervised learning. *Proceedings of ICML 2005*. | doi:10.1145/1102351.1102430 | Crossref: título, autores, año |
| MET-07 | Naeini, M. P., Cooper, G. F., & Hauskrecht, M. (2015). Obtaining well calibrated probabilities using Bayesian binning. *Proceedings of the AAAI Conference on Artificial Intelligence, 29*(1). | doi:10.1609/aaai.v29i1.9602 | Crossref: título, autores, año. Define el ECE usado en M1 |
| MET-08 | Chow, C. K. (1970). On optimum recognition error and reject tradeoff. *IEEE Transactions on Information Theory, 16*(1), 41–46. | doi:10.1109/tit.1970.1054406 | Crossref: título, autor, revista, año |
| MET-09 | Geifman, Y., & El-Yaniv, R. (2017). Selective classification for deep neural networks. *Advances in Neural Information Processing Systems, 30*. | arXiv:1705.08500 | arXiv: título, autores, año |
| MET-10 | Lewis, P., Perez, E., Piktus, A., Petroni, F., Karpukhin, V., Goyal, N., … Kiela, D. (2020). Retrieval-augmented generation for knowledge-intensive NLP tasks. *Advances in Neural Information Processing Systems, 33*. | arXiv:2005.11401 | arXiv: título, autores, año |
| MET-11 | Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence embeddings using Siamese BERT-networks. *Proceedings of EMNLP-IJCNLP 2019*. | doi:10.18653/v1/d19-1410 | Crossref: título, autores, año |
| MET-12 | Cormack, G. V., Clarke, C. L. A., & Buettcher, S. (2009). Reciprocal rank fusion outperforms Condorcet and individual rank learning methods. *Proceedings of SIGIR 2009*. | doi:10.1145/1571941.1572114 | Crossref: título, autores, año |
| MET-13 | Hu, E. J., Shen, Y., Wallis, P., Allen-Zhu, Z., Li, Y., Wang, S., Wang, L., & Chen, W. (2022). LoRA: Low-rank adaptation of large language models. *Proceedings of ICLR 2022*. | arXiv:2106.09685 | arXiv: título, autores. Publicado en ICLR 2022 (OpenReview) |
| MET-14 | Qwen Team (2024). Qwen2.5 technical report. | arXiv:2412.15115 | arXiv: título, año |
| MET-15 | Ji, Z., Lee, N., Frieske, R., Yu, T., Su, D., Xu, Y., … Fung, P. (2023). Survey of hallucination in natural language generation. *ACM Computing Surveys, 55*(12), 1–38. | doi:10.1145/3571730 | Crossref: título, autores, revista, año |
| MET-16 | Peffers, K., Tuunanen, T., Rothenberger, M. A., & Chatterjee, S. (2007). A design science research methodology for information systems research. *Journal of Management Information Systems, 24*(3), 45–77. | doi:10.2753/mis0742-1222240302 | Crossref: título, autores, revista, año |
| MET-17 | Hevner, A. R., March, S. T., Park, J., & Ram, S. (2004). Design science in information systems research. *MIS Quarterly, 28*(1), 75–105. | doi:10.2307/25148625 | Crossref: título, autores, revista, año |
| MET-18 | SAE International (2025). *J1979-DA: Digital annex of E/E diagnostic test modes*. | doi:10.4271/j1979da_202504 | Crossref: título, editor. Norma; la J1979 base se cita por su anexo digital, que es el documento con identificador |
| MET-19 | International Organization for Standardization. *ISO 15031-5: Road vehicles — Communication between vehicle and external equipment for emissions-related diagnostics — Part 5: Emissions-related diagnostic services*. | doi:10.3403/30301556 (edición BSI) | Crossref: título. `[VERIFY_SOURCE: confirmar edición, 2015 o posterior]` |

## Referencias que se buscaron y no se citan

Ninguna en esta tanda: todas las consultadas resolvieron. Si un capítulo necesita una
referencia que no está aquí ni en la lista maestra, se verifica antes de escribir la cita, no
después.
