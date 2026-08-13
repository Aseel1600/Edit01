# Legendas cinéticas agressivas — sistema BLANK: a legenda como instrumento (ADSR)

> Sistema autónomo de folha em branco para legendas cinéticas em vídeo imobiliário.
> Formatos: **reels 9:16 (1080×1920)** e **tours 16:9 (1920×1080)**.
> Relógio canónico: **24 fps** (1 s = 24 f). Todas as receitas e partituras deste doc estão em frames @24.
> Tipografia, cor e estrutura são escolhas livres deste doc — nada é herdado, tudo é decidido aqui.

---

## 0. Arranque em 5 minutos (a primeira legenda a sair já)

1. Comp AE (ou timeline Resolve): **1080×1920, 24 fps**, fundo = o teu clip.
2. Escreve a palavra-chave do hook (uma só, ex.: `T3`).
3. Escala: 3 keyframes — `f0 = 60%` · `f4 = 114%` · `f7 = 100%`. Easy Ease Out no `f4`.
4. Opacidade: `f0 = 0` → `f1 = 100`.
5. Placa atrás: rectângulo `#0D0D0F` a 50% (se o vídeo por baixo for claro).
6. SFX: impacto seco (soco sub) colado **no frame f4** — no *settle*, não no nascimento.
7. Exporta H.264, 1080×1920, 20–30 Mbps, AAC 320 kbps 48 kHz.

Se isto funcionou, o resto do doc é só escalar o mesmo gesto com intenção musical.

---

## 1. O modelo: ADSR — a legenda é um instrumento de percussão

Toda a legenda é tratada como uma **nota tocada num instrumento**, com um envelope de quatro fases:

| Fase | Nome tipográfico | O que acontece | Pergunta que responde |
|---|---|---|---|
| **A — Attack** | Ataque | Do invisível ao pico (com overshoot controlado) | "Com que força nasce?" |
| **D — Decay** | Assentamento | O overshoot resolve para 100% | "Onde pára?" |
| **S — Sustain** | Vida | O tempo parado a ser lido | "Quanto tempo aguenta?" |
| **R — Release** | Saída | A morte da nota: seca, fantasma ou varrida | "Como cede o lugar à próxima?" |

### As seis leis do envelope

1. **Nada é linear.** Velocidade muda sempre: ease-out no ataque, ease-in na saída. Linear = PowerPoint.
2. **Um overshoot por gesto.** O segundo overshoot é *bounce* — e bounce é amador. Se precisas de mais energia, sobe o overshoot do primeiro, não adiciones outro.
3. **S mede-se em leitura, não em gosto.** Palavra corrente: mínimo 12 f. Palavra de valor (feature): 18–24 f. Número/preço: 24–48 f. Se não é para ler, S = 0 e o R encadeia directamente na próxima nota.
4. **R é uma decisão musical, não um fade.** Três mortes válidas: **seca** (corte no frame, a próxima palavra empurra), **fantasma** (cai a 20% de opacidade e morre em 6 f), **varrida** (sai colada ao movimento da câmara).
5. **O ecrã nunca fica vazio mais de 8 f** dentro de um hook de 3 s. Vazio = o polegar escapa.
6. **Agressividade é contraste de dinâmica, não velocidade constante.** Um `ff` só grita porque houve um `p` antes. Se tudo é forte, nada é forte — é ruído.

### Glossário de dinâmicas usado no doc

| Marca | Significado musical | Tradução tipográfica |
|---|---|---|
| `ff` (fortíssimo) | golpe máximo | palavra-soco com overshoot + shake curto |
| `sfz` (sforzando) | acento súbito isolado | pop de número com flash de 1 f |
| `stac` (staccato) | notas curtas separadas | rajada de palavras no beat |
| `gliss` (glissando) | deslize entre notas | palavra desliza colada ao whip pan |
| `trem` (tremolo) | repetição rápida da mesma nota | micro-vibração contida |
| `sub p` (subito piano) | subitamente suave | corte de energia: texto pequeno e quieto |
| `mart` (martellato) | martelado | palavra cravada verticalmente |
| `pizz` (pizzicato) | beliscado | etiqueta pinpoint com ponto + linha |
| `cresc` (crescendo) | subida contínua | escada de palavras acumulativas |
| `rin` (rinforzando) | reforço fora do pulso | ênfase sincopada, contra o beat |

---

## 2. Relógio mestre @24 fps

### 2.1 Unidades canónicas

| Gesto | Frames @24 | ≈ ms | Nota de produção |
|---|---|---|---|
| Tick / acento micro | 2 f | 83 | flash, piscar de placa, 1 f de brilho |
| Ataque de palavra-soco | 3–5 f | 125–208 | sempre com overshoot (112–118%) |
| Ataque de linha | 6–8 f | 250–333 | linha inteira, sem stagger |
| Ataque de bloco | 8–12 f | 333–500 | máximo; acima disto é preguiça |
| Assentamento (overshoot → 100%) | +2–4 f | 83–167 | nunca ultrapassar 4 f |
| Hold mínimo — palavra corrente | 12 f | 500 | abaixo disto é ilegível em telemóvel |
| Hold — palavra de valor | 18–24 f | 750–1000 | features: `varanda`, `suite` |
| Hold — número / preço | 24–48 f | 1–2 s | o cérebro lê números mais devagar |
| Gap entre palavras em rajada | 4–8 f | 167–333 | nunca todas ao mesmo tempo |
| Release seco | 3–4 f | 125–167 | corte ou micro-saída |
| Release com deslocamento | 6–10 f | 250–417 | saída varrida por câmara |
| Duração total — legenda curta | 36–72 f | 1,5–3 s | janela de hook |
| Shake pós-impacto | 2–4 f | 83–167 | amplitude 4–8 px, morre a zero |

