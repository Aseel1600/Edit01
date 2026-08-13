# Legendas cinéticas agressivas — sistema SOL

Playbook de execução para **reels 9:16** e **tours 16:9** com tipografia muito viva, multicolor, ritmada e controlável. A abordagem aqui é modular: primeiro define-se o nível de agressão, depois constrói-se uma grelha de beats, e só então se aplicam receitas de animação.

Este documento complementa:

- [`LEGENDAS-CINETICAS-AGRESSIVAS.md`](LEGENDAS-CINETICAS-AGRESSIVAS.md) — biblioteca-base de pops, whips, stacks e timings;
- [`TIPOGRAFIA-REAL-ESTATE.md`](TIPOGRAFIA-REAL-ESTATE.md) — regras de gama, hierarquia, densidade e legibilidade;
- [`MASTERING.md`](MASTERING.md) — ramps, optical flow, montagem, áudio e export;
- [`ESTILO-CLIENTE.md`](projects/video-service-business/clients/Mario%20Garces/ESTILO-CLIENTE.md) — locks do Mário Garcês.

> **Locks vencem este playbook.** Para Mário Garcês: usar **Montserrat** nas legendas e cartão; respeitar pesos, geometria, barra vermelho/azul, localização completa locked e restantes medidas aprovadas. “Agressivo” muda movimento, escala e cor permitida — não muda a identidade do cliente.

---

## 1. O modelo SOL: Slam, Organização, Leitura

Uma legenda agressiva funciona quando as três camadas estão presentes:

1. **Slam** — ataque visual curto, inequívoco e sincronizado;
2. **Organização** — palavras, cores e direcções obedecem a uma gramática;
3. **Leitura** — o hold é calmo o suficiente para a informação entrar.

O erro comum é prolongar o slam durante toda a frase. A energia deve ocupar cerca de **20–30% do beat**; os restantes **70–80%** são settle e leitura.

Anatomia recomendada @24 fps:

```text
f00–02  preparação / pré-eco
f03–10  ataque principal
f11–15  overshoot e settle
f16–47  hold legível
f48–55  saída
```

Para hooks extremos, encurta o hold; não alongues o ataque:

```text
f00–01  preparação
f02–07  ataque
f08–11  settle
f12–27  hold
f28–33  saída
```

---

## 2. Primeiro escolhe o modo de energia

### Modo A — Brand-safe agressivo

Para brokers, imóveis de gama média-alta e clientes com manual rigoroso.

- 1 família tipográfica;
- 2 pesos;
- branco + cor de marca + 1 cor funcional;
- máximo de 2 direcções de entrada por sequência;
- overshoot de `104–110%`;
- 1 efeito protagonista por beat;
- SFX curtos, secos e discretos;
- texto cobre no máximo 18–22% da área útil.

**Densidade:** 1 legenda por divisão hero; 2–4 planos seguidos podem respirar sem texto.

### Modo B — Social high-energy

Para reels orientados a retenção, imóveis mid-market, open house e lançamento.

- 3–4 cores activas por peça, mas só 2 simultâneas por beat;
- per-word e per-character permitidos;
- overshoot de `110–118%`;
- wipes, underlines e cards em contra-tempo;
- alteração de direcção entre beats;
- SFX em camadas: ar + impacto + detalhe;
- texto cobre no máximo 28–32% da área útil.

**Densidade:** 1 evento tipográfico a cada 0,8–1,8 s no hook; depois baixar para 1 a cada 3–5 s.

### Modo C — Max-aggression

Para teaser de 6–15 s, anúncio “just listed”, contagem decrescente ou corte de evento. Não é o modo normal de um tour.

- 4–5 cores totais;
- cortes de frase em sílabas ou blocos;
- deformação de largura/peso, smear e pseudo-3D pontuais;
- overshoot até `122%`, apenas em palavras hero;
- flashes de 1 frame;
- shakes de 2–4 frames apenas no impacto;
- cobertura máxima de 38% no hook e 25% no resto;
- após 3 beats fortes, inserir **12–24 frames sem animação nova**.

