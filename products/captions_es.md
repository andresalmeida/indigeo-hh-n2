# Pies de figura — producto descriptivo HH N2-T v1.2 (AD-1)

**Figura F3.** Media cantonal de HH N2-T v1.2 en soporte propio, por corte (2014, 2016, 2018, 2020 y 2022), en los 218 cantones continentales.
- **Color:** el extremo superior de la media, en escala lineal común de 0 a 25 para los cinco paneles.
- **Trama:** marca los pares de cantón y corte cuyos dos extremos difieren en más de 0.001. Son escenarios del modelo, no un error estadístico.
- **Lectura:** reconstrucción descriptiva bajo la receta, admitida como AD-1; no es cambio observado. Cada nivel se calcula sobre el soporte propio de su corte, que cambia entre cortes, así que los niveles de cortes distintos no se restan.
- **Fuera del mapa:** Galápagos, la entidad ISLA y el territorio sin cantón no se dibujan, y nada se asigna a un cantón vecino.
- **Geometría:** simplificada, solo para mostrar.
- **Datos:** valores, extremos y conteos en `tables/levels.csv`.

**Figura F4.** Signo del intervalo condicional de la diferencia modelada bajo la receta, por cantón e intervalo bienal, sobre el soporte común de los cinco cortes.
- **Signo:** positivo o negativo cuando todo el intervalo queda a un lado de cero; indeterminado cuando lo incluye.
- **El intervalo** acota los escenarios modelados. No es un intervalo de confianza, ni una prueba de significancia, ni la incertidumbre total.
- **Un signo** no es un cambio observado ni una tendencia. Los tres signos son una leyenda diagnóstica, no categorías de intensidad.
- **VIIRS:** el intervalo 2020–2022 cruza la versión del producto (V2.1 → V2.2) sin puente. Con la banda eléctrica de 2020 en lugar de la de 2022, 17 cantones cambian el estado de su signo.
- **UTM:** junto al meridiano 78° O el control del cruce entre mallas falló (TEMP987); véase F5.
- **Validación temporal:** no hay; G-T1 sigue abierto.
- **Datos:** `tables/differences.csv`.

**Figura F5.** Cantones con celdas cubiertas por las dos mallas UTM (17S y 18S) en la franja del meridiano 78° O: 32 de 218.
- **Asignación:** el ensayo asigna cada celda por el meridiano.
- **Lo que mostró U1:** ningún cantón cambia el estado de su signo entre las tres asignaciones probadas (por el meridiano, toda la franja desde 17S, toda desde 18S), y 186 cantones no dependen de la asignación.
- **Lo que no aprueba:** la costura. El control del cruce falló sus tolerancias (TEMP987), y junto al meridiano una franja más estrecha que una celda se cuenta dos veces o ninguna.
- **Cantón 401:** su porción doblemente cubierta difiere en signo entre mallas; es una porción, no el cantón.
- **Origen:** la sensibilidad se cita tal como se midió en U1, sin recalcularla.
- **Datos:** `tables/utm.csv`.

**Figura F6.** Benchmark B1–B4 (plan r2, una sola corrida autorizada).
- **A.** ρ de Spearman entre cada mapa y el puntaje visual compuesto del respaldo local de Aragón, en 150 parcelas D0 con soporte común completo, cada una en el año calendario de su imagen.
  - El puntaje visual es un proxy histórico, con linaje pendiente.
  - Mismo año calendario no significa misma fecha.
  - Los dos extremos de N2 son dos marcas, no un intervalo, y ningún ρ individual lleva intervalo.
- **B.** Diferencia pareada ρ(N2) − ρ(SDG15), con su intervalo de remuestreo iid (2 000 remuestras, percentiles 2.5–97.5): ambos intervalos incluyen el 0.
- **Lectura de A y B:**
  - La asociación de orden es parecida en esta muestra, pero eso no demuestra equivalencia, no inferioridad ni superioridad de exactitud.
  - N2 se reconcilió con el SDG15, así que los dos mapas no son independientes.
  - El intervalo de remuestreo no conserva los estratos ni la dependencia espacial, no garantiza una cobertura del 95 % y no es un intervalo de los escenarios del modelo.
- **C, aparte del benchmark.** R0, la reconstrucción del respaldo local, da el mismo conteo de 529 parcelas que el artículo, sin acreditar que sean las mismas, pero no reproduce las métricas de su Tabla 6. Los valores del artículo se muestran con los dos decimales con que se publicaron.
- **Datos:** `tables/benchmark_rho.csv`, `tables/benchmark_differences.csv`, `tables/R0_vs_table_6.csv` y `tables/benchmark_support_and_selection.json`.