### 2.2 Grelha musical: BPM → frames

A legenda bate na **música**, não na voz (a voz manda só na MELODIA — ver §3).

`frames por batida = 1440 ÷ BPM` (a 24 fps)

| BPM | 1 batida | ½ batida | ¼ batida | Uso típico |
|---|---|---|---|---|
| 90 | 16 f | 8 f | 4 f | tour calmo, luxo lento |
| 100 | 14,4 f | 7,2 f | 3,6 f | reels suave |
| 110 | 13,1 f | 6,5 f | 3,3 f | reels médio |
| **120** | **12 f** | **6 f** | **3 f** | **default de produção — grelha limpa** |
| 126 | 11,4 f | 5,7 f | 2,9 f | house / reels energético |
| 128 | 11,25 f | 5,6 f | 2,8 f | EDM comercial |
| 140 | 10,3 f | 5,1 f | 2,6 f | hype máximo |

**Regra prática:** edita a 120 BPM sempre que a música for neutra — 12/6/3 f são inteiros, as keyframes caem no frame e o Sync fica perfeito. Se a música for 126/128, arredonda cada evento para o frame mais próximo e **nunca** deixes um evento a meio-frame.

### 2.3 Conversões de frame rate

O relógio canónico é 24 fps. Se o deliverable for outro:

| Destino | Factor | 3 f → | 4 f → | 6 f → | 8 f → | 12 f → | 24 f → |
|---|---|---|---|---|---|---|---|
| 25 fps | ×1,04 | 3 | 4 | 6 | 8 | 12,5→13 | 25 |
| 30 fps | ×1,25 | 4 | 5 | 7,5→8 | 10 | 15 | 30 |
| 60 fps | ×2,5 | 7,5→8 | 10 | 15 | 20 | 30 | 60 |

Não re-afaças o feeling: o que importa são os **ms percebidos**, não o número de frames. A tabela acima preserva os ms.

---

## 3. Orquestra: as cinco vozes tipográficas

Cada legenda pertence a **uma** voz. A voz define tamanho, cor, envelope e movimento default. Misturar duas vozes na mesma palavra é proibido.

| Voz | Função | Tamanho 9:16 (1080×1920) | Tamanho 16:9 (1920×1080) | Cor | Envelope padrão (A·D·S·R) | Movimento |
|---|---|---|---|---|---|---|
| **BUMBO** | palavra-soco do hook (1 por cena) | 140–220 px | 90–140 px | impacto | 3–4 · 3 · 18–36 · 3–4 | escala + shake 2–4 f |
| **TAROLA** | palavra de emenda / transição | 90–140 px | 60–90 px | neutra | 2–3 · 2 · 8–16 · 3 | chicote lateral |
| **PRATO** | número, preço, área | 150–260 px | 100–170 px | impacto | 2 · 3 · 24–48 · 4 | pop + flash 1 f |
| **BAIXO** | linha-âncora persistente (contexto) | 48–64 px | 36–48 px | neutra | 8 · 0 · cena toda · 6 | entra e fica quieta |
| **MELODIA** | legenda de fala, palavra a palavra | 72–96 px | 48–64 px | neutra + 1 palavra em impacto | por palavra: 2–3 · 1 · até ser substituída · 2 | stagger por batida da voz |

**Regras da orquestra:**

- **Um BUMBO por cena.** Dois bombos na mesma cena = paredes que caem as duas e nenhuma se ouve.
- **PRATO nunca partilha linha** com outra palavra. Números tocam sozinhos.
- **BAIXO não compete:** senta-se na zona viva-baixa (§9) e nunca sobe à zona dourada enquanto lá estiver um BUMBO.
- **MELODIA é a única voz sincronizada à voz.** Todas as outras sincronizam à música.
- Cortes tipográficos sugeridos (fontes abertas, escolha livre): BUMBO/TAROLA — condensada black (*Archivo Black*, *Bebas Neue*); MELODIA/BAIXO — grotesca média (*Inter Tight*, *Sora*, *Space Grotesk*); PRATO — qualquer uma das anteriores com **tabular figures (`tnum`) ligado** para os dígitos não dançarem durante o hold.

---

## 4. Cor como dinâmica

A cor não é decoração — é o volume da orquestra. Quatro paletas fechadas; escolhe **uma por vídeo** pela fotografia do imóvel.

### 4.1 Paletas

**NÉON ASFALTO** — noite urbana, luxo escuro, interiores dramáticos
| Papel | Hex | Uso |
|---|---|---|
| Fundo/placa | `#0D0D0F` | placas a 45–60% |
| Texto neutro | `#F4F1EA` | osso, nunca branco puro |
| Impacto | `#D7FF3B` | lima eléctrica — BUMBO/PRATO |
| Secundário | `#FF4D2E` | laranja-sinal — 1 acento por vídeo |

**CIMENTO QUENTE** — tijolo, madeira, luz de dia, bairros históricos
| Papel | Hex | Uso |
|---|---|---|
| Fundo/placa | `#17130E` | placas a 45–60% |
| Texto neutro | `#F2E9DC` | areia |
| Impacto | `#FF6B35` | terracota viva |
| Secundário | `#FFC53D` | âmbar — detalhe |

**COBALTO POP** — vidro, mar, arquitectura contemporânea
| Papel | Hex | Uso |
|---|---|---|
| Fundo/placa | `#0A1428` | azul-noite |
| Texto neutro | `#FFFFFF` | aqui branco funciona |
| Impacto | `#2E7DFF` | cobalto aberto |
| Secundário | `#00E5C0` | menta — detalhe |

