import React from "react";
import { loadFont } from "@remotion/google-fonts/SpaceGrotesk";
import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { AbsoluteFill, Audio, Img, OffthreadVideo, Sequence, staticFile } from "remotion";
import { PropertyLabels, PropertyLabelSpec } from "../components/PropertyLabel";

/**
 * Paulo Martins / T4 em Esmoriz · peca normal, VERSAO 2.
 *
 * O mesmo filme que o `_build_video.py` monta em ffmpeg: os mesmos 9 clips da casa
 * vazia, a mesma ordem, as mesmas duracoes, as mesmas transicoes, a mesma musica.
 * **So mudam as legendas**, que passam da barra coral + `drawtext` para o sistema em
 * `components/PropertyLabel.tsx`.
 *
 * ⚠️ **Porque e Remotion e nao ffmpeg.** As legendas novas tem desfoque do fundo e
 * rampas com curvas de aceleracao. Em ffmpeg isso obriga a recortar a regiao,
 * `boxblur`, tingir e recompor, e as curvas so se fazem em `geq`, avaliado pixel a
 * pixel por fotograma: com seis legendas a 1080p o render escrevia a 4,3 KB/s, ou
 * seja horas por peca. Aqui o desfoque e `backdrop-filter` e as curvas sao
 * `interpolate` com `Easing`.
 *
 * ⚠️ As legendas ficam FORA do `TransitionSeries`, como irmas dele. Dentro de uma
 * `Sequence` o `useCurrentFrame()` seria rebaseado ao inicio dessa sequencia e os
 * tempos absolutos deixavam de bater.
 *
 * ⚠️ Os clips trazem audio gerado (um deles fala ingles) e vao todos com `muted`.
 */
const { fontFamily: GROTESK } = loadFont();

const H = 1080;
const ESC = H / 1080;

const CORAL = "#FF6B4A";      // marca ShowingReel: o cliente nao tem cor propria
const AREIA = "#8FABBD";      // filete do cartao final, o mesmo do build em ffmpeg

/** duracao de cada plano em fotogramas, na ordem do filme */
const SHOTS: { src: string; frames: number }[] = [
  { src: "paulo/clip-01.mp4", frames: 106 },   // open space, abre a peca
  { src: "paulo/clip-02.mp4", frames: 106 },   // cozinha e ilha
  { src: "paulo/clip-03.mp4", frames: 96 },    // garagem
  { src: "paulo/clip-04.mp4", frames: 110 },   // escada
  { src: "paulo/clip-05.mp4", frames: 120 },   // quarto com roupeiro
  { src: "paulo/clip-06.mp4", frames: 110 },   // quarto com porta
  { src: "paulo/clip-07.mp4", frames: 115 },   // quarto com janela
  { src: "paulo/clip-08.mp4", frames: 96 },    // casa de banho
  { src: "paulo/clip-09.mp4", frames: 130 },   // terraco, fecha a peca
];

/**
 * Transicao QUE ENTRA em cada plano. As duas da garagem sao mais longas: e o unico
 * plano cinzento e frio no meio de interiores brancos, e a mudanca de cor salta com
 * o fundido normal.
 */
const TRANS_IN = [0, 17, 24, 24, 17, 17, 17, 17, 17];
const CARD_TRANS = 19;
const CARD_FRAMES = 96;

/** primeiro fotograma de cada plano no filme */
const shotStarts = SHOTS.reduce<number[]>((acc, _, i) => {
  acc.push(i === 0 ? 0 : acc[i - 1] + SHOTS[i - 1].frames - TRANS_IN[i]);
  return acc;
}, []);

/** fotograma em que o cartao final comeca a entrar */
const CARD_IN =
  shotStarts[SHOTS.length - 1] + SHOTS[SHOTS.length - 1].frames - CARD_TRANS;

export const TOTAL_FRAMES = CARD_IN + CARD_FRAMES;

/**
 * Legenda de um plano: entra 6 fotogramas depois de ele aparecer e sai antes da
 * transicao seguinte, para nunca haver duas legendas ao mesmo tempo.
 */
const label = (
  i: number,
  eyebrow: string | undefined,
  title: string,
  align: "left" | "right",
): PropertyLabelSpec => ({
  start: shotStarts[i] + 6,
  end: shotStarts[i] + SHOTS[i].frames - (TRANS_IN[i + 1] ?? CARD_TRANS) - 2,
  eyebrow,
  title,
  align,
});

