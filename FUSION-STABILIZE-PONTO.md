# Fusion — estabilizar tremor com um ponto (lock)

Truque para eliminar micro-tremor / handheld: trackear **um ponto fixo na cena** e fazer Match Move em Background Only. O plano fica “colado” a esse ponto (efeito tripé / locked-on).

Complementa [`MASTERING.md`](MASTERING.md) e [`SPEED-RAMPS.md`](SPEED-RAMPS.md). Estabiliza **antes** de ramps agressivos ou optical flow quando o judder vem de shake.

Referência rápida YouTube: [LOCK Stabilize in 30 Seconds](https://www.youtube.com/watch?v=bDeCjPOsbkg).

---

## Quando usar

| Situação | Este método? |
|----------|----------------|
| Micro-tremor / handheld leve | ✅ Ideal |
| Queres um ponto da arquitectura **duro** (canto de janela, parafuso) | ✅ |
| Dolly / push intencional que queres manter | ⚠️ Só se o ponto for estático no mundo; o movimento de câmara “bom” também pode ser anulado |
| Tremor forte + rotação/escala | Preferir **Planar Tracker → Stabilize** (secção abaixo) |
| Clip I2V já com morph | ⚠️ Pode piorar bordas; testa A/B |

---

## Passo a passo (Tracker · 1 ponto)

1. Na **Edit**, playhead em cima do clip → página **Fusion**  
   (`MediaIn1` → `MediaOut1`)
2. `Ctrl + Space` ou `Shift + Space` → escreve **Tracker** → Enter  
   (nó entre MediaIn e MediaOut)
3. No viewer, arrasta o **quadrado do tracker** para um ponto de **alto contraste** que **não se mexa no mundo**:
   - canto de janela, interseção de parede/rodapé, parafuso, aresta de móvel fixo  
   - **não** pessoas, folhas, reflexos, carros
4. (Opcional) Adaptive Mode → **Best Match**; alarga a search box se o track falhar
5. Clica **Track Forward** (▶) no Inspector do Tracker  
   Se perder o ponto a meio: corrige posição nesse frame e continua, ou track Backward a partir do meio
6. No Inspector do Tracker:
   - **Operation** → **Match Move**
   - **Merge** → **Background Only**
7. Volta à **Edit** → play — o tremor nesse ponto deve desaparecer
8. Bordas pretas / vazias → **Zoom** ligeiro (~1.05–1.15) no Transform do clip (Edit Inspector) ou nó **Transform** no Fusion até tapar as margens

---

## Escolher o ponto (checklist)

- [ ] Contraste alto (aresta clara/escura)
- [ ] Visível durante **quase todo** o clip
- [ ] Objecto/arquitectura **fixos** (não parallax de algo perto se o fundo deve ficar estável — em RE costuma ser canto de parede/janela)
- [ ] Longe de zonas que o optical flow / I2V já “derrete”

---

## Alternativa: Planar Tracker (área)

Quando um ponto não chega (rotação, escala, superfície):

1. Fusion → **Planar Tracker** entre MediaIn e MediaOut  
2. Operation Mode **Track** → desenha polígono numa superfície plana  
3. **Set** no frame de referência → Track Forward / Backward  
4. Operation Mode → **Stabilize** → desliga Rotation/Scale se só quiseres XY  
5. **Compute Stabilization**  
6. Zoom para tapar bordas  

Vídeo útil: *How to Stabilize Footage in Fusion (DaVinci Resolve 20)* e guias Planar Stabilize.

---

## Ordem na pipeline

```
Clip com tremor
  → Fusion Tracker lock (este doc)  OU  Planar Stabilize
  → (opcional) pré-interp 48 fps / Optical Flow
  → Speed ramps
  → Grade / finish
```

Não estabilizes **depois** de um TimeStretcher / ramp complexo sem testar — o track pode ficar dessincronizado. Preferir estabilizar no footage “limpo”, depois retime.

---

## Anti-padrões

1. Trackear um objecto que se move → o vídeo “cola-se” ao objecto.  
2. Zoom excessivo a tapar bordas → perde resolução / crop agressivo.  
3. Usar isto para “salvar” I2V com warp geométrico — não é o remédio certo.  
4. Confundir com **Camera Tracker** (esse é para 3D / legendas no espaço, não para lock 2D simples).

---

## Relação com outros docs

| Doc | Uso |
|-----|-----|
| [`FUSION-LEGENDAS-169.md`](projects/video-service-business/clients/Mario%20Garces/T4%20Lumiar%20-%20Quinta%20dos%20Alcoutins/_davinci/FUSION-LEGENDAS-169.md) | Camera Tracker 3D para texto (outro fluxo) |
| [`MOTION-FLUIDEZ.md`](projects/video-service-business/clients/Mario%20Garces/T4%20Lumiar%20-%20Quinta%20dos%20Alcoutins/_davinci/MOTION-FLUIDEZ.md) | Judder de slow 24 fps (não é shake) |
| [`SPEED-RAMPS.md`](SPEED-RAMPS.md) | Retime depois da estabilização |

---

*Guardado para reutilizar em produção Resolve / Fusion.*