**MÁRMORE NOIR** — prime, penthouse, silêncio caro
| Papel | Hex | Uso |
|---|---|---|
| Fundo/placa | `#101010` | preto pleno |
| Texto neutro | `#EDEAE4` | marfim |
| Impacto | `#D4AF37` | ouro velho — só sobre escuro |
| Secundário | `#C0C7CE` | prata — detalhe |

### 4.2 Regras duras

1. **Uma cor de impacto por cena.** Mudar de cor de impacto = mudar de cena. A cor secundária aparece no máximo **uma vez por vídeo**.
2. **Contraste mínimo 7:1** entre palavra-chave e o que está atrás — medido no frame congelado (qualquer verificador WCAG serve).
3. **Sobre vídeo, a legibilidade vem da placa** (`#0D0D0F` a 45–60%, ou scrim em gradiente), nunca só da sombra. Sombra dura como único recurso = amador.
4. **Números são monocromáticos.** Nunca duas cores dentro do mesmo preço/área.
5. **Ouro só sobre escuro.** `#D4AF37` sobre céu ou parede clara morre — nesse caso desce para texto neutro + placa.
6. **Inversão é gesto, não hábito.** Inverter (texto escuro sobre bloco de cor de impacto) é válido **uma vez por vídeo**, no momento de maior aposta (preço, CTA).

---

## 5. Dinâmicas: 10 receitas frame-a-frame

Cada receita é uma dinâmica musical com envelope, setup AE, setup Fusion e SFX emparelhado. IDs novos: sem herança de nenhum outro sistema.

---

### FF-SOCO — fortíssimo
**Função:** a palavra que para o polegar. Uma por hook.
**Envelope @24:** A `3–4 f` (60% → 112–118%) · D `3 f` (→ 100%) · S `18–36 f` · R `3–4 f` seco.
**AE:** escala kf `f0=60 / f4=114 / f7=100`, Easy Ease Out no f4; opacidade `f0=0 → f1=100`; shake 4 f × 6–8 px a começar **no f4**.
**Fusion:** `Size` com as mesmas 3 chaves; tangente Bézier longa à saída de f0, achatada em f7; `Perturb` (Strength 6, Speed 24) apenas f4–f8.
**SFX:** impacto seco SUB 60–90 Hz **no frame do settle (f4)**. Sem whoosh. Pré-silêncio de 6–12 f antes do golpe duplica o impacto.
**Voz/cor:** BUMBO · impacto · placa 45–60%.
**Armadilha:** dois FF seguidos = grito contínuo. Intercala com SUBP ou STAC.

### SFZ-NÚMERO — sforzando
**Função:** preço, área, qualquer dígito que vende.
**Envelope @24:** A `2 f` (70% → 112% + flash de placa 1 f) · D `3 f` · S `24–48 f` · R `4 f`.
**AE:** escala `f0=70 / f2=112 / f5=100`; placa de impacto pisca `f1–f2` (opacidade 0→60→0); `tnum` ligado.
**Fusion:** `Size` 3 chaves + flash via `Background` da placa animado; Spline com pico acima do valor final.
**SFX:** tick metálico 2–4 kHz no f2 + sub leve. Nada de riser: o número não pede licença.
**Voz/cor:** PRATO · impacto · linha sozinha, centrada.
**Armadilha:** dois números em SFZ seguidos canibalizam-se — o segundo entra em SUBP.

### STAC-RAJADA — staccato
**Função:** listas de features em rajada no beat (`3 QUARTOS` / `2 VARANDAS` / `1 OPORTUNIDADE`).
**Envelope @24:** por palavra — A `2–3 f` · D `1–2 f` · S `até à próxima (4–8 f de gap)` · R `2 f` seco ou substituída.
**AE:** uma layer por palavra, in-points escalonados 6–8 f (½ batida @120 BPM); entradas alternadas esquerda/direita ou baixo/cima com 60–100 px de curso.
**Fusion:** uma Text+ por palavra; Follower não é preciso — escalona os clipes na Edit page; cursos espelhados.
**SFX:** tick por palavra (varia o pitch ±10% para não soar a metrónomo); a última palavra da rajada ganha SFZ com impacto.
**Voz/cor:** TAROLA · neutra; a última palavra pode subir a impacto.
**Armadilha:** rajada > 4 palavras vira metralhadora — parte em duas rajadas com 12 f de respiração.

### GLISS-CÂMARA — glissando
**Função:** palavra que entra/sai **colada ao movimento do clip** (whip pan, tilt, push-in).
**Envelope @24:** A `4–6 f` (deslocamento 400–800 px na direcção da câmara) · D `2 f` · S `12–24 f` · R `6–10 f` varrido (sai na direcção do próximo corte).
**AE:** posição com curso igual ao vector do pan; motion blur ligado; R sai no mesmo vector do corte seguinte.
**Fusion:** `Center` no Layout com as mesmas chaves; motion blur no `Merge`/`Transform`.
**SFX:** whoosh de ar 6–12 kHz cobrindo A e R; pico do whoosh no settle.
**Voz/cor:** TAROLA · neutra.
**Armadilha:** gliss contra o movimento da câmara só em RIN (síncope) — fora disso, lê-se como erro.

### TREM-TENSÃO — tremolo
**Função:** urgência contida (`só esta semana`, `última unidade`) sem bounce infantil.
**Envelope @24:** entra com STAC normal; durante S, vibração de **2–3 px a 12–24 Hz**; R seco.
**AE:** posição: `wiggle(12, 2.5)` gated por slider para durar só o S; escala nunca vibra (só posição).
**Fusion:** `Perturb` Strength 2–3, Speed 12–24, animado só no S.
**SFX:** nenhum, ou sub-bass contínuo a -20 dB. Trem com whoosh é paródia.
**Voz/cor:** TAROLA ou BAIXO · secundário (o único sítio onde o secundário vive bem).
**Armadilha:** amplitude > 4 px vira vibrato cómico; o trem é sentido, não visto.

