/**
 * CatSpace — "MILO: THE CAT WHO WANTED SPACE"
 *
 * Vertical viral short. 1080x1920, 30 fps, 1650 frames (55.000s),
 * cut as 30 hand-generated keyframes at 55 frames each (1.833s per frame).
 *
 * Every timing constant below is derived from FPS/SHOT_FRAMES so the
 * "30 frames in 55 seconds at 30 fps" contract can't silently drift.
 */
import React from "react";
import {
  AbsoluteFill,
  Audio,
  Img,
  Sequence,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
  Easing,
} from "remotion";
import { ANTON_WOFF2_BASE64 } from "./antonFont";

/**
 * Anton is vendored from the @fontsource/anton npm package and inlined as a
 * base64 data URI rather than fetched from Google Fonts, so the composition
 * renders with no external network access. It is installed synchronously at
 * module scope — an async FontFace load behind delayRender() is not used here
 * because the handle outlives the render loop and trips Remotion's timeout.
 */
const DISPLAY_FONT = "AntonLocal";

if (typeof document !== "undefined") {
  const style = document.createElement("style");
  style.textContent = `@font-face{font-family:'${DISPLAY_FONT}';font-style:normal;font-weight:400;font-display:block;src:url(data:font/woff2;base64,${ANTON_WOFF2_BASE64}) format('woff2');}`;
  document.head.appendChild(style);
}

export const FPS = 30;
export const SHOT_COUNT = 30;
export const SHOT_FRAMES = 55; // 1.8333s per keyframe
export const TOTAL_FRAMES = SHOT_COUNT * SHOT_FRAMES; // 1650 = 55.000s
const XFADE = 7; // cross-dissolve length in frames

const ACCENT = "#FFC93C";
const ACCENT_2 = "#5BE3FF";

/** Ring of offsets used to fake a thick text outline via text-shadow. */
const OUTLINE_OFFSETS: [number, number][] = (() => {
  const r = 7;
  const out: [number, number][] = [];
  for (let i = 0; i < 16; i++) {
    const a = (i / 16) * Math.PI * 2;
    out.push([
      Math.round(Math.cos(a) * r * 10) / 10,
      Math.round(Math.sin(a) * r * 10) / 10,
    ]);
  }
  return out;
})();

type Shot = {
  /** file in public/cat-space */
  src: string;
  /** caption; wrap a word in *asterisks* to highlight it */
  caption: string;
  /** ken burns direction */
  dir: "in" | "out";
  /** pan bias */
  pan: [number, number];
  /** camera shake amount (0-1), used for the launch beats */
  shake?: number;
  /** white flash on the cut */
  flash?: number;
  /** caption tint */
  tint?: string;
  /** oversized hook styling */
  hook?: boolean;
};

export const SHOTS: Shot[] = [
  { src: "shot01.png", caption: "This cat is going to *space*.", dir: "in", pan: [0, -0.4], hook: true },
  { src: "shot02.png", caption: "His name is *Milo*.", dir: "out", pan: [0, 0] },
  { src: "shot03.png", caption: "Every night. *Same moon*.", dir: "in", pan: [0.3, -0.2] },
  { src: "shot04.png", caption: "They said cats *don't fly*.", dir: "out", pan: [-0.3, 0] },
  { src: "shot05.png", caption: "Milo said: *watch me*.", dir: "in", pan: [0, 0.2], tint: ACCENT, flash: 0.35 },
  { src: "shot06.png", caption: "He drew the *blueprints*.", dir: "out", pan: [0.2, 0.3] },
  { src: "shot07.png", caption: "He built the *rocket*.", dir: "in", pan: [0, -0.3] },
  { src: "shot08.png", caption: "*Safety* first.", dir: "out", pan: [0, 0] },
  { src: "shot09.png", caption: "Launch attempt *one*.", dir: "in", pan: [-0.2, 0.2] },
  { src: "shot10.png", caption: "...that was *not* space.", dir: "out", pan: [0.4, 0], shake: 0.5, flash: 0.5 },
  { src: "shot11.png", caption: "*Forty-seven* times.", dir: "in", pan: [0, 0.3] },
  { src: "shot12.png", caption: "He almost *quit*.", dir: "out", pan: [0, -0.2] },
  { src: "shot13.png", caption: "Then he found *the fence*.", dir: "in", pan: [0, -0.3], tint: ACCENT_2 },
  { src: "shot14.png", caption: "So he *trained*.", dir: "out", pan: [-0.3, 0.2] },
  { src: "shot15.png", caption: "*Zero-g* practice.", dir: "in", pan: [0.3, 0.1] },
  { src: "shot16.png", caption: "He studied the *stars*.", dir: "out", pan: [0.2, -0.2] },
  { src: "shot17.png", caption: "*G-force* training.", dir: "in", pan: [0, 0], shake: 0.35 },
  { src: "shot18.png", caption: "They built him a *suit*.", dir: "out", pan: [0, -0.25], tint: ACCENT },
  { src: "shot19.png", caption: "The *long walk*.", dir: "in", pan: [0.25, 0] },
  { src: "shot20.png", caption: "*No* turning back.", dir: "out", pan: [0, 0.2] },
  { src: "shot21.png", caption: "*Three.*", dir: "in", pan: [0, 0], tint: ACCENT },
  { src: "shot22.png", caption: "*Two.*", dir: "in", pan: [0, 0.3], shake: 0.5, flash: 0.6, tint: ACCENT },
  { src: "shot23.png", caption: "*One.*", dir: "in", pan: [0, -0.5], shake: 0.7, tint: ACCENT },
  { src: "shot24.png", caption: "*LIFTOFF.*", dir: "in", pan: [0, -0.6], shake: 1, flash: 0.85, tint: ACCENT },
  { src: "shot25.png", caption: "And then... *silence*.", dir: "out", pan: [0, 0] },
  { src: "shot26.png", caption: "He *floated*.", dir: "in", pan: [0, 0.15] },
  { src: "shot27.png", caption: "He saw *home*.", dir: "out", pan: [0, -0.2], tint: ACCENT_2 },
  { src: "shot28.png", caption: "*Worth it.*", dir: "in", pan: [0, 0] },
  { src: "shot29.png", caption: "Wait. Was that a *can opener*?", dir: "in", pan: [0, 0.1], tint: ACCENT, flash: 0.3 },
  { src: "shot30.png", caption: "Space is nice. *Dinner is better.*", dir: "out", pan: [0, 0.2] },
];

