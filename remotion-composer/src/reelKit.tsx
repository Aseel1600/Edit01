// Shared visual system for FeeEdge vertical reels (1080x1920), extracted from
// FeeEdgeReel.tsx so new reels keep the exact look of the 65k-view winner.
import {
  AbsoluteFill, Img, staticFile, spring, interpolate,
  useCurrentFrame, useVideoConfig,
} from "remotion";
import { loadFont } from "@remotion/google-fonts/Sora";
const { fontFamily } = loadFont();

export const BG = "#08090b", EMERALD = "#10b981", EMERALD_B = "#34d399",
  AMBER = "#f59e0b", WHITE = "#f8fafc", MUTED = "#8b9099", FAINT = "#4b5563";
export { fontFamily };

export const useFade = (dur: number, inF = 8, outF = 10) => {
  const f = useCurrentFrame();
  return interpolate(f, [0, inF, dur - outF, dur], [0, 1, 1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
};

export const useRise = (delay = 0, dist = 28) => {
  const f = useCurrentFrame(); const { fps } = useVideoConfig();
  const s = spring({ frame: f - delay, fps, config: { damping: 18, stiffness: 95 } });
  return { opacity: s, transform: `translateY(${(1 - s) * dist}px)` };
};

export const Bg: React.FC<{ children: React.ReactNode }> = ({ children }) => (
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

export const Center: React.FC<{ children: React.ReactNode; op: number }> = ({ children, op }) => (
  <AbsoluteFill style={{ opacity: op, justifyContent: "center", alignItems: "center",
    textAlign: "center", padding: "0 90px" }}>{children}</AbsoluteFill>
);

// A growing labelled bar, used in the comparison payoff scenes.
export const Bar: React.FC<{ label: string; value: number; shownMax: number; barMax: number; color: string; delay: number; prefix?: string; suffix?: string }> =
  ({ label, value, shownMax, barMax, color, delay, prefix = "$", suffix = "" }) => {
  const f = useCurrentFrame(); const { fps } = useVideoConfig();
  const grow = spring({ frame: f - delay, fps, config: { damping: 16, stiffness: 70 } });
  const shown = Math.round(interpolate(grow, [0, 1], [0, value]));
  return (<div style={{ display: "flex", flexDirection: "column", alignItems: "center", width: 300 }}>
    <div style={{ fontSize: 66, fontWeight: 800, color: WHITE, marginBottom: 16, opacity: grow }}>{prefix}{shown.toLocaleString("en-US")}{suffix}</div>
    <div style={{ height: 380, display: "flex", alignItems: "flex-end" }}>
      <div style={{ width: 150, height: (value / barMax) * 380 * grow, borderRadius: "14px 14px 5px 5px",
        background: `linear-gradient(180deg, ${color}, ${color}cc)`, boxShadow: `0 0 70px ${color}44` }} /></div>
    <div style={{ fontSize: 34, color: MUTED, marginTop: 22, fontWeight: 600, whiteSpace: "nowrap" }}>{label}</div>
  </div>);
};
