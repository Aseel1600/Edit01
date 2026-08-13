# Legendas cinéticas agressivas — motor KIMI (gramática + rig procedural)

Versão **1** — ângulo diferente dos outros dois playbooks: aqui a legenda é tratada como um **instrumento afinado**, não como uma lista de receitas nem como um sistema de energia. Duas ideias centrais:

1. **Gramática do movimento** — cada palavra tem uma *função* (gancho, dado, lugar, benefício, CTA) e cada função tem uma **assinatura de movimento** que não muda dentro da peça.
2. **Rig procedural** — uma comp AE onde o timing se muda **arrastando markers**, a caixa se ajusta **à tinta** sozinha, a cor reage ao plano e o pulso reage à música. Menos keyframes manuais, mais sistema.

Complementa, não substitui:

- [`LEGENDAS-CINETICAS-AGRESSIVAS.md`](LEGENDAS-CINETICAS-AGRESSIVAS.md) — biblioteca-base R1–R8 (pop cascade, whip slam, stacked, scramble, mask wipe, kick pulse), grelha de tempo e pipeline;
- [`LEGENDAS-CINETICAS-AGRESSIVAS-SOL.md`](LEGENDAS-CINETICAS-AGRESSIVAS-SOL.md) — modos de energia A/B/C, grelha BPM, papéis de cor, receitas SOL-01–10, SFX em 3 camadas, safe zones medidas;
- [`TIPOGRAFIA-REAL-ESTATE.md`](TIPOGRAFIA-REAL-ESTATE.md) — gama, hierarquia, densidade, legibilidade;
- [`MASTERING.md`](MASTERING.md) — ramps, optical flow, áudio e export;
- [`ESTILO-CLIENTE.md`](projects/video-service-business/clients/Mario%20Garces/ESTILO-CLIENTE.md) — locks do Mário Garcês.

> **Locks vencem este playbook.** No Mário: **Montserrat** (variável — confirmar o peso, senão sai Regular), título **Medium** + sobretítulo **Bold CAPS**, caixa medida **pela tinta**, barra 4 px vermelho/azul, aresta visível em **x=67**, frase longa parte em **duas linhas** (nunca encolher letra), localização sempre completa `T4 Lumiar – QUINTA dos ALCOUTINS`. “Agressivo” muda movimento e cor permitida — nunca identidade.

---

## 1. Gramática do movimento: função → assinatura

O erro mais caro em kinetic agressivo não é o bounce a mais — é o **mesmo tipo de informação entrar de maneiras diferentes** ao longo da peça. O espectador aprende uma gramática nos primeiros 3 beats; se a quebrares, cada legenda nova custa atenção em vez de a dar.

### Tabela de assinaturas

| Função | Exemplos | Assinatura de movimento | Família de easing | Cor (papel) | SFX |
|--------|----------|-------------------------|-------------------|-------------|-----|
| **GANCHO** | `ESPERA`, `NOVO`, `ESGOTOU EM 48H` | Impacto vertical ou slam, overshoot 112–118%, 1 flash máx. | Orgânico (overshoot) | HERO | slam + ar |
| **DADO** | `188 m²`, `€685 000`, `T4` | Mecânico: decode, odómetro, tile com lock. **Nunca elástico** | Mecânico (duro/linear) | DADO | click / blip |
| **LUGAR** | `LUMIAR`, `QUINTA DOS ALCOUTINS` | Ancoragem: wipe L→R, flip board, parallax lento. Settle mais longo que os outros | Âncora (wipe/mask) | BASE ou ACÇÃO | whoosh grave |
| **BENEFÍCIO** | `LUZ O DIA TODO`, `VISTA ABERTA` | Respiração: karaoke fill, baseline wave, color chase suave | Orgânico calmo | BASE → HERO | nenhum, ou ar só |
| **CTA** | `MARQUE A SUA VISITA` | Pulso rítmico + halo; entrada única, saída suave, nunca corte seco | Pulso | ACÇÃO | assinatura própria (1 som só do CTA) |

### Três regras de ouro

1. **Uma função, uma assinatura.** Se o preço entra com odómetro no hook, a área não entra com elastic na cozinha. DADO é sempre mecânico.
2. **Famílias de easing não se misturam no mesmo beat.** Mecânico + orgânico no mesmo frame lê-se como erro de render.
3. **A assinatura do CTA recicla a do GANCHO.** Fecha o sistema; o espectador reconhece o som/movimento do início e percebe “acabou — age”.

### Teste rápido

Pausa em qualquer frame e pergunta: *“que tipo de informação é isto?”* Só pela pose do texto (sem ler) devia ser óbvio se é dado, lugar ou emoção. Se não é, a assinatura está fraca.

