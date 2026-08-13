# LEGENDAS CINÉTICAS — BLANK SOL

Sistema de produção para tipografia agressiva em vídeos imobiliários verticais e horizontais.

O objectivo não é “legendar o que se ouve”. É transformar palavras em cortes, impactos, direcção do olhar, escala e urgência — sem tapar o imóvel nem destruir a leitura.

---

## 0. A consola de intensidade

Antes de animar, atribuir ao vídeo um nível de pressão. Esta decisão governa cortes, escala, densidade, SFX e frequência de entradas.

| Nível | Comportamento | Uso recomendado | Ocupação tipográfica |
|---|---|---|---|
| P1 — Pulso | Entradas secas, poucos acentos | Tour elegante, arquitectura, luxo | 8–18% do enquadramento |
| P2 — Ataque | Escala, cortes por palavra, barras e flashes | Reels de captação, lançamento, open house | 18–35% |
| P3 — Cerco | Tipografia invade planos, palavras gigantes, transições tipográficas | Hooks, preço, escassez, mudança de zona | 30–55% |
| P4 — Ruptura | Texto torna-se cenário, máscara o imóvel, quebra a composição | 1–3 momentos por vídeo, nunca contínuo | 45–80% |

**Regra de contraste:** se tudo grita, nada é agressivo. Um reel P3 deve conter pelo menos 20–30% de tempo P1 para criar diferença de pressão.

**Mapa rápido de energia:**

```text
0–2 s      P4  — interromper o scroll
2–6 s      P2  — dar contexto sem perder velocidade
6–12 s     P3  — prova / transformação / característica decisiva
12–18 s    P1  — respirar e mostrar espaço
18–24 s    P3  — valor, localização genérica, benefício ou detalhe
24–30 s    P4  — chamada à acção
```

---

## 1. Gramática temporal a 24 fps

Todos os tempos abaixo assumem **24 fps**. Um frame dura **41,67 ms**.

### Unidades úteis

| Frames | Tempo | Sensação |
|---:|---:|---|
| 1 f | 0,042 s | Flash subliminar, corte de forma, ruído |
| 2 f | 0,083 s | Impacto duro, quase sem leitura |
| 3 f | 0,125 s | Acento perceptível |
| 4 f | 0,167 s | Entrada muito rápida mas legível |
| 6 f | 0,250 s | Ataque principal |
| 8 f | 0,333 s | Entrada forte, mais controlada |
| 10 f | 0,417 s | Movimento expressivo |
| 12 f | 0,500 s | Meio segundo; leitura curta |
| 18 f | 0,750 s | Leitura de 2–4 palavras |
| 24 f | 1,000 s | Frase curta estabilizada |
| 36 f | 1,500 s | Benefício ou frase de apoio |
| 48 f | 2,000 s | Limite habitual antes de perder urgência |

### Envelope base de uma palavra-impacto

```text
f00–f02  pré-eco visual: linha, bloco, sombra ou fragmento
f03–f08  entrada principal: 6 frames
f09–f11  overshoot / assentamento: 3 frames
f12–f25  retenção legível: 14 frames
f26–f30  saída: 5 frames
```

Duração total: **31 frames / 1,29 s**.

### Envelope base de uma frase curta

```text
f00–f05  construção do primeiro grupo
f06–f11  segundo grupo ou palavra de contraste
f12–f17  palavra-chave
f18–f41  frase completa em retenção
f42–f47  saída direccional
```

Duração total: **48 frames / 2 s**.

### Limites de leitura

- Palavra única: **12–18 f** de retenção.
- Duas a quatro palavras: **18–30 f**.
- Cinco a sete palavras: **30–42 f**.
- Mais de sete palavras: dividir em duas placas, reduzir o texto ou passar para legenda funcional.
- Números grandes podem entrar em 4–6 f, mas devem permanecer **18 f ou mais**.
- Uma palavra nunca deve estar em movimento durante todo o seu tempo no ecrã. Entrar, assentar, ser lida, sair.

### Relação com voz e música

- Antecipar uma palavra em **1–2 f** quando a dicção é rápida.
- Fazer a palavra-chave aterrar **no transiente**, não começar a animação no transiente.
- Para uma entrada de 6 f, iniciar 5 f antes do kick para o overshoot coincidir com o kick.
- Em locução pausada, atrasar o acento visual 1 f pode dar sensação de peso.
- Não sincronizar todas as sílabas. Sincronizar substantivos, números, verbos fortes e mudanças de intenção.

---

## 2. Anatomia de cada mensagem

Cada bloco tipográfico deve cumprir uma função única.

