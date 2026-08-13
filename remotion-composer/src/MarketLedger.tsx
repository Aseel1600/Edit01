import React from "react";
import {
  AbsoluteFill,
  Audio,
  Easing,
  Img,
  OffthreadVideo,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
  CalculateMetadataFunction,
} from "remotion";

// ---------------------------------------------------------------------------
// MarketLedger — bespoke "atelier" editorial market-brief composition.
// Parameterized for any market/language: all copy, currency, accent, and the
// insight scene are prop-driven (defaults reproduce the approved Columbus clip).
// ---------------------------------------------------------------------------

export interface MarketLedgerProps {
  data: {
    accent: string; // brand accent (gold US / azure PT / ...)
    location: string;
    period: string;
    masthead: string; // e.g. "MARKET BRIEF" / "BOLETIM DE MERCADO"
    hookLine1: string;
    hookLine2: string;
    hookSub: string;
    statLabel: string;
    statValue: number;
    statPrefix: string; // "$" / ""
    statSuffix: string; // "" / " €/m²"
    statGroup: string; // thousands separator: "," / " "
    yoy: string; // "+1.2%" / "+5,8%"
    yoyLabel: string; // "YEAR OVER YEAR" / "HOMÓLOGO"
    chartTitle: string;
    chart: { m: string; v: number }[];
    chartYMin?: number | null;
    insightLabel: string;
    insightValue: number | null; // count-up number, or null → use insightDisplay
    insightDisplay: string | null; // shown directly (e.g. "8,9%") when no count-up
    insightSuffix: string;
    insightDelta: string;
    insightCaption: string;
    insightTally: number | null; // tally-mark row count, or null to skip
    ctaTagline: string;
    brand: string;
    handle: string;
    sourceNote: string;
    // Optional client logo (path under remotion-composer/public). Stacked lockups
    // must scale by HEIGHT, so logoHeight drives the size and width stays auto.
    logo?: string | null;
    logoHeight?: number | null;
    // PREMIUM tier: play footage behind the data (e.g. the agent walking a home).
    // A scrim goes over it so the numbers stay readable; scrimOpacity tunes how
    // hard the footage is knocked back (0.55 default reads well over bright rooms).
    backgroundVideo?: string | null;
    scrimOpacity?: number | null;
    // PREMIUM presenter layout: the agent stands in the right third of the
    // footage, so the data is scaled down into a free column on the LEFT rather
    // than sitting across her face. Only meaningful with backgroundVideo.
    presenter?: boolean | null;
    // Held end card: contact lines under the logo (phone, email, agency).
    ctaContact?: string[] | null;
    // AI disclosure. Required whenever a real person's likeness is recreated —
    // it protects the person on screen, so it stays legible but never shouts.
    aiNote?: string | null;
    // Optional SECOND chart (e.g. two-market pieces like Almada + Seixal).
    // When present it takes over the insight window and inherits insightCaption;
    // the big-number insight panel is skipped.
    chart2?: { m: string; v: number }[] | null;
    chart2Title?: string | null;
    chart2YMin?: number | null;
    // Temas SEM números: uma lista ocupa a janela do gráfico (list) e/ou a do
    // destaque (list2). Quando presente, ganha ao gráfico dessa janela.
    list?: ListItem[] | null;
    listTitle?: string | null;
    list2?: ListItem[] | null;
    list2Title?: string | null;
  };
  sections: Record<string, [number, number]>;
  captions: { word: string; startMs: number; endMs: number }[];
  audio: { narration: string; music: string };
}

const INK = "#0B0F17";
const INK2 = "#0E1420";
const IVORY = "#F3ECDD";
const GREEN = "#63D39A";
const MUTED = "#8A93A5";
// Presenter mode shrinks every scene to 53%, so MUTED grey on footage stops
// reading. Small labels get this instead: same quiet role, enough contrast.
const LABEL = "rgba(243,236,221,0.82)";
const HAIR = "rgba(243,236,221,0.13)";
const DISPLAY = "Bahnschrift, 'DIN Condensed', 'Segoe UI', sans-serif";
const SERIF = "Georgia, 'Times New Roman', serif";
const CAPTION_FONT = "'Segoe UI', Arial, system-ui, sans-serif";