### SUBP-SEGREDO — subito piano
**Função:** o twist/revelação. Gritaste (FF) → agora sussurras.
**Envelope @24:** A `8–12 f` **sem overshoot** (ease puro, 90% → 100%) · D `0` · S `24–72 f` · R `6 f` fantasma.
**AE:** escala 90→100 com Easy Ease; opacidade 0→100 em 6 f; tamanho 40–50% do BUMBO; parado, centrado, muito ar à volta.
**Fusion:** idem; nenhum modificador de energia.
**SFX:** **corta a música 6–12 f** antes de aparecer; entra só o ambiente do clip ou um sub-bass grave. O silêncio é o efeito.
**Voz/cor:** BAIXO elevado a protagonista · neutro ou secundário.
**Armadilha:** SUBP sem um FF anterior não é piano — é só fraco. A dinâmica precisa do contraste.

### MART-COLUNA — martellato
**Função:** títulos de capítulo em tours (`COZINHA`, `SUITE`) cravados como estaca.
**Envelope @24:** A `3 f` vertical de cima (curso 300–600 px) · D `3 f` com micro-poeira/parallax do fundo · S `24–48 f` · R `4–6 f` para baixo ou seco.
**AE:** posição Y com overshoot invertido (passa 4–6% abaixo e sobe); no settle, escala da placa 100→102% em 3 f simula poeira a assentar.
**Fusion:** `Center.Y` idem; poeira = `Transform` no grupo do fundo com 2–4 px de settle.
**SFX:** impacto grave + cauda de sala (reverb curto 0,4–0,8 s) — o "cravar" precisa de peso e de ar.
**Voz/cor:** BUMBO · impacto ou neutro consoante o capítulo; em tour, alterna: capítulo par = impacto, ímpar = neutro.
**Armadilha:** martellato com ease linear é um tijolo a cair — o ease-out é obrigatório.

### PIZZ-ETIQUETA — pizzicato
**Função:** etiquetas pinpoint sobre features durante glides (`luz oeste`, `recuperador`, `deck 14 m²`).
**Envelope @24:** ponto nasce `2 f` · linha desenha-se `6–10 f` · texto A `3 f` · S `24–60 f` (segue o tracking do clip) · R fantasma `6 f`.
**AE:** círculo 8–12 px + shape path (Trim Paths 0→100%) + texto ligado ao tracking (mocha/tracker do clip).
**Fusion:** `Ellipse` + `Polyline` (Length animado) + Text+ parenteados ao `Tracker`.
**SFX:** pluck/pizz muito curto 1–2 kHz a -18 dB, quase subliminar.
**Voz/cor:** BAIXO · neutro; linha e ponto podem usar impacto a 100% mas finos (2–3 px).
**Armadilha:** mais de 3 etiquetas em simultâneo = planta de electricista; escalona 8–12 f entre elas.

### CRESC-ESCADA — crescendo
**Função:** subida emocional acumulativa (três frases que constroem até ao clímax do imóvel).
**Envelope @24:** degrau 1 pequeno/quieto → degrau 2 +20% escala, +impacto parcial → degrau 3 FF-SOCO completo. Entre degraus: 12–18 f.
**AE:** três layers em escada física no ecrã (cada degrau sobe 120–180 px e sobe de tom); escala acumulada 70% → 85% → 100%+overshoot.
**Fusion:** idem, três Text+ com `Center.Y` a subir e `Size` a crescer.
**SFX:** riser contínuo a subir durante os 3 degraus, **corta seco** no settle do degrau 3 + impacto. O riser nunca resolve sozinho — é o corte que o paga.
**Voz/cor:** TAROLA → TAROLA → BUMBO; cor: neutro → neutro → impacto.
**Armadilha:** degraus todos ao mesmo tamanho = escada sem degraus. A geometria tem de subir no ecrã **e** na escala **e** na cor.

### RIN-SÍNCOPE — rinforzando
**Função:** surpresa rítmica — o acento cai **fora** do beat esperado (½ batida antes/depois).
**Envelope @24:** qualquer das dinâmicas acima, deslocada ±3–6 f do beat; ideal com STAC ou TAROLA.
**AE/Fusion:** desloca o in-point da layer ±3–6 f em relação à grelha; mantém tudo o resto disciplinado na grelha.
**SFX:** tick deslocado com ela; a síncope morre se o SFX ficar na grelha.
**Voz/cor:** TAROLA · neutro.
**Armadilha:** uma síncope por sequência. Duas síncopes seguidas não são groove — é dessincronia.

### Tabela-resumo

| ID | Voz | A·D·S·R (f) | SFX | Não usar quando |
|---|---|---|---|---|
| FF-SOCO | BUMBO | 3–4·3·18–36·3–4 | impacto sub | já houve um FF na cena |
| SFZ-NÚMERO | PRATO | 2·3·24–48·4 | tick + sub | outro número acabou de tocar |
| STAC-RAJADA | TAROLA | 2–3·1–2·gap·2 | ticks ±pitch | lista > 4 itens |
| GLISS-CÂMARA | TAROLA | 4–6·2·12–24·6–10 | whoosh de ar | clip estático (não há vector) |
| TREM-TENSÃO | TAROLA/BAIXO | STAC·—·S vibrado·2 | sub-bass | há voz por cima |
| SUBP-SEGREDO | BAIXO↑ | 8–12·0·24–72·6 | silêncio | não houve FF antes |
| MART-COLUNA | BUMBO | 3·3·24–48·4–6 | grave + reverb | reels rápidos < 15 s |
| PIZZ-ETIQUETA | BAIXO | 2+6–10·—·24–60·6 | pluck | mais de 3 em simultâneo |
| CRESC-ESCADA | T→T→B | degraus 12–18 f | riser cortado | música sem subida |
| RIN-SÍNCOPE | TAROLA | ±3–6 f da grelha | tick deslocado | mais de 1 por sequência |

