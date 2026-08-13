import {
  AbsoluteFill,
  Sequence,
  Img,
  staticFile,
  spring,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { loadFont } from "@remotion/google-fonts/Sora";

const { fontFamily } = loadFont();

// ── Brand tokens ──────────────────────────────────────────────────────────
const BG = "#08090b";
const EMERALD = "#10b981";
const EMERALD_BRIGHT = "#34d399";
const AMBER = "#f59e0b";
const WHITE = "#f8fafc";
const MUTED = "#8b9099";
const FAINT = "#4b5563";

// ── Helpers ─────────────────────────────────────────────────────────────────
const useFade = (dur: number, inF = 12, outF = 14) => {
  const frame = useCurrentFrame();
  return interpolate(
    frame,
    [0, inF, dur - outF, dur],
    [0, 1, 1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );
};

const useRise = (delay = 0, dist = 26) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = spring({ frame: frame - delay, fps, config: { damping: 18, stiffness: 90 } });
  return { opacity: s, transform: `translateY(${(1 - s) * dist}px)` };
};

// ── Persistent branded background + logo lockup ─────────────────────────────
const Bg: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <AbsoluteFill style={{ backgroundColor: BG, fontFamily }}>
    {/* emerald depth */}
    <AbsoluteFill
      style={{
        background:
          "radial-gradient(1300px 820px at 82% 8%, rgba(16,185,129,0.16), transparent 60%)," +
          "radial-gradient(1100px 760px at 8% 100%, rgba(16,185,129,0.08), transparent 62%)",
      }}
    />
    {/* faint grid */}
    <AbsoluteFill
      style={{
        backgroundImage:
          "linear-gradient(rgba(255,255,255,0.025) 1px, transparent 1px)," +
          "linear-gradient(90deg, rgba(255,255,255,0.025) 1px, transparent 1px)",
        backgroundSize: "64px 64px",
        maskImage: "radial-gradient(circle at 50% 45%, black, transparent 78%)",
      }}
    />
    {/* persistent logo lockup */}
    <div style={{ position: "absolute", top: 56, left: 68, display: "flex", alignItems: "center", gap: 14, opacity: 0.92 }}>
      <Img src={staticFile("feeedge/logo-mark.png")} style={{ width: 42, height: 42 }} />
      <div style={{ fontSize: 27, fontWeight: 800, letterSpacing: -0.5, color: WHITE }}>
        Fee<span style={{ color: EMERALD_BRIGHT }}>Edge</span>
      </div>
    </div>
    {/* disclaimer */}
    <div style={{ position: "absolute", bottom: 46, right: 72, fontSize: 18, color: FAINT, letterSpacing: 0.3 }}>
      Estimates, not financial advice
    </div>
    {children}
  </AbsoluteFill>
);

