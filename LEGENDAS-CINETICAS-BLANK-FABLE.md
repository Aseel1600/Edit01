# Legendas cinéticas agressivas — sistema PARTITURA (notação + física de materiais)

Playbook de produção para **reels 9:16** e **tours 16:9** de imobiliário, com um princípio organizador próprio: **a peça escreve-se antes de se animar**. Primeiro compõe-se uma *partitura de legendas* em texto puro — beats, dinâmicas, materiais, holds — e só depois se traduz para After Effects ou Resolve/Fusion. O software executa; a partitura decide.

Duas ideias estruturam tudo:

1. **Notação** — cada legenda é um evento escrito numa linha, com marcações de dinâmica emprestadas da música (`pp`, `f`, `ff`, `sfz`, staccato, legato, fermata). Discutes o vídeo com o cliente na partitura, não no render.
2. **Física de materiais** — cada legenda é feita de um *material* (AÇO, BORRACHA, VIDRO, TINTA, LUZ, PAPEL). O material determina easing, frames, sombra, som e saída. Nunca animas "um texto"; animas um objeto com massa e comportamento.

Tudo a **24 fps**. Frames escrevem-se `f00`, `f12`, etc.

---

## 1. A partitura: sintaxe

Uma peça inteira cabe num bloco de texto como este:

```text
PEÇA: reel-apartamento-rio | 9:16 | 24fps | ~34s | música 92 BPM

[B01 | f000–f052 | plano: fachada, push-in]
  "PARA DE FAZER SCROLL"        BORRACHA  ff   ↓slam    hold 30f
  SFX: sub-thud + whoosh-curto

[B02 | f052–f070 | plano: hall, pan direita]
  tacet                                                  (respiro: só imagem)

[B03 | f070–f122 | plano: sala, orbit lento]
  "94 m² DE SALA"               VIDRO     sfz  decode   hold 34f
  + "PÉ-DIREITO 3,1 m"          VIDRO     mf   decode   hold 26f  @f094
  SFX: click ×2 + blip

[B04 | f122–f170 | plano: varanda, tilt-up]
  "RIO À FRENTE. SEMPRE."       TINTA     f    wipe→    hold 36f  legato
  SFX: whoosh-grave

[B10 | f760–f816 | plano: porta, câmara parada]
  "VEM VER ANTES DE TODOS"      LUZ       ff<  bloom    hold 40f  fermata
  SFX: riser 8f + impacto
```

### Anatomia de uma linha de evento

```text
"TEXTO"    MATERIAL    DINÂMICA    ENTRADA    hold Nf    [artic.]  [@fNNN]
```

| Campo | Valores | O que fixa |
|---|---|---|
| `TEXTO` | a frase exata, com maiúsculas finais | copy fechado antes de animar |
| `MATERIAL` | AÇO, BORRACHA, VIDRO, TINTA, LUZ, PAPEL | física completa (ver §2) |
| `DINÂMICA` | `pp mp mf f ff sfz` + `<` `>` | escala, contraste, direito a cor de acento |
| `ENTRADA` | `↓slam ↑rise ←whip →whip wipe→ decode bloom fold pop` | vetor e tipo de ataque |
| `hold Nf` | frames de leitura plena | legibilidade (ver regra 2× em §4) |
| articulação | `staccato`, `legato`, `fermata` | qualidade do settle e da saída |
| `@fNNN` | frame absoluto de entrada | eventos secundários dentro do beat |

Linhas com `+` são eventos secundários do mesmo beat (entram desfasados). `tacet` marca um beat deliberadamente sem texto — escreve-se, não se deixa ao acaso: o silêncio visual é parte da composição.

### Porque é que isto funciona

- O copy fecha **antes** de haver keyframes — a revisão mais barata é na partitura.
- Dois editores diferentes produzem o mesmo vídeo a partir da mesma partitura.
- A densidade lê-se de relance: se vês seis beats seguidos sem `tacet`, a peça não respira — corriges no papel.
- A partitura versiona-se em git como qualquer ficheiro de texto.

---

## 2. Física de materiais

Cada material é um contrato completo: ataque, settle, sombra, saída e SFX de família. **Um material por evento; máximo 3 materiais por peça.** Misturar mais do que isso lê-se como ruído.

### AÇO — o peso da verdade

Para claims duros e preço. Entra pesado, para morto, não vibra.

```text
f00–f01  antecipação: scale 100 → 97
f02–f05  queda/entrada a velocidade quase linear
f06      IMPACTO: overshoot só 103%
f07–f08  settle seco (2 frames, sem oscilação)
```

