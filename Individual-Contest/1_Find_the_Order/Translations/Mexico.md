# Encontrar el orden

- **Límite de tiempo:** 10 minutos
- **Entorno:** una GPU (≈16 GB VRAM), sin internet
- **Tamaño de la solución:** `solution.ipynb` ≤ 1 MB
- **Almacenamiento:** 5 GB 

## Problema

Se te daran diálogos hablados en inglés entre dos participantes, el *Hablante A* y el *Hablante B*. Cada diálogo está segmentado en turnos, y cada turno contiene la voz de un único hablante. Cada turno se almacena como un archivo de audio `.wav` independiente, por lo que un diálogo completo está representado por un conjunto de archivos `.wav`, uno por cada turno. 

Lamentablemente, los turnos se han revuelto aleatoriamente, por lo que la conversación ya no tiene sentido. En el nombre de archivo `chunk_{k}.wav`, `k` se refiere al k-ésimo fragmento del conjunto despues de que se revolvieron, no al k-ésimo turno del diálogo original.

**‼️ Tu tarea consiste en reconstruir el orden cronológico original de la conversación.**

![Encontrar el orden](../find_the_order.jpg)

---

## Dataset

Cada diálogo contiene `n` archivos de audio denominados `chunk_0.wav`, `chunk_1.wav`, …, `chunk_{n-1}.wav`. Cada audio es un turno de habla. Los nombres de archivo corresponden al orden revuelto. No indican el lugar del fragmento en la conversación original. Cada diálogo tiene entre 7 y 20 fragmentos, mono, 44.1 kHz (se te permite resamplear/remuestrear).

**`prefix.json` contiene los índices de los nombres de archivo de los dos primeros fragmentos de cada diálogo.** Esto te permite identificar el verdadero comienzo del diálogo y elimina la ambigüedad entre leer la conversación hacia delante o hacia atrás.

Por ejemplo: `11: [7, 12]` significa que el primer y segundo turno del diálogo 11 son `chunk_7.wav` y `chunk_12.wav`, respectivamente.

### Qué se proporciona

Recibiras **dos carpetas con formato idéntico**:

| Carpeta | Diálogos | ¿`answers.json`? | Se utiliza para |
|--------|-----------|-----------------|-----------|
| `dataset/train/` | 1,288 | incluido | entrenar / ajustar su modelo |
| `dataset/test_public/`  | 100   | incluido | ejecutar su pipeline y calcular localmente su propia puntuación |

Durante la evaluación, la carpeta `dataset/test_public/` se sustituye de forma transparente por
una `hidden evaluation set` (`test_leaderboard_a` para la tabla de clasificación pública y `test_leaderboard_b` para la tabla de clasificación final); estas tienen el mismo tamaño y formato que `dataset/test_public/`, pero no contienen el archivo `answers.json`.

Tu notebook se ejecuta de nuevo con esos datos, y el archivo `answers.json` que genera se utiliza para calcular la puntuación. Los diálogos de prueba reservados proceden de la misma distribución que `train`, por lo que su puntuación local de `test_public` es una estimación fiel.

### Estructura de directorios

```bash
dataset/train/
    prefix.json  # {dialogue_id: [first_idx, second_idx]} indices de los primeros dos fragmentos 
    answers.json  # {dialogue_id: P}  Permutacion correcta (rank convention)
    <dialogue_id>/
        chunk_0.wav
        ...
        chunk_{n-1}.wav

dataset/test_public/
    prefix.json
    answers.json     # presente unicamente en desarrollo
    <dialogue_id>/
        chunk_0.wav
        ...
        chunk_{n-1}.wav
```

---

## Salida

Para cada diálogo, determina el orden cronológico original de los fragmentos de audio. Tu predicción debe ser una permutación `P` de `{0, 1, …, n−1}`, donde `P[i]` es la posición cronológica predicha de `chunk_i.wav` (0 = primero).

Tu archivo de salida `answers.json` debe asociar cada ID de diálogo con su permutación predicha:

```json
{
  "17": [2, 0, 1],
  "42": [0, 1],
  "108": [3, 1, 0, 4, 2, 5]
}
```

### Ejemplo

