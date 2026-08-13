# Legendas cinéticas agressivas — playbook de produção

Versão **2** — mais densa que a lista de ideias: valores frame-a-frame (@24 fps), princípios de motion, setups AE/Resolve, paletas, SFX e sequências prontas a montar.

Complementa [`TIPOGRAFIA-REAL-ESTATE.md`](TIPOGRAFIA-REAL-ESTATE.md).  
Respeita sempre `ESTILO-CLIENTE.md` quando houver fonte/cor locked (ex. Montserrat no Mário).

---

## 0. O que separa “vivo” de “barulho”

Kinetic agressivo **não** é meter bounce em tudo. É:

1. **Contraste de energia** — ataque rápido + settle limpo + hold legível  
2. **Uma ideia por beat** — uma claim, um número, um gancho  
3. **Sistema** — 4–5 cores, 2 pesos, 3 movimentos-base repetidos  
4. **Som** — whoosh/click a vender o settle  
5. **Espaço** — o vídeo respira; o texto não tapa a arquitectura  

Se removesses a cor e o bounce e a peça ainda tivesse ritmo, está bem construída.

---

## 1. Princípios (Disney → tipografia)

| Princípio | Em legendas |
|-----------|-------------|
| **Anticipation** | 2–3 frames a contrair (scale 0.92 ou Y+6) **antes** do slam |
| **Overshoot / settle** | Passa o alvo 8–15% e volta — 3–5 frames |
| **Staging** | Uma hero-word; o resto menor ou mais tarde |
| **Follow-through** | Linha 2 entra 3–4 frames depois da 1 |
| **Slow in/out** | Graph Editor: ataque íngreme, aterragem plana |
| **Arcs** | Position em curva ligeira (não só eixo ortogonal) nos whips longos |
| **Exaggeration** | No hook; no hold da sala, baixa 50% |

### Curva de velocidade mental (Graph Editor)

```
valor
  ^
  |     *  ← overshoot
  |    / \
  |   /   \___  ← settle
  |  /
  |_*           ← anticipation (opcional)
  +--------------→ tempo
   in   hit  hold
```

No AE: selecciona keyframes → `F9` (Easy Ease) → Graph Editor → puxa a pega de **influência** do primeiro keyframe para ~15–25% (ataque) e a do settle para ~60–80% (aterragem macia).

---

## 2. Grelha de tempo (@24 fps)

| Nome | Frames | Uso |
|------|--------|-----|
| Snap | 4–6 | Flash, opacity slam |
| Punch | 8–12 | Pop scale padrão |
| Whip | 10–16 | Position de fora do frame |
| Soft | 16–20 | Luxury / fade elegante |
| Hold curto | 28–40 | Agressivo (1,2–1,7 s) |
| Hold médio | 48–72 | Specs legíveis (2–3 s) |
| Stagger palavra | 2–3 | Cascata |
| Stagger linha | 3–5 | Stacked |
| Gap entre beats | 2–8 | Silêncio visual |

**Regra de leitura:** hold ≥ tempo de ler a frase **2×** em voz alta. Se não der, a frase é longa demais — corta palavras, não a animação.

---

## 3. Sistema visual

### Tipografia
- **1 família** (Montserrat / similar): Black/ExtraBold no punch, Medium no corpo, Bold CAPS no label  
- Tracking: CAPS +100 a +200; corpo normal  
- Evitar Thin/Light; stroke 2–4 px ou sombra dura `(4, 4) opacity 40–60%`  
- Quebra: máx. **2 linhas**; preferir 1  

### Paletas (escolhe **uma** por peça)

**Neon punch (social máximo)**
```
#FFFFFF  #FF2D55  #00E5FF  #FFD60A  #0A0A0A
```

**Broker hot (RE-friendly agressivo)**
```
#FFFFFF  #E11D2E  #1C355E  #F5C518  #111827
```

**Acid editorial**
```
#F7F7F2  #111111  #C8F53C  #FF4D00  #2A2A2A
```

Uso: branco = base; 1 accent por beat; amarelo/lima = **1×** por ecrã (preço ou palavra nuclear).

### Safe zones (9:16)
- Evitar ~12% inferior (UI IG/TikTok)  
- Evitar cantos superiores extremos (username / Close)  
- Hero text: centro / centro-baixo, nunca a tapar rostos ou a lareira do plano  

### Safe zones (16:9)
- Terço inferior clássico; margem ≥ 5%  
- Logos nos cantos; legenda **não** compete com a placa de localização locked  

---

## 4. Anatomia de um beat

```
[anticipation 2f] → [ataque 6–12f] → [overshoot 3–5f] → [HOLD] → [out 6–10f]
                         ↑
                    SFX whoosh/click
```

Camadas típicas (de baixo para cima):
1. Bloco / pill / underline (opcional)  
2. Palavra(s)  
3. Accent flash / grain (opcional, 1–2 f)  