const ease = Easing.out(Easing.cubic);

export const calculateMarketLedgerMetadata: CalculateMetadataFunction<
  MarketLedgerProps
> = async ({ props }) => {
  const ends = Object.values(props.sections || {}).map((s) => s[1]);
  const last = ends.length ? Math.max(...ends) : 33;
  return { durationInFrames: Math.ceil((last + 0.6) * 30) };
};

const group = (n: number, sep: string) =>
  Math.round(n).toString().replace(/\B(?=(\d{3})+(?!\d))/g, sep);

const envelope = (
  frame: number,
  fps: number,
  win: [number, number],
  fade = 0.45
) => {
  const [a, b] = [win[0] * fps, win[1] * fps];
  return interpolate(
    frame,
    [a, a + fade * fps, b - fade * fps, b],
    [0, 1, 1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: ease }
  );
};

// -------------------------------------------------------------- backdrop
const Backdrop: React.FC<{ accent: string }> = ({ accent }) => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();
  const drift = interpolate(frame, [0, 1000], [0, 60]);
  const cols = 7;
  const rows = 13;
  return (
    <AbsoluteFill>
      <AbsoluteFill
        style={{ background: `linear-gradient(160deg, ${INK2} 0%, ${INK} 55%, #070A10 100%)` }}
      />
      <AbsoluteFill
        style={{
          background: `radial-gradient(46% 32% at ${28 + drift * 0.2}% 22%, ${accent}26, transparent 60%), radial-gradient(50% 40% at 82% 96%, rgba(99,211,154,0.10), transparent 60%)`,
        }}
      />
      <svg width={width} height={height} style={{ position: "absolute", inset: 0 }}>
        {Array.from({ length: cols + 1 }).map((_, i) => (
          <line key={"v" + i} x1={(width / cols) * i} y1={0} x2={(width / cols) * i} y2={height} stroke={HAIR} strokeWidth={1} />
        ))}
        {Array.from({ length: rows + 1 }).map((_, i) => (
          <line key={"h" + i} x1={0} y1={(height / rows) * i} x2={width} y2={(height / rows) * i} stroke={HAIR} strokeWidth={1} />
        ))}
      </svg>
      <AbsoluteFill style={{ boxShadow: "inset 0 0 320px rgba(0,0,0,0.65)" }} />
    </AbsoluteFill>
  );
};