### A — Interrupção

Faz parar o scroll. Pode omitir contexto temporariamente.

Exemplos:

- “ISTO NÃO É UMA SALA.”
- “ESPERA PELO TERRAÇO.”
- “3 SEGUNDOS.”
- “OLHA PARA A LUZ.”

Tratamento: 1–4 palavras dominantes, P3 ou P4, entrada em 4–8 f.

### B — Orientação

Diz ao espectador o que está a ver.

Exemplos:

- “SUÍTE PRINCIPAL”
- “COZINHA ABERTA”
- “LUZ A SUL”
- “TERRAÇO PRIVADO”

Tratamento: P1 ou P2, 18–36 f de retenção, alinhamento consistente.

### C — Prova

Converte imagem em argumento.

Exemplos:

- “32 m² DE ÁREA SOCIAL”
- “LUZ NATURAL TODO O DIA”
- “2 FRENTES”
- “ELEVADOR DIRECTO”

Tratamento: número ou benefício em escala 2–4 vezes superior ao texto de apoio.

### D — Viragem

Muda ritmo, divisão ou promessa.

Exemplos:

- “MAS HÁ MAIS.”
- “AGORA, O MELHOR.”
- “E DEPOIS…”

Tratamento: placa curta, ruptura de paleta, corte de silêncio ou whoosh reverso.

### E — Acção

Fecha com instrução inequívoca.

Exemplos:

- “GUARDA PARA VISITAR”
- “MARCA A VISITA”
- “ENVIA A QUEM PROCURA”
- “VÊ O TOUR COMPLETO”

Tratamento: P3, botão visual opcional, retenção mínima de 36 f.

---

## 3. Sistemas de cor livres

Escolher um sistema por vídeo. Não misturar paletas só porque há planos diferentes.

### Sistema Solar — máximo contraste

```text
Carvão      #111111
Branco quente #F6F1E8
Amarelo eléctrico #FFD400
Vermelho de impacto #FF3B30
```

Uso:

- Branco quente para texto funcional.
- Amarelo eléctrico para números, preço, metros quadrados e palavras de desejo.
- Vermelho apenas para ruptura, urgência ou negação.
- Carvão em placas, sombras duras e contornos.

### Sistema Cobalto — arquitectura contemporânea

```text
Azul cobalto #2457FF
Azul noite   #071426
Gelo         #EAF2FF
Lima         #C8FF32
```

Uso:

- Cobalto para planos frios, vidro, cidade e interiores modernos.
- Lima como acento curto; nunca em parágrafos.
- Azul noite como placa a 88–94% de opacidade.

### Sistema Terracota — matéria e conforto

```text
Terracota   #E95D3C
Areia       #E8D7BD
Vinho escuro #471F2B
Creme       #FFF7EA
```

Uso:

- Ideal para pedra, madeira, campo, interiores quentes.
- A agressividade vem da escala e do corte, não de cores néon.

### Sistema Ácido — reel de alta energia

```text
Preto absoluto #050505
Branco          #FFFFFF
Verde ácido     #B6FF00
Magenta         #FF2A8A
```

Uso:

- Limitar magenta a uma palavra ou detalhe por placa.
- Alternar fundos pretos e imagem; evitar pôr verde ácido sobre relva.

### Regras de contraste

- Texto pequeno: procurar contraste WCAG aproximado de **4,5:1**.
- Texto grande e pesado: mínimo prático de **3:1**, desde que não atravesse textura complexa.
- Se o plano tem muita textura, usar uma destas soluções: placa sólida, gradiente local, sombra dura, stroke exterior ou máscara de desfoque localizada.
- Não resolver leitura com cinco efeitos ao mesmo tempo.
- Verificar sempre em telemóvel a 50% de brilho.

---

## 4. Tipografia como matéria

Não existe uma família obrigatória. Escolher pelo gesto.

### Papéis tipográficos

1. **Martelo** — grotesca pesada, condensada ou ultra black. Hooks e números.
2. **Lâmina** — sans estreita, medium ou semibold. Etiquetas e orientação.
3. **Voz** — sans legível de largura normal. Legenda funcional.
4. **Contraponto** — serifada editorial ou itálica expressiva. Luxo, surpresa, detalhe emocional.
5. **Código** — mono ou semi-mono. Plantas, coordenadas internas, dados, contagens.

### Escalas de referência

Valores aproximados para composição; ajustar à métrica da fonte.

#### Reel 1080 × 1920

