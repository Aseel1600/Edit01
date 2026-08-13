# Speed Ramps na Produção

Guia de produção OpenMontage: o que são, onde funcionam, velocidades, curvas, transições, áudio, motion blur e armadilhas — com foco em **imobiliário / I2V** e DaVinci Resolve, mas aplicável a FCP, Premiere e AE.

Complementa [`MASTERING.md`](MASTERING.md). Em projectos Resolve com footage IA a 24 fps, ver também o handoff local `MOTION-FLUIDEZ.md` (ex.: Mario Garcês `_davinci/`).

---

## 1. O que é um speed ramp

**Speed ramp** = a velocidade de um *mesmo* clip muda ao longo do tempo (ex.: 300% → 70% → 400%), com transição gradual ou brusca entre segmentos.

Não é o mesmo que:

| Técnica | Diferença |
|---------|-----------|
| **Constant speed** | Um % único no clip inteiro (ex. 50% forever) |
| **Time freeze / hold frame** | Congela um fotograma |
| **Cut to slow-mo** | Trocas de velocidade *entre* clips |
| **Optical flow / Speed Warp** | *Como* o NLE inventa frames no slow — não é o ramp em si |

O ramp é o **desenho rítmico**. O optical flow / Pixel Motion / Frame Blend é o **motor de interpolação** que tenta fazer o slow parecer fluido.

---

## 2. Porquê funciona (psicologia de edição)

1. **Contraste de tempo** — o cérebro lê o hold lento como “importante” porque acabou de ver velocidade.
2. **Entrada / saída de cena** — o ramp in “chega” à divisão; o ramp out “sai” sem precisar de transição visual pesada.
3. **Sync com música** — o pico de velocidade alinha com kick / riser / whoosh; o hold com o groove ou com a legenda.
4. **Mascarar cortes** — um out rápido + in rápido no clip seguinte pode sentir-se como um único gesto (desde que o movimento da câmara continue na mesma lógica).

Regra de ouro da indústria (FCP / RE / lifestyle): **menos ramps, melhores ramps.** Um ou dois por beat forte > um em cada plano.

---

## 3. Onde ficam melhor

### 3.1 Por género

| Género | Uso típico | Notas |
|--------|------------|-------|
| **Real estate / listing** | Entrada e saída de cada divisão | Hold no centro para legenda e leitura do espaço |
| **Sports / action** | Impacto, aterragem, dunk, crash | Filmar a 60–120+ fps; whoosh + crash zoom |
| **Automotive / product** | Reveal, pan rápido → slow no detalhe | Bom parallax ajuda o optical flow |
| **Wedding / lifestyle** | Momentos emocionais (beijo, first look) | Ramps suaves; não “TikTok” em excesso |
| **Music video / social** | Sync agressivo com beat | Pode ir a 10–20× no pico |
| **Narrative cinema** | Raro; mais “speed punch” pontual | Overuse = linguagem de trailer YouTube |

### 3.2 Por tipo de plano (imobiliário)

**Melhor:**

- Dolly / push-in **constante** numa direcção
- Lateral track paralelo a fachada / corredor
- Reveal de sala grande com movimento estável
- Exterior com parallax claro (edifício vs fundo)

**Aceitável com cuidado:**

- Pan curto (< ~15% do frame)
- Orbit muito suave

**Mau para ramp + optical flow:**

- WC, espelhos, vidros, água
- Azulejo, relva, grelhas, texturas repetitivas
- Planos quase estáticos (o ramp vira “nada a acontecer” + stutter)
- I2V que já tem morph / warp
- Zoom digital forte no NLE *por cima* do ramp (piora judder)

### 3.3 Momentos da peça

| Momento | Ramp? | Porquê |
|---------|-------|--------|
| Abertura / hero shot | Sim, moderado | Hook + estabelecer |
| Divisões hero (sala, suíte, terraço) | Sim | Hold longo + legenda |
| Passagens / corredores | Sim, curto | Ritmo; hold curto |
| Detalhes (torneira, puxador) | Opcional / suave | Ou só constant slow |
| Cartão do agente / CTA | **Não** | Legibilidade > estilo |
| Planta / mapa | **Não** | |
| Transição AI já morphada | Quase não | Morph + ramp = melado |