// -------------------------------------------------------------- masthead
const Masthead: React.FC<{ label: string; location: string; period: string; accent: string }> = ({
  label, location, period, accent,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const w = interpolate(frame, [8, 34], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: ease });
  const blink = Math.sin((frame / fps) * Math.PI * 2) > -0.2 ? 1 : 0.25;
  return (
    <div style={{ position: "absolute", top: 92, left: 84, right: 84 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", fontFamily: DISPLAY, letterSpacing: "0.28em", fontSize: 26, color: IVORY, fontWeight: 600 }}>
        <span style={{ display: "flex", alignItems: "center", gap: 14 }}>
          <span style={{ width: 12, height: 12, borderRadius: "50%", background: accent, opacity: blink, boxShadow: `0 0 16px ${accent}` }} />
          {label}
        </span>
        <span style={{ color: MUTED, letterSpacing: "0.24em" }}>{period}</span>
      </div>
      <div style={{ height: 2, background: `linear-gradient(90deg, ${accent}, ${HAIR})`, transform: `scaleX(${w})`, transformOrigin: "left", marginTop: 20 }} />
      <div style={{ fontFamily: DISPLAY, letterSpacing: "0.2em", fontSize: 30, color: MUTED, marginTop: 16, opacity: w, fontWeight: 600 }}>{location}</div>
    </div>
  );
};

// -------------------------------------------------------------- HOOK
const SceneHook: React.FC<{ win: [number, number]; line1: string; line2: string; sub: string; accent: string; dense?: boolean }> = ({
  win, line1, line2, sub, accent, dense,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const op = envelope(frame, fps, win);
  const s = win[0] * fps;
  const clip = interpolate(frame, [s + 8, s + 40], [100, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: ease });
  const clip2 = interpolate(frame, [s + 26, s + 56], [100, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: ease });
  return (
    <div style={{ position: "absolute", left: 84, right: 84, top: 720, opacity: op }}>
      <div style={{ fontFamily: DISPLAY, fontWeight: 700, fontSize: 138, lineHeight: 0.92, color: IVORY, letterSpacing: "-0.02em" }}>
        <div style={{ clipPath: `inset(0 ${clip}% 0 0)` }}>{line1}</div>
        <div style={{ clipPath: `inset(0 ${clip2}% 0 0)`, color: accent }}>{line2}</div>
      </div>
      <div style={{ fontFamily: SERIF, fontStyle: "italic", fontSize: dense ? 64 : 40, color: dense ? LABEL : MUTED, marginTop: 30, opacity: interpolate(frame, [s + 50, s + 70], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) }}>{sub}</div>
    </div>
  );
};

// -------------------------------------------------------------- STAT
const SceneStat: React.FC<{
  win: [number, number]; label: string; value: number; prefix: string; suffix: string; grp: string; yoy: string; yoyLabel: string; accent: string; dense?: boolean;
}> = ({ win, label, value, prefix, suffix, grp, yoy, yoyLabel, accent, dense }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const op = envelope(frame, fps, win);
  const s = win[0] * fps;
  const count = interpolate(frame, [s + 8, s + 52], [0, value], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.quad) });
  const rule = interpolate(frame, [s + 40, s + 66], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: ease });
  const tag = interpolate(frame, [s + 54, s + 72], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: ease });
  return (
    <div style={{ position: "absolute", left: 84, right: 84, top: 700, opacity: op }}>
      <div style={{ fontFamily: DISPLAY, letterSpacing: dense ? "0.2em" : "0.26em", fontSize: dense ? 42 : 30, color: dense ? LABEL : MUTED, fontWeight: 600, marginBottom: 30 }}>{label}</div>
      <div style={{ fontFamily: DISPLAY, fontWeight: 700, fontSize: 200, lineHeight: 0.9, color: IVORY, letterSpacing: "-0.03em", fontVariantNumeric: "tabular-nums" }}>
        {prefix}{group(count, grp)}{suffix}
      </div>
      <div style={{ height: 3, width: "100%", background: `linear-gradient(90deg, ${accent}, ${HAIR})`, transform: `scaleX(${rule})`, transformOrigin: "left", marginTop: 26 }} />
      <div style={{ display: "flex", alignItems: "center", gap: 16, marginTop: 34, opacity: tag, transform: `translateY(${(1 - tag) * 18}px)` }}>
        <span style={{ fontFamily: DISPLAY, fontWeight: 700, fontSize: 46, color: INK, background: GREEN, padding: "6px 20px", letterSpacing: "0.02em" }}>▲ {yoy}</span>
        <span style={{ fontFamily: DISPLAY, fontSize: dense ? 46 : 38, color: dense ? LABEL : MUTED, letterSpacing: "0.1em" }}>{yoyLabel}</span>
      </div>
    </div>
  );
};