/** Voice-over cues, hand-placed against measured clip durations (seconds). */
const VO: { src: string; at: number; vol?: number }[] = [
  { src: "vo1.mp3", at: 0.0 },
  { src: "vo2.mp3", at: 10.5 },
  { src: "vo3.mp3", at: 19.6 },
  { src: "vo4.mp3", at: 29.2 },
  { src: "mc1.mp3", at: 33.5, vol: 0.92 },
  { src: "mc2.mp3", at: 40.75, vol: 0.92 },
  { src: "vo5.mp3", at: 44.15 },
  { src: "milo1.mp3", at: 51.4 },
  { src: "milo2.mp3", at: 53.05 },
];

const asset = (f: string) => staticFile(`cat-space/${f}`);

// --------------------------------------------------------------------------
// Caption
// --------------------------------------------------------------------------

const Caption: React.FC<{ text: string; hook?: boolean; tint?: string }> = ({
  text,
  hook,
  tint,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const pop = spring({ frame, fps, config: { damping: 13, stiffness: 190, mass: 0.6 } });
  const scale = interpolate(pop, [0, 1], [0.72, 1]);
  const rise = interpolate(pop, [0, 1], [46, 0]);
  const out = interpolate(frame, [SHOT_FRAMES - 6, SHOT_FRAMES], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const parts = text.split(/(\*[^*]+\*)/g).filter(Boolean);
  const size = hook ? 108 : 88;

  return (
    <AbsoluteFill
      style={{
        justifyContent: "flex-end",
        alignItems: "center",
        paddingBottom: 300,
        opacity: out,
      }}
    >
      <div
        style={{
          transform: `translateY(${rise}px) scale(${scale})`,
          maxWidth: 900,
          textAlign: "center",
          fontFamily: `${DISPLAY_FONT}, 'Arial Black', Impact, sans-serif`,
          fontSize: size,
          lineHeight: 1.02,
          letterSpacing: -1,
          textTransform: "uppercase",
          color: "#FFFFFF",
          // hard outline built from stacked shadows — reliable in headless
          // Chromium, where -webkit-text-stroke + paint-order is inconsistent
          textShadow: [
            ...OUTLINE_OFFSETS.map(([x, y]) => `${x}px ${y}px 0 #000`),
            "0 12px 30px rgba(0,0,0,0.9)",
            "0 0 80px rgba(0,0,0,0.7)",
          ].join(", "),
        }}
      >
        {parts.map((p, i) =>
          p.startsWith("*") && p.endsWith("*") ? (
            <span key={i} style={{ color: tint ?? ACCENT }}>
              {p.slice(1, -1)}
            </span>
          ) : (
            <span key={i}>{p}</span>
          )
        )}
      </div>
    </AbsoluteFill>
  );
};

// --------------------------------------------------------------------------
// Shot
// --------------------------------------------------------------------------

const ShotView: React.FC<{ shot: Shot; index: number }> = ({ shot, index }) => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();

  const p = interpolate(frame, [0, SHOT_FRAMES], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.33, 0, 0.67, 1),
  });

  const zoom =
    shot.dir === "in"
      ? interpolate(p, [0, 1], [1.06, 1.19])
      : interpolate(p, [0, 1], [1.19, 1.06]);

  const px = interpolate(p, [0, 1], [0, shot.pan[0] * 60]);
  const py = interpolate(p, [0, 1], [0, shot.pan[1] * 60]);

  // camera shake on the launch beats
  const sh = shot.shake ?? 0;
  const sx = sh ? Math.sin(frame * 2.9) * 9 * sh * (1 - p * 0.45) : 0;
  const sy = sh ? Math.cos(frame * 3.7) * 9 * sh * (1 - p * 0.45) : 0;

  // dissolve in from the previous shot
  const fadeIn =
    index === 0
      ? 1
      : interpolate(frame, [0, XFADE], [0, 1], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        });

  const flash = shot.flash
    ? interpolate(frame, [0, 4, 12], [shot.flash, shot.flash * 0.55, 0], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      })
    : 0;

  return (
    <AbsoluteFill style={{ opacity: fadeIn, backgroundColor: "#05060B" }}>
      <AbsoluteFill style={{ overflow: "hidden" }}>
        <Img
          src={asset(shot.src)}
          style={{
            width,
            height,
            objectFit: "cover",
            transform: `translate(${px + sx}px, ${py + sy}px) scale(${zoom})`,
            transformOrigin: "center center",
          }}
        />
      </AbsoluteFill>

      {/* cinematic grade: top + bottom falloff so captions always read */}
      <AbsoluteFill
        style={{
          background:
            "linear-gradient(180deg, rgba(3,5,12,0.62) 0%, rgba(3,5,12,0) 26%, rgba(3,5,12,0) 52%, rgba(3,5,12,0.78) 100%)",
        }}
      />
      {/* vignette */}
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(ellipse at 50% 46%, rgba(0,0,0,0) 42%, rgba(0,0,0,0.55) 100%)",
        }}
      />
      {flash > 0 && (
        <AbsoluteFill style={{ backgroundColor: "#FFFFFF", opacity: flash }} />
      )}

      <Caption text={shot.caption} hook={shot.hook} tint={shot.tint} />
    </AbsoluteFill>
  );
};

