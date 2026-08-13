import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

interface HeroTitleProps {
  /** Subtitle color — pass the theme accent for brand consistency. */
  subtitleColor?: string;
  title: string;
  subtitle?: string;
}

export const HeroTitle: React.FC<HeroTitleProps> = ({ title, subtitle, subtitleColor }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Staggered letter-by-letter spring, wrapped by WORD so lines never break
  // mid-word and the accent color always covers whole words.
  const titleWords = title.split(" ").filter((w) => w.length > 0);
  // Character index offsets per word (for the stagger delay across the title)
  const charOffsets: number[] = [];
  let charCount = 0;
  for (const w of titleWords) {
    charOffsets.push(charCount);
    charCount += w.length + 1;
  }

  return (
    <AbsoluteFill
      style={{
        justifyContent: "center",
        alignItems: "center",
        background:
          "radial-gradient(ellipse at center, rgba(15,23,42,0.35) 0%, rgba(15,23,42,0.55) 100%)",
      }}
    >
      <div style={{ textAlign: "center", maxWidth: "85%" }}>
        {/* Main title with per-character spring */}
        <div
          style={{
            fontSize: 92,
            fontWeight: 800,
            fontFamily: "Space Grotesk, Inter, system-ui, sans-serif",
            lineHeight: 1.2,
            display: "flex",
            justifyContent: "center",
            flexWrap: "wrap",
            columnGap: "0.28em",
            rowGap: 4,
          }}
        >
          {titleWords.map((word, wi) => (
            <span key={wi} style={{ display: "inline-flex", whiteSpace: "nowrap" }}>
              {word.split("").map((char, ci) => {
                const delay = (charOffsets[wi] + ci) * 1.2;
                const charSpring = spring({
                  frame: frame - delay,
                  fps,
                  config: { damping: 12, stiffness: 150 },
                });

                return (
                  <span
                    key={ci}
                    style={{
                      display: "inline-block",
                      opacity: charSpring,
                      transform: `translateY(${interpolate(charSpring, [0, 1], [30, 0])}px)`,
                      color: wi === 0 ? "#22D3EE" : "#F8FAFC", // Accent the first WORD
                    }}
                  >
                    {char}
                  </span>
                );
              })}
            </span>
          ))}
        </div>

        {/* Subtitle */}
        {subtitle && (
          <div
            style={{
              marginTop: 20,
              opacity: spring({
                frame: frame - charCount * 1.2 - 5,
                fps,
                config: { damping: 20 },
              }),
              fontSize: 38,
              fontWeight: 400,
              color: subtitleColor ?? "#A78BFA",
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
            backgroundColor: "#22D3EE",
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
