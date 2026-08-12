# Referencias verificadas — baselines clásicos de detección de anomalías

> Verificadas contra Crossref/proceedings oficiales el 2026-08-12 (complemento de línea B).
> Justifican los baselines del ADR-0011.

- **Isolation Forest:** Liu, F.T.; Ting, K.M.; Zhou, Z.-H. (2008). *Isolation Forest.* ICDM 2008,
  pp. 413–422. DOI [10.1109/ICDM.2008.17](https://doi.org/10.1109/ICDM.2008.17). Versión de
  revista: *Isolation-Based Anomaly Detection*, ACM TKDD 6(1), 2012, art. 3.
  DOI [10.1145/2133360.2133363](https://doi.org/10.1145/2133360.2133363). Aislamiento por
  particiones aleatorias; coste lineal y memoria baja — apto edge.
- **LOF:** Breunig, M.M.; Kriegel, H.-P.; Ng, R.T.; Sander, J. (2000). *LOF: Identifying
  Density-Based Local Outliers.* SIGMOD 2000, pp. 93–104.
  DOI [10.1145/342009.335388](https://doi.org/10.1145/342009.335388). Atipicidad relativa a la
  densidad local — clave con normalidad multimodal (nuestro caso, ADR-0011 §hallazgo 1).
- **One-Class SVM:** Schölkopf, B.; Platt, J.C.; Shawe-Taylor, J.; Smola, A.J.; Williamson, R.C.
  (2001). *Estimating the Support of a High-Dimensional Distribution.* Neural Computation 13(7),
  1443–1471. DOI [10.1162/089976601750264965](https://doi.org/10.1162/089976601750264965).
  Antecedente: *Support Vector Method for Novelty Detection*, NIPS 1999
  ([proceedings](https://papers.nips.cc/paper_files/paper/1999/hash/8725fb777f25776ffa9076e44fcfd776-Abstract.html), sin DOI).
- **Z-score robusto (mediana/MAD):** Leys, C.; Ley, C.; Klein, O.; Bernard, P.; Licata, L. (2013).
  *Detecting outliers: Do not use standard deviation around the mean, use absolute deviation
  around the median.* J. Experimental Social Psychology 49(4), 764–766.
  DOI [10.1016/j.jesp.2013.03.013](https://doi.org/10.1016/j.jesp.2013.03.013). Fórmula del
  z modificado (0,6745·(x−med)/MAD, umbral 3,5): Iglewicz, B.; Hoaglin, D.C. (1993). *How to
  Detect and Handle Outliers.* ASQC Quality Press, ISBN 978-0-87389-247-6 (libro, sin DOI;
  ficha verificada en WorldCat/ASQ).
- **Survey marco:** Chandola, V.; Banerjee, A.; Kumar, V. (2009). *Anomaly Detection: A Survey.*
  ACM Computing Surveys 41(3), art. 15.
  DOI [10.1145/1541880.1541882](https://doi.org/10.1145/1541880.1541882). Taxonomía canónica
  (anomalía puntual/contextual/colectiva) — nuestras held-out son colectivas/contextuales.