---

## 2. O motor: rig procedural em AE

Objectivo: **mudar o timing de um beat = arrastar um marker**, não re-keyframear 6 propriedades. Mudar de cliente = trocar controlos numa layer, não reconstruir comps.

### 2.1 Arquitectura da comp

```text
CAPTIONS_1080x1920_24
├── CTRL                 (sliders + cores + dropdown de modo)
├── GUIA_SAFE            (overlay de safe zone, toggle, nunca renderiza)
├── FLASH_1F             (adjustment layer, opcional, opacity por marker)
├── BEAT_01 ... BEAT_NN  (texto + caixa auto + expressões; markers próprios)
└── AUDIO_AMPLITUDE      (depois de Convert Audio to Keyframes)
```

**Protocolo de markers** (na layer do próprio beat, comentário = comando):

| Marker | Significado |
|--------|-------------|
| `#IN` | início do ataque |
| `#HIT` | frame do impacto (overshoot no seu pico **aqui**) |
| `#LOCK` | valor final correcto (decode/odómetro/scramble) |
| `#OUT` | início da saída |

A convenção `#HIT` separada de `#IN` é o detalhe que mais peças falham: **o impacto sonoro cai no overshoot, não no primeiro frame do movimento.**

### 2.2 Control layer `CTRL`

Sliders e controlos mínimos:

```text
IN_FRAMES      10      duração do ataque
SETTLE_FRAMES   5      overshoot → 100%
OUT_FRAMES      8
OVERSHOOT     114      % (112–118 social; 104–110 brand-safe)
PAD_PX         28      padding da caixa auto
PULSE_MAX       6      % de pulso no beat da música
BASE_COLOR  #FFFFFF
HERO_COLOR  (por peça)
DADO_COLOR  (por peça)
INK_COLOR   #0B1020
MODE        BRAND_SAFE / SOCIAL / MAX   (dropdown)
```

Troca de imóvel ou de cliente = editar `CTRL` + colar copy. As receitas ficam intactas.

### 2.3 Expressão master IN/OUT (Scale)

Colocar em `Scale` da layer de texto do beat. Requer motor de expressões **JavaScript** (Project Settings → Expressions → JavaScript; não Legacy ExtendScript).

```javascript
// SCALE do beat — lê #IN e #OUT dos markers da própria layer
const ctrl = thisComp.layer("CTRL");
const over = ctrl.effect("OVERSHOOT")("Slider");
const inF  = ctrl.effect("IN_FRAMES")("Slider");
const stF  = ctrl.effect("SETTLE_FRAMES")("Slider");
const outF = ctrl.effect("OUT_FRAMES")("Slider");

function tMark(name) {
  for (let i = 1; i <= marker.numKeys; i++) {
    if (marker.key(i).comment === name) return marker.key(i).time;
  }
  return null;
}
const tIn  = tMark("IN")  !== null ? tMark("IN")  : inPoint;
const tOut = tMark("OUT") !== null ? tMark("OUT") : outPoint - framesToTime(outF);

let s = 0;
if (time < tIn) {
  s = 0;
} else if (time < tIn + framesToTime(inF)) {
  const p = (time - tIn) / framesToTime(inF);
  s = (1 - Math.pow(1 - p, 3)) * over;              // easeOutCubic até overshoot
} else if (time < tIn + framesToTime(inF + stF)) {
  const p = (time - tIn - framesToTime(inF)) / framesToTime(stF);
  s = over + (100 - over) * (1 - Math.pow(1 - p, 2)); // settle macio
} else if (time <= tOut) {
  s = 100;                                           // hold
} else {
  const p = Math.min((time - tOut) / framesToTime(outF), 1);
  s = 100 * (1 - p * p);                             // easeInQuad na saída
}
[s, s];
```

Variantes por assinatura: GANCHO usa `over` de 114–118; DADO usa a mesma estrutura mas com `over = 104` e ataque quase linear; LUGAR troca Scale por Position X com a mesma máquina de markers.

### 2.4 Caixa auto-ajustável à tinta (`sourceRectAtTime`)

A lição paga no Mário — **a caixa mede-se pela tinta, não pela métrica da fonte** — em AE resolve-se de graça:

```javascript
// Shape layer "CAIXA" → Rectangle Path → Size
const txt = thisComp.layer("BEAT_TXT");
const pad = thisComp.layer("CTRL").effect("PAD_PX")("Slider");
const r = txt.sourceRectAtTime(time, false);
[r.width + pad * 2, r.height + pad * 1.4];
```

```javascript
// Shape layer "CAIXA" → Position (centrada na tinta, não na métrica)
const txt = thisComp.layer("BEAT_TXT");
const r = txt.sourceRectAtTime(time, false);
txt.toComp([r.left + r.width / 2, r.top + r.height / 2]);
```

