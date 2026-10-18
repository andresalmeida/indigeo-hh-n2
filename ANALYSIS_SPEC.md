# Plan 046 — qué información añade la distribución de HH a la media cantonal

Fecha: 2026-10-17. Encargo directo del usuario: desarrollar los puntos 1 y 2 propuestos, con las tablas ya calculadas, una figura y texto para el manuscrito. Análisis exploratorio descriptivo; no validación temática, inferencia causal ni cambio observado. Esta especificación se fija antes de examinar las filas completas del nuevo análisis; las tablas de entrada ya eran conocidas por el proyecto.

## Fuentes y alcance

Sólo CSV sellados A (medias OWN y COMMON), B (bandas y particiones OWN y COMMON) y F5/utm.csv (pertenencia a la franja). 218 cantones continentales, 2014/2016/2018/2020/2022. No arrays, solver, Earth Engine, datos de parcelas ni BR. No se modifican categorías, fuentes, AD-1, índices cerrados ni SSOT. Los resultados nuevos se guardan en una cápsula separada, sin publicar.

La unidad es cantón × año × soporte; se excluyen subtotales y los territorios auxiliares de los CSV B. OWN usa el soporte anual; COMMON la intersección de los cinco cortes. Se comprobarán códigos, nombres, unicidad, completitud, denominadores y hashes antes de analizar.

## Pregunta y medidas

¿Hasta qué punto una media, o su banda ordinal, deja sin describir la superficie clasificada como presión alta? Alta conserva el corte HH ≥ 15; no es un umbral ecológico validado. Para cada cantón se mantienen los dos extremos de la media y el rango de porcentaje de superficie alta [garantizada, posible]. Nunca se sustituye por un punto medio.

Comparación principal: 2020, COMMON, 218 cantones. Se elige 2020 para que el ejemplo principal no cruce de versión VIIRS en 2022, no porque se haya observado el contraste más favorable. Las cinco fechas se analizan por separado como sensibilidad descriptiva.

Dos medias son próximas si la mayor distancia entre sus extremos no supera ε: max(|L_i − U_j|, |U_i − L_j|) ≤ ε. ε principal = 0.25 unidades HH; sensibilidades = 0.10 y 0.50. Es una convención descriptiva explícita, sin equivalencia científica ni prueba estadística.

Brecha mínima conservadora de superficie alta en puntos porcentuales:

    max(0, garantizada_i − posible_j, garantizada_j − posible_i).

Es una separación garantizada condicional a los intervalos del modelo, no un intervalo de confianza. Se entrega también la brecha máxima compatible con esos rangos. Para el ejemplo se exige además que ambas medias tengan una sola banda y sea la misma. Se enumeran TODOS los pares admisibles y se elige el de mayor brecha mínima; desempates: menor distancia máxima de medias, códigos cantonales ascendentes. Se declara expresamente que es un ejemplo extremo seleccionado, no un caso representativo ni evidencia inferencial.

Resultados de conjunto: número de pares próximos, número con brechas mínimas ≥ 1/5/10 puntos porcentuales, distribución del porcentaje alto dentro de cada banda de la media y amplitud de extremos. Los pares comparten cantones: no son observaciones independientes; no se calculan p-valores ni intervalos de muestreo. Los resúmenes entre cantones no ponderados describen cantones, no superficie nacional.

## Robustez y límites

- Repetir las medidas con OWN/COMMON, cinco años y ε 0.10/0.25/0.50, sin cambiar bandas.
- Repetir excluyendo completamente los 32 cantones que F5 identifica como tocados por la franja UTM; quedan 186. Es sensibilidad por exclusión, no corrección de UTM ni medición causal de su efecto. Mostrar también si el par principal pertenece a esa franja.
- Mantener fijo el par principal y describirlo en los otros soportes/cortes; no sustituirlo silenciosamente por otros pares si deja de ser próximo.
- Medir proporción de celdas entre bandas y cambios de categoría de la media OWN↔COMMON. Escenarios no equivalen a incertidumbre total. Las diferencias entre cortes no se interpretan como cambio observado, y 2022 conserva la advertencia VIIRS.
- El área es nominal de malla de 900 m²/celda. La superficie alta utiliza el soporte válido de la misma unidad, año y base. No se suman porcentajes posibles de bandas solapadas.

## Entrega y comprobación

CSV unidos con todos los cantones, todos los pares próximos, resúmenes por banda y robustez; JSON con selección determinista y fuentes por SHA-256; figura estática SVG/PDF/PNG para manuscrito; métodos, pie y párrafo de resultados/limitaciones. Una revisión independiente comprobará fórmulas, selección, denominadores y afirmaciones contra los CSV. Se inspeccionará el PNG renderizado antes de sellar la cápsula. No se promete un resultado favorable: si la brecha no es sustantiva se informa tal cual.
