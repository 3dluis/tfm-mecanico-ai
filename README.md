# Trabajo práctico del TFM

**Explicación verificable y abstención en el diagnóstico vehicular mediante inteligencia artificial y
recuperación aumentada**

Este directorio **es** el trabajo práctico del Trabajo Fin de Máster en Inteligencia Artificial
(UAX, Luis Daniel Díaz, 2026), empaquetado para que se pueda leer, ejecutar y verificar sin
depender de ningún otro repositorio ni de la máquina en que se construyó.

> **Entrega final**, noviembre de 2026.

## Qué hay aquí

| Dónde | Qué es |
|---|---|
| `notebooks/` | los siete notebooks científicos, uno por bloque experimental |
| `notebooks/html/` | **los mismos notebooks ya ejecutados**, con sus figuras dentro: se abren en un navegador sin instalar nada |
| `src/mecanico_ia_exp/` | el código: generador de señales, modelos, recuperación, verificador de suficiencia y las funciones de visualización |
| `artifacts/` | las tablas, las métricas, las figuras del documento y el análisis contrafactual |
| `experiments/` | el registro JSON de cada ejecución, con su commit, su semilla y sus métricas |
| `data/` | la muestra redistribuible y los conjuntos sintéticos que sí pueden viajar |
| `configs/` | la configuración, los manifiestos y el censo de artefactos históricos |
| `scripts/` | instalación, ejecución y verificación del paquete |
| `tests/` | las pruebas que sostienen lo anterior |

### La documentación del laboratorio no viaja en el paquete

Metodología, decisiones, auditorías, pre-registros y el texto fuente de la memoria estaban en
`docs/` y ese directorio **no forma parte del paquete**.

Lo que sigue citando rutas de `docs/` (este README más abajo y los apartados de trazabilidad de
los notebooks) nombra documentos que no están presentes aquí. Eso tiene **dos consecuencias
concretas**: las pruebas que comprueban que esos documentos y los artefactos concuerdan no viajan,
porque sin los documentos no pueden pasar; además, el manifiesto de congelación de la evaluación
final ancla por huella un documento de metodología, de modo que esa verificación concreta no se
puede ejecutar aquí. Las 528 pruebas que sí viajan se ejecutan: 515 pasan, una se omite y doce
necesitan PostgreSQL con pgvector.

## Por dónde empezar, según lo que se quiera hacer

**Leer sin instalar nada.** Los HTML de `notebooks/html/`. No hacen falta Python ni Jupyter: se
abren en cualquier navegador y traen dentro sus figuras y sus tablas.

> **La memoria académica no viaja en esta copia.** Este repositorio publica el **trabajo
> práctico**; el documento se entrega por su propio cauce.

**Ejecutar los notebooks.**

```bash
bash scripts/instalar.sh            # necesita internet UNA vez, para las dependencias
bash scripts/ejecutar_notebooks.sh  # a partir de aquí, sin red
```

**Comprobar que el paquete está completo.**

```bash
uv run python scripts/verificar_entrega.py
```

Recorre nueve familias de comprobaciones (ficheros, dependencias, notebooks, figuras, métricas,
datos, documentación, huellas y Git) y termina con código distinto de cero si algo falta. Las huellas
que compara están en `MANIFEST.json`, que se regenera con `scripts/generar_manifiesto.py`.

## Qué se puede reproducir y qué no

**Se reproduce.** Todas las figuras del documento se regeneran desde los registros congelados
con `uv run python scripts/figuras_memoria.py`. El conjunto canónico `synthetic_v2` se
reconstruye **bit a bit** desde su plan y su semilla. Una medición lo comprueba sesión
a sesión. Los siete notebooks se ejecutan en CPU, sin red y sin servicios externos.

**Qué no se reproduce y dónde está dicho.** Dos conjuntos, `synthetic_v1` y `synthetic_v3`, son
anteriores a la calibración del generador contra el manual de taller: el generador publicado
produce **otras señales**, de modo que no se pueden reconstruir y no se intenta. Dos figuras son
artefactos históricos cuya rutina ya no existe o cuyos datos intermedios no se guardaron; viajan
con su huella y con el motivo. El anexo C de la memoria lo detalla.

**Qué no viaja y por qué.** El manual de taller del fabricante tiene una licencia que no permite
redistribuirlo. Con él no viajan el índice documental ni los embeddings, que se construyen de
él. Los adaptadores del modelo de lenguaje pesan 28 MB cada uno y derivan de un modelo base con
licencia propia: viaja su configuración, que es lo que hace auditable el ajuste. `MANIFEST.json`
enumera cada exclusión con su motivo.

## Las dos modalidades

**DEMO** es lo que este paquete entrega entero: CPU, sin GPU, sin PostgreSQL, sin credenciales y
sin red durante la ejecución. Permite explorar las señales, regenerar las figuras, consultar las
métricas y las atribuciones, analizar la evaluación final y leer los resultados negativos.

**FULL** reejecuta las fases que dependen de los recursos de arriba. **No es autónoma**: exige
el manual, el índice vectorial y, para el ajuste del redactor, una GPU. Donde una prueba o un
notebook necesita algo que no está, **se detiene diciendo qué falta y cómo obtenerlo**, en lugar
de saltarse el paso en silencio.

## Verificar una huella

```bash
shasum -a 256 artifacts/figures/memoria/FIG-5-13_fiabilidad.png
uv run python -c "import json;print(json.load(open('MANIFEST.json'))['huellas_sha256']['artifacts/figures/memoria/FIG-5-13_fiabilidad.png'])"
```

---

# Resumen del trabajo

## Qué se investiga

