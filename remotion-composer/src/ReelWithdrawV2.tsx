// Withdrawal reel, v2. Rebuilt from the X ad funnel data on the v1 cut:
// 15,145 video starts -> 4,202 reached 2 seconds (72% gone) -> 348 completions,
// but 21 of those 348 completers clicked (6%). The offer and CTA were fine; the
// hook was buried. v1 opened on "SAME USDT." in muted grey with ~80% of the
// frame empty and the actual payoff ("$1 or $25") rising at frame 20, so the
// scroll-stopping moment landed at ~0.7s at the earliest and read as a blank
// post before that.
//
// v2 rules, all aimed at frame 0:
//  - the payoff IS frame 0: no fade-in ramp, no spring delay on the hero
//  - three stacked elements fill the vertical frame instead of one line
//  - numbers 240px (v1: 170px), high contrast, no grey on the hook
//  - 4 scenes and ~14s instead of 5 scenes and ~19.8s, so completion is cheaper
import { Sequence, spring, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { Bg, Center, Bar, useFade, useRise, WHITE, MUTED, AMBER, EMERALD_B } from "./reelKit";

// Fade OUT only. useFade() always ramps in, and even a 1-frame ramp leaves frame
// 0 at opacity 0, which is the exact failure this cut exists to fix: the hook
// has to be fully visible on the very first frame.
const useFadeOutOnly = (dur: number, outF = 8) =>
  interpolate(useCurrentFrame(), [dur - outF, dur], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

// The whole argument, readable in one frame. useFade(dur, 0, 8) = no in-ramp.
const Payoff: React.FC<{ dur: number }> = ({ dur }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  // Slight settle on the amber number only, so there is motion without the
  // frame ever being empty: starts at 0.96 scale, not at zero opacity.
  const settle = spring({ frame: f, fps, config: { damping: 14, stiffness: 200 }, from: 0.96, to: 1 });
  return (
    <Center op={useFadeOutOnly(dur)}>
      <div style={{ fontSize: 46, fontWeight: 700, letterSpacing: 3, color: MUTED, marginBottom: 26 }}>
        SEND $1,000 USDT
      </div>
      <div style={{ display: "flex", alignItems: "baseline", gap: 44, transform: `scale(${settle})` }}>
        <span style={{ fontSize: 240, fontWeight: 800, color: EMERALD_B, letterSpacing: -8 }}>$1</span>
        <span style={{ fontSize: 84, fontWeight: 700, color: MUTED }}>or</span>
        <span style={{ fontSize: 240, fontWeight: 800, color: AMBER, letterSpacing: -8,
          textShadow: "0 0 110px rgba(245,158,11,.45)" }}>$25</span>
      </div>
      <div style={{ marginTop: 40, background: "rgba(245,158,11,.14)", border: `2px solid ${AMBER}`,
        color: AMBER, fontWeight: 800, fontSize: 44, padding: "14px 38px", borderRadius: 999 }}>
        25× on the wrong network
      </div>
    </Center>
  );
};

const Mechanism: React.FC<{ dur: number }> = ({ dur }) => {
  const a = useRise(2), b = useRise(14);
  const chip = (label: string, note: string, color: string, style: React.CSSProperties) => (
    <div style={{ ...style, width: 640, padding: "24px 34px", borderRadius: 22,
      background: "rgba(255,255,255,.04)", border: `1px solid ${color}55`, marginBottom: 18, textAlign: "left" }}>
      <div style={{ fontSize: 54, color, fontWeight: 800, letterSpacing: -.5 }}>{label}</div>
      <div style={{ fontSize: 34, color: MUTED, fontWeight: 500, marginTop: 6 }}>{note}</div>
    </div>
  );
  return (
    <Center op={useFade(dur)}>
      <div style={{ ...a, fontSize: 66, fontWeight: 800, letterSpacing: -1.2, color: WHITE, marginBottom: 34, lineHeight: 1.15 }}>
        Same coin. Same amount.
      </div>
      {chip("TRC20 · Tron", "about a dollar", EMERALD_B, b)}
      {chip("ERC20 · Ethereum", "pays Ethereum gas", AMBER, b)}
    </Center>
  );
};

const Agitate: React.FC<{ dur: number }> = ({ dur }) => {
  const a = useRise(2), b = useRise(16);
  return (
    <Center op={useFade(dur)}>
      <div style={{ ...a, fontSize: 76, fontWeight: 800, letterSpacing: -1.4, color: WHITE, lineHeight: 1.15 }}>
        Almost nobody checks.
      </div>
      <div style={{ ...b, fontSize: 52, color: EMERALD_B, marginTop: 30, fontWeight: 700 }}>
        It just leaves the balance.
      </div>
      <div style={{ display: "flex", gap: 150, alignItems: "flex-end", marginTop: 56 }}>
        <Bar label="TRC20" value={1} shownMax={25} barMax={25} color={EMERALD_B} delay={6} />
        <Bar label="ERC20" value={25} shownMax={25} barMax={25} color={AMBER} delay={14} />
      </div>
    </Center>
  );
};

const Cta: React.FC<{ dur: number }> = ({ dur }) => {
  const a = useRise(2), b = useRise(18);
  return (
    <Center op={useFade(dur)}>
      <div style={{ ...a, fontSize: 70, fontWeight: 800, letterSpacing: -1.2, color: WHITE, lineHeight: 1.18 }}>
        Check the route<br />before you send.
      </div>
      <div style={{ ...b, marginTop: 40, fontSize: 60, fontWeight: 800, color: EMERALD_B }}>feeedge.com</div>
      <div style={{ ...b, marginTop: 16, fontSize: 38, color: MUTED, fontWeight: 500 }}>Free. About 10 seconds.</div>
    </Center>
  );
};

// Scene lengths are overwritten by gen_reel_vo_v2.py once the VO is measured, so
// each line lands on its own scene. Defaults here are a sane ~14s cut.
// VO-locked (see gen_vo_withdraw_v2.py) except `payoff`, which gets ~25 extra
// frames beyond its narration so the hook holds on screen a beat after the line
// lands. Everything after it moves fast.
export const S = { payoff: 122, mechanism: 99, agitate: 101, cta: 113 };

export const ReelWithdrawV2: React.FC = () => {
  let t = 0;
  const seq = (d: number) => { const from = t; t += d; return { from, durationInFrames: d }; };
  return (
    <Bg>
      <Sequence {...seq(S.payoff)}><Payoff dur={S.payoff} /></Sequence>
      <Sequence {...seq(S.mechanism)}><Mechanism dur={S.mechanism} /></Sequence>
      <Sequence {...seq(S.agitate)}><Agitate dur={S.agitate} /></Sequence>
      <Sequence {...seq(S.cta)}><Cta dur={S.cta} /></Sequence>
    </Bg>
  );
};