---

## 4. Matemática: quão lento podes ir sem inventar frames

Antes de rampares, calcula o **chão seguro** (todos os frames originais, sem duplicar):

```
chão_seguro_% = (fps_timeline / fps_fonte) × 100
```

Exemplos:

| Fonte | Timeline | Chão sem stutter “óptico” |
|-------|----------|---------------------------|
| 60 fps | 30 fps | **50%** |
| 60 fps | 24 fps | **40%** |
| 48 fps | 24 fps | **50%** |
| 30 fps | 24 fps | **80%** |
| **24 fps** | **24 fps** | **100%** (qualquer slow <100% repete ou interpola) |

Implicações práticas:

- **Filmar / gerar a 60 fps** e montar a 24/30 = ramp clássico de sports/RE (Cole Connor e fluxos FCP).
- **Fonte IA a 24 fps na timeline 24** = não há “slow gratuito”. Abaixo de ~85–90% o hold treme salvo interpolação forte (e em IA o Optical Flow Free muitas vezes falha).
- Em FCP, workflows RE usam frequentemente **~40%** como base quando a fonte é 60 e a timeline é 24 (é o chão matemático).

---

## 5. Receitas de velocidade (produção)

Percentagens são **ponto de partida**. Ajusta ao movimento do plano e ao BPM.

### 5.1 Modelo OpenMontage / listing (fonte boa ou pré-interpolada)

```
[RAMP IN]     →  [HOLD]      →  [RAMP OUT]    →  [CORTE]
 0,8–1,2 s        3,5–6 s         0,6–1,0 s        0–2 frames
 250–400 %        50–70 %*        300–500 %
```

\* Com fonte **24 fps IA sem pré-interp**, sobe o hold para **~85–90%** (ver §11).

| Tipo de plano | Hold | In | Out |
|---------------|------|----|-----|
| Hero (sala, terraço, suíte) | 5–6,5 s | 1,0–1,2 s | 0,8–1,3 s |
| Secundário (cozinha, quarto) | 2,5–3,5 s | 0,7–1,0 s | 0,6–1,0 s |
| Passagem | 1,5–2,5 s | 0,5–0,8 s | 0,5–0,8 s |

**Legendas:** entram ~0,3 s após o fim do ramp in; saem ~0,5 s antes do ramp out.

### 5.2 Reel social / beat-sync (mais agressivo)

| Zona | Velocidade típica |
|------|-------------------|
| Hold | 40–80% (se fonte ≥48–60 fps) |
| Pico whoosh | 200–400% |
| Pico “ninja” / smash | **10–20×** (1000–2000%) num burst curto |
| Freeze dramático | 0–1% num beat (Studio Sunday / FCP “to 0%”) |

Burst de 20× só funciona se:

- for **muito curto** (fracção de segundo a ~1 s),
- tiver **motion blur** e/ou whoosh,
- e o hold a seguir for legível.

### 5.3 Sports / impact (Cole Connor–style Resolve)

- Timeline **30 fps**, fonte **60 fps** → slow natural até 50%.
- Speed points: rápido → lento no impacto → (opcional) rápido outra vez.
- **Temporal Motion Blur** / Vector MB nos trechos rápidos.
- Whoosh no acelerar; por vezes crash zoom no hit.
- Curvas com ease (não degraus lineares).

### 5.4 Receita conservadora (IA 24 fps, Resolve Free)

Preferência validada em projecto real (Mario / Lumiar):

```
~85–90%  →  220–280% (pico curto)  →  ~90%
```

- Pico **≤250–300%** se a fonte for 24 fps e o whoosh for longo.
- Hold **não** a 40–60% sem 48 fps pré-interp ou Studio Speed Warp.
- Whoosh pode continuar alto; o tremer está no **abrandar**, não no acelerar.

---

## 6. Curvas e easing (o que separa amador de pro)

Um ramp “em escada” (100% → 300% sem ease) sente-se mecânico.

### Boas práticas

