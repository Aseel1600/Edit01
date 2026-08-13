import { AbsoluteFill, Easing, interpolate, useCurrentFrame, useVideoConfig } from "remotion";

/**
 * Legenda informativa · estética imobiliária premium e minimalista.
 *
 * Um único componente serve todas as legendas: o conteúdo, o alinhamento e os
 * tempos vêm de um array de dados, não de componentes diferentes por legenda.
 *
 * Tudo é desenhado em HTML/CSS pelo Remotion. Não há PNG, SVG nem pré-render,
 * e por isso o `backdrop-filter: blur(6px)` desfoca mesmo o vídeo por baixo, que
 * é o que a especificação pede.
 *
 * ⚠️ Nada de animações CSS, estados ou temporizadores: cada fotograma é uma função
 * pura de `useCurrentFrame()`, senão o render em paralelo do Remotion produz
 * fotogramas inconsistentes.
 */

/** Especificação a 1080p. Tudo escala por `height / 1080`. */
const REF_HEIGHT = 1080;
const IN_FRAMES = 14;
const OUT_FRAMES = 14;
const RISE_PX = 14;

const SAND = "#D8B27D";
const WARM_WHITE = "#FFFDF8";

export interface PropertyLabelSpec {
  /** primeiro fotograma em que a legenda aparece (inclusive) */
  start: number;
  /** último fotograma em que a legenda aparece (inclusive) */
  end: number;
  /** linha superior, desenhada em caixa alta */
  eyebrow?: string;
  /** linha principal */
  title: string;
  /** encostar à esquerda ou à direita, conforme o espaço livre da imagem */
  align?: "left" | "right";
}

export const PropertyLabels: React.FC<{ labels: PropertyLabelSpec[] }> = ({ labels }) => {
  const frame = useCurrentFrame();
  return (
    <>
      {labels.map((spec, i) => (
        <PropertyLabel key={`${spec.title}-${i}`} spec={spec} frame={frame} />
      ))}
    </>
  );
};

const PropertyLabel: React.FC<{ spec: PropertyLabelSpec; frame: number }> = ({ spec, frame }) => {
  const { height } = useVideoConfig();

  // ⚠️ Fora do intervalo devolve `null` ANTES de qualquer cálculo: assim só a
  // legenda activa é montada, e não há caixas invisíveis a pesar no render.
  if (frame < spec.start || frame > spec.end) return null;

  const local = frame - spec.start;
  const span = spec.end - spec.start;

  // entrada: 0 -> 1 em ease-out cubic. saída: 1 -> 0 em ease-in quadratic.
  const fadeIn = interpolate(local, [0, IN_FRAMES], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  const fadeOut = interpolate(local, [span - OUT_FRAMES, span], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.in(Easing.quad),
  });
  const opacity = Math.min(fadeIn, fadeOut);

  // o deslocamento só acontece à entrada, e usa a mesma cúbica da opacidade
  const s = height / REF_HEIGHT;
  const rise = interpolate(local, [0, IN_FRAMES], [RISE_PX * s, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  const alignRight = spec.align === "right";

  return (
    <AbsoluteFill
      style={{
        // ⚠️ o alinhamento é feito pelo flex e não por `left`/`right` fixos: a
        // caixa tem largura automática pelo conteúdo, e assim encosta ao lado
        // certo sem se saber a largura de antemão
        justifyContent: "flex-end",
        alignItems: alignRight ? "flex-end" : "flex-start",
        paddingLeft: 88 * s,
        paddingRight: 88 * s,
        paddingBottom: 82 * s,
        pointerEvents: "none",
      }}
    >
      <div
        style={{
          display: "flex",
          opacity,
          transform: `translateY(${rise}px)`,
          backgroundColor: "rgba(16, 22, 21, 0.74)",
          backdropFilter: `blur(${6 * s}px)`,
          WebkitBackdropFilter: `blur(${6 * s}px)`,
          boxShadow: `0 ${8 * s}px ${22 * s}px rgba(0, 0, 0, 0.20)`,
          borderRadius: 0,
          border: "none",
        }}
      >
        {/* barra lateral esquerda, areia */}
        <div style={{ width: 4 * s, backgroundColor: SAND, flexShrink: 0 }} />
        <div
          style={{
            padding: `${19 * s}px ${26 * s}px ${18 * s}px ${24 * s}px`,
            display: "flex",
            flexDirection: "column",
          }}
        >
          {spec.eyebrow ? (
            <div
              style={{
                fontFamily: "Arial, Helvetica, sans-serif",
                fontSize: 18 * s,
                fontWeight: 700,
                textTransform: "uppercase",
                letterSpacing: 3.5 * s,
                color: SAND,
                lineHeight: 1,
                // ⚠️ o tracking acrescenta espaço DEPOIS da última letra e
                // desequilibrava o padding da direita; compensa-se aqui
                marginRight: -3.5 * s,
                marginBottom: 7 * s,
                whiteSpace: "nowrap",
              }}
            >
              {spec.eyebrow}
            </div>
          ) : null}
          <div
            style={{
              fontFamily: "Arial, Helvetica, sans-serif",
              fontSize: 37 * s,
              fontWeight: 500,
              letterSpacing: -0.8 * s,
              color: WARM_WHITE,
              lineHeight: 1,
              whiteSpace: "nowrap",
            }}
          >
            {spec.title}
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

export default PropertyLabels;
