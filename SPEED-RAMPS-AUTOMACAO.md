# Automatizar speed ramps para o DaVinci Resolve

Investigação feita a **2026-08-10**. Complementa [`SPEED-RAMPS.md`](SPEED-RAMPS.md), que trata
do **desenho** do ramp; este trata de **como o produzir sem o fazer à mão, clip a clip**.

---

## A resposta curta, e é incómoda

🔴 **A API de scripting do Resolve NÃO permite definir velocidade nem speed points.**

Não é uma limitação da versão Free: é da API, em todas as versões, incluindo a 20.3. O único
controlo de retime exposto é o **modo de interpolação**, via `TimelineItem:SetProperty`:

```python
item.SetProperty("RetimeProcess", 3)   # 0=Project  1=Nearest  2=Frame Blend  3=Optical Flow
```

Isto diz **como** interpolar. Não diz a que velocidade, nem onde ficam os pontos. As chaves
suportadas pelo `SetProperty` são de transformação geométrica (`Pan`, `Tilt`, `ZoomX`,
`ZoomY`, `RotationAngle`, `CropLeft`...) e não incluem velocidade.

➡️ **Consequência directa: não há como escrever um script Python que abra o Resolve e desenhe
o ramp do plano 07.** Quem o disser está enganado ou a falar de outra coisa.

Mas há **três caminhos** que funcionam, e um deles encaixa bem no nosso fluxo.

---

## Caminho A — gerar FCPXML com os ramps já lá dentro

**O que é:** escrever um `.fcpxml` por script, com os segmentos de velocidade descritos, e
importá-lo no Resolve. O Resolve **lê retime variável de FCPXML** e transforma-o em curvas de
retime reais, editáveis no `Ctrl+R` como se as tivesses feito à mão.

**A favor**

- O ramp chega **editável**. Se um hold ficar curto, ajustas no Resolve sem refazer nada.
- Sai de um script, portanto é reproduzível e versionável.
- Mantém a decisão de interpolação no Resolve, por clip, que é onde ela deve estar.

**Contra**

- O formato é chato e mal documentado; a validação é por tentativa.
- Round-trip de volta para FCP tem casos especiais que o manual do Resolve trata à parte.
- Um erro de timebase e a montagem inteira sai desalinhada.

**Quando escolher:** quando quiseres o ramp **discutível**, ou seja, quando ainda vais afinar.

---

## Caminho B — cozinhar o ramp em ffmpeg, antes do Resolve

**O que é:** o clip chega ao Resolve **já com o ramp gravado**. O Resolve só corta e faz cor.

Este é o caminho que melhor resolve o problema que o [`SPEED-RAMPS.md`](SPEED-RAMPS.md)
descreve no §11: **fonte IA a 24 fps numa timeline a 24 não tem slow de graça**, e o Optical
Flow do Resolve Free quase não salva material de IA.

**A receita em duas fases, e a ordem importa:**

```
1. INTERPOLAR primeiro, para haver fotogramas verdadeiros
   ffmpeg -i plano.mp4 -vf "minterpolate=fps=48:mi_mode=mci:mc_mode=aobmc:vsbmc=1" -crf 12 plano48.mp4

2. RAMPAR depois, sobre os 48 fps, e sair a 24
   ffmpeg -i plano48.mp4 -vf "setpts=<EXPRESSÃO>,fps=24" -an plano_ramp.mp4
```

⚠️ **Nunca ao contrário.** Rampar primeiro e interpolar depois faz o `minterpolate` inventar
por cima de fotogramas já duplicados, e aí a parede derrete.

⚠️ `minterpolate` é **muito** lento, dezenas de vezes o tempo real em HD. É trabalho de
madrugada, não de véspera de entrega.

### A expressão do `setpts`, a sério

Um ramp com degraus (`250%` e a seguir `88%`, sem transição) sente-se mecânico, e é o erro
que o `SPEED-RAMPS.md` chama de escada. Para ter **ease**, a velocidade tem de variar de forma
contínua, e isso obriga a integrar.

Se a velocidade for `v(t)` (multiplicador: 2,0 = dobro da velocidade), o tempo de saída é

```
O(t) = ∫₀ᵗ dτ / v(τ)
```

Para um troço em que `v` varia **linearmente** de `v0` a `v1` ao longo de `d` segundos, com
`k = (v1 − v0) / d`, o integral tem forma fechada:

```
O(t) = (1/k) · ln( (v0 + k·t) / v0 )        quando k ≠ 0
O(t) = t / v0                                quando k = 0  (velocidade constante)
```

