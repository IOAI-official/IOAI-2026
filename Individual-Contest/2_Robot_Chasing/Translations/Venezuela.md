# Persecución de robots

- **Límite de tiempo:** 5 minutos
- **Entorno:** una GPU (≈16 GB VRAM), sin internet
- **Tamaño de la solución:** `solution.ipynb` ≤ 1 MB
- **Almacenamiento:** 5 GB 

## Tarea

Hay seis robots. Cada robot opera en una habitación pequeña representada mediante una cuadrícula. Cada habitación tiene un área de juego de `6×6` rodeada de paredes, por lo que el array `image` completo tiene tamaño `8×8` (área de juego + paredes).

Cada robot recibe una instrucción en inglés que describe una tarea. Una imagen de la habitación puede tomarse en cualquier momento mientras el robot la esté llevando a cabo. El objetivo es predecir la siguiente acción del robot.

Los robots no siempre siguen el camino más corto. El Robot 0 puede comportarse de manera diferente al Robot 1, pero cada robot sigue su propio patrón coherente. Utilice los ejemplos de entrenamiento, que incluyen las siguientes acciones correctas de cada robot, para aprender sus patrones.

![Robot](../robot.jpg)

Hay tres tipos de misiones:

- **ir hasta** un objeto, por ejemplo `"approach the red ball"`;
- **recoger** un objeto, por ejemplo `"grab the blue key"`;
- **colocar un objeto junto a otro**, por ejemplo
  `"place the red box beside the green ball"`.

La misma instrucción puede escribirse de varias maneras. El conjunto de prueba puede contener nuevas combinaciones de frases, colores y tipos de objetos conocidos. Sin embargo, se garantiza que cada palabra, patrón de frase, color, tipo de objeto y tipo de misión utilizado en el conjunto de prueba también aparece en el conjunto de entrenamiento.

Cada muestra tiene los siguientes campos:

| Campo | Significado |
|---|---|
| `robot_id` | cuál de los 6 robots es (`0`–`5`) |
| `imagen` | la habitación, un arreglo de enteros `8×8×2` en el que el canal 0 contiene la categoria del objeto (p. ej., 1=vacío, 2=pared, 10=robot) y el canal 1 contiene la categoria de color  (0–5). |
| `dirección` | la dirección hacia la que está orientado actualmente el robot |
| `misión` | la instrucción visible en lenguaje natural |
| `transporta` | es `null` o `[indice del objeto, indice de color]` para el objeto transportado |

Las filas son imagenes independientes en orden aleatorio. No forman episodios ordenados, y durante la evaluación no se dispone de ninguna observación ni acción anterior.

El archivo `visualize_dataset.ipynb`  permite inspeccionar las observaciones disponibles para el modelo en diferentes situaciones.

## Codificación de la cuadrícula

`imagen[fila][columna] = [indice del objeto, indice de color`]. El primer índice es la fila, de arriba abajo, y el segundo es la columna, de izquierda a derecha. El arreglo incluye el borde exterior de las paredes, por lo que el interior transitable es de tamaño `6×6`.

Indices de objetos:

| id | objeto |
|---:|---|
| 1 | celda vacía |
| 2 | pared |
| 5 | llave |
| 6 | pelota |
| 7 | caja |
| 10 | robot |
| 11 | token |

Pueden aparecer tokens en la habitación, pero nunca se los menciona en las misiones.

Los ids de color son `0` rojo, `1` verde, `2` azul, `3` morado, `4` amarillo y `5` gris. El canal de color no tiene significado para las celdas vacías ni para las paredes.

La imagen solo tiene los dos canales mencionados. La dirección del robot se proporciona una sola vez al principio, en el campo de nivel superior `dirección`; no está duplicada dentro de cada `imagen`.

## Acciones

Las acciones de movimiento utilizan los siguientes valores para los códigos `0`–`3`, :

| acción | significado |
|---:|---|
| 0 | moverse hacia arriba |
| 1 | moverse hacia abajo |
| 2 | moverse hacia la izquierda |
| 3 | moverse hacia la derecha |
| 4 | recoger |
| 5 | soltar |


El campo `dirección` indica la orientación actual mediante: 0 = Arriba (fila - 1), 1 = Abajo (fila + 1), 2 = Izquierda (columna - 1), 3 = Derecha (columna + 1).

Una acción de movimiento primero gira el robot hacia esa dirección y después intenta desplazarlo una celda. Una pared o un objeto pueden bloquear el movimiento, pero la dirección cambia de todos modos. Las acciones `recoger` y `soltar` actúan sobre la celda adyacente definida por la dirección (p. ej., si dirección=0 (moverse hacia arriba), soltar o recoger actúan sobre la casilla (fila - 1, columna)).

## Dataset

Se proporcionan dos carpetas:

| Carpeta | Filas | ¿`labels.json`? | Utilícela para |
|---|---:|---|---|
| `dataset/train/` | 60,000 | incluido | entrenar el modelo |
| `dataset/test_public/` | 3,600 | incluido en la copia de desarrollo | ejecutar y autoevaluar el programa |

Cada carpeta contiene `observations.json`, una lista JSON de las muestras (imágenes) descritas anteriormente. `labels.json` es una lista JSON alineada de acciones (`0`–`5`).

El conjunto de entrenamiento contiene exactamente 10,000 filas por robot y 20,000 filas de cada conjunto de tareas. El conjunto de prueba público contiene 600 filas por robot. Agrupe las `imágenes` usando numpy.asarray(...)` si necesita un arreglo.

En el momento de la calificación, `dataset/test_public/` se sustituye de forma transparente por un conjunto oculto de
3,600 observaciones con el mismo formato, pero sin `labels.json`. La tabla de clasificación
pública utiliza `test_leaderboard_a`; la clasificación final utiliza
`test_leaderboard_b`. 

Un notebook que lea incondicionalmente las etiquetas `labels.json` fallará en la evaluacion.
Las etiquetas, en la evaluacion, deben leerse únicamente de `dataset/train/`.

## Salida

Escriba `predictions.json` en el directorio de trabajo del notebook. Debe ser una lista
JSON que contenga una acción (`0`–`5`) por cada fila de
`dataset/test_public/observations.json`, en el mismo orden. Para un conjunto de prueba hipotético que contenga seis muestras, una salida válida sería:

```json
[0, 3, 2, 2, 5, 4]
```

Un archivo JSON ausente o no válido, un número incorrecto de predicciones, un valor no entero
o una acción fuera de `{0,1,2,3,4,5}` se rechazan sin puntuación.

## Puntuación

La puntuación es la **exactitud media por robot** en una escala de `0`–`100`. Primero se calcula la exactitud
de forma independiente para cada robot y después se promedia entre los seis robots. Por lo tanto, cada
robot tiene el mismo peso.

## Cómo enviar

1. Abra `solution.ipynb` y ejecute todas las celdas.
2. Confirme que escribe `predictions.json` con 3,600 predicciones para el conjunto de
   prueba público.
3. Mejore el modelo si lo desea; el baseline proporcionado solo muestra el
   formato requerido de entrada y salida.
4. En la pestaña Git de JupyterLab, prepare y confirme `solution.ipynb` y, a continuación, haga push.
5. Vuelva a la página del concurso y haga clic en **Enviar**.

Envíe exactamente un archivo llamado `solution.ipynb`.