**Proibição:** não usar este modo num imóvel luxury só porque a música tem BPM alto. A gama e o cliente continuam a mandar.

---

## 3. Grelha de beats @24 fps

### 3.1 Criar a grelha

Antes de abrir o AE ou Fusion:

1. marca kicks, snares, vocal cuts e transições da música;
2. classifica cada marker como `K` (kick), `S` (snare), `V` (voz) ou `T` (transição);
3. atribui uma função visual a cada beat;
4. deixa beats intencionalmente vazios.

Exemplo para música a **120 BPM**:

```text
1 beat = 0,5 s = 12 frames
1 barra 4/4 = 2 s = 48 frames
```

Mapa de uma barra:

```text
f00 K  bloco entra
f12 S  palavra hero troca de cor
f24 K  número faz lock
f36 S  underline corta
f44–47 saída rápida
```

Exemplo a **96 BPM**:

```text
1 beat = 0,625 s = 15 frames
1 barra = 60 frames
```

Não arredondar todos os eventos para 15 frames se a música derivar. Colocar markers no áudio real e usar os frames exactos.

### 3.2 Regra de pré-sync

O olho tolera o movimento a começar antes do som; tolera menos um impacto visual atrasado.

- whoosh começa **2–4 frames antes** do hit;
- texto atinge o overshoot **no hit**;
- click/tick coincide com o primeiro frame do valor final;
- sub-hit grave pode cair **1 frame depois** para sensação de peso;
- reverse whoosh termina no primeiro frame sem texto.

### 3.3 Escala de energia por secção

```text
HOOK       90–100%
FACHADA    65–80%
SALA       55–70%
COZINHA    45–60%
QUARTOS    35–50%
TERRAÇO    60–75%
CTA        75–90%
LOGOS      10–20%
```

Assim a peça mantém contraste. Se tudo está a 100%, nada parece forte.

---

## 4. Sistema de cor multicolor sem arco-íris

### 4.1 Papéis, não cores aleatórias

Atribui um papel fixo a cada cor:

```text
BASE       texto principal
HERO       palavra emocional / benefício
DADO       preço, área, quartos
ACÇÃO      CTA
INK        caixa, sombra, stroke
```

Exemplo **Broker Electric**:

```text
BASE   #FFFFFF
HERO   #FF3B30  vermelho energético
DADO   #FFD60A  amarelo numérico
ACÇÃO  #2F80ED  azul confiança
INK    #0B1020  navy quase preto
```

Exemplo **Poolside Acid**:

```text
BASE   #F7F7F2
HERO   #B8F500  lima
DADO   #00D8FF  ciano
ACÇÃO  #FF5A36  laranja
INK    #111111
```

Exemplo **Luxury Voltage**:

```text
BASE   #F4F0E8
HERO   #C7A44A  dourado seco
DADO   #D84A3A  terracota
ACÇÃO  #214761  azul petróleo
INK    #101820
```

### 4.2 Regras de rotação

- uma palavra não muda de cor mais de **uma vez** durante o hold;
- não mostrar mais de **duas cores saturadas** no mesmo frame;
- dados repetidos mantêm sempre a mesma cor;
- vermelho pode significar hero ou CTA, mas não ambos na mesma peça;
- em interiores quentes, privilegiar ciano/azul; em exteriores frios, amarelo/laranja;
- testar contraste sobre o plano real, não apenas em fundo preto.

### 4.3 Técnica “color chase”

Boa para uma frase de 3–5 palavras:

```text
f00–05  todas entram em BASE
f06     palavra 1 → HERO
f09     palavra 1 → BASE; palavra 2 → HERO
f12     palavra 2 → BASE; palavra 3 → HERO
f15     palavra nuclear fica HERO
```

O chase dura no máximo 12 frames. Depois a composição estabiliza.

---

## 5. Receitas novas frame-a-frame

Valores de posição abaixo referem-se a comp 1920×1080. Em vertical, usar percentagens ou escalar pelo lado curto.

### SOL-01 · Compressor slam por palavra

Sensação: a palavra é esmagada horizontalmente e explode para a largura certa.