// o lado escolhe-se para nao tapar o motivo de cada plano, nao por alternar
const LABELS: PropertyLabelSpec[] = [
  label(0, "T4 · Esmoriz", "208 m² de área bruta", "left"),   // a ilha fica a direita
  label(1, "Interior", "Sala e cozinha em open space", "left"),
  label(2, undefined, "Garagem", "left"),
  label(3, undefined, "Dois pisos", "right"),                 // a escada sobe pela esquerda
  label(4, "Quartos", "Roupeiro embutido", "left"),
  label(8, "Exterior", "Terraço com guarda de vidro", "left"),
];

const ClipScene: React.FC<{ src: string }> = ({ src }) => (
  <AbsoluteFill>
    <OffthreadVideo
      src={staticFile(src)}
      muted
      style={{ width: "100%", height: "100%", objectFit: "cover" }}
    />
  </AbsoluteFill>
);

const EndCard: React.FC = () => (
  <AbsoluteFill
    style={{
      backgroundColor: "#F5F5F5",
      alignItems: "center",
      justifyContent: "center",
      fontFamily: GROTESK,
    }}
  >
    <div style={{ fontSize: 92 * ESC, fontWeight: 700, color: "#282624", letterSpacing: -1 }}>
      T4 · Esmoriz
    </div>
    <div style={{ fontSize: 34 * ESC, color: "#696662", marginTop: 26 * ESC }}>
      208 m² de área bruta
    </div>
    <div
      style={{
        width: 300 * ESC,
        height: 2,
        backgroundColor: AREIA,
        marginTop: 60 * ESC,
        marginBottom: 60 * ESC,
      }}
    />
    <Img src={staticFile("paulo/lockup_escuro.png")} style={{ width: 260 * ESC }} />
    <AbsoluteFill style={{ justifyContent: "flex-end" }}>
      <div style={{ height: 8 * ESC, backgroundColor: CORAL }} />
    </AbsoluteFill>
  </AbsoluteFill>
);

export const PauloMartinsCinematicoV2: React.FC = () => (
  <AbsoluteFill style={{ backgroundColor: "black" }}>
    <TransitionSeries>
      {SHOTS.flatMap((shot, i) => [
        ...(i === 0
          ? []
          : [
              <TransitionSeries.Transition
                key={`t-${i}`}
                presentation={fade()}
                timing={linearTiming({ durationInFrames: TRANS_IN[i] })}
              />,
            ]),
        <TransitionSeries.Sequence key={`s-${i}`} durationInFrames={shot.frames}>
          <ClipScene src={shot.src} />
        </TransitionSeries.Sequence>,
      ])}
      <TransitionSeries.Transition
        presentation={fade()}
        timing={linearTiming({ durationInFrames: CARD_TRANS })}
      />
      <TransitionSeries.Sequence durationInFrames={CARD_FRAMES}>
        <EndCard />
      </TransitionSeries.Sequence>
    </TransitionSeries>

    {/* ⚠️ irmas do TransitionSeries, para o frame nao ser rebaseado */}
    <PropertyLabels labels={LABELS} />

    {/* ⚠️ marca e aviso saem ANTES do cartao final, que tem marca propria; a
        `Sequence` corta-os no fotograma certo sem precisar de contas por dentro */}
    <Sequence from={0} durationInFrames={CARD_IN} layout="none">
      <AbsoluteFill>
        <Img
          src={staticFile("paulo/sr_credit.png")}
          style={{
            position: "absolute",
            left: 46 * ESC,
            top: 43 * ESC,
            height: 54 * ESC,
            opacity: 0.95,
          }}
        />
      </AbsoluteFill>
      <AbsoluteFill style={{ justifyContent: "flex-end", alignItems: "center" }}>
        <div
          style={{
            fontFamily: GROTESK,
            fontSize: 22 * ESC,
            color: "rgba(255,255,255,0.92)",
            textShadow: "0 0 4px rgba(0,0,0,0.65), 0 1px 2px rgba(0,0,0,0.85)",
            marginBottom: 32 * ESC,
          }}
        >
          Animações geradas com IA a partir das fotografias do imóvel
        </div>
      </AbsoluteFill>
    </Sequence>

    <Audio src={staticFile("paulo/music.mp3")} volume={0.85} />
  </AbsoluteFill>
);

export default PauloMartinsCinematicoV2;
