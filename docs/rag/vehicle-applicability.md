# Aplicabilidad al vehículo

## Grados

| Grado | Significado | ¿Evidencia fuerte? |
|---|---|---|
| `EXACT_MATCH` | Coinciden identidad y refinamiento comprobables | Sí |
| `COMPATIBLE` | Coincide la identidad; no consta que difiera nada más | Solo bajo política declarada |
| `PARTIAL_MATCH` | Coincide la identidad, difiere un campo secundario | No |
| `UNKNOWN` | Falta información para decidir | **Nunca** |
| `INCOMPATIBLE` | Difiere un campo identificador | No |

**Identidad**: fabricante, modelo, año.
**Refinamiento**: generación, mercado, código de motor, transmisión.

## Por qué `UNKNOWN` no es evidencia

Es la decisión de diseño más importante de este módulo. `UNKNOWN` significa que
no se puede afirmar que el documento aplique. Tratarlo como válido convertiría la
ignorancia en respaldo, que es precisamente el fallo que este trabajo estudia.

Ante la duda, el validador devuelve `UNKNOWN` y el agente se queda sin esa
evidencia. Es preferible abstenerse a sostener una explicación sobre
documentación de otro coche.

## Por qué el motor importa

Un mismo modelo y año puede llevar motorizaciones, transmisiones, mercados y
configuraciones de emisiones distintas. «Toyota Corolla 2020» por sí solo **no
selecciona un procedimiento de taller**.

Cuando se disponga del vehículo real conviene registrar VIN, código de motor,
tren motriz y mercado, sin almacenar información personal innecesaria. Si un
procedimiento solo aplica a un motor concreto, ese dato se conserva en el
fragmento y el validador lo usa.

## Ejemplo

```python
validador = VehicleApplicabilityValidator(perfil_del_experimento)
grado = validador.validate(perfil_declarado_por_el_documento)

if not validador.is_strong_evidence(perfil_declarado_por_el_documento):
    # El fragmento no puede sostener la afirmación por sí solo.
    ...
```