| Papel | Tamanho | Entrelinha | Tracking |
|---|---:|---:|---:|
| Martelo | 130–260 px | 78–92% | -40 a -5 |
| Lâmina | 64–110 px | 90–105% | -10 a +30 |
| Voz | 48–72 px | 105–120% | -5 a +15 |
| Contraponto | 90–180 px | 85–100% | -25 a +10 |
| Código | 36–56 px | 105–120% | +20 a +80 |

#### Tour 1920 × 1080

| Papel | Tamanho | Entrelinha | Tracking |
|---|---:|---:|---:|
| Martelo | 110–230 px | 78–92% | -35 a 0 |
| Lâmina | 52–96 px | 90–105% | -10 a +35 |
| Voz | 40–64 px | 105–120% | 0 a +20 |
| Contraponto | 76–160 px | 85–100% | -20 a +10 |
| Código | 30–48 px | 105–120% | +20 a +80 |

### Regras de composição

- Quebrar linhas por significado, não por largura automática.
- Manter palavras operativas juntas: “LUZ NATURAL”, “TERRAÇO PRIVADO”, “MARCA A VISITA”.
- Uma linha pode ser cortada pela margem de propósito; uma legenda funcional não.
- Usar variação de largura e peso antes de adicionar mais cores.
- Números devem ter prioridade óptica e tabular quando há contagem animada.
- Compensar visualmente letras redondas e diagonais; não confiar apenas no alinhamento matemático.

---

## 5. Zonas seguras e território do imóvel

### 9:16 — 1080 × 1920

Criar três zonas:

```text
Topo reservado a interface:       150 px
Laterais mínimas funcionais:        84 px
Fundo reservado a interface:       300 px
Área segura principal:
  x = 84–996
  y = 150–1620
```

Para publicação cruzada e interfaces variáveis, usar uma zona ainda mais conservadora:

```text
x = 108–972
y = 190–1540
```

**P4 pode sair da zona segura**, mas a palavra essencial deve continuar decifrável dentro dela.

### 16:9 — 1920 × 1080

```text
Margem lateral funcional: 120 px
Margem superior:            72 px
Margem inferior:           108 px
Área segura:
  x = 120–1800
  y = 72–972
```

Se houver controlos de player ou legendas opcionais, elevar textos baixos para **y ≤ 900 px**.

### Reserva semântica

Antes de colocar texto, identificar o “território inviolável” do plano:

- Vista principal de uma janela.
- Bancada, ilha ou detalhe material.
- Linha de horizonte.
- Porta que revela continuidade.
- Pessoa a abrir ou demonstrar algo.
- Ponto de fuga da divisão.

O texto agressivo pode invadir esse território durante **2–6 f** numa transição, mas não deve permanecer sobre ele durante a leitura.

### Regra do vazio móvel

O texto deve procurar o espaço negativo que surge ao longo do movimento de câmara. Se a câmara desliza para a direita e abre parede vazia à esquerda, a tipografia pode entrar nessa abertura — não precisa de nascer sempre no centro.

---

## 6. Doze módulos de movimento

Cada módulo tem intenção, timing e receita. Combinar no máximo três módulos numa mesma placa.

### M01 — Golpe de escala

**Intenção:** impacto imediato.

```text
f00 escala 165%, opacidade 0%
f01 escala 150%, opacidade 100%
f05 escala 94%
f08 escala 103%
f11 escala 100%
```

Curva: entrada expo-out; correcção back-out curta. Adicionar blur direccional apenas nos primeiros 3 f.

### M02 — Corte de lâmina

**Intenção:** texto afiado, urbano.

Separar palavra em 2–4 tiras horizontais. Cada tira entra de direcção alternada.

```text
f00–f03  tiras exteriores
f02–f05  tiras interiores
f06      palavra recomposta
f07–f20  leitura
```

Deslocamento: 8–16% da largura do frame. Evitar gaps superiores a 8 px no estado final.

### M03 — Compressão lateral

**Intenção:** dar densidade sem zoom.

```text
f00 scaleX 28%, tracking +180
f06 scaleX 108%, tracking -30
f09 scaleX 100%, tracking final
```

Manter scaleY a 100%. Funciona melhor com fontes pesadas.

### M04 — Palavra-câmara

**Intenção:** a palavra torna-se transição.

Escalar uma palavra até uma contraforma ou haste preencher o ecrã; cortar para o plano seguinte dentro dessa forma.

```text
f00–f08  leitura da palavra
f09–f16  escala 100% → 900%
f14      iniciar máscara do plano seguinte
f17      plano seguinte a ocupar o frame
```

Usar em mudanças de divisão ou da fachada para o interior.

### M05 — Carimbo físico

**Intenção:** prova, estatuto, exclusividade.