---

## 6. After Effects: o rig ADSR

### 6.1 Setup do rig

1. Comp `1080×1920 · 24 fps`. Cria um Null chamado `RIG-ADSR`.
2. Aplica **5 Slider Controls** (Effects > Expression Controls) com estes nomes e defaults:
   - `Ataque (f)` = 4
   - `Overshoot (%)` = 12
   - `Release (f)` = 4
   - `Shake (px)` = 6
   - `Beat (f)` = 12  *(= 120 BPM; ajusta pela tabela §2.2)*
3. Parenteia os sliders de todas as layers de texto a este Null — mudas a energia do vídeo inteiro num sítio só.

### 6.2 Expressões do envelope

**Escala — ataque com overshoot** (em `Scale`; easeOutBack com overshoot afinável):

```js
rig = thisComp.layer("RIG-ADSR");
A  = Math.max(1, rig.effect("Ataque (f)")("Slider")) * thisComp.frameDuration;
c1 = 1.70158 * (rig.effect("Overshoot (%)")("Slider") / 10);
t  = time - inPoint;
if (t <= 0)     { [0, 0]; }
else if (t < A) {
  p = t / A;
  s = (1 + (c1 + 1) * Math.pow(p - 1, 3) + c1 * Math.pow(p - 1, 2)) * 100;
  [s, s];
} else { [100, 100]; }
```

**Opacidade — envelope A/R completo** (em `Opacity`; S é o tempo entre in/outPoint):

```js
rig = thisComp.layer("RIG-ADSR");
A = rig.effect("Ataque (f)")("Slider") * thisComp.frameDuration;
R = rig.effect("Release (f)")("Slider") * thisComp.frameDuration;
tIn  = time - inPoint;
tOut = outPoint - time;
if (tIn < 0 || tOut < 0) { 0 }
else { Math.min(linear(tIn, 0, A, 0, 100), linear(tOut, 0, R, 0, 100)); }
```

**Shake que morre** (em `Position`; começa no settle):

```js
rig = thisComp.layer("RIG-ADSR");
A   = rig.effect("Ataque (f)")("Slider") * thisComp.frameDuration;
D   = 4 * thisComp.frameDuration;
amp = rig.effect("Shake (px)")("Slider");
t   = time - inPoint - A;
(t > 0 && t < D) ? wiggle(24, amp * (1 - t / D)) : value;
```

**MELODIA palavra-a-palavra na grelha** (Text Animator: `Opacity 0` + `Position Y +80`; Range Selector → *Based On: Words, Units: Index*; expressão em `Start`):

```js
rig   = thisComp.layer("RIG-ADSR");
beatF = rig.effect("Beat (f)")("Slider");
passo = beatF * thisComp.frameDuration;
i     = Math.floor((time - inPoint) / passo) + 1;
total = ("" + text.sourceText).split(/\s+/).length;
Math.max(0, Math.min(i, total));
```

Advanced do Range Selector: `Shape = Ramp Up`, `Ease High = 60–80%`, `Ease Low = 0%`.

**Variante por marcadores** (quando a palavra segue a voz gravada e não a grelha — marca cada palavra com `*` na layer durante o playback):

```js
total = ("" + text.sourceText).split(/\s+/).length;
n = 0;
for (k = 1; k <= marker.numKeys; k++) { if (time >= marker.key(k).time) n++; }
Math.min(n, total);
```

### 6.3 Graph Editor — as duas curvas que mandam

- **Ataque (vale tudo):** curva de velocidade com saída longa do primeiro keyframe e entrada esmagada no keyframe do pico — a palavra *acelera para a parede*. Influência 70–85% no ease-out.
- **Saída varrida:** espelho — arranca devagar e sai a fundo (ease-in 60–75%). Nunca uses "Easy Ease" simétrico: meio-tijolo, meio-pena.
- **Regra do pico único:** se a curva de velocidade tem dois picos, tens um bounce disfarçado. Apaga um.

### 6.4 Exportar como sistema (não como one-off)

- Selecciona as layers de texto de uma receita → `Composition > Essential Graphics` → exporta `.mogrt` com sliders expostos (Ataque, Overshoot, Cor de impacto).
- Assim o Premiere/Edit page reutiliza a dinâmica sem abrir o AE — e a equipa não "re-inventa" o FF-SOCO em cada vídeo.

---

## 7. DaVinci Resolve / Fusion: o mesmo envelope sem AE

### 7.1 Anatomia mínima no Fusion

`MediaIn (clip) → Merge (fundo) ← Text+ (primeiro plano) → MediaOut`

