import React from 'react';
import {
  AbsoluteFill,
  Img,
  Video,
  interpolate,
  spring,
  useCurrentFrame,
} from 'remotion';

const FPS = 30;
const DURATION_IN_FRAMES = 36000;
const CUT_INTERVAL_FRAMES = Math.round(4.5 * FPS);
const END_LOOP_START = DURATION_IN_FRAMES - 15 * FPS;
const REHOOK_FRAMES = [3, 6, 9, 12, 15].map((m) => m * 60 * FPS);

export type MediaType = 'image' | 'video';

export interface EvidenceItem {
  id: string;
  type: MediaType;
  src: string; // Ruta accesible por Remotion (relativa o web)
  caption?: string;
  duration?: number; // En segundos u opcional
  startTime?: number; // Frame de inicio en timeline del capítulo
}

export interface UnTioBlancoHipocritaProps {
  evidences?: EvidenceItem[];
  title?: string;
  subtitle?: string;
  backgroundVideo?: string;
}

type Beat = {
  id: string;
  title: string;
  subtitle: string;
  start: number;
  duration: number;
  accent: string;
  bg: string;
};

const BEATS: Beat[] = [
  { id: 'hook', title: 'Gancho provocador', subtitle: 'La pregunta que valida la miniatura.', start: 0, duration: 900, accent: '#ff4d4d', bg: '#050505' },
  { id: 'conflict', title: 'Conflicto y promesa', subtitle: 'Qué está en juego y qué vas a ganar.', start: 900, duration: 4500, accent: '#ff9f0a', bg: '#0b0f1a' },
  { id: 'chapter-1', title: 'Capítulo 1: Antecedentes', subtitle: 'Revelación inesperada #1.', start: 5400, duration: 9000, accent: '#30d158', bg: '#07110b' },
  { id: 'chapter-2', title: 'Capítulo 2: Nudo forense', subtitle: 'Evidencias, contradicciones y re-hook central.', start: 14400, duration: 9000, accent: '#0a84ff', bg: '#050b18' },
  { id: 'chapter-3', title: 'Capítulo 3: Giro dialéctico', subtitle: 'Clímax de análisis y consecuencia práctica.', start: 23400, duration: 9000, accent: '#bf5af2', bg: '#120718' },
  { id: 'synthesis', title: 'Síntesis abierta', subtitle: 'Conexión directa con el siguiente vídeo.', start: 32400, duration: 3600, accent: '#64d2ff', bg: '#040b10' },
];

const REHOOK_MESSAGES: Record<number, string> = {
  5400: 'Pero lo que nadie vio hasta ahora es esto.',
  10800: 'Aquí cambia el marco: el dato que reordena la historia.',
  16200: 'Si pensabas que ya estaba claro, falta la pieza forense.',
  21600: 'Este es el punto donde la versión cómoda se rompe.',
  27000: 'La consecuencia práctica es más incómoda de lo que parece.',
};

const getBeat = (frame: number): Beat =>
  BEATS.find((b) => frame >= b.start && frame < b.start + b.duration) ?? BEATS[0];

const hashNumber = (n: number): number => {
  let x = n >>> 0;
  x = Math.imul(x ^ 0xdeadbeef, 0x85ebca6b);
  x = Math.imul(x ^ (x >>> 16), 0xc2b2ae35);
  x ^= x >>> 16;
  return x >>> 0;
};

// ==================== COMPONENTES VISUALES ====================

const Scanlines: React.FC = () => (
  <AbsoluteFill
    style={{
      pointerEvents: 'none',
      background: `
        linear-gradient(rgba(18,16,16,0) 50%, rgba(0,0,0,0.28) 50%),
        linear-gradient(90deg, rgba(255,0,0,0.035), rgba(0,255,0,0.02), rgba(0,0,255,0.035))
      `,
      backgroundSize: '100% 4px, 3px 100%',
      zIndex: 20,
      opacity: 0.18,
    }}
  />
);

const Vignette: React.FC<{ accent: string }> = ({ accent }) => (
  <AbsoluteFill
    style={{
      pointerEvents: 'none',
      boxShadow: `inset 0 0 180px rgba(0,0,0,0.92), inset 0 0 120px ${accent}15`,
      zIndex: 15,
    }}
  />
);

