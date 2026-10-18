# Precisiones antes de calcular

La revisión independiente del plan046 señaló tres precisiones que se adoptan sin cambiar ninguna fórmula ni corte:

1. La proximidad de medias es **robusta entre extremos**: la mayor diferencia posible entre ambos intervalos no supera ε. No es una distancia mínima entre intervalos, ni afirma equivalencia. Un intervalo ancho puede no cumplirla incluso frente a otro idéntico. Se usa esa terminología en los resultados.
2. Cada par contiene dos cantones distintos. Es no ordenado, se genera una sola vez y sus códigos se ordenan numéricamente antes del desempate.
3. El porcentaje de celdas entre bandas se divide por el soporte válido de ese cantón, año y base. Las celdas con intervalo inválido se cuentan aparte y nunca se convierten en presión cero. Se cotejan soporte total y válido con las tablas de entrada; si hay discrepancia no prevista, el análisis se detiene.

Especificación original conservada con SHA-256 df3efac30b4f9de64b23960d66a0d0e6e6b285327fc9f17074463f8cf3d57151. La revisión es `plans/046-hh-within-canton-heterogeneity/method_review.md`. Estas precisiones se fijaron antes de examinar los resultados del análisis nuevo.
