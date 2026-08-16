# F-PREREG — reconciliación y congelación del pre-registro (`prereg-v1.0`)

**Estado:** DEFINIDA, NO EJECUTADA · **Bloquea:** cualquier afirmación confirmatoria ·
**No bloquea:** H2, H3, H4 ni la memoria, que son exploratorios o descriptivos.

## Por qué existe

La regla F10 del proyecto es explícita: **ningún experimento confirmatorio puede ejecutarse
antes de congelar el pre-registro.** Hoy conviven dos documentos con pretensión de
pre-registro y no están reconciliados, de modo que ni siquiera está claro qué se congelaría.
Mientras eso siga así:

- toda la serie EXP-ANOM-001…010-R2 es **exploratoria**, sin excepción;
- `PROMOTE_CANDIDATE` en F22 significa candidato, **no** adopción;
- el estado `SUPPORTED` de H1 es exploratorio y no puede presentarse como validación.

## Entradas

| Documento | Ubicación | Nota |
|---|---|---|
| Pre-registro principal | `docs/experiments/preregistered/PROTO-CONF-001.md` (rama `main`) | Congelado para H-EVT con `arms-freeze-v1` y datos ocultos `suite_conf_v1` (semillas 901-925) |
| Pre-registro alternativo / v2 | rama `backup-alineacion-cientifica` | Parte del «paquete de alineación científica» sin adoptar |
| Protocolo ML v1 y adendas | `docs/experiments/protocolo_ml_v1*.md` | Define la línea exploratoria; no es un pre-registro confirmatorio |

## Procedimiento (en este orden, sin saltarse pasos)

1. **Comparar** ambos documentos y producir una tabla de diferencias explícita: hipótesis,
   métricas, criterios, particiones, semillas, brazos, reglas de parada.
2. **Resolver contradicciones** una a una, dejando por escrito cuál se adopta y por qué. Una
   contradicción resuelta «en silencio» invalida el freeze entero.
3. **Congelar hipótesis** confirmatorias: enunciado, dirección del efecto y condición de
   falsación. Solo las que se vayan a poder contrastar realmente en el plazo.
4. **Congelar métricas** y su forma exacta de cálculo (incluida la agregación multi-semilla).
5. **Congelar criterios** de decisión numéricos, con sus umbrales.
6. **Congelar datasets y semillas**: qué partición confirmatoria se usa, qué semillas quedan
   reservadas y la comprobación de que no se han gastado.
   Reservadas hoy: **901-925, 11000-20036, 30000-30079, 55000, 111000+**.
7. **Crear el tag `prereg-v1.0`** en el repositorio. El tag es la prueba de anterioridad.

## Reglas durante la ejecución de la tarea

- **No reinterpretar experimentos exploratorios como confirmatorios.** Ni uno. Si un
  resultado exploratorio es interesante, se cita como exploratorio.
- No ajustar el pre-registro a lo que ya se sabe que sale bien. Si una hipótesis se
  pre-registra sabiendo el resultado, no es un pre-registro: es una declaración.
- Ningún confirmatorio se ejecuta hasta que apruebes el freeze explícitamente.

## Salida

- `docs/experiments/preregistered/PROTO-CONF-001.md` reconciliado, o un documento nuevo que
  lo supersede declarándolo;
- tabla de diferencias y decisiones adoptadas;
- tag `prereg-v1.0`;
- nota en el roadmap indicando qué queda habilitado a partir de ese punto.

## Coste estimado

Trabajo documental, sin cómputo. La parte cara es la decisión, no la ejecución.
