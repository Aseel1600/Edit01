# Masterização de vídeo · imobiliário e tours animados

Guia genérico OpenMontage para peças montadas a partir de **fotografias animadas (I2V)**, **speed ramps**, **legendas** e **música** — típico de listings, reels e vídeos 16:9 de agentes.

Aplica-se a qualquer projecto; planos específicos de cliente ficam em ficheiros locais (ex.: `PLANO-VIDEO-100s.md`).

---

## Resposta rápida: optical flow no final?

**Não.** Não aplicar optical flow / Pixel Motion como passo global no export final.

Interpolação por fluxo óptico é decisão **por clip e por zona de retime** — não um efeito de “master bus” sobre o filme inteiro.

Aplicar interpolação a toda a timeline no fim tende a:

- aumentar render e artefactos acumulados;
- “derreter” linhas de arquitectura, texturas e detalhes em clips AI;
- mascarar problemas que deviam ser corrigidos **antes** (geração, ramp, corte).

**Regra:** testar optical flow **clip a clip**; usar como última opção entre métodos de interpolação; voltar atrás se aparecer warping.

---

## O que é masterizar neste tipo de vídeo

Masterizar ≠ só export. São **cinco camadas**, por ordem:

| # | Camada | Conteúdo | Ferramentas típicas |
|---|--------|----------|---------------------|
| 1 | **Clips** | I2V estável, movimento simples | Geração (Veo, Kling, etc.) |
| 2 | **Retime** | Speed ramps, hold lento | After Effects, Resolve, Premiere |
| 3 | **Montagem** | Cortes, ritmo, música, SFX | Resolve (grátis), Premiere |
| 4 | **Gráficos** | Legendas, marcas, cartão, CTA | After Effects |
| 5 | **Finish** | Cor leve, níveis, loudness, export | Resolve, AE, ffmpeg |

---

## Pipeline recomendado (sem DaVinci Studio)

```
Geração I2V (clips longos, movimento constante)
    ↓
AE: Time Remap + Pixel Motion (só onde teste OK) → pre-render por plano
    ↓
Resolve GRÁTIS ou Premiere: montagem + cor leve + áudio
    ↓
(opcional) AE: legendas cinéticas + cartão → export final
```

Alternativa batch: scripts ffmpeg / montagem automática quando o projecto já tiver pipeline (`_montar_*.py`) — menos flexível nos ramps, zero dependência de NLE paga.

---

## Fase 1 · Geração (antes do retime)

| Prática | Porquê |
|---------|--------|
| Movimento **único e constante** numa direcção | Ramps aplicados em post; I2V não deve acelerar/desacelerar sozinho |
| Clips **mais longos** que o timeline final (ex.: 8–12 s source para 5–7 s final) | Ramps comem tempo; precisas de margem |
| **24 fps** (ou 30 fps) **consistente** em todo o projecto | Evita judder na montagem |
| Evitar orbit, zoom agressivo, pan >15% | Optical flow e I2V degradam |
| WC / espelhos: slide mínimo ou plano quase estático | Reflexos quebram interpolação |

---

## Fase 2 · Speed ramps e optical flow

### Modelo de ritmo (por divisão)

```
[RAMP IN rápido] → [HOLD lento] → [RAMP OUT rápido] → [CORTE seco]
     0,8–1,2 s         3,5–6 s          0,6–1,0 s         0–2 frames
```

- **Hero rooms** (sala, terraço, suíte): hold 5–6 s  
- **Secundárias** (detalhe cozinha, WC): hold 2,5–3,5 s  
- **Passagem** (corredor): hold 1,5–2,5 s  

### After Effects — Pixel Motion

1. `Layer → Time → Enable Time Remapping`
2. Keyframes no Time Remap (ease in/out)
3. `Layer → Frame Blending → Pixel Motion`
4. Preview a 100% nas **bordas, linhas rectas, espelhos**