1. **Ease in / ease out** nos keyframes de velocidade (Resolve Keyframe Tray / Retime Curve; AE Easy Ease; FCP speed transitions entre segmentos).
2. **Alongar o roll-off** no abrandar (o olho perde detalhe se o slow “bate” de repente).
3. **Pico curto, hold estável** — a velocidade alta não precisa de durar; o hold sim.
4. Em Resolve 20+: Keyframe tray → curva **Retime Speed** → Ease In/Out → handles com Shift.
5. Evitar demasiados speed points no mesmo clip (3–5 segmentos chegam na maioria dos casos RE).

### Forma típica (S-curve)

```
velocidade
    ^
400 |     /\
    |    /  \
    |   /    \________  hold
 80 |__/
    +------------------→ tempo
      in   pico   hold   out
```

---

## 7. Transições a acrescentar (e quais evitar)

O ramp **já é** uma transição de energia. Empilhar efeitos a mais = ruído.

### 7.1 Combinações que funcionam

| Transição / gesto | Quando | Notas |
|-------------------|--------|-------|
| **Corte seco** no pico do ramp out | Default imobiliário OpenMontage | Limpo; deixa o ritmo falar |
| **Whoosh SFX** no acelerar | Quase sempre em RE social | Ligeiramente *antes* do pico visual (~1–3 frames) |
| **Impact / hit / sub drop** no momento do slow | Sports, smash reveal | |
| **Crash zoom** (scale) sincronizado com o hit | Action / highlight | Com moderação em RE |
| **Match cut de movimento** | Dolly out → dolly in na divisão seguinte | Continuidade > efeito |
| **Dip to color / flash** muito curto | Music video | Raro em listing sério |
| **Zoom transition pack** (tipo Ryan Nangle / FCP) | Social RE agressivo | Só se o pack casar com a marca |

### 7.2 O que evitar em cima do ramp

- Cross dissolve longo no meio do hold
- Morph AI + ramp forte
- Várias transições 3D (whip, spin, glitch) no mesmo corte
- Legenda a entrar *durante* o pico de velocidade (ilegível)
- Áudio do clip a “chipmunk” — **mute sempre** o áudio da fonte retimada e usa música/SFX

### 7.3 Áudio — checklist de produção

1. **Mute** do áudio embutido do clip com ramp.
2. **Whoosh** alinhado ao ramp in e/ou out (não ao hold).
3. Whoosh **ligeiramente adiantado** ao pico visual.
4. Nível: whooshes fracos somem na mix (−9 dB já falhou em produção real); calibra contra a música.
5. Música: idealmente BPM conhecido; alinha picos de ramp a kicks / fills.
6. No hold: espaço para voz-off ou silêncio rítmico — não encher de SFX.

---

## 8. Motion blur (porque o fast digital parece “errado”)

Acelerar em post **remove** o motion blur natural do obturador. O resultado fica crisp e “staccato”.

### Abordagens

| Ferramenta | Método |
|------------|--------|
| **Resolve Free** | Compound clip ou Adjustment Clip → Fusion: **Optical Flow (OF)** → **Vector Motion Blur** (não o Motion Blur simples). Animar **Blend** 1→0 (só nas zonas rápidas). OF mode **Classic** = mais lento, mais limpo. |
| **Resolve** | Temporal Motion Blur / efeitos de blur direcional nos trechos rápidos |
| **AE** | CC Force Motion Blur / Pixel Motion blur / plugin (RSMB, etc.) |
| **Filmar certo** | Shutter angle ~180° na captura; high fps ajuda o slow, não o fake-fast |

Marca na timeline onde começa/acaba o fast; desliga o blur no hold (senão o slow fica “sujo”).

Cache: Playback → Render Cache → **Smart** — este stack é pesado.

---

## 9. Optical flow e interpolação (por NLE)

### 9.1 DaVinci Resolve

| Recurso | Free | Studio |
|---------|------|--------|
| Retime Controls / Curve | ✅ | ✅ |
| Retime Process: Nearest / Frame Blend / **Optical Flow** | ✅ | ✅ |
| Motion Estimation: Standard / Enhanced Faster/Better | ✅ | ✅ |
| **Speed Warp** (neural) | ❌ | ✅ |

Fluxo Edit page:

1. Clip → `Ctrl/Cmd+R` (Retime Controls) → Add Speed Point.
2. Ajusta % por segmento (ou Retime Curve).
3. Inspector → **Retime and Scaling** → Optical Flow → **Enhanced Better** (arquitectura / linhas rectas).
4. Espelhos / azulejo: desce para **Frame Blend** em vez de desistir do ramp.
5. Ease na curva.