```text
f00 rotação -5°, escala 135%, opacidade 0
f02 opacidade 100
f04 escala 96%, rotação +1°
f07 escala 100%, rotação 0°
```

Adicionar displacement de 1–2 px e textura muito subtil. SFX de impacto seco, não cartoon.

### M06 — Esteira de palavras

**Intenção:** lista acelerada.

Palavras passam verticalmente e uma fica presa.

```text
cada palavra: 4 f de deslocamento + 2 f de intervalo
palavra final: overshoot 3 f + retenção 18–30 f
```

Exemplo: “LUZ / ESPAÇO / SILÊNCIO / VISTA”, ficando “VISTA”.

### M07 — Construção arquitectónica

**Intenção:** relacionar texto com linhas do imóvel.

Linhas finas desenham uma grelha em 5–8 f; letras surgem como se fossem compartimentos.

```text
f00–f05 linhas principais
f03–f08 letras por máscara
f09–f12 acento cromático
f13–f36 retenção
```

Ideal para plantas, fachadas e vistas ortogonais.

### M08 — Empurrão espacial

**Intenção:** a tipografia parece deslocar a imagem.

Ao entrar da esquerda, o texto desloca temporariamente o vídeo 4–8% para a direita, com sombra ou placa.

```text
f00–f06 entrada conjunta
f07–f10 overshoot
f11–f28 retenção
f29–f34 saída e reposição da imagem
```

Evitar em footage com estabilização frágil ou horizonte sensível.

### M09 — Substituição por batida

**Intenção:** comparar opções ou revelar vantagem.

Manter o mesmo alinhamento e substituir uma palavra a cada batida.

```text
f00 “PEQUENO?”
f12 “ESCURO?”
f24 “FECHADO?”
f36 “NÃO AQUI.”
```

Cada substituição: smear ou deslocamento de 3–4 f, nunca crossfade simples.

### M10 — Eco de profundidade

**Intenção:** volume e velocidade.

Criar 3–5 duplicados da palavra com atraso de 1 f, opacidade decrescente e deslocamento de 8–20 px. O último duplicado é o texto nítido.

Não usar em frases longas. Perde legibilidade rapidamente.

### M11 — Revelação por objecto

**Intenção:** integrar texto no plano.

Rotoscopar uma parede, porta, pilar, sofá ou bancada e deixar o texto passar por trás durante 4–12 f.

Obrigatório:

- Bordas de máscara suaves mas não desfocadas.
- Motion blur coerente.
- Grão do texto integrado se a composição procura realismo.
- Evitar que mais de 30% da palavra-chave fique escondida durante a retenção.

### M12 — Queda gravitacional

**Intenção:** peso e inevitabilidade.

```text
f00 y = -180 px, rotação -2°
f05 y = +22 px
f08 y = -8 px
f11 y = 0
```

Adicionar squash vertical de 94% no impacto e recuperar em 3 f.

---

## 7. Receitas prontas

### Receita R1 — Hook “PARECE PEQUENO?”

Duração: **48 f / 2 s**.

```text
f00–f03  flash de placa preta a 70%; SFX reverse tick
f04–f09  “PARECE” entra por M03
f08–f13  “PEQUENO?” cai por M12, 1,6× maior
f14       impacto sonoro + micro shake de 2 px por 2 f
f15–f27  retenção
f28–f35  texto divide-se pelo centro; revela plano amplo
f36–f47  “OLHA OUTRA VEZ.” em M01, pequeno e centrado
```

### Receita R2 — Área social em número

Duração: **60 f / 2,5 s**.

```text
f00–f05  linha de medição cresce sobre o pavimento
f06–f13  número conta até ao valor final
f14      valor aterra com SFX sub grave
f15–f20  unidade surge por máscara
f21–f47  retenção com tracking estável
f48–f59  número expande e faz wipe para o plano seguinte
```

Hierarquia:

```text
[ 32 ]       Martelo, 220–300 px vertical / 180–240 px horizontal
[ m² ]       Lâmina, 70–100 px
[ ÁREA SOCIAL ] Código ou Lâmina, 38–60 px
```

### Receita R3 — Sequência de divisões

Uma placa de **24 f / 1 s** por divisão.

```text
f00–f04  nome entra no sentido do movimento de câmara
f05–f07  acento assenta
f08–f18  retenção
f19–f23  saída no sentido do corte seguinte
```

Alternar alinhamento esquerdo/direito conforme o vazio do plano, mantendo a mesma altura óptica.

### Receita R4 — Contraste “NÃO É X. É Y.”

Duração: **72 f / 3 s**.

