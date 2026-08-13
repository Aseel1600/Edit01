import { Composition, CalculateMetadataFunction } from "remotion";
import { PropertyLabelDemo } from "./PropertyLabelDemo";
import { ToLiveCascais } from "./ToLiveCascais";
import { PauloMartinsCinematicoV2, TOTAL_FRAMES as PM_FRAMES } from "./clientes/PauloMartinsCinematicoV2";
import { Explainer, ExplainerProps } from "./Explainer";
import {
  CinematicRenderer,
  calculateCinematicMetadata,
} from "./CinematicRenderer";
import { signalFromTomorrowWithMusicFixture } from "./cinematic/fixtures";
import { TalkingHead, TalkingHeadProps } from "./TalkingHead";
import {
  TitledVideo,
  calculateTitledVideoMetadata,
} from "./TitledVideo";
import { EndTag, EndTagProps } from "./components/EndTag";
import { HeroTitle } from "./components/HeroTitle";
import { ProductReveal, ProductRevealProps } from "./components/ProductReveal";
import { CaptionOverlay, WordCaption } from "./components/CaptionOverlay";
import { CollageBurst, CollageBurstProps } from "./CollageBurst";
import { LyricOverlay, LyricOverlayProps } from "./LyricOverlay";
import { MarketLedger, calculateMarketLedgerMetadata } from "./MarketLedger";
import { FeeEdgeAd } from "./FeeEdgeAd";
import { FeeEdgeReel } from "./FeeEdgeReel";
import { ReelFunding } from "./ReelFunding";
import { ReelSpread } from "./ReelSpread";
import { ReelWithdraw } from "./ReelWithdraw";
import { ReelWithdrawV2, S as SW2 } from "./ReelWithdrawV2";
import { CardWithdrawA, CardWithdrawB } from "./CardWithdraw";

// ---------------------------------------------------------------------------
// Theme System — prevents every video from looking like dark fintech
// ---------------------------------------------------------------------------

export interface ThemeConfig {
  primaryColor: string;
  accentColor: string;
  backgroundColor: string;
  surfaceColor: string;
  textColor: string;
  mutedTextColor: string;
  headingFont: string;
  bodyFont: string;
  monoFont: string;
  chartColors: string[];
  springConfig: { damping: number; stiffness: number; mass: number };
  transitionDuration: number;
  captionHighlightColor: string;
  captionBackgroundColor: string;
}

export const THEMES: Record<string, ThemeConfig> = {
  "clean-professional": {
    primaryColor: "#2563EB",
    accentColor: "#F59E0B",
    backgroundColor: "#FFFFFF",
    surfaceColor: "#F9FAFB",
    textColor: "#1F2937",
    mutedTextColor: "#6B7280",
    headingFont: "Inter",
    bodyFont: "Inter",
    monoFont: "JetBrains Mono",
    chartColors: ["#2563EB", "#F59E0B", "#10B981", "#8B5CF6", "#EC4899", "#06B6D4"],
    springConfig: { damping: 20, stiffness: 120, mass: 1 },
    transitionDuration: 0.4,
    captionHighlightColor: "#2563EB",
    captionBackgroundColor: "rgba(255, 255, 255, 0.85)",
  },
  "flat-motion-graphics": {
    primaryColor: "#7C3AED",
    accentColor: "#EC4899",
    backgroundColor: "#0F172A",
    surfaceColor: "#1E293B",
    textColor: "#F8FAFC",
    mutedTextColor: "#94A3B8",
    headingFont: "Space Grotesk",
    bodyFont: "Space Grotesk",
    monoFont: "Fira Code",
    chartColors: ["#7C3AED", "#EC4899", "#06B6D4", "#F59E0B", "#10B981", "#EF4444"],
    springConfig: { damping: 12, stiffness: 80, mass: 1 },
    transitionDuration: 0.3,
    captionHighlightColor: "#22D3EE",
    captionBackgroundColor: "rgba(15, 23, 42, 0.75)",
  },
  "minimalist-diagram": {
    primaryColor: "#1A1A2E",
    accentColor: "#E94560",
    backgroundColor: "#FAFAFA",
    surfaceColor: "#FFFFFF",
    textColor: "#1A1A2E",
    mutedTextColor: "#6B7280",
    headingFont: "IBM Plex Sans",
    bodyFont: "IBM Plex Sans",
    monoFont: "IBM Plex Mono",
    chartColors: ["#E94560", "#1A1A2E", "#0F3460", "#9CA3AF"],
    springConfig: { damping: 25, stiffness: 150, mass: 1 },
    transitionDuration: 0.5,
    captionHighlightColor: "#E94560",
    captionBackgroundColor: "rgba(250, 250, 250, 0.9)",
  },
  "anime-ghibli": {
    primaryColor: "#2D5016",
    accentColor: "#FFB347",
    backgroundColor: "#0A0A1A",
    surfaceColor: "#1A2332",
    textColor: "#F0E6D3",
    mutedTextColor: "#A8957E",
    headingFont: "Noto Serif JP",
    bodyFont: "Noto Sans",
    monoFont: "Fira Code",
    chartColors: ["#FFB347", "#2D5016", "#FF6B9D", "#A8E6CF", "#6B4C8A", "#E8927C"],
    springConfig: { damping: 18, stiffness: 60, mass: 1 },
    transitionDuration: 1.0,
    captionHighlightColor: "#FFB347",
    captionBackgroundColor: "rgba(10, 10, 26, 0.8)",
  },
};