---

## 5. Receitas frame-a-frame

Valores para **1920×1080** (escala proporcional em 1080×1920).  
Origin = ponto final da palavra. Position delta em px.

### R1 · Pop cascade (palavras)

Por palavra, Scale + Opacity:

| Frame | Scale % | Opacity |
|------:|--------:|--------:|
| 0 | 0 | 0 |
| 2 | 40 | 100 |
| 8 | 118 | 100 |
| 12 | 100 | 100 |
| hold… | 100 | 100 |
| hold+0 | 100 | 100 |
| hold+8 | 0 | 0 |

- Stagger +2 f ou +3 f por palavra  
- Cores intercaladas da paleta  
- Anchor Point no **centro** da palavra  
- Motion Blur ON (AE) nas layers  

**AE shortcut:** Animate → Enable per-character **não** no pop de palavra inteira; usa layers separadas ou Text Evo / preset.

### R2 · Whip slam (frase)

Position X (entra da direita) + Scale:

| Frame | X | Scale | Opacity |
|------:|--:|------:|--------:|
| 0 | +900 | 90 | 0 |
| 2 | +900 | 90 | 100 |
| 10 | −80 | 112 | 100 |
| 14 | 0 | 100 | 100 |

Out (sobe):

| Frame | Y | Opacity |
|------:|--:|--------:|
| 0 | 0 | 100 |
| 8 | −120 | 0 |

No frame 10–11: solid branco 100% opacity **1–2 frames** (Adjustment / flash) opcional.

### R3 · Stacked punch

Ordem de montagem:
1. **f0–4:** retângulo accent, Scale X `0 → 100` (anchor esquerda)  
2. **f3:** linha 1 (preço) — Pop R1  
3. **f6:** linha 2 CAPS — Y `+40 → 0`, opacity `0 → 100` em 8 f  
4. **f10:** linha 3 detail — igual, mais pequena  

Out: tudo sobe Y `0 → −60` + opacity em 8 f, **ou** Scale X do bloco `100 → 0` (anchor esquerda).

### R4 · Vida própria (matriz de direcções)

Não repeats o mesmo eixo em beats consecutivos.

| Beat | In (delta) | Out (delta) | Scale in |
|-----:|------------|-------------|----------|
| 1 | Y +120 | X −200 | Pop |
| 2 | X +160 | Y −100 | Whip |
| 3 | Y −100 | X +180 | Pop |
| 4 | scale only | Y +80 + fade | Soft |
| 5 | X −140 | scale → 0 | Whip |

Hold 32–40 f. Rodar cores A→B→C→branco→A.

### R5 · Number scramble → lock

1. **f0–6:** texto com expressão / manual swap de dígitos a cada 1–2 f; cor accent  
2. **f7:** valor final correcto; cor branco  
3. **f7–11:** Scale `108 → 100`  
4. Click SFX em f7  

Expressão AE (opcional, layer texto):

```javascript
// scramble até marker "LOCK"
seedRandom(index + timeToFrames(time), true);
tLock = 7/24; // segundos
if (time < tLock) {
  digits = "0123456789";
  s = "";
  for (i = 0; i < 3; i++) s += digits[Math.floor(random(10))];
  s + " m²"
} else {
  "188 m²"
}
```

### R6 · Mask wipe + recolor

1. Texto final já posicionado (opacity 100)  
2. Track matte / máscara: rect L→R, 8–12 f  
3. Duplica texto por baixo em accent; segunda máscara atrasa 2 f → “reveal bicolor”  
4. Out: máscara R→L ou Y↓  

### R7 · Anticipation punch (uma palavra nuclear)

| Frame | Scale | Y |
|------:|------:|--:|
| 0 | 100 | 0 |
| 3 | 88 | +8 |
| 4 | 88 | +8 |
| 10 | 122 | −6 |
| 14 | 100 | 0 |

Parece “respirar” antes do hit — muito mais caro que pop seco.

### R8 · Kick pulse (beat-sync)

Em cada kick da música (marca markers):
- Scale `100 → 106 → 100` em **3 frames**  
- Fill flash accent **1 frame** (opcional)  
- Só no bloco hook/CTA (máx. 4–6 pulses)

---

## 6. Text Animators (AE) — quando 1 layer chega

Em vez de 20 layers, numa só Text layer:

**Animate →**
- **Position** Y `+40`, Range Selector Start `0→100%` em 10 f, Based on **Words** ou **Characters**  
- **Scale** `0%` com Offset staggered  
- **Fill Color** — segundo Animator, End a seguir ao primeiro  
- **Blur** `12 → 0` no ataque (caro visual, 1× por beat)

Advanced → Ease High / Ease Low nos Range Selectors ≈ overshoot barato.