// -------------------------------------------------------------- CHART
const SceneChart: React.FC<{
  win: [number, number]; title: string; chart: { m: string; v: number }[]; accent: string; yMin?: number | null; dense?: boolean;
  /** Optional serif caption under the chart — used when a chart occupies the insight window. */
  caption?: string | null;
  /** Unique gradient id so two charts in one composition don't share defs. */
  gradId?: string;
}> = ({ win, title, chart, accent, yMin, dense, caption, gradId = "ml-area" }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const op = envelope(frame, fps, win);
  // A bigger pad in presenter mode keeps the first/last value labels off the
  // frame edge — at 53% they were sitting ~10px from it.
  const W = 912, H = 520, pad = dense ? 92 : 8;
  const vals = chart.map((c) => c.v);
  // yMin (e.g. 0) keeps small real changes looking small — auto-scaling a +1% move
  // into a steep climb would misrepresent the data.
  const min = yMin != null ? yMin : Math.min(...vals) - 12;
  // With a y-floor the line rides near the top, so give the value labels
  // proportional headroom. Auto-scaled charts keep their original padding.
  const peak = Math.max(...vals);
  const max = yMin != null ? peak + (peak - min) * 0.18 : peak + 12;
  const x = (i: number) => pad + (i * (W - pad * 2)) / (chart.length - 1);
  const y = (v: number) => H - pad - ((v - min) / (max - min)) * (H - pad * 2);
  const pts = chart.map((c, i) => [x(i), y(c.v)] as [number, number]);
  const linePath = "M " + pts.map((p) => `${p[0].toFixed(1)} ${p[1].toFixed(1)}`).join(" L ");
  const areaPath = linePath + ` L ${x(chart.length - 1)} ${H - pad} L ${x(0)} ${H - pad} Z`;
  const draw = interpolate(frame, [win[0] * fps + 14, win[0] * fps + 74], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: ease });
  const areaOp = interpolate(frame, [win[0] * fps + 44, win[0] * fps + 78], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const s = win[0] * fps;
  return (
    <div style={{ position: "absolute", left: 84, right: 84, top: 690, opacity: op }}>
      {/* Presenter mode scales this whole scene down, so the dark-gold title and
          the muted month labels stop reading. Lift them when packed. */}
      <div style={{ fontFamily: DISPLAY, letterSpacing: "0.26em", fontSize: dense ? 38 : 30, color: dense ? IVORY : accent, fontWeight: 600, marginBottom: 22 }}>{title}</div>
      <svg width={W} height={H} style={{ overflow: "visible" }}>
        <defs>
          <linearGradient id={gradId} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={accent} stopOpacity={0.32} />
            <stop offset="100%" stopColor={accent} stopOpacity={0} />
          </linearGradient>
        </defs>
        <line x1={pad} y1={H - pad} x2={W - pad} y2={H - pad} stroke={HAIR} strokeWidth={1.5} />
        <path d={areaPath} fill={`url(#${gradId})`} opacity={areaOp} />
        <path d={linePath} fill="none" stroke={accent} strokeWidth={dense ? 8 : 5} strokeLinecap="round" strokeLinejoin="round" pathLength={1} strokeDasharray={1} strokeDashoffset={draw} />
        {pts.map((p, i) => {
          const appear = interpolate(frame, [s + 20 + i * 14, s + 34 + i * 14], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: ease });
          const isLast = i === pts.length - 1;
          return (
            <g key={i} opacity={appear}>
              <circle cx={p[0]} cy={p[1]} r={isLast ? 12 : 7} fill={isLast ? GREEN : IVORY} stroke={INK} strokeWidth={3} />
              <text x={p[0]} y={p[1] - 30} fill={isLast ? GREEN : IVORY} fontFamily={DISPLAY} fontWeight={700} fontSize={dense ? (isLast ? 76 : 66) : (isLast ? 52 : 40)} textAnchor="middle" style={{ fontVariantNumeric: "tabular-nums" }}>{chart[i].v}</text>
              <text x={p[0]} y={H + 46} fill={dense ? "rgba(243,236,221,0.78)" : MUTED} fontFamily={DISPLAY} fontSize={dense ? 48 : 30} letterSpacing="0.12em" textAnchor="middle">{chart[i].m}</text>
            </g>
          );
        })}
      </svg>
      {caption && (
        // Os rótulos dos meses vivem FORA da caixa do svg (y = H + 46, overflow
        // visible), por isso a margem tem de os saltar ou a legenda cola-se-lhes.
        <div style={{ fontFamily: SERIF, fontStyle: "italic", fontSize: dense ? 62 : 44, color: IVORY, marginTop: dense ? 170 : 90, opacity: interpolate(frame, [s + 70, s + 94], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) }}>{caption}</div>
      )}
    </div>
  );
};