// Default theme when none is specified — uses the existing dark style for backwards compatibility
export const DEFAULT_THEME = THEMES["flat-motion-graphics"];

export function resolveTheme(props: Record<string, unknown>): ThemeConfig {
  const themeName = (props.theme as string) || (props.playbook as string);
  if (themeName && THEMES[themeName]) {
    return THEMES[themeName];
  }
  // Allow custom theme passed as full object
  if (props.themeConfig && typeof props.themeConfig === "object") {
    return { ...DEFAULT_THEME, ...(props.themeConfig as Partial<ThemeConfig>) };
  }
  return DEFAULT_THEME;
}

const calculateMetadata: CalculateMetadataFunction<ExplainerProps> = async ({
  props,
}) => {
  const cuts = props.cuts || [];
  if (cuts.length === 0) {
    return { durationInFrames: 30 * 60 };
  }
  const lastEnd = Math.max(...cuts.map((c) => c.out_seconds || 0));
  // Add 1 second padding for final fade
  return { durationInFrames: Math.ceil((lastEnd + 1) * 30) };
};

export const Root: React.FC = () => {
  return (
    <>
      <Composition
        id="FeeEdgeAd"
        component={FeeEdgeAd}
        durationInFrames={660}
        fps={30}
        width={1920}
        height={1080}
      />
      <Composition
        id="FeeEdgeReel"
        component={FeeEdgeReel}
        durationInFrames={719}
        fps={30}
        width={1080}
        height={1920}
      />
      <Composition
        id="ReelFunding"
        component={ReelFunding}
        durationInFrames={683}
        fps={30}
        width={1080}
        height={1920}
      />
      <Composition
        id="ReelSpread"
        component={ReelSpread}
        durationInFrames={652}
        fps={30}
        width={1080}
        height={1920}
      />
      <Composition
        id="ReelWithdraw"
        component={ReelWithdraw}
        durationInFrames={594}
        fps={30}
        width={1080}
        height={1920}
      />
      <Composition
        id="ReelWithdrawV2"
        component={ReelWithdrawV2}
        durationInFrames={SW2.payoff + SW2.mechanism + SW2.agitate + SW2.cta}
        fps={30}
        width={1080}
        height={1920}
      />
      {/* Static ad cards, 1:1. Rendered as stills, so 1 frame is enough. */}
      <Composition
        id="CardWithdrawA"
        component={CardWithdrawA}
        durationInFrames={1}
        fps={30}
        width={1200}
        height={1200}
      />
      <Composition
        id="CardWithdrawB"
        component={CardWithdrawB}
        durationInFrames={1}
        fps={30}
        width={1200}
        height={1200}
      />
      <Composition
        id="Explainer"
        component={Explainer}
        durationInFrames={30 * 60}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          cuts: [],
          overlays: [],
          captions: [],
          audio: {},
        }}
        calculateMetadata={calculateMetadata}
      />
      <Composition
        id="CinematicRenderer"
        component={CinematicRenderer}
        durationInFrames={30 * 30}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          scenes: [],
          titleFontSize: 78,
          titleWidth: 1320,
          signalLineCount: 18,
        }}
        calculateMetadata={calculateCinematicMetadata}
      />
      <Composition
        id="SignalFromTomorrowWithMusic"
        component={CinematicRenderer}
        durationInFrames={30 * 30}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={signalFromTomorrowWithMusicFixture}
        calculateMetadata={calculateCinematicMetadata}
      />
      <Composition
        id="TalkingHead"
        component={TalkingHead}
        durationInFrames={30 * 300}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          videoSrc: "",
          captions: [],
          overlays: [],
          wordsPerPage: 4,
          fontSize: 52,
          highlightColor: "#22D3EE",
        }}
      />
      <Composition
        id="TitledVideo"
        component={TitledVideo}
        durationInFrames={30 * 60}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          videoSrc: "",
          tagline: "home is a verb.",
          taglineInSeconds: 53.5,
          taglineOutSeconds: undefined,
          topPx: 150,
          fontSize: 148,
          accentColor: "#F5C470",
        }}
        calculateMetadata={calculateTitledVideoMetadata}
      />
      <Composition
        id="HeroTitle"
        component={HeroTitle}
        durationInFrames={30 * 17}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          title: "THE CALIBRATORS",
          subtitle: "The People Who Define Reality",
        }}
      />
      <Composition
        id="ProductReveal"
        component={ProductReveal}
        durationInFrames={30 * 8}
        fps={30}
        width={1280}
        height={720}
        defaultProps={{
          productImage: "airnothing/product.png",
          productName: "AirNothing Pro Max Ultra",
          price: "Starting at $999",
          tagline: "Nothing included.",
          closer: "Less is nothing.",
          accentColor: "#00D4FF",
        } as ProductRevealProps}
      />
      <Composition
        id="ProductRevealVertical"
        component={ProductReveal}
        durationInFrames={30 * 8}
        fps={30}
        width={720}
        height={1280}
        defaultProps={{
          productImage: "airnothing/product.png",
          productName: "AirNothing Pro Max Ultra",
          price: "Starting at $999",
          tagline: "Nothing included.",
          closer: "Less is nothing.",
          accentColor: "#00D4FF",
        } as ProductRevealProps}
      />
      <Composition
        id="CaptionOverlayOnly"
        component={CaptionOverlay}
        durationInFrames={30 * 300}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          words: [] as WordCaption[],
          wordsPerPage: 3,
          fontSize: 58,
          highlightColor: "#FACC15",
          backgroundColor: "rgba(15, 23, 42, 0.75)",
        }}
      />
      <Composition
        id="CollageBurst"
        component={CollageBurst}
        durationInFrames={30 * 30}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          backgroundSrc: "",
          backgroundInSeconds: 0,
          curtainStartSeconds: 1.5,
          curtainEndSeconds: 3.0,
          clips: [],
        } as CollageBurstProps}
      />
      <Composition
        id="LyricOverlay"
        component={LyricOverlay}
        durationInFrames={30 * 28}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          videoSrc: "",
          lyrics: [],
          bottomY: 0.88,
        } as LyricOverlayProps}
      />
      <Composition
        id="MarketLedger"
        component={MarketLedger}
        durationInFrames={30 * 34}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          data: {
            accent: "#E8B24C",
            location: "COLUMBUS, OHIO",
            period: "JUNE 2026",
            masthead: "MARKET BRIEF",
            hookLine1: "The real",
            hookLine2: "numbers.",
            hookSub: "Columbus housing — no spin, just the data.",
            statLabel: "MEDIAN LIST PRICE",
            statValue: 394500,
            statPrefix: "$",
            statSuffix: "",
            statGroup: ",",
            yoy: "+1.2%",
            yoyLabel: "YEAR OVER YEAR",
            chartTitle: "SPRING CLIMB · MEDIAN LIST ($K)",
            chart: [
              { m: "MAR", v: 360 },
              { m: "APR", v: 372 },
              { m: "MAY", v: 380 },
              { m: "JUN", v: 395 },
            ],
            insightLabel: "DAYS ON MARKET",
            insightValue: 39,
            insightDisplay: null,
            insightSuffix: "",
            insightDelta: "+3 vs. last June",
            insightCaption: "Buyers get a little breathing room.",
            insightTally: 39,
            ctaTagline: "Know your market.",
            brand: "HARBORLINE REALTY",
            handle: "harborline.example",
            sourceNote: "REALTOR.COM VIA FRED · JUN 2026",
          },
          sections: {
            hook: [0, 6.68],
            stat: [6.68, 14.04],
            chart: [14.04, 20.73],
            insight: [20.73, 27.9],
            cta: [27.9, 33.48],
          },
          captions: [],
          audio: {
            narration: "market-ledger/narration_full.mp3",
            music: "market-ledger/background_music.mp3",
          },
        }}
        calculateMetadata={calculateMarketLedgerMetadata}
      />
      <Composition
        id="EndTag"
        component={EndTag}
        // 5.5s at 30fps = 165 frames. Render CLI can override via --props.
        durationInFrames={165}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          text: "THE CITY KEEPS ITS OWN VIGIL.",
          palette: "cool_offwhite_on_black",
          fadeInSeconds: 0.6,
          holdSeconds: 4.3,
          fadeOutSeconds: 0.6,
        } as EndTagProps}
      />
      <Composition
        id="EndTagOverlay"
        component={EndTag}
        // 8.19s at 30fps = 246 frames. Render CLI can override via --props.
        // Intended to be composited on top of body footage, not concat'd.
        durationInFrames={246}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          text: "EARN THE LIGHT.",
          palette: "cool_offwhite_on_black",
          fadeInSeconds: 1.0,
          holdSeconds: 5.69,
          fadeOutSeconds: 1.5,
          overlay: true,
        } as EndTagProps}
      />
      {/* ToLive Cascais: o filme ja montado em ffmpeg, so com a camada de legendas.
          3223 fotogramas = 134,29 s a 24 fps. */}
      <Composition
        id="ToLiveCascais"
        component={ToLiveCascais}
        durationInFrames={8058}
        fps={60}
        width={1920}
        height={1080}
      />
      <Composition
        id="PropertyLabelDemo"
        component={PropertyLabelDemo}
        durationInFrames={210}
        fps={24}
        width={1920}
        height={1080}
      />
      <Composition
        id="PauloMartinsCinematicoV2"
        component={PauloMartinsCinematicoV2}
        durationInFrames={PM_FRAMES}
        fps={24}
        width={1920}
        height={1080}
      />
    </>
  );
};
