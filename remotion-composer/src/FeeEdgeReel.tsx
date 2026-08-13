import {
  AbsoluteFill, Sequence, Img, staticFile, spring, interpolate,
  useCurrentFrame, useVideoConfig,
} from "remotion";
import { loadFont } from "@remotion/google-fonts/Sora";
const { fontFamily } = loadFont();

const BG = "#08090b", EMERALD = "#10b981", EMERALD_B = "#34d399",
  AMBER = "#f59e0b", WHITE = "#f8fafc", MUTED = "#8b9099", FAINT = "#4b5563";

const useFade = (dur: number, inF = 8, outF = 10) => {
  const f = useCurrentFrame();
  return interpolate(f, [0, inF, dur - outF, dur], [0, 1, 1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
};
const useRise = (delay = 0, dist = 28) => {
  const f = useCurrentFrame(); const { fps } = useVideoConfig();
  const s = spring({ frame: f - delay, fps, config: { damping: 18, stiffness: 95 } });
  return { opacity: s, transform: `translateY(${(1 - s) * dist}px)` };
};

const Bg: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <AbsoluteFill style={{ backgroundColor: BG, fontFamily }}>
    <AbsoluteFill style={{ background:
      "radial-gradient(900px 900px at 80% 6%, rgba(16,185,129,.18), transparent 60%)," +
      "radial-gradient(800px 800px at 12% 100%, rgba(16,185,129,.10), transparent 62%)" }} />
    <AbsoluteFill style={{
      backgroundImage:
        "linear-gradient(rgba(255,255,255,.028) 1px,transparent 1px)," +
        "linear-gradient(90deg,rgba(255,255,255,.028) 1px,transparent 1px)",
      backgroundSize: "80px 80px",
      maskImage: "radial-gradient(circle at 50% 42%, black, transparent 80%)" }} />
    <div style={{ position: "absolute", top: 64, left: 0, right: 0, display: "flex",
      justifyContent: "center", alignItems: "center", gap: 16, opacity: .95 }}>
      <Img src={staticFile("feeedge/logo-mark.png")} style={{ width: 54, height: 54 }} />
      <div style={{ fontSize: 38, fontWeight: 800, letterSpacing: -.6, color: WHITE }}>
        Fee<span style={{ color: EMERALD_B }}>Edge</span></div>
    </div>
    <div style={{ position: "absolute", bottom: 60, left: 0, right: 0, textAlign: "center",
      fontSize: 24, color: FAINT }}>Estimates, not financial advice</div>
    {children}
  </AbsoluteFill>
);

const Center: React.FC<{ children: React.ReactNode; op: number }> = ({ children, op }) => (
  <AbsoluteFill style={{ opacity: op, justifyContent: "center", alignItems: "center",
    textAlign: "center", padding: "0 90px" }}>{children}</AbsoluteFill>
);

const Hook: React.FC<{ dur: number }> = ({ dur }) => {
  const f = useCurrentFrame(); const { fps } = useVideoConfig();
  const pop = spring({ frame: f, fps, config: { damping: 12, stiffness: 110 }, from: .8, to: 1 });
  const val = Math.round(interpolate(f, [4, 40], [0, 6630], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }));
  const sub = useRise(16);
  return (<Center op={useFade(dur)}>
    <div style={{ fontSize: 34, fontWeight: 700, letterSpacing: 5, color: AMBER, marginBottom: 30 }}>THE FEE YOU NEVER CHECK</div>
    <div style={{ fontSize: 220, fontWeight: 800, letterSpacing: -6, color: AMBER, lineHeight: 1,
      transform: `scale(${pop})`, textShadow: "0 0 110px rgba(245,158,11,.4)" }}>${val.toLocaleString("en-US")}</div>
    <div style={{ ...sub, fontSize: 48, color: WHITE, marginTop: 40, fontWeight: 500, lineHeight: 1.3 }}>
      a year in trading fees —<br />and most people never notice.</div>
  </Center>);
};