- Animação pontual (FF/SFZ/MART): keyframes directos em `Size`, `Center`, `Rotation` no Inspector da Text+.
- Overshoot à mão: abre o **Spline**, selecciona as chaves, `Smooth` e molda as tangentes **Bézier** — pico acima do valor final (112–118%) e settle 2–4 f depois. É o equivalente manual ao easeOutBack do §6.2.
- Shake/vibração (TREM): clique-direito no parâmetro → **Modify With → Perturb** (Strength 2–6, Speed 12–24); anima a Strength para ligar só durante o S.
- Rajada palavra-a-palavra (STAC/MELODIA): clique-direito em `Size` (ou `Tracking`) → **Modify With → Follower** → no separador Modifiers: `Range = Words`, `Order = Left To Right`, `Delay = 12 f` (= ½ batida @120 BPM... usa 6–8 f para rajada apertada).
- Placa de legibilidade: nó `Background` (`#0D0D0F`, alpha 0,45–0,6) mascarado por `Rectangle` atrás da Text+, parenteado à posição do texto.
- Etiquetas (PIZZ): `Ellipse` + `Polyline` com `Length` animado + Text+, tudo parenteado a um **Tracker** do clip.

**Alternativa rápida na Edit page:** os mesmos Text+ vivem no Effects Library; o Inspector da Edit expõe os mesmos parâmetros — suficiente para STAC/FF simples sem abrir o Fusion.

### 7.2 Fairlight: a partitura de impacto

- Três pistas de SFX: `SUB` (socos), `TICK` (transientes), `AR` (whooshes/risers).
- Ducking: automação de volume — SFX a −12 dB sob voz; música a −18/−22 dB sob voz.
- Master: limiter no bus, alvo **−14 LUFS integrado, true peak −1 dBTP** (social). Mede com o loudness meter do Fairlight, não a ouvido.

### 7.3 Exportação

| Destino | Container | Codec | Resolução | Bitrate | Áudio |
|---|---|---|---|---|---|
| Reels 9:16 | MP4 | H.264 | 1080×1920 | 20–30 Mbps | AAC 320 kbps, 48 kHz |
| Tour 16:9 | MP4 | H.265 | 1920×1080 | 25–35 Mbps | AAC 320 kbps, 48 kHz |

---

## 8. SFX: a orquestra invisível

### 8.1 As três camadas

| Camada | Banda | Função | Nível típico |
|---|---|---|---|
| **SUB** | 50–120 Hz | soco físico do FF/MART; corpo do impacto | −10 a −6 dB |
| **TICK** | 2–5 kHz | transientes: ticks de STAC, clique do SFZ, pluck do PIZZ | −14 a −10 dB |
| **AR** | 6–12 kHz | whooshes de GLISS, risers de CRESC, brilho do flash | −16 a −12 dB |

### 8.2 Regras de sync e dinâmica

1. **O impacto soa no settle, não no ataque.** A palavra bate quando pára de crescer (f4 no FF-SOCO). Um impacto no f0 soa a antecipado e esvazia o gesto.
2. **O riser morre 1–2 f antes do golpe.** O buraco de 1–2 frames entre riser e impacto é o que faz o golpe doer.
3. **Pré-silêncio:** 6–12 f de quase-silêncio (música cortada ou filtrada) antes de um FF duplica o impacto percebido.
4. **Um SFX por gesto.** Se a palavra entra com whoosh + impacto + tick, nenhum dos três se ouve. Escolhe a camada que serve a dinâmica.
5. **Pitch variado ±10%** nos ticks repetidos (STAC) — repetição idêntica soa a metrónomo defeituoso.
6. **Silêncio é dinâmica.** SUBP-SEGREDO não leva SFX nenhum; o corte da música **é** o efeito.

### 8.3 Fontes e organização

- Biblioteca própria + fontes livres (freesound.org e afins) + geradores de SFX por IA para preencher lacunas.
- Nomeia por dinâmica, não por objecto: `sfx_sub_ff_01.wav`, `sfx_tick_sfz_02.wav`, `sfx_ar_gliss_01.wav`. Assim a partitura monta-se pela tabela do §5 sem pensar.

---

## 9. Sala de concerto: safe zones

### 9.1 Reels 9:16 (1080×1920)

```
x:   0        100        940   1080
     |---------|----------|------|
  0  ┌───────────────────────────┐
     │ MORTO — UI da app (nome,  │
280  │ ícones)                   │
     │ VIVO-ALTO — títulos       │
500  │ pequenos, BAIXO temporário│
     │                           │
     │ ZONA DOURADA — BUMBO,     │
     │ PRATO, hooks, números     │
     │ linha de olhar ≈ y 820    │
1200 │                           │
     │ VIVO-BAIXO — BAIXO/âncora │
1450 │ MELODIA de fala           │
     │ MORTO — legenda da app,   │
1920 └───────────────────────────┘
```

- Margens: **100 px esquerda**, **140 px direita** (os ícones laterais comem a faixa direita).
- Topo morto: `y 0–280`. Base morta: `y 1450–1920` (~420 px).
- **Zona dourada `y 500–1200`:** tudo o que vende vive aqui. Linha de olhar ≈ `y 820` (43% do topo).
- MELODIA de fala senta em `y 1200–1450`, nunca mais abaixo.
- Tamanhos mínimos: MELODIA ≥ 64 px, qualquer texto ≥ 54 px. Abaixo disto, em telemóvel, é ruído.
- Máx. 4 palavras por linha; números sempre sozinhos na linha.

### 9.2 Tours 16:9 (1920×1080)

- Title-safe 5%: `x 96–1824`, `y 54–1026`. Zona viva de trabalho: `x 120–1800`, `y 80–960`.
- Capítulos (MART) no terço inferior: `y 760–900`.
- BAIXO/âncora: `y 940–990`, tamanho 36–48 px.
- Base morta `y 1000–1080` (progresso de player / CTA overlay).
- Tamanhos mínimos: corrente ≥ 44 px; nunca < 36 px.
- Máx. 22 caracteres por linha em MELODIA.

### 9.3 Regra das duas superfícies