**Armadilha crítica:** se o ramp estiver num **Fusion TimeStretcher**, o **Optical Flow da Edit não se aplica**. Ou passas o ramp para a Edit Retime Curve, ou interpolas noutro sítio (pré-48 fps / AE).

### 9.2 Final Cut Pro

- Retime → Speed Ramp presets (**to 0%** / **from 0%**) ou **Blade Speed** + Custom %.
- Speed transitions entre segmentos (gradual vs abrupt).
- Workflows RE: timeline 24, fonte 60, base ~40%, picos até 20×, Zoom transitions + whoosh.
- Optical flow / retiming quality nas preferências do clip.

### 9.3 After Effects

1. `Layer → Time → Enable Time Remapping`
2. Keyframes + Easy Ease / Graph Editor (speed vs value graph)
3. `Frame Blending → Pixel Motion` (só onde o preview nas **bordas e linhas** estiver limpo)
4. Pre-render o plano → montar no Resolve/Premiere

Pipeline OpenMontage sem Studio: AE para retime difícil → Resolve Free para montagem.

### 9.4 Premiere Pro

- Rate Stretch vs Time Remapping (keyframes).
- Optical Flow em Export / clip (cuidado com artefactos).
- Mesma lógica de chão de fps e mute de áudio.

---

## 10. Filmar / gerar a pensar no ramp

### Captura real

- **60 fps** (ou 120) se fores fazer slow significativo a 24/30.
- Movimento **único, constante**, uma direcção.
- Mais duração na source do que no timeline (ramps comem tempo): ex. 8–12 s source → 5–7 s finais.
- Evitar handheld nervoso se quiseres optical flow limpo (ou estabiliza *antes* do retime).
- Shutter coerente (~180°) para blur natural no 100%.

### Geração I2V (Veo, Kling, etc.)

| Fazer | Evitar |
|-------|--------|
| Movimento constante; ramps só em post | Pedir speed ramp no prompt |
| Clips longos com margem | Orbit / zoom agressivo |
| 24 fps consistente no projecto | Misturar 24/30/60 sem plano |
| Regenerar mais lento se precisares de hold longo | Slow extremo + OF em cima de warp IA |

**Nota de marca OpenMontage:** 60 fps em listing IA leu-se como “vídeo de telemóvel” em testes; o registo cinema ficou a **24 fps**. Isso **piora** o headroom de slow — compensa com hold alto (85–90%), pré-interp 48 fps, ou menos agressividade.

---

## 11. Footage IA a 24 fps — lições de produção

Problema: a 50% cada frame “seguro” ocupa 2 frames de timeline → **judder**. Enhanced Better no Free quase não salva IA; TimeStretcher ignora OF da Edit.

### Remédios (por ordem de custo)

1. **Sobe o piso do hold** para ~85–90%.
2. **Encurta / baixa o pico** (≤250–300% em bursts curtos).
3. **Pré-interpolar para 48 fps** fora do NLE, ReplaceClip, depois OF na timeline.
4. Passar ramp da **Fusion** para a **Edit Retime Curve**.
5. Studio + **Speed Warp** se o orçamento justificar.
6. Aceitar stutter leve > parede que “derrete”.

### Optical flow — quando usar / não usar

| Situação | Usar OF/Pixel Motion? |
|----------|------------------------|
| Ramp in/out 250–400%, pan/dolly limpo | ✅ Testar |
| Hold 60–70% com movimento suave e fonte ≥48 fps | ✅ Se preview limpo |
| Slow &lt;40% longo | ⚠️ Só se preview OK |
| WC, espelhos, reflexos | ❌ → Frame Blend |
| Texturas repetitivas | ⚠️ Ghosting |
| I2V já com warp | ❌ Amplifica |
| Planta, cartão, estático | ❌ |
| Timeline inteira no export | ❌ Nunca como “master bus” |

**Regra:** OF é decisão **por clip / por zona**, não efeito global no master (`MASTERING.md`).

### Codec / GOP (erro “decoding full resolution” no Resolve)