// -------------------------------------------------------------- INSIGHT
const SceneInsight: React.FC<{
  win: [number, number]; label: string; value: number | null; display: string | null; suffix: string; delta: string; caption: string; tally: number | null; accent: string; dense?: boolean;
}> = ({ win, label, value, display, suffix, delta, caption, tally, accent, dense }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const op = envelope(frame, fps, win);
  const s = win[0] * fps;
  const bigOpacity = interpolate(frame, [s + 6, s + 30], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: ease });
  const big =
    display != null
      ? display
      : String(Math.round(interpolate(frame, [s + 8, s + 40], [0, value ?? 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.quad) }))) + suffix;
  return (
    <div style={{ position: "absolute", left: 84, right: 84, top: 700, opacity: op }}>
      <div style={{ fontFamily: DISPLAY, letterSpacing: dense ? "0.2em" : "0.26em", fontSize: dense ? 42 : 30, color: dense ? LABEL : MUTED, fontWeight: 600, marginBottom: 24 }}>{label}</div>
      <div style={{ display: "flex", alignItems: "baseline", gap: 30 }}>
        <div style={{ fontFamily: DISPLAY, fontWeight: 700, fontSize: 260, lineHeight: 0.86, color: IVORY, letterSpacing: "-0.03em", fontVariantNumeric: "tabular-nums", opacity: display != null ? bigOpacity : 1 }}>{big}</div>
        <div style={{ fontFamily: DISPLAY, fontWeight: 700, fontSize: dense ? 56 : 54, color: GREEN, letterSpacing: "0.04em", whiteSpace: "nowrap" }}>{delta}</div>
      </div>
      {tally != null && (
        <div style={{ display: "flex", flexWrap: "wrap", gap: 9, marginTop: 26, maxWidth: 900 }}>
          {Array.from({ length: tally }).map((_, i) => {
            const t = interpolate(frame, [s + 24 + i * 1.6, s + 30 + i * 1.6], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
            return <div key={i} style={{ width: 8, height: 40, background: i >= tally - 3 ? GREEN : IVORY, opacity: t * (i >= tally - 3 ? 1 : 0.55), transform: `scaleY(${t})`, transformOrigin: "bottom" }} />;
          })}
        </div>
      )}
      <div style={{ fontFamily: SERIF, fontStyle: "italic", fontSize: dense ? 62 : 44, color: IVORY, marginTop: dense ? 48 : 40, opacity: interpolate(frame, [s + 60, s + 84], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) }}>{caption}</div>
    </div>
  );
};

// -------------------------------------------------------------- LIST
// Substitui o gráfico ou o painel de destaque em temas SEM números (ex. "viver
// no Seixal", "cedência de posição contratual"). Cada item tem uma chave curta
// opcional (um número, um imposto, uma palavra) e uma linha de texto; os itens
// entram um a um. É o mínimo necessário para uma peça qualitativa não ter de
// inventar um gráfico só para preencher a janela.
interface ListItem { k?: string | null; v: string }

const SceneList: React.FC<{
  win: [number, number]; title: string; items: ListItem[]; accent: string;
  caption?: string | null; dense?: boolean;
}> = ({ win, title, items, accent, caption, dense }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const op = envelope(frame, fps, win);
  const s = win[0] * fps;
  return (
    <div style={{ position: "absolute", left: 84, right: 84, top: 700, opacity: op }}>
      <div style={{ fontFamily: DISPLAY, letterSpacing: "0.24em", fontSize: dense ? 54 : 34, color: dense ? IVORY : accent, fontWeight: 600, marginBottom: dense ? 58 : 36 }}>{title}</div>
      {items.map((it, i) => {
        const t = interpolate(frame, [s + 16 + i * 20, s + 40 + i * 20], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: ease });
        return (
          <div key={i} style={{ display: "flex", alignItems: "baseline", gap: dense ? 40 : 24, marginBottom: dense ? 64 : 32, opacity: t, transform: `translateX(${(1 - t) * -26}px)` }}>
            <div style={{ width: 13, alignSelf: "stretch", background: accent, opacity: 0.9, flexShrink: 0 }} />
            <div>
              {it.k && (
                <div style={{ fontFamily: DISPLAY, fontWeight: 700, fontSize: dense ? 152 : 72, color: GREEN, lineHeight: 1.0, letterSpacing: "-0.02em", fontVariantNumeric: "tabular-nums" }}>{it.k}</div>
              )}
              <div style={{ fontFamily: DISPLAY, fontWeight: 600, fontSize: dense ? 120 : 52, color: IVORY, lineHeight: 1.14, letterSpacing: "0.01em" }}>{it.v}</div>
            </div>
          </div>
        );
      })}
      {caption && (
        <div style={{ fontFamily: SERIF, fontStyle: "italic", fontSize: dense ? 62 : 44, color: IVORY, marginTop: dense ? 72 : 40, opacity: interpolate(frame, [s + 30 + items.length * 20, s + 54 + items.length * 20], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) }}>{caption}</div>
      )}
    </div>
  );
};

