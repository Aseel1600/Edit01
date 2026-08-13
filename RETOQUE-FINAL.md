# Retoque final da mistura (finish)

Guia de produção OpenMontage: efeitos e passes de **polish** depois do corte, dos speed ramps e da correção técnica — o que acrescentar, em que ordem, com que intensidade, e o que evitar em imobiliário / I2V.

Complementa [`MASTERING.md`](MASTERING.md) (fase Finish) e [`SPEED-RAMPS.md`](SPEED-RAMPS.md) (ritmo).  
**Mistura** aqui = imagem + áudio no master, não só Fairlight.

---

## 1. O que é o retoque final

Não é “meter LUT cinematográfica e exportar”. É a camada que:

1. **Unifica** clips de fontes diferentes (câmaras, I2V, stills animados).
2. **Corrige** o que a montagem ainda deixa inconsistente (WB, exposição, janelas).
3. **Acrescenta carácter óptico** mínimo (glow, grain, vignette) *só se servir a marca*.
4. **Fecha o áudio** (níveis, SFX, limitador) sem tapar falhas de imagem.

Ordem mental (igual a `MASTERING.md`):

```
Correção por clip → Grade leve consistente → Match entre cortes
→ Óptica / texture (opcional) → Gráficos → Áudio → Export único
```

🔴 **Nunca** meter optical flow / frame interpolation neste passo. Isso fica no retime, clip a clip.

---

## 2. Ordem dos efeitos (imagem) — o que importa mais

A ordem muda o resultado. Receita de produção estável:

| # | Passo | Função | Onde |
|---|--------|--------|------|
| 1 | **CST / color management** | Log → Rec.709 (ou timeline gerida) | Color · CST |
| 2 | **Primaries** | Exposição, contraste, WB | Wheels / curves |
| 3 | **Secondaries RE** | Tetos brancos, castes mistas, janelas | Qualifier, Color Warper, windows |
| 4 | **Look / LUT (fraco)** | Mood de casa, não filtro Instagram | Node dedicado, mix &lt;100% |
| 5 | **Repair** | Denoise (se preciso) → depois sharpen leve | NR → Sharpen |
| 6 | **Óptica** | Softness mínima, Glow/Bloom, Halation | OFX / plugins |
| 7 | **Vignette** | Atenção ao centro (muito subtil em RE) | Window ou OFX |
| 8 | **Grain / dither** | Unificar digital “plástico” + banding | **Último** na cadeia de look |
| 9 | **Deliverable check** | Scopes, legalize, preview telefone | Parade / Vectorscope |

**Grain por último** (depois de contraste/saturação do look), para não ser esmagado pelas curvas.  
**Denoise antes de sharpen** — NR amolece; sharpen recupera textura sem reamplificar ruído.

Há debate académico “grain antes vs depois do grade” em pipelines de film emulation 3D. Em NLE de entrega web/Rec.709, a regra prática é: **corrigir → look → óptica → grain no topo**.

---

## 3. Árvore de nodes (modelo imobiliário)

### 3.1 Interior (mais nós)

```
[Primaries] → [Spare/Log trim]
     → [Lens / vignette CORRECT]   ← só se a lente tiver barrel/vinheta indesejada
     → [White / cast cleanup]      ← Color Warper, slicer, luma qualifiers
     → [Windows]                   ← power window + soft roll-off
     → [CST → Rec.709]
     → [Look / Dehancer / LUT mix baixo]
     → [Denoise?] → [Sharpen leve]
     → [Glow?] → [Grain?]
```

### 3.2 Exterior

Menos limpeza de castes; pode **abrir** saturação de céu/verde com mão leve. Match sol vs sombra entre clips adjacentes (mesmo WB de câmara ≠ mesma leitura no ecrã).

### 3.3 Timeline Group / Adjustment Clip

Para look global (grain + vignette + glow fraco): **Adjustment Clip** ou **Timeline node** *depois* do match por clip.  
Não uses o Adjustment para WB — isso tapa erros em vez de os corrigir.

