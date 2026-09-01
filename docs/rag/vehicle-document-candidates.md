# Candidatos: vehículo y documentación

Fecha: 1 de septiembre de 2026 · Rango exigido: 2000–2016, gasolina, OBD-II

El objetivo **no** es el vehículo más popular, sino el que combine mejor datos
OBD-II reales, documentación diagnóstica, manual de taller, cobertura de DTC,
trazabilidad y reproducibilidad.

## Canales oficiales de los tres fabricantes

Los tres tienen canal propio de suscripción para talleres independientes. **No
hace falta recurrir a agregadores de terceros para ninguno.**

| Fabricante | Portal oficial | Cobertura | Acceso |
|---|---|---|---|
| Mazda | mazdatechinfo.com · mazdaserviceinfo.com | Manuales desde 1996; boletines desde 1990 | Suscripción: día, mes, semestre, año |
| Honda | techinfo.honda.com | Service Information System | Pases cortos; parte de la oferta migrada a i-HDS |
| Toyota | techinfo.toyota.com (TIS) | Desde el año-modelo 1990 | Suscripción con pases cortos |

Además, la base pública de NHTSA contiene material de algunos fabricantes sin
coste.

Lo relevante: **para los tres existe una vía legítima y barata**. Un pase de un
día es suficiente para adquirir la documentación de un vehículo concreto con
cadena de procedencia verificable.

## Comparación

| Criterio | **Mazda 3 BK 2007** | Honda Civic (2000–2016) | Toyota Corolla (2000–2016) |
|---|---|---|---|
| OBD-II | Sí | Sí | Sí |
| Motor de combustión | Gasolina: ZJ 1.4, Z6 1.6, LF 2.0, L3 2.3 | Gasolina | Gasolina |
| Manual de taller | **Disponible en local, verificado en contenido** | Vía techinfo.honda.com | Vía TIS |
| Cobertura de DTC | **85 % de los ficheros de servicio; 207 códigos distintos en una muestra de 250** | Por confirmar | Por confirmar |
| Procedimientos diagnósticos | **Confirmados por inspección** | Por confirmar | Por confirmar |
| Diagramas eléctricos | Sección presente | Por confirmar | Por confirmar |
| Manual del propietario | Público | Público | Público |
| Canal oficial | mazdatechinfo.com | techinfo.honda.com | techinfo.toyota.com |
| Descargable ahora | **Sí, ya en local** | Requiere suscripción | Requiere suscripción |
| Completitud verificada | Contenido sí; procedencia no | No evaluada | Ninguna: intento fallido |
| Licencia de la copia | **No redistribuible** | Sujeta a suscripción | Sujeta a suscripción |

## Recomendación: Mazda 3 BK 2007

Es el único de los tres con **documentación diagnóstica disponible y verificada
por inspección directa** en este momento.

Cifras medidas sobre la copia local, no estimadas:

- 3 055 ficheros PDF · 238 MB
- Estructura por secciones: `introduction`, `engine`, `mission`, `srvc`, `esi_common`
- **85 %** de los ficheros de `srvc/` contienen al menos un DTC
- **207** códigos DTC distintos en una muestra aleatoria de 250 ficheros de 2 580
- Motores mencionados: **LF, Z6, ZJ**
- Texto auténtico de manual de taller Mazda: *foreword* de Mazda Motor
  Corporation, identificadores de documento del sistema ESI

Para el experimento eso significa evidencia documental real sobre la que medir
recuperación, cobertura de afirmaciones y abstención. Los otros dos candidatos
exigirían adquirir la documentación primero, y **el intento con Toyota fracasó**:
la única URL pública declarada devuelve 403 desde su almacenamiento.

## La objeción a la copia local

El **contenido** es genuino. La **procedencia de la copia** no lo es:

| | |
|---|---|
| `/Author` | `Roy` |
| `/Producer`, `/Creator` | `Soda PDF` |
| Fecha de conversión | 15 de febrero de 2019 |
| Rutas incrustadas | `file:///R:/My Websites/Files/001 NEW/Mazda 3 BK/html/...` |

Es una conversión a PDF hecha por un tercero a partir de una versión HTML, para
publicarla en un sitio web. No procede del canal oficial de Mazda.

Consecuencias, ninguna de las cuales impide el trabajo:

1. **No se redistribuye.** `redistributable: false`. Los binarios están excluidos
   del control de versiones; el repositorio registra que el documento existe, con
   su huella, sin incluirlo.
2. **`verified: false`.** Falta confirmar contra el catálogo oficial el número de
   manual, la revisión y el rango exacto de motores. Un documento sin verificar
   no puede sostener evidencia científica: el nombre del fichero no prueba nada.
3. **La cadena de procedencia queda coja.** Para la memoria del TFM conviene
   re-adquirirlo por mazdatechinfo.com. Un pase corto es asequible y produce una
   procedencia citable, que es justamente lo que la pregunta de investigación
   exige poder demostrar.

La recomendación no es descartarlo: es usarlo para construir y probar la
infraestructura, y re-adquirirlo por el canal oficial antes de que sus citas
lleguen a la memoria.

## El bloqueo que sigue en pie

Hay manual del Mazda 3 BK. **No hay datos OBD-II de un Mazda 3 BK.**

Todos los datos actuales son sintéticos: los produce un modelo paramétrico que no
corresponde a ningún vehículo real, y su identidad no puede casar legítimamente
con documentación de un Mazda. El validador de aplicabilidad lo rechazará, que es
su cometido.

La condición FULL del experimento necesita **las dos cosas del mismo vehículo**:
documentación aplicable y datos OBD-II reales. Elegir el vehículo no es solo
elegir de qué coche conseguir el manual; es comprometerse a obtener registros
OBD-II de ese mismo coche.
