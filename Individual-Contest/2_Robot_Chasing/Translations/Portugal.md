# Perseguição de Robôs

- **Limite de tempo:** 5 minutos
- **Ambiente:** uma GPU (≈16 GB VRAM), sem internet
- **Tamanho da solução:** `solution.ipynb` ≤ 1 MB
- **Armazenamento:** 5 GB 

## Tarefa

Existem seis robôs. Cada robô opera numa pequena sala representada por uma grelha. Cada sala tem uma área jogável `6×6` rodeada por paredes, pelo que o array `image` completo tem dimensões `8×8` (área jogável + paredes).

Cada robô recebe uma instrução em inglês que descreve uma tarefa. A snapshot pode ser obtida em qualquer momento enquanto o robô executa uma instrução. O seu objetivo é prever a próxima ação do robô.

Os robôs nem sempre seguem o caminho mais curto. O Robô 0 pode comportar-se de forma diferente do Robô 1, mas cada robô segue o seu próprio padrão consistente. Utilize os exemplos de treino, que incluem as próximas ações corretas, para aprender estes padrões.

![Robô](../robot.jpg)

Existem três tipos de missões:

- **ir até** um objeto, por exemplo `"approach the red ball"`;
- **apanhar** um objeto, por exemplo `"grab the blue key"`;
- **colocar um objeto junto de outro**, por exemplo
  `"place the red box beside the green ball"`.

A mesma instrução pode ser escrita de várias formas. O conjunto de teste pode conter novas combinações de expressões, cores e tipos de objetos conhecidos. No entanto, todas as palavras, padrões de expressões, cores, tipos de objetos e tipos de missões utilizados no conjunto de teste também aparecem no conjunto de treino.

Cada amostra tem os seguintes campos:

| Campo | Significado |
|---|---|
| `robot_id` | qual o robô a efetuar a instrução, entre (`0`–`5`) |
| `image` | a sala, um array de inteiros `8×8×2` em que o canal 0 contém um object_idx categórico (por exemplo, 1=vazio, 2=parede, 10=robô) e o canal 1 contém um colour_idx categórico (0–5). |
| `direction` | a direção para a qual o robô está atualmente virado |
| `mission` | a instrução decrita em linguagem natural |
| `carrying` | `null` ou `[object_idx, colour_idx]` para o objeto a ser transportado |

As linhas são snapshots independentes, dispostos por ordem aleatória. Não formam episódios e, no momento da avaliação, não está disponível qualquer observação ou ação anterior.

O notebook `visualize_dataset.ipynb` permite-lhe inspecionar as observações disponíveis para o modelo em diferentes situações.

## Codificação da grelha

`image[row][column] = [object_idx, colour_idx]`. O primeiro índice corresponde à linha, de cima para baixo, e o segundo corresponde à coluna, da esquerda para a direita. O array inclui a borda exterior de paredes, pelo que o interior navegável é `6×6`.

IDs dos objetos:

| id | objeto |
|---:|---|
| 1 | célula vazia |
| 2 | parede |
| 5 | chave |
| 6 | bola |
| 7 | caixa |
| 10 | robô |
| 11 | token |

Podem aparecer tokens na sala, mas nunca são mencionados nas missões.

Os IDs das cores são `0` vermelho, `1` verde, `2` azul, `3` roxo, `4` amarelo e `5` cinzento. O canal de cor não tem significado para células vazias nem para paredes.

A imagem contém apenas os dois canais acima. A direção do robô é fornecida no campo `direction`. Não sendo duplicada dentro de cada `image`.

## Ações

Para os códigos `0`–`3`, as ações de movimento utilizam o seguinte mapeamento absoluto:

| ação | significado |
|---:|---|
| 0 | mover para cima |
| 1 | mover para baixo |
| 2 | mover para a esquerda |
| 3 | mover para a direita |
| 4 | apanhar |
| 5 | largar |


O campo `direction` indica a orientação atual através da seguinte codificação: 0 = Cima (linha - 1), 1 = Baixo (linha + 1), 2 = Esquerda (coluna - 1), 3 = Direita (coluna + 1).

Uma ação de movimento começa por virar o robô para essa direção absoluta e, de seguida, tenta movê-lo uma célula. Uma parede ou um objeto pode bloquear o movimento, mas a direção muda na mesma. `pick up` e `drop` atuam exclusivamente sobre a célula-alvo adjacente definida pela direção (por exemplo, se direction=0, atua sobre (row - 1, col)).

## Dataset

Existem duas pastas:

| Pasta | Linhas | `labels.json`? | Utilize-a para |
|---|---:|---|---|
| `dataset/train/` | 60,000 | incluído | treinar o seu modelo |
| `dataset/test_public/` | 3,600 | incluído na cópia de desenvolvimento | executar e autoavaliar a sua pipeline |

Cada pasta contém `observations.json`, uma lista JSON das amostras descritas
acima. `labels.json` é uma lista JSON alinhada de ações (`0`–`5`).

O conjunto de treino contém exatamente 10,000 linhas por robô e 20,000 linhas de cada
família de tarefas. O teste público contém 600 linhas por robô. Envolva `image` com
`numpy.asarray(...)` se precisar de um array.

Durante o processo de avaliação, `dataset/test_public/` é substituído de forma transparente por um conjunto oculto de
3,600 observações no mesmo formato, mas sem `labels.json`. A tabela classificativa
pública utiliza `test_leaderboard_a`; enquanto que a classificação final utiliza
`test_leaderboard_b`. Um notebook que leia incondicionalmente os rótulos de teste irá falhar.
Leia rótulos apenas de `dataset/train/`.

## Saída

Escreva `predictions.json` no diretório de trabalho do notebook. Tem de ser uma lista
JSON que contenha uma ação inteira (`0`–`5`) por linha de
`dataset/test_public/observations.json`, pela mesma ordem. Para um conjunto de teste hipotético que contenha seis amostras, uma saída válida seria:

```json
[0, 3, 2, 2, 5, 4]
```

Um ficheiro JSON em falta ou inválido, um número incorreto de previsões, um valor não inteiro
ou uma ação fora de `{0,1,2,3,4,5}` é rejeitado sem pontuação.

## Pontuação

A pontuação é a **acurácia média por robô** numa escala de `0`–`100`. A acurácia é primeiro
calculada de forma independente para cada robô e, em seguida, é calculada a média para os seis robôs. Assim, cada
robô tem o mesmo peso na pontuação.

## Como submeter

1. Abra `solution.ipynb` e execute todas as células.
2. Confirme que escreve `predictions.json` com 3,600 previsões para o conjunto de
   teste público.
3. Melhore o modelo se quiser; o baseline fornecido apenas serve para deonstrar o
   formato de entrada e saída exigido.
4. No separador Git do JupyterLab, adicione `solution.ipynb` à área de staging, faça commit e depois push.
5. Regresse à página do Concurso e clique em **Submit**.

Submeta exatamente um ficheiro chamado `solution.ipynb`.
