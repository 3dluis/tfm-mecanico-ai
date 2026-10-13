"""Expresión efectiva de un fallo: ¿alteró la trayectoria, o solo se aplicó?

``fault_active`` responde a una pregunta del generador --«¿se llamó a la función
de fallo en este instante?»-- y no a la pregunta del experimento, que es si el
fallo **produjo una alteración observable**. Las dos se separan porque varias
condiciones del catálogo no alteran nada en parte de su ventana de actividad:

* el termostato bloqueado solo recorta la temperatura cuando el refrigerante ya
  superó el tope, de modo que en las primeras ventanas de una sesión de
  calentamiento la función se aplica y no cambia ni un valor;
* el fallo de encendido es episódico: fuera de un episodio la función se aplica
  y devuelve la muestra intacta.

Usar ``fault_active`` como si significara «el fallo se manifestó» convierte esas
muestras en evidencia de algo que no ocurrió.

## Cómo se determina

Por **contrafactual**. El motor de señales mantiene su estado al margen del
fallo --``tick`` devuelve una copia del diccionario de valores, y la función de
fallo muta esa copia-- así que la trayectoria sin fallo de la misma sesión, con
la misma semilla, es exactamente reproducible: basta no aplicar la función. La
comparación se hace **después del recorte a rango físico**, que es el valor que
llega al modelo: si el fallo empuja una señal fuera de lo posible y el recorte la
devuelve al mismo valor, no hay alteración observable y no debe contarse como
tal.

## Qué cuenta como observable, y por qué ese umbral

Una diferencia de 1e-16 es una diferencia aritmetica, no una alteración. El
umbral se fija **contra el ruido propio del generador**: cada señal recibe en
``obd/engine.py`` una perturbacion gaussiana con una desviacion tipica declarada, y una
alteración por debajo de una fracción de ese ruido es indistinguible del propio
proceso de generación.

El umbral de cada señal es por tanto el producto de ``RATIO_DECLARADO`` por la
desviacion tipica que el motor declara para ella. ``RATIO_DECLARADO`` es un **parámetro de este
protocolo**, no una magnitud documentada del vehículo, y se elige
deliberadamente permisivo --una décima parte del ruido-- para no ocultar
alteraciones reales.

**La desviación se almacena en unidades de ese umbral**, no en unidades físicas,
de modo que el dato no lleva ninguna decisión horneada: una lectura más estricta
con razón ``r`` se obtiene comparando ``fault_deviation_max`` contra
``r / RATIO_DECLARADO`` sin regenerar nada.

**Y para las dos condiciones en que la distinción importa, el umbral es
irrelevante:** fuera del episodio de encendido y por debajo del tope del
termostato la desviación es **exactamente cero**, no pequeña. La clasificación de
esas muestras no depende de ningún parámetro.
"""

from __future__ import annotations

from mecanico_ia_exp.obd.signals import SIGNAL_NAMES

#: Fracción del ruido propio del generador por debajo de la cual una alteración
#: no se considera observable. Parámetro declarado de este protocolo.
RATIO_DECLARADO = 0.10

#: Desviación típica del ruido que ``obd/engine.py`` añade a cada señal en cada
#: paso. Cada valor es el literal que aparece en ese módulo; donde el motor usa
#: dos --el regimen, con 12,0 en ralenti y 35,0 en marcha-- se toma **el menor**,
#: que es la elección conservadora: hace el umbral más exigente.
#:
#: ``ltft_bank1`` merece su nota: el motor lo mueve con desviacion 0,01 por paso porque
#: es un integrador lento, y eso es justamente lo que lo hace informativo cuando
#: se desplaza. Su umbral queda, por tanto, muy fino.
SIGMA_GENERADOR: dict[str, float] = {
    "rpm": 12.0,
    "vehicle_speed": 0.3,
    "engine_load": 2.0,
    "throttle_position": 1.5,
    "coolant_temperature": 0.15,
    "intake_air_temperature": 0.4,
    "maf": 0.35,
    "map": 1.2,
    "stft_bank1": 1.6,
    "ltft_bank1": 0.01,
    "oxygen_sensor": 0.03,
    "ignition_timing": 0.8,
}

#: Valor que lleva ``fault_deviation_signal`` cuando no hubo ninguna alteración.
SIN_ALTERACION = ""


def tolerancias(ratio: float = RATIO_DECLARADO) -> dict[str, float]:
    """Umbral de observabilidad de cada señal, en sus propias unidades."""
    if ratio <= 0:
        msg = f"La razón debe ser positiva, recibida {ratio}"
        raise ValueError(msg)
    faltan = set(SIGNAL_NAMES) - set(SIGMA_GENERADOR)
    if faltan:
        msg = f"Señales sin ruido declarado: {sorted(faltan)}"
        raise ValueError(msg)
    return {nombre: ratio * SIGMA_GENERADOR[nombre] for nombre in SIGNAL_NAMES}


def desviacion(
    con_fallo: dict[str, float],
    sin_fallo: dict[str, float],
    umbrales: dict[str, float],
) -> tuple[float, str]:
    """Mayor alteración de la muestra, medida en umbrales de su propia señal.

    Devuelve la magnitud y **qué señal** la lleva. Saber cuál es lo que permite
    después comprobar que la alteración está donde la ficha del fallo dice que
    debería estar, en lugar de confiar en que lo esté.
    """
    mayor = 0.0
    cual = SIN_ALTERACION
    for nombre in SIGNAL_NAMES:
        umbral = umbrales[nombre]
        relativa = abs(con_fallo[nombre] - sin_fallo[nombre]) / umbral
        if relativa > mayor:
            mayor, cual = relativa, nombre
    return mayor, cual