- Easing: ataque íngreme, aterragem quase sem curva. No AE: influência de saída ~10%, de chegada ~85%.
- Sombra dura deslocada `(0, 10px)` a 55% que **aparece só no frame do impacto** — vende a massa.
- Saída: corte seco ou queda para fora do frame em 4f. AÇO nunca faz fade.
- SFX: sub-thud 60–90 Hz + transiente metálico curto.

### BORRACHA — energia de hook

Para ganchos e frases emocionais. Elástico, exagerado, vivo.

```text
f00–f02  antecipação: scale 100 → 92 (contrai)
f03–f07  disparo até 116–120%
f08–f11  ressalto: 96% → 104% → 100%
f12      estável
```

- Easing: overshoot duplo. É o único material com direito a **duas oscilações**.
- Rotação residual de ±2° no ressalto dá vida sem custo de legibilidade.
- Saída: squash rápido (scale Y 100→80→0 em 5f) ou whip para fora.
- SFX: whoosh curto no disparo + "pop" no primeiro ressalto.
- **Limite: 2 eventos BORRACHA seguidos, nunca 3.** Ao terceiro, o exagero vira palhaçada.

### VIDRO — precisão de dados

Para números e specs: áreas, tipologia, ano, andar. Cristalino, mecânico, sem elasticidade.

```text
f00–f06  decode: caracteres aleatórios → texto final (2 iterações por carácter)
f06      LOCK: valor final + flash de 1 frame no carácter mais à direita
f07–f08  RGB split de 1 px que colapsa
```

- Alternativa ao decode: odómetro (número rola até ao valor em 8–10f, desacelerando).
- Opacidade sempre a saltos (0 → 100 num frame), nunca em rampa — vidro não esbate, parte.
- Números **em tabular figures** (fonte com algarismos monoespaçados) para o odómetro não tremer.
- Saída: desintegração em 3f ou corte.
- SFX: clicks de teclado filtrados + blip agudo no LOCK.

### TINTA — lugares e nomes

Para bairro, rua, nome do empreendimento. Entra como tinta a espalhar-se: wipe, fill, mask reveal.

```text
f00–f10  wipe esquerda→direita (mask retangular com feather 0)
f10–f14  underline desenha-se por baixo (DrawSVG/trim paths)
```

- O settle da TINTA é **mais longo que o de qualquer outro material** — um lugar merece assentar.
- Saída: o wipe inverte (direita→esquerda) ou o texto fica até ao corte de plano.
- SFX: whoosh grave e largo, sem transiente agressivo.

### LUZ — CTA e clímax

Para a chamada final e para 1 (um) momento de pico a meio. Nasce de um bloom.

```text
f00–f06  glow cresce de 0 a 300% com o texto a 0% opacity
f04–f10  texto sobe para 100% enquanto o glow recolhe para 40%
f10–...  pulso subtil de glow a cada beat da música (±15%)
```

- LUZ é o único material com **pulso contínuo durante o hold** — mantém o CTA vivo sem o mover.
- Saída: sobre-exposição de 2f que engole o texto (flash a branco/cor de acento) → corte.
- SFX: riser de 6–8f a terminar exatamente no f do texto a 100%.
- **Uma peça só tem direito a 2 eventos LUZ**: o clímax e o CTA. Mais do que isso e o CTA perde o estatuto.

### PAPEL — listas e tiles

Para grelhas de características (3 tiles: área / quartos / garagem), etiquetas, selos.

```text
f00–f05  fold: rotação X de -90° → 0° com âncora no topo (perspetiva ligeira)
f05–f07  micro-ressalto de 2°
stagger  3f entre tiles
```

- Tiles entram sempre em cascata, nunca em bloco.
- Saída: fold inverso ou slide lateral em grupo.
- SFX: "tap" de cartão por tile (variar pitch ±5% entre tiles para não soar a metralhadora).

### Tabela-resumo

| Material | Ataque | Overshoot | Settle | Saída | Usa para |
|---|---|---|---|---|---|
| AÇO | 4–6f | 103% | 2f seco | corte/queda 4f | claim, preço |
| BORRACHA | 5–7f | 116–120% | 4–6f duplo | squash 5f | hook, emoção |
| VIDRO | 6–8f decode | 0% | lock 1f | desintegra 3f | números, specs |
| TINTA | 8–12f wipe | — | longo | wipe inverso | lugar, nome |
| LUZ | 6–10f bloom | — | pulso contínuo | flash 2f | CTA, clímax |
| PAPEL | 5–7f fold | 2° rot. | 2f | fold inverso | tiles, listas |