**Pixel Motion** = interpolação por fluxo óptico nativa do AE: inventa frames intermédios analisando movimento de pixels. Alternativas mais fracas: Frame Mix (saltos), Frame Blend (embaciado).

### DaVinci Resolve (grátis ou Studio)

🔴 **Correcção (2026-08-07, verificado no Resolve do Miguel):** esta secção dizia que
optical flow era só no Studio. **É falso.** O **Retime Process** do Resolve **grátis** dá
`Nearest / Frame Blend / Optical Flow`. O que é exclusivo do Studio é o **Speed Warp**, que
é o modo neuronal dentro de Motion Estimation, não o optical flow clássico. Por causa desta
linha esteve-se a montar um round-trip para o After Effects que não era preciso.

- Retime por clip, em `Inspector → Retime and Scaling → Retime Process`
- **Optical Flow existe no Resolve grátis.** Dentro dele, `Motion Estimation` dá
  `Standard Faster / Standard Better / Enhanced Faster / Enhanced Better`; **`Speed Warp`
  é que pede Studio**
- Em arquitectura (rodapés, ombreiras, molduras) usar **Enhanced Better** — é o mais lento
  a render mas é onde as linhas rectas aguentam
- Onde optical flow está desaconselhado (espelhos, azulejo), baixar para **Frame Blend**,
  não desistir do ramp
- Motion blur vectorial nos trechos rápidos (Fusion) compensa perda de blur natural

### 🔴 "Error decoding full resolution media" no Resolve

Se o Resolve recusar um clip com *"Error decoding full resolution media for X at TC. Please
check that the file is accessible and has a valid codec"*, **o ficheiro costuma estar bom**.
Confirmar primeiro:

```bash
ffmpeg -v error -i CLIP.mp4 -f null -
```

Sem saída = descodifica limpo, e a mensagem está a mentir sobre a causa. A causa real é
quase sempre o **GOP**: os clips de Kling/Minimax vêm com **um único fotograma-chave no
ficheiro inteiro**. Ver com:

```bash
ffprobe -v error -select_streams v:0 -show_entries frame=key_frame -of csv=p=0 CLIP.mp4
```

Um só `1` para 121 fotogramas significa que mostrar o fotograma 100 obriga a descodificar
os 100 anteriores em cadeia. Em playback aguenta-se; **num retime com optical flow não**,
porque aí o Resolve salta entre fotogramas vizinhos. Daí o erro aparecer só depois do ramp,
e só a *full resolution*.

**Correcção, sem perda e sem partir o Relink:**

```bash
ffmpeg -y -i CLIP.mp4 -c:v libx264 -profile:v high -preset veryslow -qp 1 \
  -g 1 -bf 0 -pix_fmt yuv420p -an -movflags +faststart PASTA_NOVA/CLIP.mp4
```

- `-g 1 -bf 0` → todos os fotogramas independentes
- `-qp 1` → diferença máxima **2 níveis**, média 0,001; indistinguível
- **mesmo nome e mesma extensão** → Relink no Resolve mantém a timeline e os ramps
- o ficheiro engorda ~7× (9 MB → 62 MB); é o preço

🔴 **NÃO usar `-qp 0`.** Empurra o x264 para o perfil **High 4:4:4 Intra**, que o **Resolve
não abre**. Fica sem perda e ilegível. `-profile:v high -qp 1` fica em High normal e o
Resolve lê. Custou uma volta a descobrir.

⚠️ **Não pôr `-color_primaries/-color_trc/-colorspace` neste comando.** Com essas etiquetas
deixa de ser transparente: dá conversão de gama e mediu-se 9 níveis de diferença.

⚠️ **ProRes 422 HQ foi medido e perde mais:** 10 níveis de diferença e 90 MB para o mesmo
clip, além de obrigar a `.mov` e partir o Relink por nome.

⚠️ **DNxHR/ProRes seriam o óbvio, mas não entram em `.mp4`** (só `.mov`/`.mxf`), e mudar a
extensão parte o Relink por nome — ou seja, custa os ramps já feitos.