```text
f00–f08   “NÃO É SÓ UMA CASA.”
f09–f25   retenção; “SÓ” recebe cor de ruptura
f26–f31   a frase é riscada por uma barra
f32–f38   silêncio parcial + plano abre
f39–f47   “É ESPAÇO PARA FICAR.”
f48–f65   retenção
f66–f71   saída por M04
```

### Receita R5 — Call to action sem cartão morto

Duração: **72–96 f / 3–4 s**.

```text
f00–f08   footage desacelera ligeiramente; ambiente continua
f09–f16   verbo principal entra: “MARCA”
f13–f20   complemento encaixa: “A VISITA”
f21–f29   sublinha animado / seta direccional
f30–f59   retenção, com micro pulso aos f42 e f54
f60–f71   saída ou fade para preto
```

Micro pulso: 100% → 103% → 100% em 6 f. Não repetir indefinidamente.

### Receita R6 — Tour 16:9 sofisticado mas agressivo

Para um segmento de **8 s / 192 f**:

```text
f000–f023  plano limpo, estabelecer arquitectura
f024–f031  título entra por M07
f032–f071  título retido no vazio do plano
f072–f083  palavra-chave cresce 115% e muda de cor
f084–f119  texto sai; mostrar espaço sem sobreposição
f120–f131  dado curto entra por M05
f132–f167  retenção
f168–f191  transição M04 para a divisão seguinte
```

Resultado: agressividade pontual sem transformar o tour num reel contínuo.

---

## 8. Hooks montados, prontos a adaptar

### Hook H1 — A objecção

```text
0–12 f    “ACHAS QUE JÁ VISTE”
13–26 f   “TODOS OS T2?”
27–34 f   ruptura / silêncio
35–48 f   “NÃO ESTE.”
49–72 f   revelar o melhor plano
```

Movimento: M02 → M09 → M01.

### Hook H2 — A contagem

```text
0–7 f     “3”
8–15 f    “2”
16–23 f   “1”
24–35 f   “ABRE A PORTA.”
36–60 f   reveal sincronizado com abertura
```

SFX: três ticks cada vez mais graves; impacto amplo no reveal.

### Hook H3 — A promessa espacial

```text
0–15 f    “MAIS LUZ.”
16–31 f   “MAIS ESPAÇO.”
32–47 f   “MENOS RUÍDO.”
48–71 f   “TUDO AQUI.”
```

Movimento: M09 com último bloco em M12.

### Hook H4 — O detalhe escondido

```text
0–18 f    “HÁ UM DETALHE”
19–35 f   “QUE MUDA TUDO.”
36–47 f   seta ou frame parcial, sem revelar
48–71 f   detalhe + palavra específica
```

Usar pausa de 4–6 f antes da revelação.

### Hook H5 — A escala impossível

```text
0–10 f    “ISTO”
11–23 f   “É DENTRO”
24–35 f   “DA CIDADE?”
36–59 f   vista ampla
60–71 f   “SIM.”
```

“SIM.” em 60–75% da largura, M01 e impacto sub grave.

### Hook H6 — O desafio visual

```text
0–20 f    “ENCONTRA O MELHOR PORMENOR.”
21–47 f   montagem de três planos sem indicação
48–59 f   “VISTE?”
60–83 f   revelar com círculo, linha ou máscara
```

Bom para comentários e repetição do vídeo.

### Hook H7 — A transformação

```text
0–17 f    “DE CORREDOR ESCURO…”
18–29 f   wipe tipográfico
30–47 f   “…A CASA ABERTA.”
48–72 f   plano principal
```

Usar a contraforma de uma letra como transição M04.

### Hook H8 — O benefício primeiro

```text
0–13 f    “ACORDAR”
14–27 f   “COM ESTA LUZ.”
28–47 f   janela / quarto / vista
48–71 f   dado curto de orientação
```

Adequado a uma linguagem mais emocional sem perder impacto.

---

## 9. Som que dá massa às letras

Tipografia agressiva sem desenho sonoro parece leve, mesmo com boa animação.

### Biblioteca mínima por função

| Função | Tipo de SFX | Duração típica |
|---|---|---:|
| Pré-eco | reverse click, inhale, reverse paper | 3–8 f |
| Entrada | thud seco, knock, snap, slam controlado | 2–8 f |
| Deslizamento | whoosh curto, swipe de ar | 4–12 f |
| Fragmentação | glitch seco, slice, rip | 2–6 f |
| Assentamento | tap, tick grave, madeira curta | 1–4 f |
| Escala gigante | sub drop, boom curto | 8–24 f |
| Saída | suction, reverse whoosh | 4–10 f |
| Contagem | click mecânico, relay, digital tick | 1–3 f |