---

## 3. Dinâmicas: quanto grita cada evento

A dinâmica é ortogonal ao material — o mesmo AÇO pode entrar `mf` numa spec ou `ff` no preço. A dinâmica fixa **escala relativa, direito a cor de acento e violência do SFX**.

| Marca | Nome | Escala do texto* | Cor de acento | Flash | SFX |
|---|---|---|---|---|---|
| `pp` | pianissimo | 0.55× | não | não | nenhum |
| `mp` | mezzo-piano | 0.70× | não | não | opcional, -12 dB |
| `mf` | mezzo-forte | 0.85× | não | não | sim, discreto |
| `f` | forte | 1.00× | 1 palavra | não | sim |
| `ff` | fortissimo | 1.15–1.30× | frase inteira ou hero-word | 1 frame | em camadas |
| `sfz` | sforzando | 1.00× | 1 palavra, **só durante 1–2f** | sim, 1f | transiente seco |

\* relativa ao corpo-base da peça (define o corpo-base como o tamanho confortável de leitura no formato; tudo o resto deriva daí).

- `<` (crescendo): o evento entra abaixo da sua dinâmica e sobe durante o hold — ex.: `ff<` = entra `f`, chega a `ff` no fim. Útil no CTA.
- `>` (diminuendo): entra na dinâmica cheia e recolhe — ex.: hook `ff>` que dá lugar limpo ao beat seguinte.
- **Orçamento de fortissimo: máx. 3 `ff` por peça de 30–40s.** Se tudo grita, nada grita. `sfz` é o truque barato para acentuar sem gastar um `ff`: um pico de 1 frame lê-se como agressão mas não ocupa espaço.

### Articulações

| Marca | Efeito |
|---|---|
| `staccato` | settle cortado: o texto para no alvo sem nenhuma oscilação, mesmo em BORRACHA |
| `legato` | settle alongado +50%, saída em movimento contínuo para o beat seguinte |
| `fermata` | hold estendido até ao corte de plano; ignora o `hold Nf` nominal |
| `tacet` | beat sem texto (escrito de propósito) |

---

## 4. Tempo e leitura @24 fps

### Grelha de durações

| Evento | Frames | Segundos |
|---|---|---|
| Antecipação | 1–3 | 0,04–0,13 |
| Ataque (qualquer material) | 4–12 | 0,17–0,50 |
| Settle | 2–6 | 0,08–0,25 |
| Hold mínimo (1–2 palavras) | 22 | 0,92 |
| Hold frase curta (3–5 palavras) | 30–40 | 1,25–1,67 |
| Hold specs/tiles | 40–60 | 1,67–2,50 |
| Saída | 3–8 | 0,13–0,33 |
| `tacet` (respiro) | 36–72 | 1,5–3,0 |
| Desfasamento evento `+` | 8–16 | 0,33–0,67 |
| Stagger entre tiles PAPEL | 3 | 0,13 |

### Regra 2× de leitura

`hold ≥ frames necessários para ler a frase duas vezes em voz alta`. Aproximação prática: **7 frames por palavra, mínimo 22f**. Se a conta não fecha dentro do beat, o problema é o copy — corta palavras, nunca encurtes o hold abaixo do mínimo.

### Sincronização com música

Marca os transientes da música (kicks, snares, drops) na timeline **antes** de escrever a partitura. Depois:

- O frame de **impacto** (não o de entrada!) de cada evento `f`/`ff` cai num transiente. Entrada = impacto − duração do ataque.
- A 92 BPM, um beat musical = ~15,7f. Compassos de 4 tempos ≈ 63f — usa isto como módulo dos teus beats de legenda.
- Eventos `pp`/`mp` podem viver fora da grelha musical; são mobiliário, não percussão.
- Nunca "quase" no beat: um impacto 2f fora do transiente lê-se pior do que um impacto deliberadamente a meio do compasso.

---

## 5. Cor: três sistemas prontos

Escolhe **um sistema por peça**. Cada sistema define quatro papéis fixos: BASE (90% do texto), ACENTO (só com dinâmica `f`+), FUNDO-CHIP (caixas/tiles) e GUIA (underlines, barras, tracejados).

### Sistema TERRACOTA — quente, mediterrânico, moradias e reabilitado