```text
f00  Scale X 18%   Scale Y 118%  Opacity 0
f02  Scale X 18%   Scale Y 118%  Opacity 100
f07  Scale X 112%  Scale Y 94%
f11  Scale X 97%   Scale Y 103%
f15  Scale X 100%  Scale Y 100%
```

- stagger de 2 frames por palavra;
- anchor no centro para hook; à esquerda para lower third;
- smear direccional de 18–30 px entre f02 e f08;
- hit no f07; click leve no f15;
- usar apenas em Bold/ExtraBold.

### SOL-02 · Split-axis ricochet

Cada linha entra por um eixo e sai por outro.

```text
LINHA 1
f00  X -420  Y 0    Rotate -4°  Opacity 0
f08  X +24   Y 0    Rotate +1°
f12  X 0     Y 0    Rotate 0°

LINHA 2, atraso 3f
f03  X 0     Y +110 Scale 92%   Opacity 0
f11  X 0     Y -10  Scale 106%
f15  X 0     Y 0    Scale 100%

OUT
8f: linha 1 Y -90; linha 2 X +240; ambas opacity 0
```

Excelente para `VISTA ABERTA / SOBRE A CIDADE`.

### SOL-03 · Word piston

As palavras sobem como pistões, uma alta e outra baixa.

```text
palavras ímpares:  Y +90 → -12 → 0
palavras pares:    Y -90 → +12 → 0
duração:           10f + settle 4f
stagger:           2f
```

Adicionar barra de fundo com `Scale X 0 → 100%` em 7 frames. A barra deve acabar 2 frames antes da última palavra.

### SOL-04 · Weight punch

Para fontes variáveis. A geometria fica no lugar; a energia vem do peso.

```text
f00  weight 400  tracking +80
f05  weight 900  tracking -20
f09  weight 700  tracking 0
f12  weight 800  tracking 0
```

No AE, a interpolação nativa do eixo variável depende da versão/plugin. Se não for fiável:

1. criar quatro layers com pesos reais;
2. alinhar por baseline e centro óptico;
3. fazer cortes/crossfades de 1–2 frames;
4. compensar diferenças de largura com Scale X subtil.

Para Mário, manter Montserrat e pesos aprovados; não substituir por outra variable font.

### SOL-05 · Glyph spray controlado

Per-character agressivo, mas legível:

```text
f00  caracteres espalhados: X random ±70, Y random ±55, Rotate ±16°, Opacity 0
f08  110% da posição final, Opacity 100
f13  posição final, Rotate 0°
```

- seed fixo por layer;
- ordem de chegada baseada em **centro para fora**;
- blur 8 → 0;
- usar em 4–9 caracteres, nunca numa morada longa;
- não aplicar random diferente a cada preview/render.

### SOL-06 · Underline guilhotina

O underline não decora: corta e provoca a troca.

```text
f00–05  linha accent cresce X 0 → 115%
f06     linha atravessa a palavra
f07     texto por cima muda BASE → HERO
f08–11  linha encolhe 115% → 42%
f12     settle
```

SFX: whip fino a terminar no f06 + click no f07.

### SOL-07 · Data tile burst

Para `188 m²`, `4 quartos`, `2 lugares`.

```text
f00–04  tile Scale 0 → 108%, Rotate -3° → 1°
f05–09  tile 108 → 100%, Rotate 1° → 0°
f03     número entra Y +36 → 0 em 6f
f06     unidade entra X +24 → 0 em 5f
f09     label entra por máscara em 6f
```

Três tiles:

- atrasar cada tile 4 frames;
- alternar HERO/DADO/BASE;
- manter números alinhados pela baseline;
- hold mínimo de 40 frames.

### SOL-08 · Camera-parallax caption

Legenda integra-se no movimento do plano sem tracking 3D completo.

1. mede o deslocamento dominante do plano;
2. anima o texto em sentido contrário, apenas 4–8% desse deslocamento;
3. adiciona scale `102 → 100%` durante o hold;
4. mantém a caixa em espaço 2D;
5. sai antes do ramp.

