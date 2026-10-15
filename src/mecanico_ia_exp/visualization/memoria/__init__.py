"""Las figuras de la memoria, una función por figura y una sola implementación.

**Por qué este paquete existe.** Las figuras del documento se dibujaban desde un
guion de `scripts/`, fuera del paquete y fuera de la comprobación de tipos. Eso
tenía dos consecuencias: el código científico que produce una figura no se podía
importar desde un notebook, y nada impedía que la misma figura acabara dibujada
dos veces de dos maneras distintas.

Aquí vive la implementación. El guion `scripts/figuras_memoria.py` queda como lo
que debe ser: un registro de qué figura lleva cada número y una orden de consola.

**Qué garantiza cada función.** Recibe los datos de un registro de ejecución o de
una tabla congelada, y **no escribe ningún valor a mano**. Si el registro no está,
falla; no inventa el dato ni lo aproxima.

**Dónde se dibuja.** Todas a 5,9 pulgadas de ancho, que es el ancho útil de la
página con los márgenes de la plantilla. Una figura más ancha la escala el
procesador de textos al entrar, y el escalado encoge las etiquetas.
"""

from __future__ import annotations

from mecanico_ia_exp.visualization.memoria.ablaciones import fig_ablaciones, tasas_e15
from mecanico_ia_exp.visualization.memoria.base import (
    ANCHO_DE_PAGINA,
    CONDICION,
    estilo_para_impresion,
    guardar,
    numero,
    panel,
)
from mecanico_ia_exp.visualization.memoria.calibracion import (
    agrupar,
    comprobacion_de_la_reconstruccion,
    fig_calibracion,
    fig_fiabilidad,
    intervalos_de_fiabilidad,
)
from mecanico_ia_exp.visualization.memoria.datos import (
    fig_particiones,
    fig_separabilidad_dispersion,
    fig_separabilidad_nivel,
)
from mecanico_ia_exp.visualization.memoria.decision import (
    decisiones_de_e19,
    fig_decisiones_y_umbral,
)
from mecanico_ia_exp.visualization.memoria.diagnostico import (
    fig_confusiones,
    fig_confusor_de_volumen,
    fig_f1_por_clase,
)
from mecanico_ia_exp.visualization.memoria.mezcla_pobre import (
    fig_mezcla_pobre,
    separabilidad_entre_mezclas_pobres,
)
from mecanico_ia_exp.visualization.memoria.recuperacion import fig_recuperacion
from mecanico_ia_exp.visualization.memoria.riesgo_cobertura import (
    compromiso_del_umbral,
    fig_riesgo_cobertura,
)
from mecanico_ia_exp.visualization.memoria.sintesis import fig_compromiso, fig_objetivos
from mecanico_ia_exp.visualization.memoria.temporal import (
    fig_forma_del_fallo,
    fig_pareja_contrafactual,
    fig_ventana_y_descriptor,
    recuento_de_expresion,
)

__all__ = [
    "ANCHO_DE_PAGINA",
    "CONDICION",
    "agrupar",
    "comprobacion_de_la_reconstruccion",
    "compromiso_del_umbral",
    "decisiones_de_e19",
    "estilo_para_impresion",
    "fig_ablaciones",
    "fig_calibracion",
    "fig_compromiso",
    "fig_confusiones",
    "fig_confusor_de_volumen",
    "fig_decisiones_y_umbral",
    "fig_f1_por_clase",
    "fig_fiabilidad",
    "fig_forma_del_fallo",
    "fig_mezcla_pobre",
    "fig_objetivos",
    "fig_pareja_contrafactual",
    "fig_particiones",
    "fig_recuperacion",
    "fig_riesgo_cobertura",
    "fig_separabilidad_dispersion",
    "fig_separabilidad_nivel",
    "fig_ventana_y_descriptor",
    "guardar",
    "intervalos_de_fiabilidad",
    "numero",
    "panel",
    "recuento_de_expresion",
    "separabilidad_entre_mezclas_pobres",
    "tasas_e15",
]