---

## 4. Catálogo de efeitos — quando, quanto, armadilhas

### 4.1 Correção (não é “efeito”, mas é 80% do finish)

| Ferramenta | Uso em RE | Notas |
|------------|-----------|-------|
| **Lift / Gamma / Gain** | Base | Highlights sob ~90–95 IRE se quiseres “premium”, não estourados |
| **Contrast + Pivot** | Separar paredes / móveis | Pivot nos mids |
| **Color Warper** | Empurrar verdes/magenta para neutro | Toque leve; fácil exagerar |
| **Qualifier + window** | Tetos, paredes, janelas | Feather generoso |
| **Hue vs Hue / Lum vs Sat** | Tirar saturação de shadows/highlights plásticos | |

YouTube útil (RE): *Jeremy Deihl – colors in Resolve for real estate* — Color Warper + limpeza de tetos/casts; PowerGrade separado interior vs exterior; Dehancer como look opcional.

**Meta imobiliário OpenMontage:** brancos neutros, madeiras vivas mas reais, saturação contida. Comprador nota **incoerência entre divisões** mais do que LUT “cinema”.

### 4.2 LUT / Film Look / Dehancer

| Recurso | Free Resolve | Studio | Uso recomendado |
|---------|--------------|--------|-----------------|
| LUTs .cube | ✅ | ✅ | Starting point; baixar mix 30–60% |
| **Film Look Creator** (grain, bloom, halation, weave, vignette) | ❌ | ✅ | Atalho Studio; ainda assim dial back em RE |
| Film Grain OFX dedicado | ❌* | ✅ | *Workarounds Free abaixo |
| Glow OFX | ✅ (básico) | ✅ | Bloom de highlights |
| Film Halation OFX | parcial / Studio | ✅ | Só em practicals / janelas |
| Dehancer / FilmConvert (3rd party) | plugin | plugin | RE premium; Jeremy e outros usam |

Em listing: LUT kodak/cinema **forte** = risco de “falso”. Preferir **correcção limpa + 10–20% de look**.

### 4.3 Glow / Bloom

**O quê:** luz que “sangra” dos highlights (janelas, candeeiros).

| Parâmetro | Partida |
|-----------|---------|
| Threshold | Acima da pele / paredes; isola só brilhos |
| Blend / Global | **10–20%** |
| Composite | Soft Light ou ecrã suave |

✅ Bom em: exteriores golden hour, salões com grandes vãos, night shots.  
❌ Mau em: WC, espelhos, azulejo (vira melado), I2V já soft.

### 4.4 Halation

**O quê:** franja quente (âmbar/rosa) em volta de highlights de alto contraste — carácter de película.

| Parâmetro | Partida |
|-----------|---------|
| Mix | **&lt;10%** |
| Radius | Pequeno |
| Isolação | Só practicals / janelas via threshold |

Em imobiliário diurno limpo: **quase zero**. Em lifestyle / noite / “editorial”: um toque.

Free sem Halation OFX: Soft Light glow quente + blur seletivo nos highlights (aproximação).

### 4.5 Softness / Pro-Mist digital

Film é menos “crisp” que digital. Um **Gaussian Blur** mínimo (Horizontal/Vertical Strength quase 0, subir à milésima) ou soft glow global.

⚠️ Em arquitectura, softness a mais = “vídeo barato”. Preferir **sharpen selectivo nos mids** + grain fino a blur global.

### 4.6 Sharpen

| Regra | Detalhe |
|-------|---------|
| Depois do denoise | Sempre |
| Amount baixo | RE: 2–4 “pontos” no estilo Jeremy; zoom 100% em bordas de bancada |
| Evitar halos | Contadores, azulejo, molduras |
| Não global crunch | Preferir midtone detail |

I2V já vem por vezes *oversharp* ou *plastic*: sharpen pode piorar. A/B obrigatório.