Clips Kling/Minimax com **um só keyframe** rebentam no retime+OF. Remux/reencode all-intra (`-g 1 -bf 0 -qp 1`, profile high — **não** `-qp 0`). Detalhe operacional em `MASTERING.md`.

---

## 12. Anti-padrões (o que não fazer)

1. Ramp em **todos** os clips — fadiga visual; perde significado.
2. Hold demasiado curto para ler o espaço / a legenda.
3. Pico longo a 1000%+ sem blur nem SFX.
4. Slow a 40% em fonte 24 fps “porque o tutorial de 60 fps fazia assim”.
5. Confiar no playback proxy sem cache Smart / render de teste.
6. Deixar áudio da câmara no clip retimado.
7. Legenda hero no meio do whoosh.
8. Zoom In Fusion + ramp + 24 fps IA (optical flow não corrige zoom digital).
9. Cross-dissolve a tapar um ramp mal feito.
10. Assumir que Free = sem Optical Flow (falso) ou que Free = Speed Warp (também falso).

---

## 13. Checklist rápido (antes de exportar)

- [ ] Fonte fps vs timeline: chão seguro calculado  
- [ ] Hold legível (duração + %); hero rooms com tempo de sobra  
- [ ] Curvas com ease; picos curtos  
- [ ] OF / Frame Blend / Speed Warp escolhido **por clip**  
- [ ] Se Fusion TimeStretcher → confirmar se OF da Edit está a ser ignorado  
- [ ] Motion blur só nas zonas rápidas  
- [ ] Áudio fonte muted; whoosh sync (ligeiro early) + música  
- [ ] Sem ramp no cartão / CTA  
- [ ] Preview a 100% em bordas, rodapés, ombreiras, espelhos  
- [ ] Cache Smart; export de teste curto do pior plano  

---

## 14. Referências e tutoriais (pesquisa)

### YouTube / criadores (conceitos a roubar)

| Tema | O que extrair |
|------|----------------|
| **Cole Connor – Resolve speed ramps** | 60→30; speed points; Temporal MB; whoosh; ease; crash zoom |
| **FCP real-estate speed ramps** | Base ~40% (60→24); Blade Speed; picos até 20×; não abusar |
| **Ryan Nangle – Zoom transitions + ramp** | Empacotar gesto visual com o whoosh |
| **Studio Sunday / Vlad – ramp to 0% / 1%** | Freeze dramático no beat; usar com parcimónia |
| **Creative Video Tips – Resolve MB** | Compound + OF Classic + Vector Motion Blur; Blend keyframes |

Links úteis (docs / artigos):

- [Apple FCP – Variable speed effects](https://support.apple.com/guide/final-cut-pro/create-variable-speed-effects-ver95783cbbc/mac)
- [Creative Video Tips – Speed ramp + motion blur (Resolve)](https://creativevideotips.com/tutorials/speed-ramp-with-motion-blur-in-davinci-resolve)
- Guias gerais (Kapwing, Pixflow, ViteLNK): steepness do ramp vs polish; mute source; whoosh early

### Documentação interna OpenMontage

| Ficheiro | Conteúdo |
|----------|----------|
| [`MASTERING.md`](MASTERING.md) | Pipeline listing, OF por clip, GOP/codec, modelo in/hold/out |
| `PLANO-VIDEO-*.md` (cliente) | Tempos e % por plano |
| `_davinci/MOTION-FLUIDEZ.md` | 24 fps IA, piso 85–90%, TimeStretcher vs Edit |

---

## 15. Resumo de bolso

```
FILMA / GERA: movimento constante, fps alto se precisares de slow verdadeiro.
DESENHA:     in rápido → hold legível → out rápido → corte.
CURVA:       ease, pico curto, hold estável.
VELOCIDADE:  respeita o chão (timeline/fonte); IA 24fps → hold ~85–90% ou pré-48fps.
POLISH:      OF só onde limpar; Vector MB no fast; mute áudio; whoosh no pico.
TRANSIÇÃO:   corte seco + SFX > pack de efeitos em cima do ramp.
DISCIPLINA:  poucos ramps bem feitos batem muitos ramps medianos.
```

---

*Documento vivo — actualizar quando um projecto invalidar uma receita (fps, NLE, ou tipo de fonte).*