Guarda: selecciona propriedades → Effects & Presets → **Save Animation Preset**.

---

## 7. Resolve (sem AE)

| Objectivo | Como |
|-----------|------|
| Pop simples | Text+ → Inspector Scale keyframes 0→1.2→1 |
| Whip | Position X keyframes + Ease no Keyframe panel |
| Stacked | 3× Text+ staggered |
| Flash | Adjustment Clip 1–2 f + Brightness |
| Blur no ataque | Fusion: Text+ → Blur → Merge; anima Blur Size 15→0 |
| Motion blur | Fusion Vector MB ou Merge Motion Blur nos merges rápidos |

Limite Free: Text+ keyframes por API/UI são mais toscos que AE. Para agressão séria → **AE → ProRes 4444 / PNG sequence com alpha** → V2 no Resolve.

---

## 8. Áudio (a metade do “vivo”)

| Evento visual | SFX |
|---------------|-----|
| Whip in | Whoosh curto, **1–3 f early** |
| Slam / pop settle | Click / tick / soft hit |
| Scramble lock | UI blip |
| Stacked linha 1 | Hit low |
| Out | Whoosh reverse ou nada |

Níveis: SFX abaixo da música; whoosh audível (−12 a −6 dB tipicamente — calibra).  
Mute sempre o áudio do clip de vídeo retimado.

---

## 9. Sequências prontas

### Hook A — 6 s (máxima agressão)
```
0:00  ESPERA          R7 anticipation + R1 pop (#FF2D55)
0:01  PELO            R2 whip L→R (#00E5FF)
0:02  JARDIM          R1 slam + flash 2f (#FFD60A)
0:03  stacked         R3 preço/zona/tip
0:05  OUT             direcções cruzadas R4
```

### Hook B — 4 s (número)
```
0:00  scramble→188 m²   R5
0:02  ÚTEIS             R1 branco
0:03  OUT scale         
```

### Por divisão (tour, menos cansativo)
```
ramp in → +0.3s → legenda R2 ou R4 (1 claim) → hold → out −0.5s antes do ramp out
```
Cores: só **uma** accent por divisão; resto branco.

### CTA final
```
MARQUE A SUA VISITA   R2 slam brand red
telefone              R3 linha 2
logos                 fade only (sem bounce)
```

---

## 10. Pipeline recomendado

```
1. Picture lock + ramps OK
2. Lista de beats (copy curta) + markers na timeline da música
3. AE: comps 1920×1080 ou 1080×1920, fundo transparente
4. Uma comp por beat OU uma comp master com markers
5. Export ProRes 4444 / QuickTime PNG+alpha
6. Resolve V2+ · sync SFX
7. Preview telemóvel @100%
```

**Não** animes legendas no mesmo compound onde o Optical Flow do ramp já está a sofrer — overlay separado.

---

## 11. Controlo de qualidade

- [ ] Lê-se no telemóvel sem pausar  
- [ ] Nenhuma palavra entra no whoosh do ramp  
- [ ] Máx. 1 pop “elástico” por 3 s  
- [ ] Paleta ≤ 5 cores  
- [ ] Safe UI respeitada  
- [ ] SFX sync (early whoosh)  
- [ ] Arquitectura do plano ainda se vê  
- [ ] Cliente com font locked → pesos Montserrat/Gotham ok  

---

## 12. Anti-padrões (versão dura)

1. Bounce preset em 100% das layers  
2. Rainbow random por letra  
3. Frase de anúncio com `|` animada palavra a palavra  
4. Thin gold script + glow  
5. Texto 3D em todos os planos  
6. Hold 15 frames com 8 palavras  
7. Kinetic a tapar o único ponto de interesse do I2V  
8. Copiar TikTok caption style em tour Sotheby's-like  

---

## 13. Upgrade path (do “ok” ao “melhor”)

| Nível | O que fazer |
|-------|-------------|
| 1 | Pop + fade, 1 cor accent |
| 2 | + overshoot + stagger + whoosh |
| 3 | + matriz R4 + stacked R3 + scramble números |
| 4 | + anticipation R7 + mask wipe + beat markers |
| 5 | Presets AE reutilizáveis + biblioteca SFX + brand kit |

A v1 deste doc parava no nível 2. Esta v2 cobre **3–4** com valores utilizáveis.

---

## 14. Referências

- YouTube: *How to Edit Viral Realtor Captions in After Effects* (word layers, F9, graph, Text Evo)  
- AE Text Animators (Range Selectors / per-word)  
- [`TIPOGRAFIA-REAL-ESTATE.md`](TIPOGRAFIA-REAL-ESTATE.md) — densidade por gama  
- mReal Estate / Captions.ai — referências de layout, não de tom obrigatório  

---

*Playbook vivo — se uma receita for usada em cliente, anotar hex e fps reais no ESTILO-CLIENTE.*