Exemplo: câmara desliza 120 px para a direita; texto deriva 6–10 px para a esquerda. O resultado parece preso ao espaço, sem competir com a arquitectura.

### SOL-09 · Hard-cut typography

Sem easing. Energia editorial por cortes.

```text
f00–02  palavra A, 130%, HERO
f03–05  palavra A, 100%, BASE
f06–08  palavra B, 130%, DADO
f09–17  frase final composta, 100%
```

Adicionar 1 frame de bloco de cor entre palavras. Funciona melhor com música seca e montagem de 6–12 s.

### SOL-10 · Echo stack

```text
f00  layer principal entra
f02  eco 1 fica 14 px atrás, HERO, opacity 75%
f04  eco 2 fica 28 px atrás, DADO, opacity 45%
f08  ecos convergem para principal
f12  só principal permanece
```

Não usar blending aditivo sobre paredes brancas. Preferir ecos sólidos com matte/stroke.

---

## 6. After Effects — setups de produção

### 6.1 Per-character Animator robusto

Numa Text Layer:

1. `Animate > Position`, definir `Y = 70`;
2. adicionar `Scale = 0%`, `Rotation = 8°`, `Opacity = 0%`;
3. Range Selector:
   - Based On: `Characters Excluding Spaces`;
   - Units: `Percentage`;
   - Shape: `Ramp Up`;
   - Ease High: `70%`;
   - Ease Low: `15%`;
4. animar `Offset -100% → 100%` em 12 frames;
5. duplicar Animator só para Fill Color com 2 frames de atraso.

Para um overshoot real, usar dois Animators:

- Animator A leva caracteres de `0 → 112%`;
- Animator B corrige de `112 → 100%`, atrasado 3 frames.

### 6.2 Expressão de stagger por layer

Aplicar em `Time Remap` ou usar como referência para deslocar a animação:

```javascript
// Controlos numa layer "CTRL":
// "Stagger Frames" e "Group Size"
st = thisComp.layer("CTRL").effect("Stagger Frames")("Slider");
group = Math.max(1, Math.round(thisComp.layer("CTRL").effect("Group Size")("Slider")));
delay = Math.floor((index - 1) / group) * framesToTime(st);
valueAtTime(time - delay);
```

Recomendado:

- `Stagger Frames = 2`;
- `Group Size = 1` para cascata;
- `Group Size = 2` para pares;
- separar controlos por família de layers para evitar que fundos e logos herdem o stagger.

### 6.3 Expressão de impacto amortecido

Aplicar a Scale após um keyframe de entrada:

```javascript
amp = 10;      // percentagem
freq = 4.2;    // oscilações por segundo
decay = 8.0;   // amortecimento
n = 0;
if (numKeys > 0) {
  n = nearestKey(time).index;
  if (key(n).time > time) n--;
}
if (n > 0) {
  t = time - key(n).time;
  v = velocityAtTime(key(n).time - thisComp.frameDuration / 10);
  value + (v / 100) * amp * Math.sin(freq * t * 2 * Math.PI) / Math.exp(decay * t);
} else {
  value;
}
```

Usar com prudência:

- `decay 8–12` para 1 settle curto;
- evitar em logos;
- desligar em renders com muitos elementos se gerar jitter subpixel;
- converter para keyframes antes do handoff a terceiros.

### 6.4 Smear sem plugin

```text
Text layer
  → pre-comp
  → Transform effect (skew/scale independente)
  → Directional Blur 20–45
  → máscara para limitar o smear ao ataque
```

Animar o blur `35 → 0` entre f02 e f09. Activar `Repeat Edge Pixels`. O smear deve desaparecer antes do settle.

### 6.5 Control layer obrigatório

Criar `CTRL_CAPTIONS` com:

- `ENERGY` 0–100;
- `STAGGER_FRAMES`;
- `OVERSHOOT`;
- `ACCENT_1`, `ACCENT_2`, `BASE`, `INK`;
- `SAFE_VERTICAL` e `SAFE_HORIZONTAL`;
- checkbox `FLASH_1F`;
- dropdown `BRAND_SAFE / SOCIAL / MAX`.