const Agitate: React.FC<{ dur: number }> = ({ dur }) => {
  const a = useRise(4), b = useRise(24);
  return (<Center op={useFade(dur)}>
    <div style={{ ...a, fontSize: 76, fontWeight: 800, letterSpacing: -1.5, color: WHITE, lineHeight: 1.12 }}>
      Every trade takes a <span style={{ color: AMBER }}>cut.</span></div>
    <div style={{ ...b, fontSize: 52, color: MUTED, marginTop: 32, fontWeight: 500 }}>
      Every funding window, another.</div>
  </Center>);
};

const NeverCheck: React.FC<{ dur: number }> = ({ dur }) => {
  const a = useRise(4), b = useRise(22);
  return (<Center op={useFade(dur)}>
    <div style={{ ...a, fontSize: 72, fontWeight: 800, letterSpacing: -1.5, color: WHITE, lineHeight: 1.15 }}>
      You picked your platform once.</div>
    <div style={{ ...b, fontSize: 52, color: EMERALD_B, marginTop: 30, fontWeight: 700 }}>
      You never re-checked the bill.</div>
  </Center>);
};

const Audit: React.FC<{ dur: number }> = ({ dur }) => {
  const f = useCurrentFrame(); const { fps } = useVideoConfig();
  const card = useRise(4, 40);
  const check = spring({ frame: f - 34, fps, config: { damping: 11, stiffness: 130 }, from: 0, to: 1 });
  const t = useRise(28);
  return (<Center op={useFade(dur)}>
    <div style={{ ...card, position: "relative", width: 420, height: 340, borderRadius: 26,
      background: "rgba(255,255,255,.035)", border: "1px solid rgba(255,255,255,.09)", padding: 40, marginBottom: 56 }}>
      <div style={{ fontSize: 26, color: MUTED, fontWeight: 700, letterSpacing: 1, marginBottom: 26 }}>your-trades.csv</div>
      {[0, 1, 2, 3].map((i) => (<div key={i} style={{ height: 20, borderRadius: 6, marginBottom: 18,
        width: `${88 - i * 12}%`, background: "rgba(255,255,255,.12)" }} />))}
      <div style={{ position: "absolute", right: -36, bottom: -36, width: 120, height: 120, borderRadius: 999,
        background: EMERALD, display: "flex", alignItems: "center", justifyContent: "center",
        transform: `scale(${check})`, boxShadow: `0 0 70px ${EMERALD}66` }}>
        <svg width="60" height="60" viewBox="0 0 24 24" fill="none" stroke="#04120c" strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round"><path d="M20 6 L9 17 L4 12" /></svg>
      </div>
    </div>
    <div style={{ ...t }}>
      <div style={{ fontSize: 66, fontWeight: 800, letterSpacing: -1.5, color: WHITE, lineHeight: 1.1 }}>
        Upload your trades.<br />See your <span style={{ color: EMERALD_B }}>real bill.</span></div>
      <div style={{ fontSize: 40, color: MUTED, marginTop: 26, fontWeight: 500 }}>
        Free. Nothing leaves your browser.</div>
    </div>
  </Center>);
};

const Bar: React.FC<{ label: string; value: number; max: number; color: string; delay: number }> = ({ label, value, max, color, delay }) => {
  const f = useCurrentFrame(); const { fps } = useVideoConfig();
  const grow = spring({ frame: f - delay, fps, config: { damping: 16, stiffness: 70 } });
  const shown = Math.round(interpolate(grow, [0, 1], [0, value]));
  return (<div style={{ display: "flex", flexDirection: "column", alignItems: "center", width: 300 }}>
    <div style={{ fontSize: 66, fontWeight: 800, color: WHITE, marginBottom: 16, opacity: grow }}>${shown}</div>
    <div style={{ height: 380, display: "flex", alignItems: "flex-end" }}>
      <div style={{ width: 150, height: (value / max) * 380 * grow, borderRadius: "14px 14px 5px 5px",
        background: `linear-gradient(180deg, ${color}, ${color}cc)`, boxShadow: `0 0 70px ${color}44` }} /></div>
    <div style={{ fontSize: 34, color: MUTED, marginTop: 22, fontWeight: 600, whiteSpace: "nowrap" }}>{label}</div>
  </div>);
};