// -------------------------------------------------------------- CTA
const SceneCTA: React.FC<{
  win: [number, number]; tagline: string; brand: string; handle: string; accent: string;
  logo?: string | null; logoHeight?: number | null; contact?: string[] | null;
}> = ({ win, tagline, brand, handle, accent, logo, logoHeight, contact }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  // The end card is the last thing on screen: it fades IN and then stays put.
  // Letting envelope() fade it out leaves the piece ending on an empty frame.
  const op = interpolate(frame, [win[0] * fps, (win[0] + 0.5) * fps], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const s = win[0] * fps;
  // Front-loaded: the logo is the whole point of the end card, so it has to be
  // fully on screen well before the piece ends, not arriving as it cuts.
  const rule = interpolate(frame, [s + 6, s + 26], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: ease });
  const brandIn = interpolate(frame, [s + 16, s + 36], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: ease });
  const contactIn = interpolate(frame, [s + 34, s + 56], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: ease });
  return (
    <AbsoluteFill style={{ opacity: op, justifyContent: "center", alignItems: "center", textAlign: "center", padding: "0 90px" }}>
      <div style={{ fontFamily: SERIF, fontStyle: "italic", fontSize: 66, color: accent, marginBottom: 40, opacity: interpolate(frame, [s + 20, s + 46], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) }}>{tagline}</div>
      <div style={{ height: 2, width: 420, background: `linear-gradient(90deg, transparent, ${accent}, transparent)`, transform: `scaleX(${rule})` }} />
      {logo ? (
        <Img
          src={staticFile(logo)}
          style={{ height: logoHeight || 200, width: "auto", marginTop: 48, opacity: brandIn, transform: `translateY(${(1 - brandIn) * 14}px)` }}
        />
      ) : (
        <div style={{ fontFamily: DISPLAY, fontWeight: 700, fontSize: 92, color: IVORY, letterSpacing: "0.04em", marginTop: 44 }}>{brand}</div>
      )}
      {handle ? (
        <div style={{ fontFamily: DISPLAY, fontSize: 36, color: MUTED, letterSpacing: "0.22em", marginTop: 16 }}>{handle.toUpperCase()}</div>
      ) : null}
      {contact && contact.length ? (
        <div style={{ marginTop: 44, opacity: contactIn, transform: `translateY(${(1 - contactIn) * 12}px)` }}>
          <div style={{ height: 1, width: 260, background: HAIR, margin: "0 auto 30px" }} />
          {contact.map((line, i) => (
            <div key={i} style={{ fontFamily: DISPLAY, fontSize: 44, letterSpacing: "0.10em", color: IVORY, marginTop: i ? 14 : 0 }}>{line}</div>
          ))}
        </div>
      ) : null}
    </AbsoluteFill>
  );
};

// Presenter mode ends on a held contact card. Rather than cutting the footage
// (abrupt) or freezing a frame (dead), the room is dimmed down under the card
// while the agent keeps breathing behind it.
const ClosingVeil: React.FC<{ win: [number, number] }> = ({ win }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = win[0] * fps;
  const o = interpolate(frame, [s + 10, s + 46], [0, 0.84], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: ease });
  return <AbsoluteFill style={{ background: INK, opacity: o }} />;
};

// -------------------------------------------------------------- CAPTIONS
type Cap = { word: string; startMs: number; endMs: number };
const buildPages = (caps: Cap[], maxWords: number) => {
  const pages: { words: Cap[]; startMs: number; endMs: number }[] = [];
  let cur: Cap[] = [];
  const flush = () => { if (cur.length) { pages.push({ words: cur, startMs: cur[0].startMs, endMs: cur[cur.length - 1].endMs }); cur = []; } };
  caps.forEach((c) => {
    cur.push(c);
    const w = c.word.trim();
    if (cur.length >= maxWords || (/[.?!]$/.test(w) && cur.length >= 3) || (/[,;:]$/.test(w) && cur.length >= 4)) flush();
  });
  flush();
  return pages;
};