Ligar expressões aos controlos. Assim a mesma receita produz variantes sem reconstrução.

---

## 7. DaVinci Resolve / Fusion — equivalente prático

### 7.1 Macro-base

Node tree:

```text
Text+ → Transform_Text → DirectionalBlur → Merge_Text
Background_Color → Rectangle_Mask → Transform_Block → Merge_Text
MediaIn → Merge_Text → MediaOut
```

Configuração:

- `Transform_Text` para pop/whip;
- `DirectionalBlur` animado só no ataque;
- `Transform_Block` com pivot lateral para wipes;
- `Merge_Text > Blend` para opacity;
- activar Motion Blur no Transform quando o movimento excede ~80 px em menos de 8 frames.

### 7.2 Follower por carácter

No Text+:

1. activar `Follower`;
2. em Modifiers, animar `Delay` por carácter;
3. Shading: variar Fill/Outline;
4. Transform: Position Y, Size e Rotation;
5. usar delay de `2 frames` por carácter para palavra curta;
6. para frase, mudar para delay por palavra ou separar layers.

### 7.3 Beat grid no Resolve

- criar markers de timeline nos transientes;
- usar nomes `K01`, `S01`, `LOCK`, `OUT`;
- colocar o keyframe de overshoot no marker, não o primeiro keyframe;
- compor uma Fusion Clip por beat, não uma Fusion Clip gigante para o reel inteiro;
- guardar Macro com controlos publicados para cor, amplitude, stagger e duração.

### 7.4 Quando fazer round-trip

Usar AE → ProRes 4444/PNG alpha quando houver:

- per-character complexo;
- weight morph;
- smear multicamada;
- mais de 3 estados de cor;
- expressions/presets já aprovados.

Manter em Fusion quando houver:

- lower thirds;
- pop/slide simples;
- 2–3 tiles de dados;
- wipes e máscaras;
- necessidade de alterar copy até ao fim.

---

## 8. SFX: desenhar o impacto em três camadas

### Camada 1 — Ar

Whoosh curto, sem graves excessivos.

- começa 2–4 frames antes;
- termina no overshoot;
- pan subtil acompanha a direcção da entrada;
- cortar abaixo de 120–180 Hz se competir com o kick.

### Camada 2 — Corpo

Impacto curto no hit:

- thump leve para preço/área;
- clap seco para troca de frase;
- knock de madeira/metal suave conforme o mood do imóvel;
- duração útil abaixo de 180 ms na maioria dos beats.

### Camada 3 — Detalhe

Click, tick, blip ou snap no lock:

- ideal para dígitos, underline e mudança de cor;
- 0–1 frame de tolerância;
- variar pitch ±2 semitons entre eventos repetidos;
- não usar o mesmo click em mais de 3 ocorrências consecutivas.

### Ducking local

Em vez de baixar a música durante toda a legenda:

- duck de `1–2 dB`;
- ataque 1–2 frames antes do impacto;
- release 4–8 frames;
- só nos hits principais.

Verificar loudness e export final em [`MASTERING.md`](MASTERING.md).

---

## 9. Safe zones medíveis

### 9:16 — 1080×1920

Zona conservadora para Reels/TikTok:

```text
esquerda:  x ≥ 72
direita:   x ≤ 900
topo:      y ≥ 170
fundo:     y ≤ 1580
```

- CTA e texto essencial acima de `y=1480`;
- evitar a coluna direita de aproximadamente 140 px;
- não pôr números importantes atrás de captions automáticas;
- testar no telemóvel com UI real, não só no viewer.

### 16:9 — 1920×1080

```text
margem exterior mínima: 96 px
lower-third útil: y ≈ 700–900
título central: y ≈ 360–650
```

- respeitar overscan de 5%;
- manter logos e texto legal fora do limite;
- se houver versão 9:16 derivada, criar layout próprio; não fazer crop cego da composição 16:9.

### Safe zone arquitectónica

Antes de escolher a posição, marcar:

