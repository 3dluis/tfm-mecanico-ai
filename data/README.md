# Datos

## Qué hay en este directorio

| Ruta | Versionado | Contenido |
|---|---|---|
| `data/samples/synthetic_sample.parquet` + `.meta.json` | sí | Muestra sintética redistribuible: 18 sesiones (3 por condición, 6 condiciones), 600 s a 1 Hz, 10 800 filas, 1,3 MB. Generada el 13-09-2026 con `uv run mecanico-exp generate-synthetic --dataset-id synthetic_sample --sessions-per-fault 3 --duration-s 600` (semilla 20260901) sobre el commit `487e98a`; el `.meta.json` registra generador, versión, semilla y fecha |
| `data/raw/synthetic/` | no (se regenera) | Los conjuntos de los experimentos: `synthetic_v1` (36 sesiones), `synthetic_v2` (72 sesiones; el de todos los resultados de la memoria) y `synthetic_v3`. Generador determinista: dos ejecuciones con la misma semilla producen ficheros idénticos (verificado en E2) |
| `data/raw/real/` | vacío | Reservado para datos reales (E3, no ejecutado) |
| `data/processed/` | no | Ventanas, descriptores y conjuntos de ajuste derivados; se regeneran con `preprocess` y `training-data` |

## Flujo de demostración con la muestra

La muestra tiene el mismo esquema que `synthetic_v2` y admite el reparto por sesión sin
particiones vacías. Para ejecutarla con los runners:

```
cp data/samples/synthetic_sample.parquet data/samples/synthetic_sample.meta.json data/raw/synthetic/
uv run mecanico-exp preprocess --dataset-id synthetic_sample
uv run mecanico-exp train-baseline --dataset-id synthetic_sample
```

Produce `experiments/E6_baseline_synthetic_sample.json` y las tablas y figura de E6. **No es
un resultado del TFM**: con 3 sesiones por condición el reparto deja una sesión por partición
y las cifras no son comparables con las de `synthetic_v2`. Sirve para comprobar que el flujo
funciona y para ver el formato de los datos.

## Qué no está incluido y por qué

| Dato | Motivo | Cómo obtenerlo |
|---|---|---|
| Manual de taller del Mazda 3 BK (3 055 PDF, 238 MB) | Documentación del fabricante, `access_type: licensed`, `redistributable: false`; el manifiesto además declara `verified: false` (procedencia no oficial) | Por el canal del fabricante (Mazda Technical Information, según `corpus/vehicles/mazda-3-bk-2007/manifest.yaml`); colocarlo en `corpus/vehicles/mazda-3-bk-2007/raw/user-provided/workshop-manual/` y ejecutar `scripts/ingest_mazda.py multilingual`. El manifiesto registra las huellas SHA-256 con las que verificar que es el mismo contenido |
| Índice vectorial (2 × 6 158 vectores en PostgreSQL) | Derivado del manual; no redistribuible por la misma razón | Se reconstruye con la ingesta anterior (68 s en MPS) |
| Pesos del adaptador LoRA (`adapter_model.safetensors`, 28 MB × 2) | Tamaño; y el adaptador está marcado no canónico | `uv run mecanico-exp finetune-slm --adapter-dir slm_lora_v2` (~75 min en M4 Pro); configuración e historial de pérdida sí versionados en `models/slm_lora_v2/` |
| Modelo base Qwen2.5-3B-Instruct | Tamaño; se descarga de Hugging Face al primer uso | `transformers` lo descarga en `from_pretrained` |
| `synthetic_v1`, `v2`, `v3` completos | Política del proyecto: se versiona el generador, no su salida | `uv run mecanico-exp generate-synthetic --dataset-id synthetic_v2 --sessions-per-fault 12` |

No hay datos personales ni sensibles en ningún conjunto: toda la telemetría es sintética.