const BackgroundAsset: React.FC<{ beat: Beat; frame: number; backgroundVideo?: string }> = ({ beat, frame, backgroundVideo }) => {
  const zoom = interpolate((frame % 420) / 420, [0, 1], [1, 1.065]);

  if (backgroundVideo) {
    return (
      <AbsoluteFill style={{ overflow: 'hidden', zIndex: 5 }}>
        <Video
          src={backgroundVideo}
          style={{ width: '100%', height: '100%', objectFit: 'cover', filter: 'grayscale(0.7) opacity(0.4)' }}
          muted
          loop
        />
      </AbsoluteFill>
    );
  }

  return (
    <AbsoluteFill style={{ overflow: 'hidden', opacity: 0.28, zIndex: 5 }}>
      <div
        style={{
          width: '100%',
          height: '100%',
          background: `linear-gradient(135deg, ${beat.bg} 0%, #000000 100%)`,
          transform: `scale(${zoom})`,
          filter: 'grayscale(0.85) contrast(1.15) saturate(0.6)',
        }}
      />
    </AbsoluteFill>
  );
};

const Waveform: React.FC<{ accent: string; frame: number }> = ({ accent, frame }) => (
  <div style={{ display: 'flex', gap: 6, height: 84, alignItems: 'flex-end' }}>
    {Array.from({ length: 28 }).map((_, i) => {
      const h = 18 + 66 * Math.abs(Math.sin((frame + i * 37) / 11));
      return (
        <div
          key={i}
          style={{
            width: 6,
            height: h,
            borderRadius: 3,
            background: accent,
            opacity: 0.72,
          }}
        />
      );
    })}
  </div>
);