- rosto/agente;
- janelas com vista;
- ilha de cozinha;
- lareira;
- piscina;
- linha do horizonte;
- placa/localização locked;
- logótipos.

A legenda deve ocupar a zona de menor valor comercial do plano. Se não existir, usar título curto em ecrã cheio entre planos.

---

## 10. Sequências de hook prontas

### Hook 01 · “Não parece real” — 4 s / 96 frames

```text
f00–11  “NÃO” — SOL-01, HERO vermelho
f12–25  “PARECE” — SOL-03, BASE + color chase
f26–43  “REAL” — hard cut 130% → 100%, DADO amarelo
f44–59  plano respira; eco converge
f60–83  “ATÉ ABRIR A PORTA” — split-axis, 2 linhas
f84–95  saída guilhotina para o primeiro interior
```

SFX: suck-back em f00, slam em f26, maçaneta/click em f83.

### Hook 02 · Preço revelado — 3 s / 72 frames

```text
f00–11  “QUANTO VALE” per-character de centro para fora
f12–23  “ESTA VISTA?” underline guilhotina
f24–35  silêncio visual / plano aberto
f36–47  preço em scramble
f48      lock correcto + hit
f49–63  hold
f64–71  tile colapsa para o canto
```

Se o preço não puder ser divulgado, trocar por `188 m² DE LUZ E VISTA`; não fabricar suspense vazio.

### Hook 03 · Três provas — 5 s / 120 frames

```text
f00–27   tile 1 “188 m²”
f28–55   tile 2 “4 QUARTOS”
f56–83   tile 3 “VISTA ABERTA”
f84–103  três tiles formam uma stack
f104–119 stack sai em direcções diferentes
```

Cada tile usa uma cor funcional fixa. O terceiro recebe o maior impacto.

### Hook 04 · Localização com vida própria — 4 s

```text
f00–09   tipologia entra por compressor slam
f10–19   zona entra por split-axis
f20–31   localização completa assenta e fica legível
f32–47   hero-word muda de cor
f48–71   hold limpo
f72–83   elementos cinéticos saem
f84–95   placa/localização locked permanece em fade, se aplicável
```

Para Mário Garcês, usar sempre a forma completa locked:

```text
T4 Lumiar – QUINTA dos ALCOUTINS
```

### Hook 05 · 16:9 editorial — 6 s / 144 frames

```text
f00–23   plano sem texto
f24–39   linha fina atravessa o frame
f40–55   título entra hard-cut, sem bounce
f56–71   palavra hero faz Weight Punch
f72–119  hold amplo sobre o movimento da câmara
f120–135 texto divide-se por eixo
f136–143 corte para a divisão
```

É agressivo por ritmo e escala, não por encher o ecrã.

---

## 11. Presets: workflow para velocidade sem “template look”

### 11.1 Biblioteca mínima

Criar presets com nomes funcionais:

```text
SOL_IN_Compressor_08f
SOL_IN_PistonWords_12f
SOL_IN_GlyphSpray_13f
SOL_ACCENT_Guillotine_12f
SOL_DATA_TileBurst_16f
SOL_OUT_SplitAxis_08f
SOL_SFX_WhooshShort_Pre03f
SOL_SFX_ClickLock_00f
```

O nome inclui duração para evitar abrir presets à tentativa.

### 11.2 Preset não deve guardar

- copy;
- font;
- cores finais;
- posição absoluta;
- duração do hold;
- localização de cliente;
- escala dependente apenas de 1080p.

Deve guardar:

- relação temporal;
- curvas;
- overshoot parametrizado;
- blur/smear;
- ordem de eventos;
- markers esperados.

### 11.3 Processo de aplicação

```text
1. aplicar brand kit
2. colar copy final
3. escolher modo A/B/C
4. aplicar preset de IN
5. ajustar hold à leitura
6. aplicar preset de OUT
7. ligar cores aos controlos
8. sincronizar overshoot ao marker
9. rever com áudio
10. rever sem áudio
```

Se a animação só funciona com o SFX ligado, o movimento ainda não está suficientemente claro.