### 4.7 Denoise / Noise Reduction

| | Free | Studio |
|--|------|--------|
| Temporal / Spatial NR forte | Limitado | ✅ Temporal + UltraNR |
| Quando | ISO alto, noite, compressão I2V | |

Pipeline: **NR → Sharpen**. Em Free, NR agressivo + sharpen leve; se o clip for irrecuperável, regenerar / Topaz fora do NLE.

### 4.8 Vignette

| Tipo | Uso |
|------|-----|
| **Correcção** | Remover vinheta da lente UWA (RE interiors) |
| **Criativa** | Escurecer cantos para foco — **muito** subtil |

Power window circular, feather extremo, opacity baixa. Em listing wide: vignette criativa forte = “filtro”; comprador sente o espaço menor.

### 4.9 Lens distortion / chromatic aberration

- **Corrigir** barrel de ultra-wide (interiores) — sim, cedo na árvore.  
- **Acrescentar** CA / dirt / gate weave — quase nunca em RE comercial; ok em music video / film look agressivo.

### 4.10 Film grain

**Função em finish:** unificar looks, esconder banding em céus/paredes lisas, tirar “CGI plástico” de I2V.

| Partida | Valor |
|---------|-------|
| Estilo | 35 mm fino (não 8 mm grit) |
| Mix / opacity | **12–20%** (sentir no telefone e no desktop) |
| Shadows vs highlights | Menos grain no céu / parede branca se notar-se |
| Animação | Grain estático = fake; usar grain animado / OFX |

**Studio:** Film Grain OFX ou Film Look Creator.  
**Free:** overlay de grain com blend Soft Light/Overlay a opacidade baixa; ou export + grain em AE/ffmpeg; ou plugin.

Grain **depois** do look. Não apliques grain e depois um blur forte.

### 4.11 Dither / banding

Paredes lisas + H.264 8-bit = banding. Grain fino ou dither no export ajuda mais do que curves agressivas em azuis.

### 4.12 Efeitos a evitar no finish de listing

| Efeito | Porquê |
|--------|--------|
| Gate weave / flicker de película | Distrai; parece erro |
| Lens dirt / heavy flare | Suja arquitectura |
| Heavy split-tone teal/orange | Desvaloriza “cor real do imóvel” |
| Bloom extremo | Janelas viram neon |
| Sharpen + NR AI em loop | Halo + plastic |
| Segundo optical flow no deliverable | Derrete linhas |

---

## 5. Receitas por tipo de peça

### A) Listing premium limpo (default OpenMontage)

```
Primaries + match → janelas controladas → saturação contida
→ sharpen mínimo → grain 0–12% só se banding/I2V
→ sem halation / bloom forte
→ Rec.709, sem LUT cinema pesada
```

### B) Reel social / lifestyle

```
Primaries → look quente leve (LUT 30–50%)
→ glow 10–15% nos brilhos → vignette suave
→ grain 12–18% → whoosh já na edição
```

### C) Night / golden hour exterior

```
Primaries (proteger highlights) → bloom/halation baixo
→ grain fino → saturação cuidada nos laranjas
```

### D) Footage I2V “plástico”

```
Não cures com LUT.
Match exposição → grain fino unificador → soft midtone
→ se warp/OF artifacts: baixa sharpen; não blooms
```

---

## 6. Áudio na mistura final

O finish de imagem sem áudio fechado não é entrega.

| Passo | Alvo |
|-------|------|
| Mute clips retimed | Sem chipmunk |
| Música | Nível estável; duck se voz |
| Whoosh / hits | Sync aos ramps; early 1–3 frames; audível na mix |
| Limiter master | True peak ≤ **−1 dBTP** |
| Loudness web 16:9 | ~**−16 LUFS** integrated |
| Loudness Reels/Shorts | ~**−14 LUFS** |

SFX e música **depois** do picture lock. Não “consertes” um ramp feio com whoosh mais alto.