// --------------------------------------------------------------------------
// Chrome: grain, progress bar
// --------------------------------------------------------------------------

const Grain: React.FC = () => {
  const frame = useCurrentFrame();
  const shift = (frame * 37) % 200;
  return (
    <AbsoluteFill
      style={{
        opacity: 0.06,
        mixBlendMode: "overlay",
        backgroundImage:
          "url(\"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='200' height='200'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='3'/></filter><rect width='200' height='200' filter='url(%23n)'/></svg>\")",
        backgroundPosition: `${shift}px ${shift * 0.7}px`,
      }}
    />
  );
};

const Progress: React.FC = () => {
  const frame = useCurrentFrame();
  const pct = (frame / TOTAL_FRAMES) * 100;
  return (
    <AbsoluteFill style={{ justifyContent: "flex-start" }}>
      <div style={{ height: 9, width: "100%", background: "rgba(255,255,255,0.14)" }}>
        <div
          style={{
            height: "100%",
            width: `${pct}%`,
            background: `linear-gradient(90deg, ${ACCENT_2}, ${ACCENT})`,
            boxShadow: `0 0 22px ${ACCENT}`,
          }}
        />
      </div>
    </AbsoluteFill>
  );
};

// --------------------------------------------------------------------------
// Root composition
// --------------------------------------------------------------------------

export const CatSpace: React.FC = () => {
  const frame = useCurrentFrame();

  // music ducks under every voice cue
  const ducked = VO.some((v) => {
    const s = v.at * FPS;
    return frame > s - 6 && frame < s + 9 * FPS;
  });

  const fadeOut = interpolate(frame, [TOTAL_FRAMES - 18, TOTAL_FRAMES], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ backgroundColor: "#05060B" }}>
      <AbsoluteFill style={{ opacity: fadeOut }}>
        {SHOTS.map((shot, i) => (
          <Sequence
            key={shot.src}
            from={i * SHOT_FRAMES}
            durationInFrames={SHOT_FRAMES + XFADE}
            layout="none"
          >
            <ShotView shot={shot} index={i} />
          </Sequence>
        ))}

        <Grain />
        <Progress />
      </AbsoluteFill>

      <Audio src={asset("score.wav")} volume={ducked ? 0.17 : 0.34} />
      {VO.map((v) => (
        <Sequence key={v.src} from={Math.round(v.at * FPS)} layout="none">
          <Audio src={asset(v.src)} volume={v.vol ?? 1} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