A caixa segue a largura real dos glifos — muda a copy, muda a caixa, sem retocar nada. Para a barra lateral estilo Mário (4 px, vermelho em cima/azul em baixo): duas shape layers finas parentadas à caixa, altura = metade da altura da caixa cada, X = aresta esquerda da caixa.

### 2.5 Contraste adaptativo (`sampleImage`)

O texto escolhe sozinho entre claro/escuro conforme o plano por trás — acabou o “branco sobre cozinha branca”:

```javascript
// Effect > Generate > Fill (na layer de texto) → propriedade Color
const bg   = thisComp.layer("VIDEO");
const ctrl = thisComp.layer("CTRL");
const pt   = bg.fromComp(thisLayer.transform.position);   // ponto em layer-space do vídeo
const c    = bg.sampleImage(pt, [80, 50], true, time);    // amostra pós-effects
const lum  = 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2];
const claro = ctrl.effect("BASE_COLOR")("Color");
const escuro = ctrl.effect("INK_COLOR")("Color");
lum > 0.55 ? escuro : claro;
```

Regras de segurança:

- `sampleImage` corre **por frame** e é caro — em beats longos, avalia uma vez no `#HIT` e **congela** (senão o texto pisca quando um reflexo passa atrás);
- raio de amostragem proporcional ao corpo da letra (texto grande → área maior);
- com a caixa semi-opaca do Mário (`rgba(16,22,21,0.74)`) isto é quase desnecessário — a caixa já garante contraste; usar só em texto directo sobre vídeo.

### 2.6 Pulso ligado à música (audio-reactive)

Depois de *Animation → Keyframe Assistant → Convert Audio to Keyframes* (gera `Audio Amplitude`):

```javascript
// Scale do bloco hook/CTA — pulso por amplitude
const amp = thisComp.layer("AUDIO_AMPLITUDE").effect("Both Channels")("Slider");
const mx  = thisComp.layer("CTRL").effect("PULSE_MAX")("Slider");
const n   = Math.min(Math.max((amp - 2) / 24, 0), 1);   // calibrar 2/24 à faixa
const b   = 100 + n * mx;
[b, b];
```

- Só no hook e no CTA (máx. 4–6 pulsos — mesma regra do R8);
- calibra `2` e `24` olhando para o gráfico do slider: o limiar deve apanhar kicks, não o tapete da música;
- se o resultado tremer, suaviza o slider (`Smoother`) antes de ligar a expressão.

### 2.7 Decode reveal (source text)

DADO/GANCHO “à Matrix”, mas com **lock progressivo esquerda→direita** — lê-se a nascer, não a piscar:

```javascript
// Source Text da layer
const alvo  = "188 m²";
const passo = framesToTime(2);      // 2 f por carácter
const ab    = framesToTime(6);      // quanto cada char demora a fazer lock
const chars = "ABCDEFGHJKMNPQRSTUVWXYZ0123456789";
seedRandom(Math.floor(time / passo), true);
let out = "";
for (let i = 0; i < alvo.length; i++) {
  const tLock = inPoint + i * passo + ab;
  if (alvo[i] === " ") { out += " "; continue; }
  out += (time >= tLock) ? alvo[i] : chars[Math.floor(random(chars.length))];
}
out;
```

Click SFX **só no lock do último carácter** — um blip por char é ruído (ver §6).

### 2.8 Odómetro de preço com formatação PT

```javascript
// Source Text — conta de 0 ao alvo com easeOutQuart
const alvo = 685000;
const t0 = marker.key(1).time;              // marker #IN
const d  = framesToTime(16);
const p  = Math.min(Math.max((time - t0) / d, 0), 1);
const e  = 1 - Math.pow(1 - p, 4);
const v  = Math.round(alvo * e).toString();
let out = "", c = 0;
for (let i = v.length - 1; i >= 0; i--) {
  out = v[i] + out;
  if (++c % 3 === 0 && i > 0) out = " " + out;   // milhares com espaço, à PT
}
out + " €";
```

Regras: **só inteiros** (cêntimos a correr parecem bug); a unidade (`m²`, `€`, `T4`) entra **depois** do lock, nunca a correr junto; SFX = ratchet curto durante a subida + click no lock.

### 2.9 Bake antes do handoff

Expressões são para trabalhar, não para entregar: *Animation → Keyframe Assistant → Convert Expression to Keyframes* em cada propriedade antes de exportar para terceiros. Motivos: jitter subpixel em alguns renders, fontes ausentes na máquina do cliente, e review frame-a-frame sem motor de expressões.

---