Desenha **primeiro em 9:16** com a zona dourada, depois mapeia para 16:9 recentrando as vozes (BUMBO/PRATO ao centro, BAIXO desce para `y 940`). Nunca ao contrário: um layout nascido em 16:9 e "cortado" para vertical perde sempre a base — e é na base que vive a MELODIA.

---

## 10. Partituras prontas: 8 sequências de hook imobiliário

Todas @24 fps, grelha 120 BPM (12 f/batida). `[ZONA]`, `[PREÇO]` etc. são placeholders — substituir por projeto.

### PART-01 — "NÃO É PARA TODOS" (reels, produto escasso/premium, 3 s)

| f | Palavra | Dinâmica | Voz/cor | SFX | Imagem |
|---|---|---|---|---|---|
| 0 | NÃO | FF-SOCO | BUMBO · impacto | impacto sub | corte duro: porta a abrir |
| 6 | É PARA | STAC | TAROLA · neutro | tick +10% | — |
| 12 | TODOS. | SUBP-SEGREDO (encolhe, quieta) | BAIXO↑ · neutro | **música corta 8 f** | — |
| 26 | T3 · [ZONA] | CRESC degrau 1 | TAROLA · neutro | riser começa | 1.ª divisão |
| 44 | 128 m² | CRESC degrau 2 | TAROLA+ · neutro | riser sobe | 2.ª divisão |
| 60 | E ISTO: | CRESC degrau 3 (texto) | BUMBO · impacto | riser corta | corte para o money shot |
| 66 | (vídeo respira 12 f sem texto) | — | — | impacto + música volta | sala em hero shot |

### PART-02 — "PREÇO NO PRIMEIRO FRAME" (reels, promoção directa, 2,5 s)

| f | Palavra | Dinâmica | Voz/cor | SFX | Imagem |
|---|---|---|---|---|---|
| 0 | [PREÇO] | SFZ-NÚMERO | PRATO · impacto | tick + sub | fachada, push-in |
| 4 | (flash da placa) | — | — | — | — |
| 30 | era [PREÇO-ANTIGO] | SUBP (riscado, 60%) | BAIXO · neutro | — | — |
| 48 | SÓ ESTA SEMANA | TREM-TENSÃO | TAROLA · secundário | sub-bass contínuo | — |
| 60 | → MARCA VISITA | RIN-SÍNCOPE (−4 f) | BUMBO · impacto | impacto sub | corte para CTA final |

### PART-03 — "RAJADA DE FEATURES" (reels genérico, 2 s)

| f | Palavra | Dinâmica | Voz/cor | SFX | Imagem |
|---|---|---|---|---|---|
| 0 | 3 QUARTOS | STAC (entra esq.) | TAROLA · neutro | tick 0% | corte 1 |
| 8 | 2 VARANDAS | STAC (entra dir.) | TAROLA · neutro | tick +10% | corte 2 |
| 16 | LUZ OESTE | STAC (entra baixo) | TAROLA · neutro | tick −10% | corte 3 |
| 24 | 1 OPORTUNIDADE. | SFZ (a rajada paga aqui) | BUMBO · impacto | impacto sub | money shot |

### PART-04 — "ESCADA" (reels ou tour, emocional, 4 s)

| f | Palavra | Dinâmica | Voz/cor | SFX | Imagem |
|---|---|---|---|---|---|
| 0 | NÃO É UMA CASA. | CRESC degrau 1 (70%, y baixo) | TAROLA · neutro | riser nasce | detalhe |
| 18 | É UMA DECISÃO. | CRESC degrau 2 (85%, sobe 150 px) | TAROLA · neutro | riser sobe | divisão |
| 36 | É O PRÓXIMO CAPÍTULO. | CRESC degrau 3 = FF-SOCO | BUMBO · impacto | riser corta + impacto | hero shot |
| 48 | [ZONA] · [PREÇO] | BAIXO entra e fica | BAIXO · neutro | — | — |

### PART-05 — "O SEGREDO" (retenção até ao fim, hook 2 s)

| f | Palavra | Dinâmica | Voz/cor | SFX | Imagem |
|---|---|---|---|---|---|
| 0 | TODOS PERGUNTAM | FF-SOCO | BUMBO · impacto | impacto sub | entrada |
| 10 | O PREÇO. | SUBP-SEGREDO | BAIXO↑ · neutro | música corta 10 f | — |
| 30 | está no fim do vídeo. | SUBP (mais pequeno ainda) | BAIXO · neutro | ambiente do clip | montagem continua |
| — | …no fim: [PREÇO] | SFZ-NÚMERO | PRATO · impacto | tick + sub | último shot |

### PART-06 — "CAPÍTULOS DE TOUR" (16:9, por divisão)

| f | Palavra | Dinâmica | Voz/cor | SFX | Imagem |
|---|---|---|---|---|---|
| 0 | COZINHA | MART-COLUNA | BUMBO · impacto (capítulo par) | grave + reverb 0,6 s | corte para a divisão |
| 6 | ilha · 14 m² · luz sul | PIZZ-ETIQUETA ×3 (escalonadas 10 f) | BAIXO · neutro | plucks −18 dB | glide da divisão |
| 48 | T3 · [ZONA] · 128 m² | BAIXO persistente | BAIXO · neutro | — | fica até ao próximo capítulo |

Repete por divisão, alternando capítulo impacto/neutro (par/ímpar). Próximo capítulo entra **no frame do corte**, nunca 6 f depois — o título chega com a imagem, não atrás dela.

### PART-07 — "ETIQUETAS VIVAS" (9:16 ou 16:9, durante glide da sala)