### Camadas de impacto

Um impacto principal pode ter:

1. **Ataque** — click ou snap, muito curto.
2. **Corpo** — thud médio.
3. **Peso** — sub discreto.
4. **Cauda** — room ou textura de 6–12 f.

Não usar as quatro camadas em todas as palavras. Reservar para hook, número decisivo e CTA.

### Sincronização

- Ataque no frame exacto do assentamento.
- Whoosh começa 2–5 f antes da entrada visual.
- Sub pode começar 1 f antes para parecer maior.
- Glitch deve durar menos do que a leitura; idealmente 2–4 f.
- Um corte para silêncio de 4–8 f pode ser mais agressivo do que outro boom.

### Mistura

- SFX devem reforçar, não mascarar locução.
- Fazer duck de música em 1–2 dB nos impactos principais.
- Filtrar graves de pequenos ticks para não acumular lama.
- Variar pitch ±1–3 semitons em repetições.
- Evitar clipping na soma de boom + música + voz.
- Ouvir também no altifalante do telemóvel; sub sem ataque desaparece.

---

## 10. After Effects — construção operacional

### Estrutura de composição

```text
01_FOOTAGE_PRECOMP
02_GRADE_REFERENCE
10_TYPE_HERO
11_TYPE_LABELS
12_TYPE_CAPTIONS
20_MATTES
30_SFX_GUIDES
90_ADJUSTMENTS
```

Criar uma precomp por placa importante, mantendo o timing da composição principal para facilitar sincronização.

### Controlo mestre recomendado

Num Null `TYPE_CTRL`:

- `Impact Scale`
- `Overshoot`
- `Entry Frames`
- `Exit Frames`
- `Tracking Start`
- `Blur Amount`
- `Shadow Distance`
- `Accent Colour`
- `Plate Opacity`
- `Global Pressure` de 0 a 100

### Receita AE — entrada agressiva

1. Texto a 100% no estado final.
2. Animar Scale com 165% → 94% → 103% → 100%.
3. Animar Opacity 0% → 100% em 1–2 f.
4. Activar Motion Blur.
5. Aplicar `CC Force Motion Blur` apenas se o blur nativo não acompanhar deformações.
6. Adicionar `Transform` para controlar skew ou shutter angle separadamente.
7. Usar Graph Editor: velocidade alta à entrada, assentamento curto.

### Receita AE — palavras por sílaba ou grupo

Usar Text Animator:

```text
Animator 1: Position Y = 110 px
Animator 2: Scale = 160%
Animator 3: Tracking = 80
Range Selector:
  Based On = Words
  Shape = Ramp Up ou Square
  Ease High = 80–100%
```

Animar Offset ao longo de 6–16 f. Converter para máscaras ou layers separados quando for necessária direcção independente por palavra.

### Receita AE — integração atrás de objecto

1. Duplicar footage.
2. Rotoscopar o objecto no layer superior.
3. Texto entre footage base e matte.
4. Refinar borda a 0,5–2 px.
5. Igualar grão com `Match Grain` ou ruído subtil.
6. Se houver deslocamento de câmara, trackar em Mocha AE e aplicar ao texto.
7. Rever frame a frame em 100%; halos denunciam o efeito.

### Expressão simples de atraso por layer

Aplicar a layers duplicados para eco:

```jsx
delay = index * thisComp.frameDuration;
thisComp.layer("TYPE_MASTER").transform.position.valueAtTime(time - delay);
```

Usar duplicados com opacidade decrescente e atraso máximo de 4 f.

### Shutter e nitidez

- Entradas normais: shutter angle 180°.
- Smears agressivos: 270–360°, apenas durante 2–4 f.
- Texto parado deve ficar nítido; desligar blur residual se necessário.
- Não aplicar sharpen global à tipografia; usar contraste e desenho correctos.

---

## 11. Resolve / Fusion — construção operacional

### Árvore base Fusion

```text
MediaIn
  └─ ColorCorrector / Blur local opcional
Text+ ─ Transform ─ DirectionalBlur ─ DropShadow
Background / placa ─ Rectangle Mask
                   └─ Merge sobre MediaIn
Foreground matte ─ Merge final
MediaOut
```

### Receita Fusion — golpe de escala

No `Transform`:

```text
frame 0: Size 1.65
frame 1: Size 1.50
frame 5: Size 0.94
frame 8: Size 1.03
frame 11: Size 1.00
```

No Spline Editor:

- Suavizar sem transformar a entrada num ease lento.
- Primeiro segmento com grande declive.
- Oscilação concluída até ao f11.

### Receita Fusion — corte em tiras

1. Duplicar `Text+` 3 vezes.
2. Aplicar `Rectangle Mask` diferente a cada cópia.
3. Animar X alternando esquerda/direita.
4. Juntar com `MultiMerge`.
5. Activar Motion Blur nos Transform.
6. Fazer todos os layers convergir no mesmo frame.

### Receita Fusion — texto no espaço

Para movimento de câmara ou perspectiva:

1. Usar `PlanarTracker` numa parede, chão ou fachada.
2. Criar `PlanarTransform`.
3. Aplicar ao grupo de texto.
4. Se necessário, distorcer com `Corner Positioner`.
5. Integrar com `LightRays`, blur mínimo e grain apenas quando o plano o pede.

### Receita Resolve Edit — versão rápida

Quando não há Fusion detalhado:

- Usar Text+ em vez de Basic Title.
- Colocar entradas de 4–8 f.
- Animar Zoom, Position e Rotation no Inspector.
- Usar Adjustment Clip apenas para efeitos que devem afectar texto e imagem em conjunto.
- Criar Compound Clips por placa.
- Guardar presets por movimento, nunca por visual completo.

### Áudio no Fairlight

- Colocar marcadores nos frames de assentamento.
- Alinhar transientes, não o início visual.
- Separar buses: `VO`, `MUSIC`, `TYPE_SFX`, `ROOM`.
- Automatizar duck da música à mão nos 3–5 impactos principais.

---

## 12. Fluxo de produção em sete passes

### Passo 1 — Extrair palavras de força

Marcar no guião:

```text
[H] hook
[N] número
[B] benefício
[V] viragem
[A] acção
```

Nem tudo merece animação.

### Passo 2 — Fazer o mapa de pressão

Desenhar P1–P4 ao longo da timeline. Garantir respiração depois de dois ataques seguidos.

### Passo 3 — Reservar território visual

Ver footage sem texto e marcar:

- rostos, se existirem;
- vistas;
- pontos de fuga;
- detalhes de venda;
- zonas vazias móveis.

### Passo 4 — Montar tipografia estática

Resolver hierarquia, quebras de linha e contraste antes de animar. Se a placa não funciona parada, movimento não a salva.

### Passo 5 — Animar apenas entradas e saídas

Primeiro teste: sem SFX, sem glow, sem textura. Avaliar leitura e ritmo.

### Passo 6 — Desenhar som e integração

Adicionar impactos, máscaras, sombras e grain conforme a intenção.

### Passo 7 — Testar no dispositivo

Exportar 10–15 s e verificar:

- telemóvel vertical;
- monitor;
- sem som;
- com som baixo;
- a 50% de brilho;
- em reprodução única e em loop.

---

## 13. Anti-padrões

### “Karaoke nervoso”

Cada palavra salta, roda ou muda de cor. O espectador segue a animação, não o imóvel.

**Correcção:** animar grupos semânticos; reservar palavras isoladas para acentos.

### Movimento sem assentamento

Texto sempre a flutuar, pulsar ou vibrar.

**Correcção:** completar a entrada em 8–12 f e garantir pelo menos 12–24 f de estabilidade.

### Três estilos no mesmo hook

Glitch, bounce, máquina de escrever e zoom em dois segundos.

**Correcção:** escolher um gesto principal e um secundário.

### Escala agressiva sem hierarquia

Todas as linhas têm o mesmo peso.

**Correcção:** uma palavra martelo, uma linha de apoio e um acento.

### Tipografia a tapar a prova

“VISTA ABERTA” em cima da própria vista.

**Correcção:** colocar texto antes da revelação, no vazio lateral, ou durante 2–4 f como transição.

### Stroke grosso como solução universal

Contorno pesado reduz qualidade editorial e cria ruído.

**Correcção:** placa localizada, gradiente, sombra curta ou mudança de posição.

### Eases demasiado suaves

Tudo demora 18 f a chegar e parece publicidade genérica.

**Correcção:** entrada rápida, assentamento controlado, retenção clara.

### Glitch decorativo

Glitch sem relação com corte, som ou mensagem.

**Correcção:** usar glitch só em ruptura, erro, negação ou transformação.

### SFX de desenho animado

Boings e pops excessivos quebram credibilidade.

**Correcção:** impactos secos, materiais, ar curto, baixa frequência discreta.

### Legendas junto à interface

Texto importante demasiado baixo ou lateral.

**Correcção:** respeitar zonas seguras e testar na plataforma final.

