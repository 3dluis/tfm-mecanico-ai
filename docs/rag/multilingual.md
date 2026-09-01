# Corpus multilingüe: español e inglés

## El caso real

El trabajo se escribe en **español**. El manual del fabricante está en **inglés**.
Una consulta en español contra documentación en inglés no es un caso raro: es el
caso normal de este experimento.

Eso se llama recuperación **translingüe**, y no funciona sola.

## La medición que lo justifica

Sin filtro por DTC, buscando el documento relevante entre los 500 primeros
resultados, sobre los cinco casos con documento conocido:

| Modelo | Idioma de la consulta | Hallados en top-500 | Posición mediana |
|---|---|---|---|
| monolingüe inglés | inglés | 5/5 | 47 |
| monolingüe inglés | **español** | **1/5** | **376** |
| multilingüe | inglés | 4/5 | 58 |
| multilingüe | **español** | **4/5** | **54** |

El modelo monolingüe **se hunde** con consultas en español: encuentra uno de
cinco documentos, y el que encuentra está en la posición 376. Seguía devolviendo
resultados, con puntuaciones de aspecto razonable, y eran casualidad.

El modelo multilingüe deja la recuperación en español al mismo nivel que en
inglés: 4 de 5, mediana 54 frente a 58.

Por eso el modelo por defecto pasa a ser
`paraphrase-multilingual-MiniLM-L12-v2`. Tiene **384 dimensiones**, las mismas
que el anterior, así que el cambio no obligó a migrar el esquema vectorial.

## Un efecto que estuvo a punto de pasar desapercibido

La primera medición se hizo **con** el filtro por DTC de la estrategia
`diagnosis-guided`, y dio Hit@10 = 1,00 en las cuatro combinaciones de modelo e
idioma. Parecía que el idioma daba igual.

No daba igual: **el filtro estaba tapando el efecto**. Una vez acotada la
búsqueda a los fragmentos que portan el código correcto, quedan pocos candidatos
y casi cualquier ordenación encuentra el bueno. El efecto del idioma solo aparece
cuando la recuperación tiene que elegir entre 6 158 fragmentos.

Es la misma lección que E4 y E5 dejaron por otras vías: **un efecto real puede
quedar enmascarado cuando el margen de maniobra es pequeño**, y medir en la
condición equivocada lleva a concluir que no existe.

## Los dos modelos conviven

El índice contiene los 6 158 fragmentos embebidos **dos veces**, una por modelo.
Es deliberado: permite comparar sobre el mismo corpus sin mantener dos bases.

La consecuencia es que **`search` filtra por modelo**. Mezclar dos espacios
vectoriales en una consulta compararía puntos de espacios distintos, y los
resultados serían ruido con aspecto de orden. Hay un test que comprueba que ambos
modelos están presentes y que cada uno se consulta por separado.

## Idioma como metadata de primera clase

`language` viaja en el documento, en el fragmento y en el registro de cada
recuperación. Determina tres cosas:

**Qué configuración usa la búsqueda de texto completo.** `to_tsvector('english',
…)` sobre texto español lematiza mal: no reconoce «ralentí» ni «combustible» como
raíces. Hay un índice por idioma, `english` y `spanish`, y cada fragmento se
busca con el suyo.

**Si un embedding es comparable con otro.** Ver la tabla de arriba.

**Qué se puede citar en qué idioma.** Una explicación en español que cita un
procedimiento en inglés debe poder mostrar el original. Traducir la cita al
redactarla la haría incomprobable contra la fuente, que es justamente lo que la
trazabilidad exige.

## La búsqueda léxica no cruza idiomas

La semántica sí; la léxica no, y no debe. Buscar «ajuste de combustible ralentí»
en un corpus inglés devuelve **cero**, y eso es correcto: cualquier coincidencia
sería un accidente ortográfico, no un hallazgo. Hay un test que lo comprueba.

## El idioma se declara, no se detecta

Sale del manifiesto del documento. Detectarlo automáticamente introduciría un
error silencioso en un campo del que dependen la búsqueda léxica y la elección
de modelo. Quien registra un documento declara su idioma; es su responsabilidad y
queda escrita.

## Documentos en español

El corpus actual es **solo inglés**: es lo que hay del Mazda 3 BK. La
infraestructura ya admite documentos en español --basta declarar `language: es`
en el manifiesto-- y los buscará con la configuración correcta.

Cuando se incorporen, convivirán con los ingleses en el mismo índice y una misma
consulta podrá recuperar de ambos, porque el espacio vectorial es compartido. Lo
que **no** se hará es traducir el manual para indexarlo: una traducción
automática deja de ser el documento del fabricante, y una cita a una traducción
no verificada no es una cita.