Cuando un sistema de diagnóstico de vehículos explica una avería a partir de telemetría OBD-II,
la explicación suele evaluarse por si el diagnóstico final es correcto. Este trabajo estudia otra
propiedad: si **cada afirmación de la explicación puede seguirse hasta la evidencia que la sostiene**
(una observación de la telemetría o un fragmento identificable del manual de taller) y si el
sistema **se abstiene** cuando esa evidencia no basta.

> ¿Puede un agente con RAG explicar el diagnóstico de un vehículo a partir de datos OBD-II,
> rastreando cada explicación hasta su evidencia de origen y reconocer cuándo la evidencia
> disponible no es suficiente para sostener una explicación en lugar de generar una hipótesis
> sin fundamento?

## Recorrido experimental

```
telemetría OBD-II sintética, calibrada contra el manual del vehículo    (E2)
  → ventanas de 120 s y 139 descriptores, reparto por sesión              (E5)
  → modelo de diagnóstico con confianza calibrada                         (E6 bosque · E7 GRU)
  → atribución SHAP: evidencia observacional                              (E9)
  → recuperación sobre el manual de taller, filtrada por vehículo y motor (E11 · E12)
  → verificador determinista de suficiencia → EXPLAIN / ABSTAIN           (E15 · E18 · E19)
  → redactor (Qwen2.5-3B con adaptador LoRA), citas comprobadas contra el índice (E13)
```

El modelo de lenguaje no diagnostica ni decide: redacta lo que los componentes anteriores
produjeron. Vehículo de referencia: Mazda 3 BK 2007, motor Z6.

## Resultados principales

Las cifras salen de los registros de `experiments/` y de las tablas de `artifacts/tables/`; cada
notebook las imprime desde ellos. Su lectura completa está en el capítulo 5 de la memoria.

- **Diagnóstico (PI.1, notebook 02).** El bosque aleatorio obtiene 0,879 de F1 macro en
  validación y 0,836 en prueba, frente a 0,074 de la clase mayoritaria. La calibración reduce el
  error de calibración de 0,144 a 0,085 en validación; en prueba apenas lo cambia (de 0,097 a
  0,092). La red recurrente (0,823) no supera al bosque.
- **Recuperación (PI.2, notebook 05).** La búsqueda semántica pura no encuentra el procedimiento
  relevante en ninguno de los cinco casos puntuados; guiada por el diagnóstico lo encuentra en los
  cinco.
- **Evaluación final sobre el conjunto de prueba (PI.3, notebook 03).** Falsa confianza 0 de 14,
  abstención innecesaria 2 de 8 y respuesta con evidencia completa en 6 de 10. Con 0 de 14 el
  intervalo de Wilson al 95 % llega al 21,5 % por ejecución; es más ancho porque las catorce
  ejecuciones proceden de siete sesiones. Una política que explicara siempre que el modelo confía
  habría dado 14 de 14.
- **Qué componente evita la falsa confianza (notebook 05).** Sin exigir que el fragmento sostenga
  lo afirmado (ablación A3), la falsa confianza en validación pasa de 0 de 9 a 6 de 9; con la
  confianza sola (A4), a 9 de 9.
- **Evidencia que parece pertinente (PI.4, notebook 05).** En tres situaciones construidas (seis
  ejecuciones) el sistema se abstiene siempre por cobertura de afirmaciones insuficiente. No se
  estima ninguna tasa.
- **Redacción.** Ninguna cita inventada. En la evaluación final, 9 de las 35 salidas del redactor
  contienen al menos una cifra que el verificador no produjo; ninguna decisión cambia, porque las
  toma el verificador.

## Límites

La telemetría es sintética y la validación externa con datos reales queda fuera de este trabajo.
El conjunto de prueba se abrió cinco veces (tres intentos de la evaluación final, una repetición
de las ablaciones y una apertura accidental). Tres de los cuatro criterios de las subpreguntas se
reformularon con parte de los resultados ya conocida. El soporte de cada afirmación lo juzga el
propio verificador, sin anotación independiente. El adaptador del redactor se ajustó sobre
ventanas de validación. Los objetivos OE2 y OE4 quedan parcialmente cumplidos (Tabla 6.1 de la
memoria).

## Cómo reproducir desde este paquete

```bash
bash scripts/instalar.sh                          # dependencias, una sola vez con red
bash scripts/ejecutar_notebooks.sh                # los siete notebooks, en CPU y sin red
uv run python scripts/verificar_entrega.py        # integridad del paquete
uv run pytest -m "not db"                         # 515 pasan; 12 más necesitan PostgreSQL
uv run python scripts/figuras_memoria.py          # las figuras de la memoria
bash scripts/reconstruir_datos.sh                 # reconstruye synthetic_v2 y comprueba sus huellas
```

Lo que exige recursos que no viajan (el manual de taller, PostgreSQL con pgvector y, para el ajuste
del redactor, una GPU) está detallado en el anexo C de la memoria.

## Estructura del paquete

| Ruta | Contenido |
|---|---|
| `src/mecanico_ia_exp/` | código: generador OBD-II, descriptores, modelos, atribución, recuperación, verificador de suficiencia y redactor |
| `experiments/` | registros JSON de cada ejecución, con commit, semilla y métricas |
| `artifacts/` | figuras, tablas y métricas de la memoria, con su procedencia |
| `research/` | decisiones de diseño (ADR-001 a ADR-004), registro de limitaciones y referencias |
| `configs/` | calibración del generador, conjuntos anotados y estado congelado de la evaluación final |
| `data/` | muestra redistribuible en `data/samples/`; el resto se regenera |
| `notebooks/` | los siete notebooks, generados desde `scripts/notebooks/` |
| `notebooks/historico/` | cuadernos de fase anteriores, conservados como registro |
| `notebooks/html/` | copia ejecutada de cada notebook, legible sin instalar nada |
| `tests/` | 29 ficheros, 528 pruebas |