```text
BASE        #FAF6F0   (osso)
ACENTO      #E8590C   (terracota queimada)
FUNDO-CHIP  #1A1512   (castanho quase preto, 82% opacidade)
GUIA        #D9B99B   (areia)
```

### Sistema GLACIAR — frio, novo, apartamentos de linha moderna

```text
BASE        #F2F5F7   (branco azulado)
ACENTO      #38E1C6   (menta elétrica)
FUNDO-CHIP  #0B1220   (azul-noite, 84% opacidade)
GUIA        #5C6B7A   (aço claro)
```

### Sistema NOITE-NEON — máxima agressão social, lançamentos e open house

```text
BASE        #FFFFFF
ACENTO-1    #FF3D71   (rosa ácido)   → hooks e claims
ACENTO-2    #C4FF4D   (lima)         → números e preço, 1× por ecrã
FUNDO-CHIP  #09090B   (preto, 88% opacidade)
GUIA        #7A7AF5   (violeta)
```

Regras transversais:

- O ACENTO obedece à dinâmica: um evento `mp` **não tem direito** a cor de acento, por muito que apeteça.
- No sistema NOITE-NEON, ACENTO-2 (lima) aparece no máximo **uma vez por ecrã** — é a nota mais aguda da paleta.
- Sobre imagem clara (cozinhas brancas, exteriores de dia): usa sempre FUNDO-CHIP atrás do texto, ou escurece o plano -0,4 EV localmente. Texto claro sobre imagem clara é o erro nº 1 em vídeo imobiliário.
- Contraste mínimo texto/fundo efetivo: 4,5:1. Mede no frame mais difícil do hold, não no primeiro.

---

## 6. Formatos e safe zones

### 9:16 (1080×1920) — reels

```text
┌─────────────────────┐ y=0
│  EVITAR  (220 px)   │  ← username, áudio, "seguir"
├─────────────────────┤ y=220
│                     │
│   ZONA DE JOGO      │  ← eventos ff/f vivem aqui,
│   (centro ótico:    │     centro ótico a y≈820
│    y 700–940)       │
│                     │
├─────────────────────┤ y=1520
│  EVITAR  (400 px)   │  ← caption da app, CTA da UI
└─────────────────────┘ y=1920
     ←120px→  margem lateral direita extra
     (ícones de like/comentário ocupam x>960)
```

- Eventos principais: entre `y=220` e `y=1520`, com o peso visual a `y≈820`.
- Coluna direita `x>960`: nunca pousar texto com hold — os ícones da UI tapam.
- Largura máxima de linha: 880 px (deixa ar dos dois lados).

### 16:9 (1920×1080) — tour master

- Title-safe clássico: 5% de margem → zona útil `x 96–1824`, `y 54–1026`.
- Terço inferior para specs/lugar: baseline da última linha a `y≈930`.
- Hooks e claims `ff` podem ocupar o centro, mas **nunca durante um movimento de câmara rápido** — no 16:9 o olho segue a arquitetura; o texto agressivo entra nos momentos de câmara estável ou no fim dos ramps.
- Na mesma produção, faz a partitura 9:16 primeiro e **reescreve** (não recortes) a versão 16:9: menos eventos, dinâmicas um nível abaixo (`ff`→`f`), holds +30%.

---

## 7. Implementação — After Effects

### Setup por material (uma vez, reutilizas sempre)

1. Comp `PARTITURA_1080x1920_24` com uma layer de texto por evento, nomeada `B03_VIDRO_94m2`.
2. Guarda **Animation Presets** por material: `mat_aco.ffx`, `mat_borracha.ffx`, `mat_vidro.ffx`, etc. Cada preset traz os keyframes-tipo do §2 relativos ao in-point da layer — aplicar preset + arrastar a layer para o frame de entrada = evento montado.
3. Dinâmica = um slider `DYN` (0,55–1,30) numa null `SCORE`; a scale de cada layer multiplica por ele via expressão:

```javascript
// Scale da layer de texto
base = [100,100];
dyn = thisComp.layer("SCORE").effect("DYN_" + thisLayer.name.split("_")[0])("Slider");
base * dyn
```

4. Flash de 1 frame (para `ff` e `sfz`): adjustment layer de 1 frame com Exposure +1,2 — duplica e arrasta, nunca keyframes de opacity.
5. Decode do VIDRO: expressão no Source Text com `seedRandom` por índice de carácter, 2 iterações, lock no frame marcado; odómetro com `Math.round(linear(time, tIn, tLock, 0, valorFinal))` e fonte tabular.
6. Overshoot da BORRACHA: em vez de keyframes à mão, expressão de mola no scale (freq 2,5, decay 5) limitada aos primeiros 12f — consistência grátis entre eventos.