| f | Elemento | Dinâmica | Voz/cor | SFX | Imagem |
|---|---|---|---|---|---|
| 0 | ponto + linha → `luz oeste` | PIZZ-ETIQUETA | BAIXO · neutro, linha impacto 2 px | pluck | glide contínuo |
| 10 | ponto + linha → `recuperador` | PIZZ-ETIQUETA | idem | pluck +10% | — |
| 20 | ponto + linha → `deck 14 m²` | PIZZ-ETIQUETA | idem | pluck −10% | — |
| 60 | as 3 morrem em fantasma 6 f | R fantasma | — | — | corte |

### PART-08 — "CTA FINAL" (ambos os formatos, 2,5 s)

| f | Palavra | Dinâmica | Voz/cor | SFX | Imagem |
|---|---|---|---|---|---|
| 0 | GOSTASTE? | STAC | TAROLA · neutro | tick | último hero shot |
| 8 | MARCA A TUA VISITA | STAC→SFZ no verbo `MARCA` | BUMBO · impacto | impacto sub | — |
| 24 | HOJE. | RIN-SÍNCOPE (−4 f, sozinho) | BUMBO · secundário | tick deslocado | — |
| 36 | link na bio / contacto | BAIXO | BAIXO · neutro | — | freeze ou último corte |

---

## 11. Anti-padrões: execuções falhadas

| # | Falha | Sintoma | Porque mata | Correção |
|---|---|---|---|---|
| 1 | **Bounce infinito** | overshoot atrás de overshoot | lê-se como bug, não como energia | um overshoot por gesto; mais energia = mais amplitude, não mais picos |
| 2 | **Tudo em fortíssimo** | cada palavra é FF-SOCO | sem `p`, o `ff` deixa de existir; cansa em 4 s | escreve a dinâmica de cada cena (ff/f/p) antes de animar |
| 3 | **Palavra-fantasma** | hold < 12 f por palavra | ilegível em telemóvel = a legenda não existe | hold mínimo da tabela §2.1, sem excepções |
| 4 | **Arco-íris de ênfase** | 3+ cores de impacto na cena | o olho não sabe onde bater | 1 cor de impacto por cena (§4.2) |
| 5 | **Número multicolor** | preço com dois tons | o PRATO perde autoridade e lê-se mais devagar | número monocromático, sempre |
| 6 | **Sincronismo cego à voz** | BUMBO a seguir palavras faladas | a voz manda na MELODIA; as outras vozes seguem a música | separar vozes por clock (§3) |
| 7 | **Whoosh universal** | SFX de ar em todos os gestos | torna-se papel de parede sónico; nada se destaca | um SFX por gesto; pré-silêncio antes do FF |
| 8 | **Impacto no nascimento** | soco no f0 do ataque | esvazia o gesto; soa a erro de sync | impacto no frame do settle (§8.2) |
| 9 | **Sombra como placa** | drop shadow sobre vídeo claro | contraste fantasma: ilegível na rua, ao sol | placa/scrim 45–60% (§4.2) |
| 10 | **Fade mole de saída** | opacidade linear 12 f | a palavra "morre a meio" e arrasta a próxima | R seco 3–4 f, ou fantasma 6 f a 20%, ou varrido |
| 11 | **CTA suicida** | call-to-action em `y>1450` no 9:16 | fica debaixo da UI da app = não existe | CTA dentro da zona dourada ou vivo-baixo (§9.1) |
| 12 | **Letra miúda** | < 54 px no vertical | ninguém lê; só ocupa espaço | mínimos do §9; se não cabe, corta palavras |
| 13 | **Dois bombos** | BUMBO + PRATO a gritar na mesma cena | canibalismo: nenhum vende | um protagonista por cena; o outro desce a BAIXO |
| 14 | **Síncope crónica** | RIN em todas as frases | groove vira dessincronia | uma síncope por sequência |

---

## 12. Ensaio geral: QA antes de exportar

### Os quatro testes (60 segundos cada)

1. **Frame congelado:** pausa em 6 pontos aleatórios. Em cada um: lê-se tudo em < 1 s? Se não → placa, contraste ou tamanho.
2. **Sem som:** mute total. A retenção visual aguenta-se sozinha? Se o vídeo "morre" sem SFX, o envelope está fraco — o SFX deve amplificar, não carregar.
3. **Sem vídeo:** olhos fechados, só áudio. A partitura (música + SUB/TICK/AR + silêncios) conta a mesma história? Se os impactos não aterram em nada, o sync está deslocado.
4. **Polegar:** mostra os primeiros 24 f a alguém com o telemóvel na mão. Parou? Se não, o FF-SOCO do f0 não é soco nenhum — re-escreve a palavra, não a animação.

### Checklist de números

- [ ] Holds ≥ 12 f (palavra) / 24 f (número) em **todas** as legendas
- [ ] Contraste ≥ 7:1 nas palavras-chave (frame congelado + verificador)
- [ ] 1 cor de impacto por cena · 1 BUMBO por cena
- [ ] Todos os eventos na grelha (12/6/3 f @120 BPM), excepto o único RIN permitido
- [ ] Impactos SFX no frame do settle · risers cortados 1–2 f antes
- [ ] CTA e MELODIA fora das zonas mortas (§9)
- [ ] Dinâmica escrita por cena (ff/f/p) — se uma cena é toda igual, re-escrever
- [ ] Loudness: −14 LUFS integrado · true peak ≤ −1 dBTP
- [ ] Export: 1080×1920 H.264 20–30 Mbps (reels) / 1920×1080 H.265 25–35 Mbps (tour)

### O teste final

Pergunta de banca: **se congelares qualquer frame e o mostrares a um estranho durante 1 segundo, ele sabe o que estás a vender e onde clicar?** Se sim, a partitura está afinada. Se não, falta contraste — de cor, de escala, ou de dinâmica. Nunca falta "mais animação".