const Captions: React.FC<{ captions: Cap[]; accent: string }> = ({ captions, accent }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const ms = (frame / fps) * 1000;
  const pages = React.useMemo(() => buildPages(captions, 4), [captions]);
  if (!pages.length) return null;
  let pi = -1;
  for (let i = 0; i < pages.length; i++) { if (pages[i].startMs <= ms) pi = i; else break; }
  if (pi < 0) return null;
  const page = pages[pi];
  const nextStart = pi + 1 < pages.length ? pages[pi + 1].startMs : page.endMs + 700;
  if (ms > nextStart + 200) return null;
  const appear = interpolate(ms, [page.startMs - 130, page.startMs + 90], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <>
      <div style={{ position: "absolute", left: 0, right: 0, bottom: 0, height: 560, background: "linear-gradient(180deg, rgba(6,8,13,0) 0%, rgba(6,8,13,0) 32%, rgba(6,8,13,0.72) 74%, rgba(6,8,13,0.92) 100%)", pointerEvents: "none" }} />
      <div style={{ position: "absolute", left: 0, right: 0, bottom: 232, textAlign: "center", padding: "0 56px", opacity: appear }}>
        <div style={{ fontFamily: CAPTION_FONT, fontSize: 52, fontWeight: 700, lineHeight: 1.24, letterSpacing: "0.004em", textWrap: "balance", textShadow: "0 2px 18px rgba(0,0,0,0.92)" }}>
          {page.words.map((c, i) => {
            const isActive = ms >= c.startMs && ms < c.endMs;
            const isPast = ms >= c.endMs;
            return <span key={i} style={{ color: isActive ? accent : isPast ? IVORY : "rgba(243,236,221,0.72)", margin: "0 9px", textShadow: isActive ? `0 0 26px ${accent}99, 0 2px 18px rgba(0,0,0,0.92)` : "0 2px 18px rgba(0,0,0,0.92)" }}>{c.word.trim()}</span>;
          })}
        </div>
      </div>
    </>
  );
};

// -------------------------------------------------------------- ROOT
// Presenter mode packs the scenes, authored full-bleed at 1080 wide, into the
// free column left of the agent. Scaling the whole group keeps every internal
// proportion (rules, tally marks, chart) instead of re-tuning each scene.
// Tuned against the rendered footage: her gesturing hand reaches x ≈ 0.45 of the
// frame, so the column has to end before that, not at the half-way line.
const PRESENTER_SCALE = 0.53;
const PRESENTER_DX = -4.5; // x_out = DX + SCALE * x_in → scene x 84..996 lands at 40..523
const PRESENTER_DY = 249; // y_out = DY + SCALE * y_in → scene y 700 lands at 620