## 3. Relógios: três escalas de sync

A grelha BPM detalhada está no [SOL §3](LEGENDAS-CINETICAS-AGRESSIVAS-SOL.md). Aqui fica a referência rápida **@24 fps** para pré-planeamento de copy (quantas palavras cabem numa barra) — e a regra dos três relógios.

### 3.1 Tabela BPM → frames

| BPM | 1 beat | 1 barra 4/4 | 1/16 (semicolcheia) |
|----:|-------:|------------:|--------------------:|
| 96  | 15,0 f | 60 f | ~3,8 f |
| 100 | 14,4 f | ~57,6 f | 3,6 f |
| 110 | ~13,1 f | ~52,4 f | ~3,3 f |
| 120 | 12,0 f | 48 f | 3,0 f |
| 126 | ~11,4 f | ~45,7 f | ~2,9 f |
| 128 | 11,25 f | 45 f | ~2,8 f |
| 140 | ~10,3 f | ~41,1 f | ~2,6 f |

**Nunca** arredondar a grelha inteira para a tabela: os markers vão nos transientes do áudio real (a música deriva). A tabela serve para escrever copy com o comprimento certo **antes** de abrir o AE.

### 3.2 Os três relógios

| Relógio | Escala | O que sincroniza | Tolerância |
|---------|--------|------------------|-----------|
| **Micro** | 0–4 f | SFX ↔ overshoot/lock | ±1 f |
| **Meso** | beat | entrada de palavra ↔ kick/snare | 2–4 f (whoosh entra **antes**) |
| **Macro** | barra | frase/divisão nova ↔ viragem musical | ±6 f |

Mudança de secção musical (drop, breakdown, último refrão) = mudança de assinatura ou de modo de energia. É o truque mais barato para um reel de 30 s não cansar.

---

## 4. Receitas K01–K12 (novas — não repetem R1–R8 nem SOL-01–10)

Valores para **1920×1080**; em 1080×1920 escalar pelo lado curto. `@f` = frames @24 fps. Todas assumem o rig do §2 (markers `#IN/#HIT/#OUT`, `CTRL`).

### K01 · Karaoke fill (sync com VO)

O clássico das captions de narração, feito com **1 layer** em vez de 40:

1. `Animate → Fill Color → RGB`, cor = HERO;
2. Range Selector: **Based on Words**, `Units: Percentage`, `Shape: Square`, `Ease High/Low: 0`;
3. animar `Start: 0 → 100%` exactamente sobre os tempos das palavras da voz (markers no áudio da narração);
4. opcional: segundo Animator com `Tracking +20 → 0` acompanhando o fill.

Fusion: Text+ → `Follower` com delay por palavra + Shading no Fill.  
**Regra dura:** o fill nunca chega **depois** da palavra falada — mais vale não ter fill nenhum. Uso: BENEFÍCIO, narração, depoimentos.

### K02 · Decode reveal

Expressão do §2.7. Agressão controlável: `passo` 1 f = fúria; 3 f = elegante. Só em 3–9 caracteres. DADO e GANCHO curto. Nunca numa morada.

### K03 · Chop stack (fatiado editorial)

A frase cortada em **3 tiras horizontais** que chegam em contra-fase:

```text
tira topo:   X −140 → 0    f00–f09
tira meio:   X +180 → 0    f03–f12
tira fundo:  X −100 → 0    f06–f15
convergência: tudo alinha em f15; micro-gap 1 px entre tiras some no settle
```

AE: 3 layers duplicadas do texto + máscaras rectangulares (topo 0–33%, meio 33–66%, fundo 66–100%) + Position. Fusion: Text+ → 3× `RectangleMask → Transform` → Merge em cadeia. Energia alta sem nenhum scale — bom para quando já houve 2 pops seguidos.

### K04 · RGB split hit (2–3 f, só no `#HIT`)

1. Duplica o texto 2×; layer A: `Shift Channels` (só R), blending **Add**, Position X −6; layer B: só B, Add, X +6;
2. existem apenas do frame `#HIT` ao `#HIT + 2` (ou 3, máximo absoluto);
3. ampliar o offset com o tamanho da letra: ~4 px a 60 pt, ~8–10 px a 140 pt.

Mais de 3 frames e deixa de ser impacto — passa a erro de impressão. Nunca em DADO pequeno (destrói dígitos).

### K05 · Knockout window (vês a casa através das letras)

Texto gigante (140–200 pt, 1–2 palavras) como **janela**:

1. plano wide escurecido ~40% (exposure/curves) como fundo;
2. texto como **Alpha Matte** do segundo plano (close-up da ilha, da vista, da lareira);
3. dentro das letras passa o close-up a 100%; scale da janela `100 → 104` durante o hold (respira);
4. entrada: scale `92 → 100` + opacity em 10 f — sem slam. O luxo aqui é o silêncio: **zero SFX**.