const RehookOverlay: React.FC<{ frame: number; accent: string }> = ({ frame, accent }) => {
  const activeRehook = REHOOK_FRAMES.find((r) => frame >= r && frame < r + 150);
  if (!activeRehook) return null;

  const local = frame - activeRehook;

  const opacity = interpolate(local, [0, 12, 120, 150], [0, 1, 1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const y = spring({ frame: local, fps: FPS, config: { damping: 12, stiffness: 120 } });

  // Glitch effect
  const glitchX = Math.sin(local * 0.8) * 3;
  const glitchScale = 1 + Math.sin(local * 1.3) * 0.015;

  return (
    <AbsoluteFill
      style={{
        justifyContent: 'center',
        alignItems: 'center',
        opacity,
        pointerEvents: 'none',
        zIndex: 30,
      }}
    >
      <div
        style={{
          transform: `translateY(${interpolate(y, [0, 1], [28, 0])}px) translateX(${glitchX}px) scale(${glitchScale})`,
          background: 'rgba(0,0,0,0.78)',
          border: `2px solid ${accent}`,
          borderRadius: 24,
          padding: '36px 48px',
          maxWidth: '70%',
          textAlign: 'center',
          boxShadow: `0 0 80px ${accent}44`,
        }}
      >
        <div style={{ fontSize: 56, fontWeight: 800, lineHeight: 1.08 }}>
          {REHOOK_MESSAGES[activeRehook] ?? 'Giro narrativo.'}
        </div>
      </div>
    </AbsoluteFill>
  );
};

const DynamicCut: React.FC<{ beat: Beat; frame: number; evidences?: EvidenceItem[] }> = ({ beat, frame, evidences = [] }) => {
  const cutIndex = Math.floor(frame / CUT_INTERVAL_FRAMES);
  const variant = hashNumber(cutIndex) % 4;
  const localFrame = frame % CUT_INTERVAL_FRAMES;

  const scale = interpolate(localFrame, [0, 10], [1.02, 1], { extrapolateRight: 'clamp' });
  const justify = variant === 0 ? 'center' : variant === 1 ? 'flex-start' : variant === 2 ? 'flex-end' : 'center';
  const align = variant === 3 ? 'flex-start' : 'center';
  const showEvidence = variant === 2 || variant === 3;

  // Seleccionar la evidencia correspondiente si existe
  const currentEvidence = evidences.length > 0 ? evidences[cutIndex % evidences.length] : null;

  return (
    <AbsoluteFill
      style={{
        justifyContent: justify as any,
        alignItems: align as any,
        transform: `scale(${scale})`,
        padding: 96,
        zIndex: 10,
      }}
    >
      <div style={{ maxWidth: 1200 }}>
        <div style={{ fontSize: 28, letterSpacing: 4, textTransform: 'uppercase', color: beat.accent, marginBottom: 18 }}>
          {beat.title}
        </div>
        <div style={{ fontSize: 72, fontWeight: 900, lineHeight: 1.04, marginBottom: 24 }}>
          {beat.subtitle}
        </div>
        <div style={{ fontSize: 36, opacity: 0.82, maxWidth: 1000 }}>
          Cada corte de {CUT_INTERVAL_FRAMES / FPS}s sostiene estimulación visual sin romper la narrativa.
        </div>
      </div>

      {showEvidence && (
        <div
          style={{
            position: 'absolute',
            right: 96,
            bottom: 180,
            width: 480,
            borderRadius: 24,
            border: `2px solid ${beat.accent}55`,
            background: 'rgba(255,255,255,0.06)',
            backdropFilter: 'blur(10px)',
            padding: 28,
            overflow: 'hidden',
          }}
        >
          <div style={{ fontSize: 24, textTransform: 'uppercase', letterSpacing: 2, color: beat.accent, marginBottom: 10 }}>
            {currentEvidence?.caption || 'Evidencia'}
          </div>

          {currentEvidence ? (
            <div style={{ width: '100%', height: 180, borderRadius: 12, overflow: 'hidden', marginBottom: 12 }}>
              {currentEvidence.type === 'video' ? (
                <Video
                  src={currentEvidence.src}
                  style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                  muted
                  loop
                />
              ) : (
                <Img
                  src={currentEvidence.src}
                  style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                />
              )}
            </div>
          ) : (
            <div style={{ fontSize: 34, fontWeight: 700, marginBottom: 18 }}>
              Dato / clip / captura de apoyo.
            </div>
          )}

          <Waveform accent={beat.accent} frame={frame} />
        </div>
      )}
    </AbsoluteFill>
  );
};

const EndLoop: React.FC<{ frame: number }> = ({ frame }) => {
  const local = frame - END_LOOP_START;
  const enter = spring({ frame: local, fps: FPS, config: { damping: 12, stiffness: 90 } });
  const pulse = 1 + 0.02 * Math.sin(local / 8);

  return (
    <AbsoluteFill style={{ backgroundColor: '#020409', justifyContent: 'center', alignItems: 'center', color: '#fff' }}>
      <div style={{ textAlign: 'center', maxWidth: 1300, padding: 48 }}>
        <div style={{ fontSize: 68, fontWeight: 900, lineHeight: 1.06, opacity: enter, transform: `translateY(${interpolate(enter, [0, 1], [30, 0])}px)` }}>
          Esto no se cierra aquí: la siguiente pieza continúa exactamente desde este punto.
        </div>
        <div style={{ marginTop: 42, fontSize: 40, opacity: 0.86 }}>
          Pulsa la tarjeta recomendada para mantener el hilo.
        </div>
        <div
          style={{
            marginTop: 64,
            width: 760,
            height: 430,
            borderRadius: 36,
            border: '3px solid #64d2ff',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            transform: `scale(${pulse})`,
            boxShadow: '0 0 100px rgba(100,210,255,0.22)',
            background: 'linear-gradient(135deg, rgba(100,210,255,0.12), rgba(255,255,255,0.04))',
          }}
        >
          <div style={{ fontSize: 44, fontWeight: 800, padding: 32, textAlign: 'center' }}>
            Espacio seguro para end screen / tarjeta de YouTube
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ==================== COMPONENTE PRINCIPAL ====================

export const UnTioBlancoHipocrita: React.FC<UnTioBlancoHipocritaProps> = ({
  evidences = [],
  title,
  subtitle,
  backgroundVideo,
}) => {
  const frame = useCurrentFrame();
  const beat = getBeat(frame);

  if (frame >= END_LOOP_START) {
    return <EndLoop frame={frame} />;
  }

  return (
    <AbsoluteFill
      style={{
        backgroundColor: beat.bg,
        color: '#ffffff',
        fontFamily: 'Inter, Arial, sans-serif',
      }}
    >
      <BackgroundAsset beat={beat} frame={frame} backgroundVideo={backgroundVideo} />
      <Vignette accent={beat.accent} />
      <DynamicCut beat={beat} frame={frame} evidences={evidences} />
      <RehookOverlay frame={frame} accent={beat.accent} />
      <Scanlines />

      {/* Barra inferior */}
      <div
        style={{
          position: 'absolute',
          left: 0,
          right: 0,
          bottom: 0,
          height: 92,
          display: 'flex',
          alignItems: 'center',
          background: 'rgba(0,0,0,0.35)',
          borderTop: `1px solid ${beat.accent}33`,
          padding: '0 36px',
          zIndex: 25,
        }}
      >
        <div style={{ fontSize: 28, fontWeight: 700, color: beat.accent, marginRight: 18 }}>
          NOW
        </div>
        <div style={{ fontSize: 28, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
          {title || beat.title} · {subtitle || beat.subtitle}
        </div>
      </div>
    </AbsoluteFill>
  );
};

UnTioBlancoHipocrita.defaultProps = {
  evidences: [],
};