export const MarketLedger: React.FC<MarketLedgerProps> = ({ data, sections, captions, audio }) => {
  const a = data.accent;
  const presenter = !!data.presenter;
  const dataScenes = (
    <>
      <SceneHook win={sections.hook} line1={data.hookLine1} line2={data.hookLine2} sub={data.hookSub} accent={a} dense={presenter} />
      <SceneStat win={sections.stat} label={data.statLabel} value={data.statValue} prefix={data.statPrefix} suffix={data.statSuffix} grp={data.statGroup} yoy={data.yoy} yoyLabel={data.yoyLabel} accent={a} dense={presenter} />
      {data.list ? (
        <SceneList win={sections.chart} title={data.listTitle ?? data.chartTitle} items={data.list} accent={a} dense={presenter} />
      ) : (
        <SceneChart win={sections.chart} title={data.chartTitle} chart={data.chart} accent={a} yMin={data.chartYMin} dense={presenter} />
      )}
      {data.list2 ? (
        <SceneList win={sections.insight} title={data.list2Title ?? data.insightLabel} items={data.list2} accent={a} caption={data.insightCaption} dense={presenter} />
      ) : data.chart2 ? (
        // Segundo mercado com gráfico próprio (ex. Almada + Seixal): o chart2
        // ocupa a janela do insight e herda a legenda do insight.
        <SceneChart win={sections.insight} title={data.chart2Title ?? data.chartTitle} chart={data.chart2} accent={a} yMin={data.chart2YMin} dense={presenter} caption={data.insightCaption} gradId="ml-area2" />
      ) : (
        <SceneInsight win={sections.insight} label={data.insightLabel} value={data.insightValue} display={data.insightDisplay} suffix={data.insightSuffix} delta={data.insightDelta} caption={data.insightCaption} tally={data.insightTally} accent={a} dense={presenter} />
      )}
    </>
  );
  // The end card is never scaled into the side column — it owns the full frame.
  const cta = (
    <SceneCTA win={sections.cta} tagline={data.ctaTagline} brand={data.brand} handle={data.handle} accent={a} logo={data.logo} logoHeight={data.logoHeight} contact={data.ctaContact} />
  );
  return (
    <AbsoluteFill style={{ backgroundColor: INK }}>
      {data.backgroundVideo ? (
        <>
          <AbsoluteFill>
            <OffthreadVideo
              src={staticFile(data.backgroundVideo)}
              muted
              style={{ width: "100%", height: "100%", objectFit: "cover" }}
            />
          </AbsoluteFill>
          {presenter ? (
            <>
              {/* Presenter scrim: heavy on the LEFT where the data lives, light
                  on the RIGHT so the agent and the room keep their daylight. */}
              <AbsoluteFill
                style={{
                  background: `linear-gradient(90deg, rgba(11,15,23,${(data.scrimOpacity ?? 0.72) + 0.14}) 0%, rgba(11,15,23,${(data.scrimOpacity ?? 0.72) + 0.06}) 44%, rgba(11,15,23,0.20) 60%, rgba(11,15,23,0.05) 100%)`,
                }}
              />
              {/* Just enough top/bottom fall-off for the masthead and captions. */}
              <AbsoluteFill
                style={{
                  background:
                    "linear-gradient(180deg, rgba(11,15,23,0.55) 0%, rgba(11,15,23,0) 22%, rgba(11,15,23,0) 68%, rgba(11,15,23,0.5) 100%)",
                }}
              />
            </>
          ) : (
            /* Scrim: keeps the numbers readable over bright rooms, and darkens
               toward the edges so the footage still breathes in the middle. */
            <AbsoluteFill
              style={{
                background: `linear-gradient(180deg, rgba(11,15,23,${(data.scrimOpacity ?? 0.55) + 0.2}) 0%, rgba(11,15,23,${data.scrimOpacity ?? 0.55}) 38%, rgba(11,15,23,${(data.scrimOpacity ?? 0.55) + 0.28}) 100%)`,
              }}
            />
          )}
        </>
      ) : (
        <Backdrop accent={a} />
      )}
      <Masthead label={data.masthead} location={data.location} period={data.period} accent={a} />

      {presenter ? (
        <>
          <div
            style={{
              position: "absolute",
              left: 0,
              top: 0,
              width: 1080,
              height: 1920,
              transformOrigin: "0 0",
              transform: `translate(${PRESENTER_DX}px, ${PRESENTER_DY}px) scale(${PRESENTER_SCALE})`,
            }}
          >
            {dataScenes}
          </div>
          <ClosingVeil win={sections.cta} />
          {cta}
        </>
      ) : (
        <>
          {dataScenes}
          {cta}
        </>
      )}

      <Captions captions={captions} accent={a} />

      <div style={{ position: "absolute", bottom: 74, left: 84, right: presenter ? 470 : 84, display: "flex", justifyContent: "space-between", fontFamily: DISPLAY, fontSize: 27, letterSpacing: "0.14em", color: "rgba(243,236,221,0.58)", borderTop: `1px solid ${HAIR}`, paddingTop: 18 }}>
        <span>{data.brand}</span>
        <span>{data.sourceNote}</span>
      </div>

      {data.aiNote ? (
        <div
          style={{
            position: "absolute",
            bottom: 26,
            left: 0,
            right: 0,
            textAlign: "center",
            fontFamily: DISPLAY,
            fontSize: 21,
            letterSpacing: "0.2em",
            color: "rgba(243,236,221,0.55)",
          }}
        >
          {data.aiNote}
        </div>
      ) : null}


      <Audio src={staticFile(audio.narration)} />
      <Audio src={staticFile(audio.music)} volume={0.12} />
    </AbsoluteFill>
  );
};