Ou seja, um perfil trapezoidal (**in → hold → out**) escreve-se como três troços encadeados,
cada um com o seu logaritmo, somando o tempo acumulado dos anteriores. Em `setpts` isso
constrói-se com `if(lt(T,a), ..., if(lt(T,b), ..., ...))` e `T` em segundos.

➡️ **Não escrevas isto à mão.** Vale a pena um pequeno gerador em Python que receba
`(v_in, v_hold, v_out, t_in, t_hold, t_out)` e devolva a expressão. É determinístico e testa-se
com um clip de barras antes de tocar em material de cliente.

**A favor**

- Controlo total da interpolação, fora do Resolve Free e das suas limitações.
- O Resolve fica leve: sem retime, sem Optical Flow, sem cache pesada.
- Reproduzível a 100% e integra-se no fluxo Python que já existe.

**Contra**

- 🔴 **O ramp deixa de ser editável.** Mudar um hold obriga a recozinhar o clip.
- O `minterpolate` tem os seus artefactos, e em material IA com warp piora.
- Perde-se a leitura visual do ramp na timeline (as setas amarelas do Resolve).

**Quando escolher:** quando o ramp **já estiver decidido** e o que interessa for repetibilidade.

---

## Caminho C — à mão no Resolve, guiado por especificação

Continua a ser o caminho por omissão, e não é derrota nenhuma: o `SPEED-RAMPS.md` diz que
**poucos ramps bem feitos batem muitos ramps medianos**. Num vídeo de 60 s com 18 planos, os
ramps que interessam são meia dúzia.

O que se automatiza aqui não é o ramp, é **a especificação**: o guião já traz o tipo de cada
plano, a duração, e quais não levam ramp nenhum. O trabalho manual passa a ser execução, não
decisão.

---

## O que eu faria no T3 Colinas do Cruzeiro

**Híbrido, e por esta ordem:**

**1. Os quatro planos marcados `X` não levam ramp nenhum** (espelhos, vidro, azulejo). Nada a
automatizar. Velocidade constante.

**2. Os três heroes fazem-se à mão no Resolve.** São três. O tempo de escrever e depurar um
gerador de FCPXML para três planos não se paga, e são precisamente os planos onde vais querer
mexer depois de ver.

**3. As passagens, se alguma vez forem muitas, vão por ffmpeg.** São curtas, o ramp é sempre o
mesmo gesto, e não se discutem. É aí que a automação compensa: num vídeo com quatro imóveis e
oito peças, são dezenas de passagens iguais.

⚠️ **E antes de qualquer retime, o transcode all-intra**, que já é regra em casa: clips do
Kling e do MiniMax vêm com um só keyframe e rebentam no retime com Optical Flow. Script já
existe no T4: `_transcodificar_para_montagem.py`.

---

## Armadilhas que a investigação confirmou

| Armadilha | Detalhe |
|---|---|
| **API não faz retime** | Só `RetimeProcess`. Não percas tempo a procurar |
| **Fusion TimeStretcher** | Ignora o Optical Flow da página Edit. O ramp tem de estar na Edit Retime Curve |
| **Áudio retimado** | Fica em chipmunk. Mute sempre a fonte |
| **`minterpolate` depois do ramp** | Inventa por cima de fotogramas duplicados |
| **Optical Flow no master** | Nunca. É decisão por clip |
| **Ramp no cartão** | Nunca. Legibilidade acima de estilo |

---

## Fontes

- [Referência da API de scripting do Resolve v20.3](https://gist.github.com/X-Raym/2f2bf453fc481b9cca624d7ca0e19de8) — lista das chaves suportadas pelo `SetProperty`
- [Documentação não oficial da API](https://electron-rotoscope.github.io/DaVinciResolve-API-Docs/) — propriedades de TimelineItem
- [Fórum Blackmagic, definir velocidade por Python](https://forum.blackmagicdesign.com/viewtopic.php?f=21&t=207857)
- [Larry Jordan, round-trip FCP e Resolve](https://larryjordan.com/articles/round-tripping-projects-between-final-cut-pro-and-davinci-resolve/) — retime variável preservado na importação
- [Retime Controls e Retime Curves no Resolve](https://www.shutterstock.com/blog/davinci-resolve-retime-curves)
- [ffmpeg, setpts e atempo](https://ffmpeg-cookbook.com/en/articles/change-video-speed/) e [minterpolate para slow real](https://renderio.dev/blogs/ffmpeg-speed-up-slow-down-video/)

---

*Documento vivo. Se uma versão futura do Resolve expuser retime na API, isto muda todo o
capítulo e o Caminho A deixa de fazer sentido.*