// ── Scene 1: Hook ($6,630 count-up) ─────────────────────────────────────────
const HookScene: React.FC<{ dur: number }> = ({ dur }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const opacity = useFade(dur);
  const pop = spring({ frame, fps, config: { damping: 13, stiffness: 110 }, from: 0.86, to: 1 });
  const val = Math.round(interpolate(frame, [6, 48], [0, 6630], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }));
  const sub = useRise(16);
  return (
    <AbsoluteFill style={{ opacity, justifyContent: "center", alignItems: "center" }}>
      <div style={{ textAlign: "center", maxWidth: "82%" }}>
        <div style={{ fontSize: 26, fontWeight: 700, letterSpacing: 4, color: AMBER, marginBottom: 22, opacity: 0.9 }}>
          THE COST YOU NEVER CHECK
        </div>
        <div
          style={{
            fontSize: 210,
            fontWeight: 800,
            letterSpacing: -4,
            color: AMBER,
            lineHeight: 1,
            transform: `scale(${pop})`,
            textShadow: "0 0 90px rgba(245,158,11,0.35)",
          }}
        >
          ${val.toLocaleString("en-US")}
        </div>
        <div style={{ ...sub, fontSize: 42, color: WHITE, marginTop: 26, fontWeight: 500 }}>
          what trading fees quietly cost the average trader
          <br /> every single year.
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ── Scene 2: Problem ────────────────────────────────────────────────────────
const ProblemScene: React.FC<{ dur: number }> = ({ dur }) => {
  const opacity = useFade(dur);
  const l1 = useRise(6);
  const l2 = useRise(20);
  return (
    <AbsoluteFill style={{ opacity, justifyContent: "center", alignItems: "center" }}>
      <div style={{ textAlign: "center", maxWidth: 1320 }}>
        <div style={{ ...l1, fontSize: 74, fontWeight: 800, letterSpacing: -1.5, color: WHITE, lineHeight: 1.12 }}>
          Every exchange charges <span style={{ color: AMBER }}>differently.</span>
        </div>
        <div style={{ ...l2, fontSize: 48, color: MUTED, marginTop: 30, fontWeight: 500 }}>
          Most traders pick one — and never re-check.
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ── Scene 3: Comparison bars ────────────────────────────────────────────────
const Bar: React.FC<{ label: string; value: number; max: number; color: string; delay: number }> = ({
  label, value, max, color, delay,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const grow = spring({ frame: frame - delay, fps, config: { damping: 16, stiffness: 70 } });
  const h = (value / max) * 420 * grow;
  const shown = Math.round(interpolate(grow, [0, 1], [0, value]));
  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", width: 250 }}>
      <div style={{ fontSize: 52, fontWeight: 800, color: WHITE, marginBottom: 14, opacity: grow }}>
        ${shown}
      </div>
      <div style={{ height: 420, display: "flex", alignItems: "flex-end" }}>
        <div
          style={{
            width: 150, height: h, borderRadius: "12px 12px 4px 4px",
            background: `linear-gradient(180deg, ${color}, ${color}cc)`,
            boxShadow: `0 0 60px ${color}44`,
          }}
        />
      </div>
      <div style={{ fontSize: 32, color: MUTED, marginTop: 20, fontWeight: 600, whiteSpace: "nowrap" }}>{label}</div>
    </div>
  );
};

const CompareScene: React.FC<{ dur: number }> = ({ dur }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const opacity = useFade(dur);
  const title = useRise(2);
  const pill = spring({ frame: frame - 46, fps, config: { damping: 12, stiffness: 120 }, from: 0.7, to: 1 });
  return (
    <AbsoluteFill style={{ opacity, justifyContent: "center", alignItems: "center" }}>
      <div style={{ ...title, fontSize: 64, fontWeight: 800, letterSpacing: -1, color: WHITE, marginBottom: 18 }}>
        Same trades. <span style={{ color: MUTED }}>Different monthly bill.</span>
      </div>
      {/* savings pill — its own row, no collision */}
      <div
        style={{
          transform: `scale(${pill})`, opacity: pill,
          background: "rgba(52,211,153,0.14)", border: `1.5px solid ${EMERALD}`,
          color: EMERALD_BRIGHT, fontWeight: 800, fontSize: 30, letterSpacing: 0.5,
          padding: "10px 26px", borderRadius: 999, marginBottom: 40,
        }}
      >
        63% cheaper · same trading
      </div>
      <div style={{ display: "flex", gap: 320, alignItems: "flex-end" }}>
        <Bar label="Your exchange" value={250} max={250} color={AMBER} delay={8} />
        <Bar label="Cheapest for you" value={92} max={250} color={EMERALD_BRIGHT} delay={20} />
      </div>
    </AbsoluteFill>
  );
};

// ── Scene 4: Fee Audit ──────────────────────────────────────────────────────
const AuditScene: React.FC<{ dur: number }> = ({ dur }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const opacity = useFade(dur);
  const card = useRise(4, 34);
  const check = spring({ frame: frame - 40, fps, config: { damping: 11, stiffness: 130 }, from: 0, to: 1 });
  const text = useRise(24);
  return (
    <AbsoluteFill style={{ opacity, justifyContent: "center", alignItems: "center" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 90 }}>
        {/* CSV → check card */}
        <div
          style={{
            ...card, width: 360, height: 300, borderRadius: 22,
            background: "rgba(255,255,255,0.035)", border: "1px solid rgba(255,255,255,0.09)",
            padding: 34, position: "relative",
          }}
        >
          <div style={{ fontSize: 22, color: MUTED, fontWeight: 700, letterSpacing: 1, marginBottom: 22 }}>
            trades.csv
          </div>
          {[0, 1, 2, 3].map((i) => (
            <div key={i} style={{ height: 16, borderRadius: 5, marginBottom: 16, width: `${88 - i * 12}%`, background: "rgba(255,255,255,0.12)" }} />
          ))}
          <div
            style={{
              position: "absolute", right: -34, bottom: -34,
              width: 104, height: 104, borderRadius: 999, background: EMERALD,
              display: "flex", alignItems: "center", justifyContent: "center",
              transform: `scale(${check})`, boxShadow: `0 0 60px ${EMERALD}66`,
            }}
          >
            <svg width="52" height="52" viewBox="0 0 24 24" fill="none" stroke="#04120c" strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M20 6 L9 17 L4 12" />
            </svg>
          </div>
        </div>
        <div style={{ ...text, maxWidth: 720 }}>
          <div style={{ fontSize: 60, fontWeight: 800, letterSpacing: -1, color: WHITE, lineHeight: 1.1 }}>
            Run a free <span style={{ color: EMERALD_BRIGHT }}>Fee Audit.</span>
          </div>
          <div style={{ fontSize: 38, color: MUTED, marginTop: 24, fontWeight: 500, lineHeight: 1.35 }}>
            Upload your trades, see your real fee + funding bill. Nothing leaves your browser.
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ── Scene 5: CTA ────────────────────────────────────────────────────────────
const CtaScene: React.FC<{ dur: number }> = ({ dur }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const opacity = useFade(dur);
  const logo = spring({ frame, fps, config: { damping: 13, stiffness: 100 }, from: 0.7, to: 1 });
  const btn = useRise(24, 20);
  const url = useRise(34);
  return (
    <AbsoluteFill style={{ opacity, justifyContent: "center", alignItems: "center" }}>
      <div style={{ textAlign: "center" }}>
        <Img
          src={staticFile("feeedge/logo-mark.png")}
          style={{ width: 130, height: 130, transform: `scale(${logo})`, filter: `drop-shadow(0 0 60px ${EMERALD}55)` }}
        />
        <div style={{ fontSize: 108, fontWeight: 800, letterSpacing: -3, color: WHITE, marginTop: 26 }}>
          Fee<span style={{ color: EMERALD_BRIGHT }}>Edge</span>
        </div>
        <div
          style={{
            ...btn, display: "inline-block", marginTop: 30,
            background: EMERALD, color: "#04120c", fontWeight: 800, fontSize: 38,
            padding: "20px 46px", borderRadius: 14, boxShadow: `0 0 60px ${EMERALD}55`,
          }}
        >
          Run a free Fee Audit  →
        </div>
        <div style={{ ...url, fontSize: 32, color: MUTED, marginTop: 30, letterSpacing: 1, fontWeight: 600 }}>
          feeedge.com
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ── Composition ─────────────────────────────────────────────────────────────
export const FeeEdgeAd: React.FC = () => {
  // 30fps timings (frames)
  const S = { hook: 120, problem: 120, compare: 165, audit: 135, cta: 120 };
  let t = 0;
  const seq = (dur: number) => {
    const from = t;
    t += dur;
    return { from, durationInFrames: dur };
  };
  return (
    <Bg>
      <Sequence {...seq(S.hook)}><HookScene dur={S.hook} /></Sequence>
      <Sequence {...seq(S.problem)}><ProblemScene dur={S.problem} /></Sequence>
      <Sequence {...seq(S.compare)}><CompareScene dur={S.compare} /></Sequence>
      <Sequence {...seq(S.audit)}><AuditScene dur={S.audit} /></Sequence>
      <Sequence {...seq(S.cta)}><CtaScene dur={S.cta} /></Sequence>
    </Bg>
  );
};