### Graph Editor por material

| Material | Influência saída (1º kf) | Influência chegada (último kf) |
|---|---|---|
| AÇO | 10% | 85% |
| BORRACHA | 25% | expressão de mola |
| TINTA | 30% | 70% |
| PAPEL | 20% | 75% |

## 8. Implementação — Resolve / Fusion

Para quem finaliza no Resolve (cor + áudio + entrega no mesmo sítio):

1. **Text+** por evento na página Fusion (ou clips Text+ na timeline do Edit para peças simples).
2. Materiais como **macros**: constrói o AÇO uma vez (Transform + spline shaped no keyframe editor: entrada quase linear, chegada plana), grava como macro `.setting` em `Macros/Partitura/`. Idem para cada material.
3. BORRACHA: modificador **Anim Curves** no Size com curva custom de overshoot duplo, ou spline com dois picos (116 → 96 → 104 → 100).
4. VIDRO decode: **Character Level Styling** + modificador **Follower** com randomize; o lock faz-se cortando o Follower no frame certo. Odómetro: Text+ com expressão `floor(...)` num Number In ligado a uma spline.
5. TINTA: Rectangle mask no Text+ com Width animado (wipe), underline com um Background + mask animada.
6. Flash de 1 frame: nó Brightness/Contrast com Gain 2,2, ligado por um Dissolve de 1 frame — ou keyframe direto de 1f no Gain.
7. SFX na página Fairlight, alinhados aos markers de impacto (importa os markers da timeline; cada evento da partitura vira um marker com o nome do beat).

Regra prática: AE quando a peça tem >12 eventos ou materiais VIDRO/LUZ pesados; Resolve/Fusion quando a peça é curta, o grade é crítico, ou o cliente quer revisões rápidas de copy (Text+ edita-se em segundos).

---

## 9. SFX: o som é metade do impacto

Três camadas possíveis por evento; a dinâmica decide quantas entram:

| Camada | Conteúdo | `mf` | `f` | `ff` |
|---|---|---|---|---|
| AR | whoosh/riser antes do impacto (4–8f antes) | — | ✓ | ✓ |
| CORPO | o impacto (thud, slam, click, pop — família do material) | ✓ | ✓ | ✓ |
| DETALHE | cauda ou textura (ring metálico, vidro, papel) | — | — | ✓ |

- O CORPO cai **no frame de impacto/lock**, nunca no frame de entrada. Erro mais comum de sincronização.
- Pitch: varia ±4% entre eventos consecutivos do mesmo material — repetição exata soa a template.
- Mistura: SFX de legendas a -14 a -10 dB abaixo da música no momento do hit; sidechain leve (ducking de 1–2 dB na música durante 6f) faz o hit soar maior sem subir o fader.
- `pp`/`mp` não têm som. O contraste entre eventos com e sem som é uma ferramenta de hierarquia, não uma poupança.

---

## 10. Sequências de gancho prontas (partituras completas, 0–3s)

### H1 — "Proibição" (reel, sistema NOITE-NEON)

```text
[B01 | f000–f026 | plano: melhor divisão da casa, câmara parada]
  "NÃO COMPRES CASA"            AÇO      ff   ↓slam    hold 18f  staccato
  SFX: sub-thud + transiente
[B02 | f026–f070 | mesmo plano, push-in começa]
  "SEM VERES ESTA"              BORRACHA ff   ←whip    hold 30f
  + underline GUIA desenha-se                          @f040
  SFX: whoosh + pop
```

Porquê funciona: negação em AÇO (peso de autoridade) → resolução em BORRACHA (energia). Contraste de materiais = contraste retórico.

### H2 — "Número impossível" (reel, sistema GLACIAR)

```text
[B01 | f000–f014 | plano: detalhe premium (torneira, mármore), macro]
  "ISTO CUSTA"                  AÇO      mf   ↑rise    hold 10f
[B02 | f014–f058 | corte para plano geral]
  "MENOS QUE A TUA RENDA"       VIDRO    ff   decode   hold 36f
  SFX: clicks + blip no lock + sub
[B03 | f058–f082]
  tacet                                                (deixa a pergunta trabalhar)
```

O `tacet` no B03 é o gancho: o espectador fica à espera do preço — que só chega ao segundo 12.

