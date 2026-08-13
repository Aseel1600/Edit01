import { Sequence, spring, interpolate, useCurrentFrame, useVideoConfig, Img, staticFile } from "remotion";
import { Bg, Center, Bar, useFade, useRise, WHITE, MUTED, AMBER, EMERALD, EMERALD_B } from "./reelKit";

// Same frame-0 rule ReelWithdrawV2 exists to enforce: useFade() always ramps in,
// so frame 0 sits at opacity 0 and the hook reads as a blank post for the first
// third of a second. The v1 withdraw funnel lost 72% of starts before 2 seconds
// on exactly that. Fade OUT only, and no rise on the hook line itself.
const useFadeOutOnly = (dur: number, outF = 10) =>
  interpolate(useCurrentFrame(), [dur - outF, dur], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

const Hook: React.FC<{ dur: number }> = ({ dur }) => {
  const b = useRise(10);
  return (<Center op={useFadeOutOnly(dur)}>
    <div style={{ fontSize: 84, fontWeight: 800, letterSpacing: -1.5, color: WHITE, lineHeight: 1.12 }}>
      Your position<br />pays <span style={{ color: AMBER }}>rent.</span></div>
    <div style={{ ...b, fontSize: 58, color: MUTED, marginTop: 34, fontWeight: 600 }}>
      Every 8 hours.</div>
  </Center>);
};

const Agitate: React.FC<{ dur: number }> = ({ dur }) => {
  const a = useRise(4), b = useRise(24);
  return (<Center op={useFade(dur)}>
    <div style={{ ...a, fontSize: 70, fontWeight: 800, letterSpacing: -1.2, color: WHITE, lineHeight: 1.18 }}>
      Perp <span style={{ color: EMERALD_B }}>funding</span> is charged around the clock,</div>
    <div style={{ ...b, fontSize: 52, color: MUTED, marginTop: 30, fontWeight: 500 }}>
      whether you win or lose.</div>
  </Center>);
};

const Payoff: React.FC<{ dur: number }> = ({ dur }) => {
  const f = useCurrentFrame(); const { fps } = useVideoConfig();
  const pop = spring({ frame: f, fps, config: { damping: 12, stiffness: 110 }, from: .8, to: 1 });
  const val = Math.round(interpolate(f, [4, 42], [0, 96], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }));
  const sub = useRise(20);
  return (<Center op={useFade(dur)}>
    <div style={{ fontSize: 34, fontWeight: 700, letterSpacing: 4, color: AMBER, marginBottom: 26 }}>FUNDING ALONE</div>
    <div style={{ fontSize: 210, fontWeight: 800, letterSpacing: -6, color: AMBER, lineHeight: 1,
      transform: `scale(${pop})`, textShadow: "0 0 110px rgba(245,158,11,.4)" }}>${val}<span style={{ fontSize: 90 }}>/mo</span></div>
    <div style={{ ...sub, fontSize: 46, color: WHITE, marginTop: 38, fontWeight: 500, lineHeight: 1.3 }}>
      on a $10k perp position.<br />Often more than your trading fees.</div>
  </Center>);
};

const Compare: React.FC<{ dur: number }> = ({ dur }) => {
  const f = useCurrentFrame(); const { fps } = useVideoConfig();
  const title = useRise(2);
  const pill = spring({ frame: f - 44, fps, config: { damping: 12, stiffness: 120 }, from: .7, to: 1 });
  return (<Center op={useFade(dur)}>
    <div style={{ ...title, fontSize: 62, fontWeight: 800, letterSpacing: -1, color: WHITE, marginBottom: 22, lineHeight: 1.15 }}>
      Same position,<br />two venues.</div>
    <div style={{ transform: `scale(${pill})`, opacity: pill, background: "rgba(52,211,153,.14)",
      border: `2px solid ${EMERALD}`, color: EMERALD_B, fontWeight: 800, fontSize: 40, padding: "12px 34px",
      borderRadius: 999, marginBottom: 50 }}>Pay 46% less</div>
    <div style={{ display: "flex", gap: 150, alignItems: "flex-end" }}>
      <Bar label="What you pay" value={96} shownMax={96} barMax={96} color={AMBER} delay={8} suffix="/mo" />
      <Bar label="Cheaper venue" value={52} shownMax={96} barMax={96} color={EMERALD_B} delay={20} suffix="/mo" />
    </div>
  </Center>);
};

const Cta: React.FC<{ dur: number }> = ({ dur }) => {
  const f = useCurrentFrame(); const { fps } = useVideoConfig();
  const logo = spring({ frame: f, fps, config: { damping: 13, stiffness: 100 }, from: .7, to: 1 });
  const btn = useRise(20, 22), url = useRise(32);
  return (<Center op={useFade(dur)}>
    <Img src={staticFile("feeedge/logo-mark.png")} style={{ width: 150, height: 150,
      transform: `scale(${logo})`, filter: `drop-shadow(0 0 70px ${EMERALD}55)` }} />
    <div style={{ fontSize: 120, fontWeight: 800, letterSpacing: -3, color: WHITE, marginTop: 28 }}>
      Fee<span style={{ color: EMERALD_B }}>Edge</span></div>
    <div style={{ fontSize: 50, color: WHITE, marginTop: 10, fontWeight: 600, lineHeight: 1.25 }}>Fees + funding,<br />in one number.</div>
    <div style={{ ...url, fontSize: 40, color: MUTED, marginTop: 40, fontWeight: 600, letterSpacing: 1 }}>
      feeedge.com · free · 30 seconds</div>
  </Center>);
};

export const ReelFunding: React.FC = () => {
  const S = { hook: 99, agitate: 120, payoff: 206, compare: 157, cta: 101 };
  let t = 0; const seq = (d: number) => { const from = t; t += d; return { from, durationInFrames: d }; };
  return (<Bg>
    <Sequence {...seq(S.hook)}><Hook dur={S.hook} /></Sequence>
    <Sequence {...seq(S.agitate)}><Agitate dur={S.agitate} /></Sequence>
    <Sequence {...seq(S.payoff)}><Payoff dur={S.payoff} /></Sequence>
    <Sequence {...seq(S.compare)}><Compare dur={S.compare} /></Sequence>
    <Sequence {...seq(S.cta)}><Cta dur={S.cta} /></Sequence>
  </Bg>);
};