const Compare: React.FC<{ dur: number }> = ({ dur }) => {
  const f = useCurrentFrame(); const { fps } = useVideoConfig();
  const title = useRise(2);
  const pill = spring({ frame: f - 44, fps, config: { damping: 12, stiffness: 120 }, from: .7, to: 1 });
  return (<Center op={useFade(dur)}>
    <div style={{ ...title, fontSize: 62, fontWeight: 800, letterSpacing: -1, color: WHITE, marginBottom: 24, lineHeight: 1.15 }}>
      The same trades,<br />somewhere cheaper.</div>
    <div style={{ transform: `scale(${pill})`, opacity: pill, background: "rgba(52,211,153,.14)",
      border: `2px solid ${EMERALD}`, color: EMERALD_B, fontWeight: 800, fontSize: 40, padding: "12px 34px",
      borderRadius: 999, marginBottom: 52 }}>Pay 63% less</div>
    <div style={{ display: "flex", gap: 150, alignItems: "flex-end" }}>
      <Bar label="What you pay" value={250} max={250} color={AMBER} delay={8} />
      <Bar label="What you could" value={92} max={250} color={EMERALD_B} delay={20} />
    </div>
  </Center>);
};

const Cta: React.FC<{ dur: number }> = ({ dur }) => {
  const f = useCurrentFrame(); const { fps } = useVideoConfig();
  const logo = spring({ frame: f, fps, config: { damping: 13, stiffness: 100 }, from: .7, to: 1 });
  const btn = useRise(20, 22), url = useRise(32);
  return (<Center op={useFade(dur)}>
    <Img src={staticFile("feeedge/logo-mark.png")} style={{ width: 160, height: 160,
      transform: `scale(${logo})`, filter: `drop-shadow(0 0 70px ${EMERALD}55)` }} />
    <div style={{ fontSize: 130, fontWeight: 800, letterSpacing: -3, color: WHITE, marginTop: 30 }}>
      Fee<span style={{ color: EMERALD_B }}>Edge</span></div>
    <div style={{ fontSize: 50, color: WHITE, marginTop: 8, fontWeight: 600 }}>See what you're really paying.</div>
    <div style={{ ...btn, background: EMERALD, color: "#04120c", fontWeight: 800, fontSize: 50,
      padding: "26px 56px", borderRadius: 18, marginTop: 44, boxShadow: `0 0 80px ${EMERALD}55` }}>Run a free audit →</div>
    <div style={{ ...url, fontSize: 40, color: MUTED, marginTop: 34, fontWeight: 600, letterSpacing: 1 }}>
      feeedge.com · free · 30 seconds</div>
  </Center>);
};

export const FeeEdgeReel: React.FC = () => {
  const S = { hook: 113, agitate: 122, never: 117, audit: 167, compare: 114, cta: 86 };
  let t = 0; const seq = (d: number) => { const from = t; t += d; return { from, durationInFrames: d }; };
  return (<Bg>
    <Sequence {...seq(S.hook)}><Hook dur={S.hook} /></Sequence>
    <Sequence {...seq(S.agitate)}><Agitate dur={S.agitate} /></Sequence>
    <Sequence {...seq(S.never)}><NeverCheck dur={S.never} /></Sequence>
    <Sequence {...seq(S.audit)}><Audit dur={S.audit} /></Sequence>
    <Sequence {...seq(S.compare)}><Compare dur={S.compare} /></Sequence>
    <Sequence {...seq(S.cta)}><Cta dur={S.cta} /></Sequence>
  </Bg>);
};