Uso: beat “hero” do imóvel, uma vez por peça. Anti-uso: plano escuro ou ruidoso dentro das letras (a janela deixa de ler).

### K06 · Magnetic anchor (texto preso ao espaço)

Mais barato que track 3D, mais vivo que texto colado:

1. AE Motion Tracker num ponto de alto contraste do plano (puxador, esquina da ilha, varão) → Null `NULL_TRACK`;
2. texto com expressão de **lag** — segue com atraso e amplitude reduzida:

```javascript
// Position do texto
const trk  = thisComp.layer("NULL_TRACK").transform.position;
const rest = [960, 1500];                       // posição de repouso no ecrã
const segue = trk.valueAtTime(time - framesToTime(4));   // 4 f de atraso
rest + (segue - trk.valueAtTime(inPoint)) * 0.55;        // 55% da amplitude
```

3. entrada/saída normais do rig por cima disto (parentar a um Null da animação).

Ajusta `0.55` (30–70%) e o atraso (3–6 f) por plano. Sai **antes** do ramp out. Prima suave do SOL-08: ali o texto deriva em contra-fase fixa; aqui segue o plano real com folga.

### K07 · Rubber band (stretch Disney)

Só para a palavra hero do hook:

```text
f00  ScaleY 100  Skew 0
f02  ScaleY 128  Skew +6°     (esticou no arranque)
f08  ScaleY 92   Skew −3°     (comprimiu no hit)
f12  ScaleY 100  Skew 0
```

Motion blur ON. **Números nunca se deformam** — DADO esticado perde credibilidade instantaneamente.

### K08 · Flip board (aeroporto)

Para LUGAR — nomes de zona com charme mecânico:

- AE: layer 3D ON, `Animate → Rotation X`, per-character: `−90 → +12 → 0`, stagger **1–2 f**, âncora no topo da letra;
- Fusion: o Follower do Text+ não roda em X de forma fiável — fazer fake: Scale Y `0 → 110 → 100` por carácter com easing duro, ou round-trip AE.

8–14 caracteres no máximo. A localização locked do Mário (`T4 Lumiar – QUINTA dos ALCOUTINS`) é **longa demais** para K08 — fica em fade/wipe, como manda o lock.

### K09 · Odómetro

Expressão do §2.8. 14–18 f de subida, easeOutQuart. Par combo: ratchet SFX + click no lock. Manter tabular nos dígitos — se a fonte não tiver figures tabulares, a coluna “dança”; nesse caso animar cada dígito em layer própria com largura fixa.

### K10 · Halo pulse (só CTA)

1. Ellipse shape atrás do CTA: Scale `0 → 140`, Stroke `6 → 0`, Opacity `90 → 0`, **18 f**;
2. repete 2–3× com intervalo de 40–48 f (ao kick, se a grelha deixar);
3. combina com o pulso de amplitude do §2.6 no texto.

É a assinatura sonora+visual do CTA: quando o halo aparece, acabou o vídeo. Nunca usar halo noutro beat — perde o significado.

### K11 · Ghost trail (eco temporal)

Diferente do SOL-10 (ecos coloridos manuais que convergem): aqui é **motion trail temporal**:

1. Effect `Echo`: `Number of Echoes 3`, `Echo Time` = −2/24 s, `Decay 0.5`, blending **Screen** (fundos escuros) ou sólido com matte (fundos claros);
2. expressão em `Number of Echoes`: `3` durante o ataque, `0` a partir do settle — o rasto morre quando a palavra assenta;
3. nunca em texto < 40 px (a 1080) nem durante o hold.

### K12 · Baseline wave (vida no hold)

Micro-movimento **durante o hold**, para a peça não morrer entre beats:

```javascript
// Position Y per-character via Text Animator + Expression Selector
// Animator: Position Y = 0; Range: Characters; Expression Selector Amount:
const freq = 3.0;             // velocidade
const passo = 0.6;            // desfasamento entre chars
Math.sin(time * freq + textIndex * passo) * 4;   // amplitude ≤ 5 px
```

Regras: amplitude máxima 4–5 px a 1080 (mais que isso lê-se a ondular, não a frase); desligar quando há dado a ser lido (odómetro a correr não ondula); no Mário **não** animar peso da variável como variante — pesos Medium/Bold estão locked; a wave é só posição.

---

## 5. Fusion: quem faz o quê

Mapa honesto de round-trip:

| Receita | Fusion nativo | Notas |
|---------|---------------|-------|
| K01 karaoke | Sim | Text+ Follower, delay por palavra |
| K03 chop stack | Sim | 3× `RectangleMask → Transform` → Merges |
| K05 knockout | Sim | Text+ ligado como **effect mask** do Merge do close-up; fundo com `ColorCorrector` −40% |
| K06 magnetic | Sim | Tracker → `Unsteady`/`Merge` ou Connect To no Center do Transform |
| K10 halo | Sim | `Ellipse → Transform` animado, Soft Edge no fim |
| K04 RGB split | Sim, mas penoso | 3× ChannelBooleans + Transforms; AE é 3× mais rápido |
| K02 decode, K09 odómetro | **AE round-trip** | StyledText com expressions em Fusion é frágil; exportar ProRes 4444/PNG+alpha |
| K07 rubber, K08 flip, K12 wave | AE round-trip | per-character e skew ficam melhores no AE |

Macro útil em Fusion: `K_BEAT` com controlos publicados (`InFrames`, `Overshoot`, `CorHero`, `CorDado`) — espelho da `CTRL` do AE, para manter a mesma linguagem nos dois mundos. Restante setup Fusion (Follower, macros, quando fazer round-trip) está no [SOL §7](LEGENDAS-CINETICAS-AGRESSIVAS-SOL.md).

---

## 6. SFX: partitura, dinâmica e whoosh caseiro

As três camadas (ar / corpo / detalhe) e o pré-sync estão no [SOL §8](LEGENDAS-CINETICAS-AGRESSIVAS-SOL.md). O que este doc acrescenta:

### 6.1 Partitura de 16 passos

Trata uma barra como um step-sequencer. A 120 BPM: 1 passo = 3 f. Escreve o beat **antes** de animar:

```text
passo   1   2   3   4   5   6   7   8   9  10  11  12  13  14  15  16
música  K   .   .   .   S   .   .   .   K   .   .   .   S   .   .   .
visual  IN  .   .   HIT .   .   P2  P2H .   .   LCK .   CHS .   .   .
SFX     wh  .   .   clk .   .   .   tck .   .   blp .   .   .   .   .
```

`IN`=ataque, `HIT`=overshoot, `P2`=palavra 2, `LCK`=lock de dado, `CHS`=color chase. Regras:

- **máx. 1 evento sonoro por passo**; dois SFX no mesmo passo é ruído;
- deixar ≥ 25% dos passos vazios — o silêncio é o que faz o próximo hit parecer grande;
- o passo do `HIT` tem sempre prioridade: se a música e a legenda discordam, move-se a legenda.

### 6.2 Dinâmica (velocity)

SFX não são binários. Escala o ganho com a energia da secção (grelha do [SOL §3.3](LEGENDAS-CINETICAS-AGRESSIVAS-SOL.md)):

| Secção | Ganho relativo do SFX |
|--------|----------------------|
| Hook | 0 dB (referência) |
| Divisões | −4 a −6 dB |
| CTA | −1 a −2 dB (presente, não estridente) |
| Logos / cartão | −∞ (sem SFX; fade only) |

E variar pitch ±2 semitons em eventos repetidos (clicks de tiles) — regra já conhecida, aqui aplicada à partitura inteira.

### 6.3 Whoosh caseiro em 30 segundos

Quando a biblioteca falha (ou soa a pack):

1. ruído rosa/branco, 250–300 ms;
2. lowpass sweep 400 Hz → 3–5 kHz (sobe com o movimento);
3. pitch bend +3 a +5 semitons de início para fim;
4. envelope: ataque ~30%, decay rápido no fim;
5. EQ final: corta abaixo de 120–180 Hz para não brigar com o kick.

Grava 4 variações (curto/longo, claro/grave) e guarda na biblioteca do projecto. Loudness final e export: [`MASTERING.md`](MASTERING.md).

---

## 7. Safe zones dinâmicas

As medidas conservadoras estão no [SOL §9](LEGENDAS-CINETICAS-AGRESSIVAS-SOL.md). Aqui: o que muda por plataforma e por plano.

### 7.1 Por plataforma (1080×1920)

| Zona | Reels (IG) | TikTok | Shorts |
|------|-----------|--------|--------|
| Fundo livre até | y ≈ 1580 | y ≈ 1560 | y ≈ 1620 |
| CTA essencial acima de | y ≈ 1480 | y ≈ 1450 | y ≈ 1520 |
| Coluna direita morta | ~140 px | ~150 px | ~110 px |
| Topo (username/capa) | y ≥ 170 | y ≥ 180 | y ≥ 140 |

Valores de referência — **a UI muda sem aviso**: guardar um PNG overlay por plataforma na pasta do projecto e confirmar com um reel real antes de entregar. Na dúvida, usa os números conservadores do SOL.