---

## 7. Resolve Free vs Studio (finish)

| Precisas disto? | Free chega? | Alternativa Free |
|-----------------|-------------|------------------|
| Primaries, warper, windows, LUT | ✅ | — |
| Glow subtil | ✅ | — |
| Film Grain / Film Look Creator | ❌ | Overlay grain / AE / plugin |
| Temporal NR forte | ❌ | Pré-processar (Topaz, etc.) |
| Speed Warp (não é finish) | ❌ | Ver SPEED-RAMPS |
| Export 1080p Rec.709 | ✅ | — |

Para a maioria dos listings OpenMontage, **Free + disciplina de cor** > Studio + Film Look Creator no máximo.

---

## 8. Scopes e QA (antes de chamar “final”)

- [ ] Parade: clips adjacentes com brancos alinhados  
- [ ] Vectorscope: sem cast verde/magenta óbvio em tetos  
- [ ] Janelas: roll-off consistente (não uma divisão estourada e a seguinte correcta)  
- [ ] Zoom 100%: sem halos de sharpen, sem grain “areia” em paredes  
- [ ] Telefone + ecrã grande (artefactos I2V saltam no grande)  
- [ ] Gráficos/legendas **por cima** do grain? Idealmente grain sob o texto limpo, ou grain global muito fino  
- [ ] Áudio: true peak e LUFS  
- [ ] Export **sem** optical flow / frame blend no diálogo de render  

---

## 9. Anti-padrões

1. LUT a 100% como único “grade”.  
2. Look global antes de match por divisão.  
3. Bloom + halation + weave + dirt todos ligados “porque o preset”.  
4. Grain antes do contraste (resultados estranhos) ou grain + blur depois.  
5. Sharpen no Adjustment Clip a matar o filme inteiro.  
6. Vignette forte em wide interiors.  
7. Tratar finish como sítio para esconder ramps maus.  
8. Re-exportar com interpolação “para suavizar”.  

---

## 10. Checklist de bolso

```
1. Picture lock (cortes + ramps OK)
2. Primaries + WB + match adjacente
3. Janelas / tetos (RE)
4. Look ≤ 50% se existir
5. NR → sharpen (só se preciso)
6. Glow/halation (opcional, baixo)
7. Vignette (corrigir ou quase nada criativo)
8. Grain fino por último (se unificar)
9. Áudio: LUFS + peak + SFX
10. Scopes + telefone → export limpo
```

---

## 11. Referências

| Fonte | O que extrair |
|-------|----------------|
| [Jeremy Deihl – RE color in Resolve](https://www.youtube.com/watch?v=XgKGfqmFh-A) | Interior vs exterior PowerGrade; Warper; denoise→sharpen; Dehancer |
| FilmmakingElements – Film look Resolve | CST→LUT, softness, glow Soft Light, grain last, halation |
| Creative / AAA presets – RE grading | Normalize first; modest sat; window control; grain vs banding |
| Blackmagic docs / Toolfarm Free vs Studio | Film Look Creator, Film Grain, Temporal NR = Studio |
| [`MASTERING.md`](MASTERING.md) | Ordem finish, LUFS, export |
| [`SPEED-RAMPS.md`](SPEED-RAMPS.md) | Não misturar retime com polish |

Plugins frequentes em pro RE: **Dehancer**, **FilmConvert Nitrate**, MotionVFX packs (transições — não são grade).

---

## 12. Resumo

```
FINISH ≠ FILTRO.
Corrige e faz match primeiro.
Óptica (glow/halation/vignette) só com intenção e mix baixo.
Grain fino no fim para unificar e matar banding — não para “parecer 16mm”.
Imobiliário: cor verdadeira e consistente bate look de trailer.
Áudio fecha a mistura; whoosh não tapa imagem má.
Optical flow não entra neste capítulo.
```

---

*Documento vivo — alinhar a ESTILO-CLIENTE.md quando o cliente tiver look locked.*
