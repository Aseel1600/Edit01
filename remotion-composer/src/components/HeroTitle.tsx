import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

type HeroTitleProps = {
  title: string;
  subtitle?: string;
  /** Colour of the non-accent title characters. Default keeps the original look. */
  titleColor?: string;
  /** Colour of the first-word accent characters and the underline. Default unchanged. */
  accentColor?: string;
  /** Subtitle colour. Default unchanged. */
  subtitleColor?: string;
  /** Full CSS background for the scrim behind the title. Default unchanged. */
  scrim?: string;
};

export const HeroTitle: React.FC<HeroTitleProps> = ({
  title,
  subtitle,
  titleColor = "#F8FAFC",
  accentColor = "#22D3EE",
  subtitleColor = "#A78BFA",
  scrim = "radial-gradient(ellipse at center, rgba(15,23,42,0.35) 0%, rgba(15,23,42,0.55) 100%)",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Staggered letter-by-letter spring
  const titleChars = title.split("");

  return (
    <AbsoluteFill
      style={{
        justifyContent: "center",
        alignItems: "center",
        background: scrim,
      }}
    >
      <div style={{ textAlign: "center", maxWidth: "85%" }}>
        {/* Main title with per-character spring */}
        <div
          style={{
            fontSize: 72,
            fontWeight: 800,
            fontFamily: "Space Grotesk, Inter, system-ui, sans-serif",
            lineHeight: 1.2,
            display: "flex",
            justifyContent: "center",
            flexWrap: "wrap",
            gap: 0,
          }}
        >
          {titleChars.map((char, i) => {
            const delay = i * 1.2;
            const charSpring = spring({
              frame: frame - delay,
              fps,
              config: { damping: 12, stiffness: 150 },
            });

            return (
              <span
                key={i}
                style={{
                  display: "inline-block",
                  opacity: charSpring,
                  transform: `translateY(${interpolate(charSpring, [0, 1], [30, 0])}px)`,
                  color: i < 8 ? accentColor : titleColor, // Accent first word
                  whiteSpace: char === " " ? "pre" : undefined,
                  minWidth: char === " " ? "0.3em" : undefined,
                }}
              >
                {char}
              </span>
            );
          })}
        </div>

        {/* Subtitle */}
        {subtitle && (
          <div
            style={{
              marginTop: 20,
              opacity: spring({
                frame: frame - titleChars.length * 1.2 - 5,
                fps,
                config: { damping: 20 },
              }),
              fontSize: 28,
              fontWeight: 400,
              color: subtitleColor,
              fontFamily: "Space Grotesk, Inter, system-ui, sans-serif",
              letterSpacing: "0.1em",
              textTransform: "uppercase",
            }}
          >
            {subtitle}
          </div>
        )}

        {/* Animated underline */}
        <div
          style={{
            margin: "24px auto 0",
            height: 3,
            backgroundColor: accentColor,
            borderRadius: 2,
            width: interpolate(
              spring({
                frame: frame - 15,
                fps,
                config: { damping: 15, stiffness: 60 },
              }),
              [0, 1],
              [0, 400]
            ),
          }}
        />
      </div>
    </AbsoluteFill>
  );
};