Un diálogo tiene 3 fragmentos revueltos `chunk_0, chunk_1, chunk_2`:

| fragmento revuelto | contenido hablado | posición verdadera (rango) |
|----------------|----------------|----------------------|
| `chunk_0.wav` | *"No worries — I'll send you the notes afterwards."* | 2 (último) |
| `chunk_1.wav` | *"Hey, are you coming to the three o'clock meeting?"* | 0 (primero) |
| `chunk_2.wav` | *"I can't — I've got a dentist appointment then."* | 1 |

El orden verdadero es **chunk_1 → chunk_2 → chunk_0**, por lo que `P = [2, 0, 1]`, y `prefix.json` contiene `[1, 2]`.

⚠️ **P debe ser una permutación auténtica:** longitud n, indexada desde 0, cada valor exactamente una vez. Los valores duplicados, los valores ausentes o las entradas fuera de rango (p. ej., indexadas desde 1) obtienen una puntuación de 0 para ese diálogo, al igual que un diálogo ausente del archivo. Un archivo mal formado o que no sea JSON se rechaza.

## Puntuación

La puntuación de esta tarea es la **exactitud del ordenamiento por pares**. Para cada par de fragmentos se pregunta: _¿cuál de los dos debe ir primero?_ Un par es correcto si tu predicción los puso en el mismo orden relativo que la respuesta verdadera. 

Para un diálogo con `n` fragmentos hay: $$M = n(n-1)/2$$ pares; sea `I` el número de inversiones, es decir, pares ordenados de forma diferente a la verdad de referencia:

$$\text{score} = 1 - \frac{I}{M} \in [0, 1]$$

ℹ️ **La puntuación final es el promedio de las puntuaciones por diálogo de todos los
diálogos de la partición.**

## Modelos permitidos

Solo puedes utilizar los siguientes modelos preentrenados para resolver esta tarea, tanto durante el entrenamiento como durante la evaluación. Todos estos modelos ya están descargados y disponibles en el entorno. Se pueden consultar ejemplos de cómo utilizarlos en el notebook baseline `solution.ipynb`. Ten en cuenta que no se puede utilizar ningún otro modelo y que el programa no tiene acceso a internet.

- **Representaciones del habla:** **wav2vec 2.0**. El **codificador de Whisper** también puede utilizarse como extractor de características.
[Ficha del modelo wav2vec](https://yastatic.net/s3/contest/ioai/1/01_facebook_wav2vec2-base-960h_MODEL_CARD.html)

- **Reconocimiento automático del habla (ASR):** **OpenAI Whisper** (cualquier tamaño).
[Ficha del modelo Whisper](https://yastatic.net/s3/contest/ioai/1/03_openai_whisper-small_MODEL_CARD.html)
- **Modelo de lenguaje:** **Qwen2.5-0.5B**, que puede utilizarse tanto zero-shot como ajustado con la partición `train` proporcionada.
[Ficha del modelo Qwen](https://yastatic.net/s3/contest/ioai/1/02_Qwen_Qwen2.5-0.5B_MODEL_CARD.html)

Ten en cuenta que el límite de 10 minutos debe abarcar cualquier entrenamiento o ajuste que realices durante la evaluación, además de la inferencia sobre el conjunto de evaluación.

## Cómo enviar

- Abre `solution.ipynb` y ejecuta todas las celdas. Confirma que genera `answers.json` en el directorio de trabajo con una permutación para cada diálogo de `dataset/test_public/` (100 diálogos). Durante la evaluación, el notebook se vuelve a ejecutar en el conjunto de prueba oculto y se puntúa el `answers.json` que genera allí.
- Mejora la solución si lo deseas, o no lo hagas; el baseline por sí solo valida el pipeline.
- Abre la pestaña Git de la barra lateral izquierda de JupyterLab.
- Añade al área de preparación (**Stage**) `solution.ipynb` (el icono + situado junto al archivo).
- Introduce un mensaje de commit y haz clic en **Commit**.
- Haz clic en el icono de la nube con una flecha hacia arriba para hacer push.
- Vuelve a esta página del concurso y haz clic en **Submit**.

Envía exactamente un archivo, denominado `solution.ipynb`.