### Modelo vertical apenas recortado para horizontal

O texto fica enorme, central e destrói a arquitectura.

**Correcção:** recompor 16:9 com leitura lateral, mais espaço negativo e menor frequência de placas.

### Preset como linguagem

O mesmo movimento em todas as palavras e vídeos.

**Correcção:** guardar mecânicas modulares; redesenhar escala, timing, hierarquia e combinação para cada peça.

---

## 14. Regras específicas por formato

### Reels 9:16

- Hook legível até ao **f12–f18**.
- Primeira ruptura visual antes de 1,5 s.
- Placas grandes podem ocupar 55–70% do frame durante 4–8 f.
- Mudar de composição, escala ou direcção a cada 1–2 s, não necessariamente de cor.
- Mostrar o imóvel sem texto durante pelo menos um bloco de 18–36 f a cada 6–10 s.
- CTA mínimo de 48 f; ideal 72 f.
- Construir loop: a saída final deve preparar visual ou sonoramente o primeiro frame.

### Tours 16:9

- Tipografia deve funcionar como capítulo, orientação e prova.
- Usar ataques em momentos-chave, não continuamente.
- Retenções de 36–72 f são aceitáveis.
- Preferir movimento alinhado com a arquitectura e câmara.
- Manter horizontes e verticais dominantes limpos.
- Um momento P4 a cada 20–40 s é suficiente.
- Dados técnicos podem viver em labels discretas; benefícios entram em escala.

### Adaptação inteligente

Não redimensionar apenas.

| 9:16 | 16:9 |
|---|---|
| Composição central e vertical | Composição lateral e panorâmica |
| Quebras em 2–4 linhas | Frases mais largas, 1–2 linhas |
| Escala extrema | Escala grande mas com espaço arquitectónico |
| Cortes de 12–30 f | Retenções de 30–72 f |
| Texto pode ser transição frequente | Texto deve pontuar capítulos |
| CTA central | CTA lateral ou em placa integrada |

---

## 15. Testes de qualidade

### Teste de um frame

Parar aleatoriamente. O frame parece intencional ou apanhado a meio de um erro?

### Teste sem som

O hook, o benefício e a acção continuam claros?

### Teste sem imagem

Com fundo neutro, a hierarquia tipográfica ainda funciona?

### Teste de desfocagem

Desfocar mentalmente o frame: vê-se primeiro a palavra certa ou uma área irrelevante?

### Teste de polegar

No telemóvel, o polegar e a interface escondem CTA, preço ou dado?

### Teste de dupla leitura

É possível ler a placa uma vez sem voltar atrás? Se não, aumentar retenção ou reduzir palavras.

### Teste de propriedade

A animação reforça este plano concreto — espaço, luz, matéria, movimento — ou poderia estar sobre qualquer vídeo?

### Checklist de entrega

- [ ] Timeline confirmada a 24 fps.
- [ ] Entradas principais entre 4–12 f.
- [ ] Retenção suficiente para cada quantidade de texto.
- [ ] Palavra-chave estável e legível.
- [ ] Cor de acento usada com disciplina.
- [ ] Zonas seguras verificadas no formato final.
- [ ] Texto não tapa permanentemente argumentos visuais.
- [ ] Motion blur apenas durante movimento.
- [ ] SFX alinhados ao assentamento.
- [ ] Voz não mascarada pelos impactos.
- [ ] Pelo menos um momento de respiração visual.
- [ ] CTA retido por 48–96 f.
- [ ] Versões 9:16 e 16:9 recompostas, não só redimensionadas.
- [ ] Exportação de teste vista num telemóvel real.

---

## 16. Fórmulas de combinação

Usar estas fórmulas como ponto de partida:

```text
HOOK DURO
M01 Golpe de escala + M02 Corte de lâmina + impacto em 3 camadas

DADO PREMIUM
M07 Construção arquitectónica + contagem + tick seco

MUDANÇA DE DIVISÃO
M04 Palavra-câmara + reverse whoosh + corte no interior da letra

LISTA RÁPIDA
M06 Esteira + M09 Substituição + clicks mecânicos

BENEFÍCIO EMOCIONAL
M11 Revelação por objecto + Contraponto tipográfico + respiração sonora

CTA DE REEL
M12 Queda gravitacional + sub curto + micro pulso único

TOUR HORIZONTAL
M07 Construção + M05 Carimbo pontual + longos blocos P1
```

Princípio final: **a agressividade vem da diferença entre ataque e repouso**. Escala, velocidade, cor e som só funcionam quando a palavra certa aparece no frame certo — e depois pára tempo suficiente para ser compreendida.