### 7.2 Terço móvel (por plano, não por plataforma)

Antes de animar, anotar por plano onde está a **zona morta**:

| Plano típico | Zona de menor valor | Posição da legenda |
|--------------|--------------------|--------------------|
| Fachada | céu (terço superior) ou rua (fundo) | topo se o céu for liso; fundo se houver placa |
| Sala wide | chão em primeiro plano | terço inferior deslocado do sofá |
| Cozinha ilha | bancada (terço inferior) | fundo, nunca sobre o fogão/ilha hero |
| Quarto | parede da cabeceira | terço superior |
| Terraço/vista | céu | topo — **nunca** tapar o horizonte |
| Piscina | água lisa | canto de água; legenda nunca corta a linha de água |

A legenda **muda de sítio com o plano** — terço fixo em todos os planos é o anti-padrão nº 1 dos tours com kinetic.

### 7.3 Três testes de 5 segundos

1. **Blur test** — Gaussian blur forte no preview: se a hierarquia (o que é hero vs. detalhe) ainda se percebe em manchas, está bom;
2. **Thumb test** — tapa com o polegar a zona da UI no telemóvel: se perdes informação, move;
3. **Grey test** — preview dessaturado: se BASE/HERO/DADO deixam de se distinguir, a cor está a carregar significado a mais (reforçar com escala/peso).

---

## 8. Workflow: beat sheet como dados

O salto de produtividade não é o preset — é **a peça descrita como dados** antes de abrir o AE.

### 8.1 Beat sheet (exemplo)

```json
{
  "fps": 24, "size": [1080, 1920], "mode": "SOCIAL",
  "beats": [
    { "t": "00:00:00:00", "fn": "GANCHO",    "txt": "ESGOTOU EM 48H",          "recipe": "K07" },
    { "t": "00:00:01:12", "fn": "DADO",      "txt": "685 000 €",               "recipe": "K09" },
    { "t": "00:00:02:08", "fn": "LUGAR",     "txt": "LUMIAR",                  "recipe": "K08" },
    { "t": "00:00:04:00", "fn": "BENEFICIO", "txt": "LUZ O DIA TODO",          "recipe": "K01" },
    { "t": "00:00:26:00", "fn": "CTA",       "txt": "MARQUE A SUA VISITA",     "recipe": "K10" }
  ]
}
```

- O stage `edit` do pipeline pode **gerar este ficheiro** (copy + markers da música) e o rig do §2 monta os beats com markers `#IN/#HIT/#OUT` derivados de `t`;
- em AE, um ExtendScript curto lê o JSON e cria layers+markers; manualmente são ~3 min por beat;
- a beat sheet é o que se revê com o cliente — muito mais barato mudar `"txt"` aqui do que na comp.

### 8.2 Presets: o que se guarda

Coerente com o SOL (não guardar copy/font/cor/posição), com acréscimo de naming versionado:

```text
K_IN_Decode_p2f_v1.ffx
K_DATA_Odometer_16f_v2.ffx
K_CTA_HaloPulse_18f_v1.ffx
K_HOLD_BaseWave_4px_v1.ffx
```

Duração no nome (como o SOL pede) **+ versão** — quando afinares um preset num cliente, sobe a versão, nunca edites por cima: peças antigas têm de continuar reproduzíveis.

---

## 9. Anti-padrões novos (os deste doc)

Os clássicos estão no [v2 §12](LEGENDAS-CINETICAS-AGRESSIVAS.md) e no [SOL §12](LEGENDAS-CINETICAS-AGRESSIVAS-SOL.md). Estes são os que o rig/gramática introduzem:

1. **Hit no primeiro keyframe** — o impacto pertence ao overshoot (`#HIT`), não ao início do movimento;
2. Duas assinaturas para a mesma função na mesma peça (preço com odómetro no hook e com elastic na cozinha);
3. Karaoke fill mais lento que a voz — a cor a chegar depois da palavra é pior que nenhum fill;
4. Odómetro com decimais/cêntimos a correr;
5. Knockout (K05) sobre plano escuro ou ruidoso;
6. Ghost trail (K11) ou RGB split (K04) em texto < 40 px;
7. `sampleImage` sem congelar — texto a trocar de cor quando um reflexo passa atrás;
8. Baseline wave com amplitude > 6 px;
9. Rig com 40 layers por beat — se mudar o timing não for “arrastar 1 marker”, o rig está mal feito;
10. Expressões por fazer bake antes do handoff;
11. RGB split > 3 f (vira erro de impressão);
12. Elástico com mais de 1,5 oscilações visíveis (energia ≠ mola);
13. Rig aplicado a logos e cartão final — esses ficam em **fade only**;
14. Animar o peso da variável no Mário — pesos locked (Medium/Bold); vida vem de posição e cor, não do eixo `wght`.

