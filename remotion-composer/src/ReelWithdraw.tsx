import { Sequence, spring, useCurrentFrame, useVideoConfig, Img, staticFile } from "remotion";
import { Bg, Center, Bar, useFade, useRise, WHITE, MUTED, AMBER, EMERALD, EMERALD_B } from "./reelKit";

const Hook: React.FC<{ dur: number }> = ({ dur }) => {
  const a = useRise(4), b = useRise(20);
  return (<Center op={useFade(dur)}>
    <div style={{ ...a, fontSize: 60, fontWeight: 700, letterSpacing: 2, color: WHITE, marginBottom: 30 }}>SAME USDT.</div>
    <div style={{ ...b, display: "flex", alignItems: "baseline", gap: 40 }}>
      <span style={{ fontSize: 170, fontWeight: 800, color: EMERALD_B, letterSpacing: -4 }}>$1</span>
      <span style={{ fontSize: 70, fontWeight: 700, color: MUTED }}>or</span>
      <span style={{ fontSize: 170, fontWeight: 800, color: AMBER, letterSpacing: -4, textShadow: "0 0 90px rgba(245,158,11,.4)" }}>$25</span>
    </div>
  </Center>);
};

const Agitate: React.FC<{ dur: number }> = ({ dur }) => {
  const a = useRise(4), b = useRise(24);
  return (<Center op={useFade(dur)}>
    <div style={{ ...a, fontSize: 72, fontWeight: 800, letterSpacing: -1.4, color: WHITE, lineHeight: 1.15 }}>
      The only difference?</div>
    <div style={{ ...b, fontSize: 54, color: EMERALD_B, marginTop: 30, fontWeight: 700 }}>
      One dropdown you skip.</div>
  </Center>);
};

const Reveal: React.FC<{ dur: number }> = ({ dur }) => {
  const f = useCurrentFrame(); const { fps } = useVideoConfig();
  const trc = useRise(6), erc = useRise(18);
  const t = useRise(34);
  const chip = (label: string, note: string, color: string, style: React.CSSProperties) => (
    <div style={{ ...style, width: 620, padding: "26px 34px", borderRadius: 22, background: "rgba(255,255,255,.04)",
      border: `1px solid ${color}55`, marginBottom: 20, textAlign: "left" }}>
      <div style={{ fontSize: 52, color, fontWeight: 800, letterSpacing: -.5 }}>{label}</div>
      <div style={{ fontSize: 34, color: MUTED, fontWeight: 500, marginTop: 6 }}>{note}</div></div>
  );
  return (<Center op={useFade(dur)}>
    <div style={{ fontSize: 44, color: WHITE, fontWeight: 700, marginBottom: 34 }}>Pick your <span style={{ color: AMBER }}>network</span>:</div>
    {chip("TRC20 · Tron", "barely a dollar", EMERALD_B, trc)}
    {chip("ERC20 · Ethereum", "pays Ethereum gas", AMBER, erc)}
    <div style={{ ...t, fontSize: 42, color: MUTED, marginTop: 22, fontWeight: 500 }}>Same coin. Same destination.</div>
  </Center>);
};

const Compare: React.FC<{ dur: number }> = ({ dur }) => {
  const f = useCurrentFrame(); const { fps } = useVideoConfig();
  const title = useRise(2);
  const pill = spring({ frame: f - 44, fps, config: { damping: 12, stiffness: 120 }, from: .7, to: 1 });
  return (<Center op={useFade(dur)}>
    <div style={{ ...title, fontSize: 62, fontWeight: 800, letterSpacing: -1, color: WHITE, marginBottom: 22, lineHeight: 1.15 }}>
      Withdraw $1,000 USDT</div>
    <div style={{ transform: `scale(${pill})`, opacity: pill, background: "rgba(245,158,11,.14)",
      border: `2px solid ${AMBER}`, color: AMBER, fontWeight: 800, fontSize: 40, padding: "12px 34px",
      borderRadius: 999, marginBottom: 50 }}>25× more on the wrong network</div>
    <div style={{ display: "flex", gap: 150, alignItems: "flex-end" }}>
      <Bar label="TRC20" value={1} shownMax={25} barMax={25} color={EMERALD_B} delay={8} />
      <Bar label="ERC20" value={25} shownMax={25} barMax={25} color={AMBER} delay={20} />
    </div>
  </Center>);
};

const Cta: React.FC<{ dur: number }> = ({ dur }) => {
  const f = useCurrentFrame(); const { fps } = useVideoConfig();
  const logo = spring({ frame: f, fps, config: { damping: 13, stiffness: 100 }, from: .7, to: 1 });
  const url = useRise(32);
  return (<Center op={useFade(dur)}>
    <Img src={staticFile("feeedge/logo-mark.png")} style={{ width: 150, height: 150,
      transform: `scale(${logo})`, filter: `drop-shadow(0 0 70px ${EMERALD}55)` }} />
    <div style={{ fontSize: 120, fontWeight: 800, letterSpacing: -3, color: WHITE, marginTop: 28 }}>
      Fee<span style={{ color: EMERALD_B }}>Edge</span></div>
    <div style={{ fontSize: 50, color: WHITE, marginTop: 10, fontWeight: 600, lineHeight: 1.25 }}>Check the cheapest route<br />before you send.</div>
    <div style={{ ...url, fontSize: 40, color: MUTED, marginTop: 40, fontWeight: 600, letterSpacing: 1 }}>
      feeedge.com · free</div>
  </Center>);
};

export const ReelWithdraw: React.FC = () => {
  const S = { hook: 117, agitate: 88, reveal: 160, compare: 128, cta: 101 };
  let t = 0; const seq = (d: number) => { const from = t; t += d; return { from, durationInFrames: d }; };
  return (<Bg>
    <Sequence {...seq(S.hook)}><Hook dur={S.hook} /></Sequence>
    <Sequence {...seq(S.agitate)}><Agitate dur={S.agitate} /></Sequence>
    <Sequence {...seq(S.reveal)}><Reveal dur={S.reveal} /></Sequence>
    <Sequence {...seq(S.compare)}><Compare dur={S.compare} /></Sequence>
    <Sequence {...seq(S.cta)}><Cta dur={S.cta} /></Sequence>
  </Bg>);
};