### H3 — Abertura de tour (16:9, sistema TERRACOTA)

```text
[B01 | f000–f048 | plano: drone aproxima da fachada, ramp a desacelerar]
  tacet                                                (arquitetura primeiro)
[B02 | f048–f120 | ramp termina, câmara estabiliza]
  "QUINTA DO MIRADOURO"         TINTA    f    wipe→    hold 48f  legato
  + "MORADIA T4 · 312 m²"       VIDRO    mp   decode   hold 40f  @f072
  SFX: whoosh-grave largo, clicks a -16 dB
```

No 16:9 o texto **espera pela câmara** — entra quando o movimento assenta, nunca durante o ramp.

---

## 11. Compassos prontos (receitas por situação)

| # | Situação | Partitura resumida |
|---|---|---|
| C01 | Preço final | `"€ 485 000"  VIDRO ff  odómetro 10f  hold 44f` + flash 1f no lock + lima/acento no símbolo € |
| C02 | Grelha de specs | 3 tiles PAPEL `mf`, fold com stagger 3f, hold 52f, tap ×3 com pitch variado |
| C03 | Localização | `"CAMPO DE OURIQUE"  TINTA f  wipe→ 10f  hold 40f legato` + underline GUIA |
| C04 | Benefício emocional | `"SOL A TARDE INTEIRA"  BORRACHA f  pop  hold 34f` — sem SFX de detalhe, deixa a imagem falar |
| C05 | Urgência | `"ÚLTIMA FRAÇÃO"  AÇO ff  ↓slam  hold 26f staccato` + `sfz` na palavra ÚLTIMA (acento 1f) |
| C06 | CTA final | `"MARCA A TUA VISITA"  LUZ ff<  bloom 8f  fermata` + riser a terminar no f do texto pleno |
| C07 | Antes/depois (reabilitado) | `"2019"  VIDRO mp` canto sup. esq. → corte → `"HOJE"  BORRACHA ff  pop` centro |
| C08 | Contagem de divisões no tour | por divisão: `"COZINHA"  TINTA mp  wipe→ 8f  hold 30f` sempre na mesma posição — vira ritual, o espectador antecipa |

---

## 12. Anti-padrões

1. **Material-sopa** — 5 materiais numa peça de 30s. Máximo 3; a repetição é o que cria linguagem.
2. **Tudo `ff`** — sem orçamento de dinâmica, o hook e a spec do roupeiro gritam igual. 3 `ff` por peça, ponto.
3. **Impacto no frame de entrada** — o SFX e o flash pertencem ao frame do overshoot/lock, não ao primeiro frame de movimento.
4. **Fade em AÇO/VIDRO** — materiais duros não esbatem. Fade é para nenhum destes seis materiais; a saída é sempre física (corte, queda, wipe, fold, flash).
5. **Texto a competir com a câmara** — evento `ff` durante um whip pan ou ramp acelerado: perde os dois. Texto agressivo pede câmara estável (ou entra exatamente no travão do ramp).
6. **Hold negociado para baixo** — "fica só 14 frames para caber tudo". Não: corta copy. O hold mínimo de 22f é contrato, não sugestão.
7. **Acento em tudo** — cor de acento em eventos `pp/mp` destrói a hierarquia. A cor ganha-se com dinâmica.
8. **Ecrã cheio de texto** — mais de ~30% da área útil coberta num frame de reel = a casa desapareceu do próprio anúncio.
9. **Simetria total de timing** — todos os eventos com entrada de 6f e hold de 30f soa a metrónomo. Varia ±2f dentro da família do material.
10. **Animar antes de fechar a partitura** — a revisão do cliente em cima de keyframes custa 10× a revisão em cima de texto. Partitura aprovada primeiro, sempre.

---

## 13. Fluxo de produção resumido

```text
1. Ver o footage → marcar transientes da música e cortes de plano
2. Escrever a PARTITURA (texto puro) — copy, beats, materiais, dinâmicas, tacets
3. Rever/aprovar a partitura (cliente ou auto-revisão com as regras §12)
4. Traduzir: AE (presets .ffx por material) ou Resolve (macros .setting)
5. SFX na grelha de impactos + mistura com ducking
6. QA: regra 2× de leitura em cada hold, contraste 4,5:1 no pior frame,
   safe zones §6, orçamento de ff respeitado, materiais ≤ 3
7. Export 9:16 → reescrever a partitura para 16:9 (não recortar) → export tour
```
