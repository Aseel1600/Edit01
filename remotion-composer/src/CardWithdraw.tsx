// Static image cards for the X ad, 1200x1200 (1:1).
//
// Why 1:1 and not the 9:16 still we're currently running: the winning static is
// literally frame 0 of the reel, so it's a tall video frame. X tends to crop tall
// images in-feed, which risks cutting the pill or the label. 1:1 is the largest
// safe footprint in a timeline.
//
// Why these numbers: the live ad says "$1 or $25", which the product's own
// WITHDRAWAL_FEES data does not support (real range is $0.80 to $7.50 across
// tracked venues). A fee-comparison site cannot run a number its own page
// contradicts, so these cards use the verified figures. Still a ~9x spread,
// which is plenty, and it survives the click.
import { AbsoluteFill, Img, staticFile } from "remotion";
import { loadFont } from "@remotion/google-fonts/Sora";
import { BG, EMERALD_B, AMBER, WHITE, MUTED, FAINT } from "./reelKit";
const { fontFamily } = loadFont();

const Shell: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <AbsoluteFill style={{ backgroundColor: BG, fontFamily }}>
    <AbsoluteFill style={{ background:
      "radial-gradient(700px 700px at 82% 4%, rgba(16,185,129,.18), transparent 60%)," +
      "radial-gradient(650px 650px at 10% 100%, rgba(16,185,129,.10), transparent 62%)" }} />
    <AbsoluteFill style={{
      backgroundImage:
        "linear-gradient(rgba(255,255,255,.028) 1px,transparent 1px)," +
        "linear-gradient(90deg,rgba(255,255,255,.028) 1px,transparent 1px)",
      backgroundSize: "72px 72px",
      maskImage: "radial-gradient(circle at 50% 45%, black, transparent 78%)" }} />
    <div style={{ position: "absolute", top: 48, left: 0, right: 0, display: "flex",
      justifyContent: "center", alignItems: "center", gap: 14 }}>
      <Img src={staticFile("feeedge/logo-mark.png")} style={{ width: 46, height: 46 }} />
      <div style={{ fontSize: 34, fontWeight: 800, letterSpacing: -.5, color: WHITE }}>
        Fee<span style={{ color: EMERALD_B }}>Edge</span></div>
    </div>
    <div style={{ position: "absolute", bottom: 44, left: 0, right: 0, textAlign: "center",
      fontSize: 21, color: FAINT }}>Published rates, estimates only. Not financial advice.</div>
    {children}
  </AbsoluteFill>
);

// Variant A: the contrast that already won, at real numbers and a safe ratio.
export const CardWithdrawA: React.FC = () => (
  <Shell>
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", textAlign: "center", padding: "0 70px" }}>
      <div style={{ fontSize: 36, fontWeight: 700, letterSpacing: 2.5, color: MUTED, marginBottom: 22 }}>
        WITHDRAW 1,000 USDT
      </div>
      {/* 150px, not 190px: these are 5-character numbers ("$0.80"), so at 190px
          the pair overflowed a 1200px frame and both ends were clipped. Two
          numbers + separator + gaps now measure ~930px inside 1060px of usable
          width. Do not raise this without re-checking the render. */}
      <div style={{ display: "flex", alignItems: "baseline", gap: 30, maxWidth: "100%" }}>
        <span style={{ fontSize: 150, fontWeight: 800, color: EMERALD_B, letterSpacing: -5,
          whiteSpace: "nowrap" }}>$0.80</span>
        <span style={{ fontSize: 58, fontWeight: 700, color: MUTED }}>or</span>
        <span style={{ fontSize: 150, fontWeight: 800, color: AMBER, letterSpacing: -5,
          whiteSpace: "nowrap", textShadow: "0 0 100px rgba(245,158,11,.45)" }}>$7.50</span>
      </div>
      <div style={{ marginTop: 34, background: "rgba(245,158,11,.14)", border: `2px solid ${AMBER}`,
        color: AMBER, fontWeight: 800, fontSize: 40, padding: "13px 34px", borderRadius: 999 }}>
        9× for the identical transfer
      </div>
      <div style={{ marginTop: 30, fontSize: 34, color: MUTED, fontWeight: 500 }}>
        Same coin. Same amount. Different venue.
      </div>
    </AbsoluteFill>
  </Shell>
);

// Variant B: the same fact as data. Leans on the thing no competitor has, and
// reads as a screenshot of real rates rather than as an ad.
const ROWS: Array<[string, string, string, boolean]> = [
  ["Bitget", "ERC20", "$0.80", true],
  ["Binance", "TRC20", "$1.00", true],
  ["HTX", "ERC20", "$1.39", true],
  ["Binance", "ERC20", "$4.00", false],
  ["KuCoin", "ERC20", "$5.50", false],
  ["Kraken", "ERC20", "$7.00", false],
  ["Toobit", "ERC20", "$7.50", false],
];

export const CardWithdrawB: React.FC = () => (
  <Shell>
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", padding: "0 90px" }}>
      <div style={{ fontSize: 52, fontWeight: 800, letterSpacing: -1, color: WHITE, marginBottom: 8, textAlign: "center" }}>
        Sending 1,000 USDT costs
      </div>
      <div style={{ fontSize: 52, fontWeight: 800, letterSpacing: -1, color: AMBER, marginBottom: 30 }}>
        9× more on the wrong route
      </div>
      <div style={{ width: "100%", borderRadius: 20, overflow: "hidden",
        border: "1px solid rgba(255,255,255,.10)", background: "rgba(255,255,255,.03)" }}>
        {ROWS.map(([venue, net, fee, cheap], i) => (
          <div key={i} style={{ display: "flex", alignItems: "center", gap: 16,
            padding: "17px 26px", borderTop: i ? "1px solid rgba(255,255,255,.06)" : "none" }}>
            <div style={{ fontSize: 34, fontWeight: 700, color: WHITE, width: 200, textAlign: "left" }}>{venue}</div>
            <div style={{ fontSize: 27, fontWeight: 600, color: MUTED, letterSpacing: 1 }}>{net}</div>
            <div style={{ marginLeft: "auto", fontSize: 40, fontWeight: 800,
              color: cheap ? EMERALD_B : AMBER, fontVariantNumeric: "tabular-nums" }}>{fee}</div>
          </div>
        ))}
      </div>
      <div style={{ marginTop: 26, fontSize: 32, color: MUTED, fontWeight: 500, textAlign: "center" }}>
        Check your route free at <span style={{ color: EMERALD_B, fontWeight: 800 }}>feeedge.com</span>
      </div>
    </AbsoluteFill>
  </Shell>
);
