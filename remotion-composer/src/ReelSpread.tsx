import { Sequence, spring, useCurrentFrame, useVideoConfig, Img, staticFile } from "remotion";
import { Bg, Center, Bar, useFade, useRise, WHITE, MUTED, AMBER, EMERALD, EMERALD_B, FAINT } from "./reelKit";

const Hook: React.FC<{ dur: number }> = ({ dur }) => {
  const a = useRise(4), b = useRise(24);
  return (<Center op={useFade(dur)}>
    <div style={{ ...a, fontSize: 92, fontWeight: 800, letterSpacing: -2, color: WHITE, lineHeight: 1.08 }}>
      "Zero fees"<br />isn't <span style={{ color: AMBER }}>zero.</span></div>
    <div style={{ ...b, fontSize: 50, color: MUTED, marginTop: 36, fontWeight: 500 }}>
      The fee just moved.</div>
  </Center>);
};

const Agitate: React.FC<{ dur: number }> = ({ dur }) => {
  const a = useRise(4), b = useRise(24);
  return (<Center op={useFade(dur)}>
    <div style={{ ...a, fontSize: 74, fontWeight: 800, letterSpacing: -1.4, color: WHITE, lineHeight: 1.15 }}>
      It moved into<br />the <span style={{ color: EMERALD_B }}>price.</span></div>
    <div style={{ ...b, fontSize: 48, color: MUTED, marginTop: 30, fontWeight: 500 }}>
      They call it the spread.</div>
  </Center>);
};

const Reveal: React.FC<{ dur: number }> = ({ dur }) => {
  const f = useCurrentFrame(); const { fps } = useVideoConfig();
  const buy = useRise(6), sell = useRise(16);
  const gap = spring({ frame: f - 30, fps, config: { damping: 14, stiffness: 100 } });
  const t = useRise(38);
  const row = (label: string, price: string, color: string, style: React.CSSProperties) => (
    <div style={{ ...style, display: "flex", justifyContent: "space-between", alignItems: "center",
      width: 620, padding: "22px 34px", borderRadius: 20, background: "rgba(255,255,255,.04)",
      border: "1px solid rgba(255,255,255,.09)", marginBottom: 18 }}>
      <span style={{ fontSize: 34, color: MUTED, fontWeight: 700, letterSpacing: 1 }}>{label}</span>
      <span style={{ fontSize: 52, color, fontWeight: 800 }}>{price}</span></div>
  );
  return (<Center op={useFade(dur)}>
    {row("YOU BUY AT", "$65,024", AMBER, buy)}
    {row("YOU SELL AT", "$64,976", EMERALD_B, sell)}
    <div style={{ opacity: gap, fontSize: 44, color: WHITE, marginTop: 22, fontWeight: 700 }}>
      That <span style={{ color: AMBER }}>$48 gap</span> is yours to pay.</div>
    <div style={{ ...t, fontSize: 40, color: MUTED, marginTop: 16, fontWeight: 500 }}>Every single trade.</div>
  </Center>);
};

const Compare: React.FC<{ dur: number }> = ({ dur }) => {
  const f = useCurrentFrame(); const { fps } = useVideoConfig();
  const title = useRise(2);
  const pill = spring({ frame: f - 44, fps, config: { damping: 12, stiffness: 120 }, from: .7, to: 1 });
  return (<Center op={useFade(dur)}>
    <div style={{ ...title, fontSize: 60, fontWeight: 800, letterSpacing: -1, color: WHITE, marginBottom: 22, lineHeight: 1.15 }}>
      A "0% fee" venue can<br />cost <span style={{ color: AMBER }}>more.</span></div>
    <div style={{ transform: `scale(${pill})`, opacity: pill, background: "rgba(52,211,153,.14)",
      border: `2px solid ${EMERALD}`, color: EMERALD_B, fontWeight: 800, fontSize: 38, padding: "12px 32px",
      borderRadius: 999, marginBottom: 48 }}>All-in cost, per month</div>
    <div style={{ display: "flex", gap: 150, alignItems: "flex-end" }}>
      <Bar label={`"0% fee" venue`} value={180} shownMax={180} barMax={180} color={AMBER} delay={8} />
      <Bar label="0.1% venue" value={70} shownMax={180} barMax={180} color={EMERALD_B} delay={20} />
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
    <div style={{ fontSize: 50, color: WHITE, marginTop: 10, fontWeight: 600, lineHeight: 1.25 }}>The real cost —<br />spread included.</div>
    <div style={{ ...url, fontSize: 40, color: MUTED, marginTop: 40, fontWeight: 600, letterSpacing: 1 }}>
      feeedge.com · free · 30 seconds</div>
  </Center>);
};

export const ReelSpread: React.FC = () => {
  const S = { hook: 61, agitate: 143, reveal: 188, compare: 153, cta: 107 };
  let t = 0; const seq = (d: number) => { const from = t; t += d; return { from, durationInFrames: d }; };
  return (<Bg>
    <Sequence {...seq(S.hook)}><Hook dur={S.hook} /></Sequence>
    <Sequence {...seq(S.agitate)}><Agitate dur={S.agitate} /></Sequence>
    <Sequence {...seq(S.reveal)}><Reveal dur={S.reveal} /></Sequence>
    <Sequence {...seq(S.compare)}><Compare dur={S.compare} /></Sequence>
    <Sequence {...seq(S.cta)}><Cta dur={S.cta} /></Sequence>
  </Bg>);
};