⚠️ **Converter só os clips que dão erro**, não o lote. Uma passagem a CRF 12 sobre o filme
todo mediu 35–37 dB de PSNR (3,6 a 4,2 níveis de diferença média), o que em paredes lisas
dá banding. Um clip de cada vez, sem perda.

### Quando usar optical flow / Pixel Motion

| Situação | Usar? |
|----------|-------|
| Ramp in/out rápido (250–400%) | ✅ Testar |
| Hold lento 60–70%, pan/dolly suave | ✅ Se teste limpo |
| Slow extremo (<40% durante muito tempo) | ⚠️ Só se preview OK |
| Plano estático, planta, cartão | ❌ |
| WC, espelhos, reflexos | ❌ |
| Texturas repetitivas (relva, grelhas, azulejos) | ⚠️ Alto risco de ghosting |
| Clips I2V com warp já visível | ❌ Amplifica artefactos |

**Regra empírica:** melhores resultados em **≥50% de velocidade**; quanto mais slow, mais frames inventados = mais risco.

### Quando NÃO usar

- Export final ou “master effect” na timeline inteira  
- Layers de legendas, logos, cartão (sem retime)  
- Áudio  
- Clips já fluidos a velocidade final  
- Quando Frame Blend ou clip regenerado mais lento fica mais limpo que warp  

### Se optical flow falhar

1. Reduzir agressividade do ramp  
2. Encurtar ramp; manter só a zona limpa do movimento  
3. Mudar para **Frame Blend**  
4. Regenerar I2V **mais lento** e usar ramps só na entrada/saída  
5. Aceitar ligeiro stutter — preferível a parede que “derrete”  

### Motion blur nos ramps rápidos

Trechos acelerados perdem blur natural da câmara. Adicionar motion blur (AE ou Fusion) **só na secção rápida** — não no hold lento. Keyframe blend 0→1→0 alinhado ao ramp.

---

## Fase 3 · Montagem

| Prática | Detalhe |
|---------|---------|
| **Cortes secos** entre divisões | Default; dissolves longos matam ritmo de ramps |
| **2–3 tipos** de transição no filme todo | Consistência (corte, whip ocasional, dip-to-white raro) |
| Transições **6–12 frames** em social | Snap sem whiplash |
| **SFX discretos** nos ramp out | Whoosh curto vende o movimento |
| Música: cortes alinhados a **downbeats** e ramp out | Ritmo unificado |
| Legendas **só no hold lento** | Entram ~0,3 s após ramp in; saem ~0,5 s antes do ramp out |

Ordem de percurso típica (imobiliário):

```
Exterior → Entrada → Social (sala, cozinha) → Corredor → Quartos → WCs → Exterior/terraço → Garagem → CTA
```

---

## Fase 4 · Gráficos e legendas

- Tipografia e marcas: preferir **After Effects** (controlo frame a frame, cinético)  
- Factos numéricos: **só de fonte verificada** do cliente (ficha, anúncio) — nunca inventar m², preço, certificados  
- Placa de localização / CTA: contraste legível; testar em telemóvel e ecrã grande  
- Pre-render gráficos com alpha; compor no NLE ou export comp final do AE  

---

## Fase 5 · Finish (master real)

Ordem **sem** optical flow global:

```
1. Correção por clip (exposição, white balance)
2. Grade leve consistente (Rec.709; restrição em imobiliário premium)
3. Match relativo entre divisões adjacentes (evitar sala laranja + quarto azul)
4. Composição gráficos / legendas (se ainda não baked)
5. Áudio: níveis, ducking leve se voz, limitador no master
6. Export único — sem re-interpolar frames no codec
```

### Cor

- Imobiliário: **cor contida** — compradores notam incoerência entre divisões mais do que LUT “cinematográfica”  
- Janelas: evitar exteriores completamente estourados num plano e correctos no seguinte  
- Rec.709 para entrega web unless client pede HDR  