---

## 12. Anti-padrões específicos de alta energia

1. **Rainbow por carácter** sem semântica de cor.
2. Cinco efeitos simultâneos: scale + rotate + blur + glow + glitch.
3. Per-character numa morada completa.
4. Shake contínuo durante o hold.
5. Easing elástico com 3–4 oscilações.
6. Flashes com mais de 2 frames ou vários flashes por segundo.
7. Texto a entrar no ramp e a assentar já depois do plano estabilizar.
8. SFX todos com graves; a mistura transforma-se numa sequência de explosões.
9. Random sem seed, produzindo renders diferentes.
10. Motion blur sobre texto pequeno durante o hold.
11. Usar a mesma entrada em seis divisões seguidas.
12. Aplicar Optical Flow global depois de já haver overlays — ver [`MASTERING.md`](MASTERING.md).
13. Alterar fonte, localização ou estrutura aprovada para “dar mais energia”.
14. Desenhar 16:9 e recortar para 9:16 sem recompor.
15. Dar mais destaque à legenda do que à vista, piscina ou arquitectura que vende o imóvel.

---

## 13. Matriz de variação para não repetir

Escolher uma opção por coluna; evitar repetir a mesma combinação:

```text
ENTRADA       ACENTO          SAÍDA          COR
compressor    guilhotina      split-axis     BASE→HERO
piston        color chase     collapse       HERO fixa
hard-cut      flash 1f        whip vertical  DADO fixa
glyph spray   echo stack      mask wipe      BASE→DADO
parallax      tile burst      cut seco       monocromática
```

Regra de montagem:

- beats 1–3: aumentar energia;
- beat 4: reduzir;
- beat 5: mudar família de movimento;
- CTA: recuperar um movimento do hook para fechar o sistema.

---

## 14. QA em três passagens

### Passagem 1 — Sem som

- lê-se tudo?
- percebe-se onde olhar?
- o impacto visual cai no frame certo?
- existe contraste entre ataque e hold?
- as cores têm função consistente?

### Passagem 2 — Só som

- os SFX formam ritmo ou ruído?
- os whooshes antecipam?
- impactos competem com kick/voz?
- o CTA tem assinatura própria?

### Passagem 3 — Telemóvel e TV

- 9:16 com UI real: texto fora dos botões e captions;
- 16:9 a 2–3 metros: corpo e dados continuam legíveis;
- nenhum elemento fino cintila;
- motion blur desaparece no settle;
- preto/branco não clipam depois da correção de cor;
- locks do cliente conferidos.

Checklist final:

- [ ] 24 fps real e timings não convertidos de 30 fps por aproximação;
- [ ] uma ideia por beat;
- [ ] modo A, B ou C declarado;
- [ ] fonte e localização locked intactas;
- [ ] máximo de duas cores saturadas simultâneas;
- [ ] hold permite duas leituras;
- [ ] entrada termina depois do ramp in;
- [ ] saída começa antes do ramp out;
- [ ] SFX sincronizados ao overshoot/lock;
- [ ] overlays separados dos retimes;
- [ ] versão vertical e horizontal recompostas;
- [ ] export alpha/teste de premultiplication correcto, se houver round-trip.

---

## 15. Quando usar este doc vs `LEGENDAS-CINETICAS-AGRESSIVAS.md`

Usar **este documento** quando for preciso desenhar um **sistema completo de energia**: escolher brand-safe vs max-aggression, mapear beats, trabalhar per-character, controlar cor por função, construir expressions/macros, desenhar SFX em camadas e criar uma biblioteca de presets.

Usar [`LEGENDAS-CINETICAS-AGRESSIVAS.md`](LEGENDAS-CINETICAS-AGRESSIVAS.md) quando for preciso consultar rapidamente as receitas-base já consolidadas — pop cascade, whip slam, stacked punch, scramble, mask wipe, timings gerais e pipeline AE/Resolve.

Em produção, a combinação recomendada é: **estrutura e variação deste sistema SOL + receitas-base do playbook original + locks do cliente + finishing de `MASTERING.md`.**