---

## 10. Sequências prontas (motor KIMI)

### Hook K-A · “48 horas” — 5 s / 120 f (MAX)

```text
f00–13   ESGOTOU        K07 rubber band, HERO
f12–23   EM 48 HORAS    K03 chop stack, BASE
f24–41   685 000 €      K09 odómetro, DADO — lock em f40 com click
f42–71   hold com K12 wave fraca (3 px)
f72–95   LUMIAR         K08 flip board, ACÇÃO
f96–119  saída split + halo já a nascer para o CTA
```

### Hook K-B · “decode da vista” — 4 s / 96 f (SOCIAL)

```text
f00–19   VISTA RIO      K02 decode (passo 2 f), HERO
f20–47   plano abre; karaoke fill K01 sobre a frase do VO, BASE→HERO
f48–83   K05 knockout: dentro de “ABERTA” corre o close da varanda
f84–95   janela abre scale 104 → corte para o interior
```

### Hook K-C · “três dígitos” — 4,5 s / 108 f (SOCIAL)

```text
f00–17   188 m²         K09 + tile, DADO
f18–35   T4             K02 decode curto, DADO
f36–53   2 LUGARES      K09, DADO
f54–83   os três tiles alinham em stack (K03 convergente)
f84–107  stack sai; 1 beat vazio antes da fachada
```

### Tour por divisão (gramática aplicada)

| Divisão | Função dominante | Receita | Energia |
|---------|------------------|---------|---------|
| Fachada | LUGAR | K08 flip ou wipe âncora | 65–80% |
| Sala | BENEFÍCIO | K01 karaoke do VO + K12 wave | 55–70% |
| Cozinha | DADO | tile + K09 (m², bancada) | 45–60% |
| Quartos | respiração | fade + K12 só | 35–50% |
| Terraço | BENEFÍCIO hero | K05 knockout (1× na peça) | 60–75% |
| CTA | CTA | K10 halo + assinatura do hook | 75–90% |
| Cartão | — | fade only | 10–20% |

CTA reutiliza a assinatura do hook — fecho do sistema.

---

## 11. QA extra do motor (somar às três passagens do SOL)

- [ ] Arrastar o marker `#IN` de um beat move **tudo** (texto, caixa, flash) — se não move, o rig falhou;
- [ ] Caixa segue a tinta com copy nova (testar com a frase mais longa do cliente — ver limite de 946 px e quebra em 2 linhas no Mário);
- [ ] Contraste adaptativo congelado no hold;
- [ ] Odómetro/decode com seed fixo e formatação PT (espaço nos milhares);
- [ ] Bake das expressões feito antes do export/handoff;
- [ ] Função de cada beat declarada na beat sheet (sem função → sem assinatura → não entra);
- [ ] Locks do cliente intactos (fonte, pesos, localização completa, barra, cartão).

---

## 12. Quando usar este doc vs `LEGENDAS-CINETICAS-AGRESSIVAS.md` vs `LEGENDAS-CINETICAS-AGRESSIVAS-SOL.md`

- **Usar [`LEGENDAS-CINETICAS-AGRESSIVAS.md`](LEGENDAS-CINETICAS-AGRESSIVAS.md)** quando precisas das receitas-base consolidadas e da grelha de tempo geral: pop cascade, whip slam, stacked punch, scramble de dígitos, mask wipe, kick pulse, pipeline AE→Resolve e QA essencial. É o dicionário rápido.
- **Usar [`LEGENDAS-CINETICAS-AGRESSIVAS-SOL.md`](LEGENDAS-CINETICAS-AGRESSIVAS-SOL.md)** quando a decisão é de **sistema de energia**: brand-safe vs social vs max-aggression, grelha de beats ao BPM, papéis de cor, SFX em 3 camadas, safe zones medidas, matriz de variação e presets macro.
- **Usar este doc (KIMI)** quando vais **construir ou correr o motor**: gramática função→assinatura, rig procedural com markers `#IN/#HIT/#OUT`, caixas auto-tinta, contraste adaptativo, pulso audio-reactive, decode/odómetro com formatação PT, partitura SFX de 16 passos, beat sheet como dados e as receitas K01–K12 que os outros não cobrem.

Em produção, a combinação típica é: **modo de energia do SOL + receitas-base da v2 + motor e gramática KIMI + locks do cliente + finishing de [`MASTERING.md`](MASTERING.md).**

---

*Playbook vivo — quando um rig for usado em cliente, anotar valores reais (overshoot, passo do decode, amplitude do pulso) no ESTILO-CLIENTE desse projecto.*