### Áudio

| Destino | Alvo indicativo |
|---------|-----------------|
| Web / embed 16:9 | ~-16 LUFS integrated, true peak ≤ -1 dBTP |
| Reels / TikTok / Shorts | ~-14 LUFS; verificar música licenciada (biblioteca da plataforma ou track licenciada) |

### Export

| Campo | Valor típico |
|-------|----------------|
| Resolução | 1920×1080 (ou 1080×1920 reel) |
| Frame rate | 24 ou 30 fps (igual ao projecto) |
| Codec | H.264 ou H.265, alta qualidade |
| **Não** | Frame blending / optical flow no diálogo de export |
| **Não** | Segundo passo de interpolação sobre filme já retimed |

Resolve grátis: export 1080p suficiente. Limitações Studio (noise AI, alguns FX) raramente bloqueiam este tipo de entrega.

---

## Checklist QA antes de entregar

### Retime e imagem

- [ ] Cada ramp revisto **isolado** — sem warping em rodapés, janelas, molduras, espelhos  
- [ ] Pixel Motion / optical flow **por plano**, documentado sim/não  
- [ ] Nenhum “master optical flow” na timeline final  

### Montagem

- [ ] Ritmo coerente; sem planos mortos >1 s sem razão  
- [ ] Transições consistentes com o plano criativo  
- [ ] Legendas legíveis em telemóvel; não sobre UI de plataforma (zona central safe)  

### Cor e áudio

- [ ] White balance relativo consistente entre cortes adjacentes  
- [ ] Sem clipping de áudio; música não compete com SFX  
- [ ] Preview em **telefóne** e **ecrã grande** (artefactos AI aparecem mais no grande)  

### Conteúdo

- [ ] Todos os números e claims verificados na fonte do cliente  
- [ ] Marcas / disclaimers RE/MAX ou cliente conforme brief  
- [ ] Duração alvo atingida (±1 s)  

---

## Referência rápida · ferramenta por tarefa

| Tarefa | Melhor opção |
|--------|----------------|
| Legendas cinéticas, cartão, marcas | **After Effects** |
| Speed ramps + interpolação | **Resolve grátis** (Optical Flow → Enhanced Better); AE só se o Resolve falhar |
| Montagem, áudio, export 1080p | **Resolve grátis** ou Premiere |
| Color final leve | **Resolve grátis** (Color page) |
| Batch / repeatability | Scripts ffmpeg do projecto |

---

## Leitura externa (boas práticas)

- [Best Practices for Optical Flow Time Remapping (4K Shooters)](https://www.4kshooters.net/2015/12/11/best-practices-for-optical-flow-time-remapping-in-premiere-pro-cc/)  
- [Time Remapping in Premiere Pro (ViteLNK)](https://vitelnk.com/blog/time-remapping-in-premiere-pro)  
- [Speed Ramps in DaVinci for Real Estate (Cole Connor)](https://coleconnor.com/da-vinci-resolve-speed-ramps-real-estate-video/)  
- [Real Estate Reel Transitions (Peachgum)](https://www.peachgum.ai/blog/real-estate-reel-transitions-smooth-listing-edits)  
- [Video Editing for Real Estate (Blurit)](https://www.blurit.app/en/blog/video-editing-real-estate-guide/)  

---

## Relação com outros docs OpenMontage

| Documento | Uso |
|-----------|-----|
| `AGENT_GUIDE.md` | Routing e pipelines |
| `ESTILO-CLIENTE.md` (por cliente) | Tipografia, marcas, legendas locked |
| `DADOS-IMOVEL.md` (por cliente) | Factos permitidos em ecrã |
| `PLANO-VIDEO-*.md` (por peça) | Guião, planos, durações |

Este ficheiro é **transversal** — não substitui brief de cliente nem plano de uma peça específica.

---

*OpenMontage · guia genérico de masterização · imobiliário / I2V / speed ramps*
