import React, { useMemo } from 'react';
import {
  AbsoluteFill,
  Sequence,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
} from 'remotion';

// Deterministic pseudo-random — safe for Remotion's isolated frame rendering
const pseudoRandom = (seed: number) => {
  const x = Math.sin(seed * 12.9898 + 78.233) * 43758.5453;
  return x - Math.floor(x);
};

// ==========================================
// CONFIGURACIÓN DE ESTÉTICA FORENSE
// ==========================================
const COLORS = {
  bg: '#050505',
  text: '#F1FAEE',
  accent: '#E63946', // Rojo Sangre
  secondary: '#A8DADC',
  darkGray: '#1D3557',
};

const FONT = {
  mono: 'Courier New, monospace',
  sans: 'Impact, system-ui, sans-serif',
};

// ==========================================
// COMPONENTES REUTILIZABLES
// ==========================================

const Waveform: React.FC<{ color?: string }> = ({ color = COLORS.accent }) => {
  const frame = useCurrentFrame();

  const points = useMemo(() => {
    return Array.from({ length: 100 }, (_, i) => {
      const x = i * 19.2;
      const y = 50 + Math.sin((i + frame) * 0.3) * 30 * Math.sin(frame * 0.05 + i);
      return `${x},${y}`;
    }).join(' ');
  }, [frame]);

  return (
    <svg width="1920" height="100" viewBox="0 0 1920 100" style={{ position: 'absolute', bottom: 20, left: 0, opacity: 0.4 }}>
      <polyline points={points} fill="none" stroke={color} strokeWidth="3" />
    </svg>
  );
};

const GlitchText: React.FC<{
  text: string;
  fontSize?: number;
  delay?: number;
  shadowColors?: [string, string];
}> = ({ text, fontSize = 120, delay = 0, shadowColors = [COLORS.accent, COLORS.secondary] }) => {
  const frame = useCurrentFrame();

  const opacity = interpolate(frame, [delay, delay + 10], [0, 1], { extrapolateRight: 'clamp' });
  const glitchX = frame % 10 < 2 ? pseudoRandom(frame) * 10 - 5 : 0;
  const glitchY = frame % 15 < 2 ? pseudoRandom(frame + 999) * 10 - 5 : 0;

  return (
    <div style={{
      fontFamily: FONT.sans,
      fontSize,
      color: COLORS.text,
      textTransform: 'uppercase',
      opacity,
      transform: `translate(${glitchX}px, ${glitchY}px)`,
      textShadow: `2px 2px 0px ${shadowColors[0]}, -2px -2px 0px ${shadowColors[1]}`,
      letterSpacing: '-2px',
      textAlign: 'center',
    }}>
      {text}
    </div>
  );
};

const Ticker: React.FC<{ words: string[] }> = ({ words }) => {
  const frame = useCurrentFrame();
  const totalWidth = words.length * 3 * 280;
  const translateX = interpolate(frame, [0, 3000], [1920, -totalWidth], { extrapolateRight: 'extend' });
  
  return (
    <div style={{
      overflow: 'hidden',
      whiteSpace: 'nowrap',
      width: '100%',
      background: COLORS.accent,
      padding: '15px 0',
      position: 'absolute',
      bottom: 120,
      borderTop: '4px solid #fff',
      borderBottom: '4px solid #fff',
    }}>
      <div style={{ display: 'inline-block', transform: `translateX(${translateX}px)` }}>
        {[...Array(3)].map((_, loopIndex) => (
          words.map((word, i) => (
            <span key={`${loopIndex}-${i}`} style={{
              fontSize: 50,
              fontWeight: 900,
              color: '#000',
              marginRight: 80,
              fontFamily: FONT.sans,
              textTransform: 'uppercase',
            }}>
              {word} <span style={{ color: '#fff' }}>///</span>
            </span>
          ))
        ))}
      </div>
    </div>
  );
};

const ForensicCard: React.FC<{ title: string; content: string; color?: string }> = ({ title, content, color = COLORS.accent }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const scale = spring({ frame, fps, config: { damping: 12, stiffness: 200, mass: 0.5 } });
  const opacity = interpolate(frame, [0, 30], [0, 1], { extrapolateRight: 'clamp' });

  return (
    <div style={{
      transform: `scale(${scale})`,
      opacity,
      background: '#0a0a0a',
      border: `4px solid ${color}`,
      padding: 60,
      width: '80%',
      maxWidth: 1400,
      fontFamily: FONT.mono,
      boxShadow: `20px 20px 0px ${color}`,
    }}>
      <div style={{ fontSize: 40, color: color, fontWeight: 'bold', marginBottom: 30, borderBottom: `2px solid ${COLORS.text}`, paddingBottom: 10 }}>
        {title}
      </div>
      <div style={{ fontSize: 32, color: COLORS.text, lineHeight: 1.4 }}>
        {content}
      </div>
    </div>
  );
};

const Quote: React.FC<{ text: string; author?: string }> = ({ text, author }) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 60], [0, 1], { extrapolateRight: 'clamp' });
  const y = interpolate(frame, [0, 60], [50, 0], { extrapolateRight: 'clamp' });

  return (
    <div style={{
      opacity,
      transform: `translateY(${y}px)`,
      width: '80%',
      maxWidth: 1400,
      borderLeft: `15px solid ${COLORS.accent}`,
      paddingLeft: 40,
      fontFamily: FONT.mono,
    }}>
      <div style={{ fontSize: 60, color: COLORS.text, fontWeight: 'bold', lineHeight: 1.2, marginBottom: 20 }}>
        "{text}"
      </div>
      {author && (
        <div style={{ fontSize: 30, color: COLORS.secondary }}>
          — {author}
        </div>
      )}
    </div>
  );
};

// ==========================================
// ACTO 1: EL COLAPSO CONTRACTUAL (0 - 5 MIN)
// ==========================================
const Acto1: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.bg, justifyContent: 'center', alignItems: 'center' }}>
      <Sequence from={0} durationInFrames={300}>
        <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center' }}>
          <GlitchText text="AUDITORÍA FORENSE" fontSize={100} />
          <GlitchText text="UN TÍO BLANCO E HIPÓCRITA" fontSize={140} delay={30} />
        </AbsoluteFill>
      </Sequence>

      <Sequence from={300} durationInFrames={2700}>
        <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center' }}>
          <ForensicCard 
            title="EL TUIT DE 2019 (EL NOÚMENO)" 
            content="Si me lo dices en la calle ahora no tendrías dientes."
            color={COLORS.accent}
          />
          <div style={{ position: 'absolute', bottom: 200, fontSize: 30, color: COLORS.secondary, fontFamily: FONT.mono }}>
            Causalidad Física: Violación de políticas de integridad. Expulsión de Twitter.
          </div>
        </AbsoluteFill>
      </Sequence>

      <Sequence from={3000} durationInFrames={3000}>
        <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', flexDirection: 'row', gap: 50 }}>
          <ForensicCard 
            title="EL FENÓMENO (SU RELATO)" 
            content="Ataque coordinado de censura ideológica y sectarismo."
            color={COLORS.secondary}
          />
          <ForensicCard 
            title="EL NOÚMENO (LA REALIDAD)" 
            content="Coacción material y amenaza de agresión física directa."
            color={COLORS.accent}
          />
        </AbsoluteFill>
      </Sequence>

      <Sequence from={6000} durationInFrames={3000}>
        <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center' }}>
          <ForensicCard 
            title="ASIMETRÍA EPÍSTÉMICA" 
            content="Reacción visceral ('hartito') y verificación defensiva ante una suplantación menor en el canal de Joan Planas. FRENTE A: Apatía instrumental y tolerancia pasiva ante amenazas de muerte a mujeres en su propia comunidad."
          />
        </AbsoluteFill>
      </Sequence>
      <Waveform />
    </AbsoluteFill>
  );
};

// ==========================================
// ACTO 2: LA DERROTA JUDICIAL (5 - 10 MIN)
// ==========================================
const Acto2: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.bg, justifyContent: 'center', alignItems: 'center' }}>
      <Sequence from={0} durationInFrames={3000}>
        <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center' }}>
          <Quote text="Instrumentalización del Honor: Usar el aparato judicial del Estado para silenciar a las víctimas del acoso digital." author="Dictamen Forense" />
        </AbsoluteFill>
      </Sequence>

      <Sequence from={3000} durationInFrames={3000}>
        <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center' }}>
          <ForensicCard 
            title="LITIGIO CONTRA YOLANDA DOMÍNGUEZ" 
            content="Intento de mordaza legal. El creador demanda a la artista por calificarlo de 'machista' y 'troll', buscando revancha institucional tras perder el debate público."
          />
        </AbsoluteFill>
      </Sequence>

      <Sequence from={6000} durationInFrames={3000}>
        <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', flexDirection: 'column', gap: 40 }}>
          <div style={{ fontSize: 60, color: COLORS.accent, fontFamily: FONT.sans, textTransform: 'uppercase' }}>
            SALA DE LO CIVIL - TRIBUNAL SUPREMO (2024)
          </div>
          <ForensicCard 
            title="CONDENA EN COSTAS" 
            content="El Tribunal Supremo ratifica que existe 'base fáctica suficiente' para llamarlo machista, troll y violento con las mujeres."
            color={COLORS.accent}
          />
        </AbsoluteFill>
      </Sequence>

      <Sequence from={9000} durationInFrames={3000}>
        <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center' }}>
          <ForensicCard 
            title="TRIBUNAL CONSTITUCIONAL (MARZO 2025)" 
            content="Inadmisión definitiva del recurso. El colapso total de la estrategia judicial. La justicia valida la complicidad pasiva del creador con el linchamiento digital."
          />
        </AbsoluteFill>
      </Sequence>
      <Waveform />
    </AbsoluteFill>
  );
};

// ==========================================
// ACTO 3: EL NEGOCIO DE LA APATÍA (10 - 15 MIN)
// ==========================================
const Acto3: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.bg, justifyContent: 'center', alignItems: 'center' }}>
      <Sequence from={0} durationInFrames={4000}>
        <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center' }}>
          <Ticker words={['FEMINAZI', 'CAZURRA', 'PUTA', 'LOCA', 'ENFERMA', 'CHAROCRACIA']} />
          <div style={{ position: 'absolute', top: '20%', fontSize: 80, fontFamily: FONT.sans, color: COLORS.text, textTransform: 'uppercase' }}>
            EL VOCABULARIO DE LA CÁMARA DE ECO
          </div>
          <div style={{ position: 'absolute', top: '35%', width: '80%', textAlign: 'center', fontSize: 36, fontFamily: FONT.mono, color: COLORS.secondary }}>
            Tolerancia activa de insultos degradantes para sostener el flujo de interacciones algorítmicas y la monetización.
          </div>
        </AbsoluteFill>
      </Sequence>

      <Sequence from={4000} durationInFrames={3000}>
        <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center' }}>
          <ForensicCard 
            title="MAPA DE DIANAS DE HOSTIGAMIENTO" 
            content="Yolanda Domínguez (Arte y Feminismo) // Irene Montero (Instituciones) // Ángela Rodríguez 'Pam' (Política). Diseñadas como medios para el lucro, no como fines en sí mismas."
            color={COLORS.accent}
          />
        </AbsoluteFill>
      </Sequence>

      <Sequence from={7000} durationInFrames={5000}>
        <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', flexDirection: 'column', gap: 40 }}>
          <div style={{ fontSize: 50, color: COLORS.accent, fontFamily: FONT.sans }}>EL TRANSDUCTOR DE ENTROPÍA</div>
          <div style={{ display: 'flex', gap: 20, alignItems: 'center', fontFamily: FONT.mono, color: COLORS.text }}>
            <div style={{ padding: 20, border: `2px solid ${COLORS.secondary}` }}>NOÚMENO<br/>(Realidad Compleja)</div>
            <div style={{ fontSize: 60 }}>➔</div>
            <div style={{ padding: 20, border: `2px solid ${COLORS.secondary}` }}>FENÓMENO<br/>(Títulos PÁNICO / GAME OVER)</div>
            <div style={{ fontSize: 60 }}>➔</div>
            <div style={{ padding: 20, border: `2px solid ${COLORS.accent}`, background: '#2a0000' }}>LUCRO<br/>(Patreon / PayPal)</div>
          </div>
        </AbsoluteFill>
      </Sequence>
      <Waveform />
    </AbsoluteFill>
  );
};

// ==========================================
// ACTO 4: EL IMPERATIVO CATEGÓRICO (15 - 20 MIN)
// ==========================================
const Acto4: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.bg, justifyContent: 'center', alignItems: 'center' }}>
      <Sequence from={0} durationInFrames={2500}>
        <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center' }}>
          <ForensicCard 
            title="LA PRUEBA DE UNIVERSALIZACIÓN (KANT)" 
            content="Máxima: 'Exageraré y descalificaré con miniaturas grotescas para capturar atención'. Si esto fuera Ley Universal, el lenguaje perdería su valor veritativo y la comunicación humana colapsaría en ruido estocástico."
            color={COLORS.secondary}
          />
        </AbsoluteFill>
      </Sequence>

      <Sequence from={2500} durationInFrames={2500}>
        <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center' }}>
          <Quote text="Quiero que el PSOE continúe gobernando hasta que se pudra del todo." author="Colaboración con Wall Street Wolverine" />
          <div style={{ position: 'absolute', bottom: '20%', fontSize: 40, fontFamily: FONT.mono, color: COLORS.accent, textAlign: 'center', width: '80%' }}>
            SCHADENFREUDE Y ACELERACIONISMO: El placer ante la desgracia ajena y la degradación institucional por encima del bienestar social.
          </div>
        </AbsoluteFill>
      </Sequence>

      <Sequence from={5000} durationInFrames={3500}>
        <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', flexDirection: 'column', gap: 40 }}>
          <div style={{ fontSize: 80, color: COLORS.text, fontFamily: FONT.sans, textTransform: 'uppercase' }}>
            CONCLUSIÓN DE LA AUDITORÍA
          </div>
          <div style={{ fontSize: 40, color: COLORS.secondary, fontFamily: FONT.mono, textAlign: 'center', width: '80%', lineHeight: 1.5 }}>
            El modelo de negocio de "Un Tío Blanco Hetero" no es una rebelión contra el sistema, sino la explotación cínica de sus peores incentivos algorítmicos.
            <br/><br/>
            <span style={{ color: COLORS.accent, fontWeight: 'bold' }}>
              La hipocresía estructural de exigir libertad para amenazar, mientras se demanda a quienes denuncian el acoso.
            </span>
          </div>
        </AbsoluteFill>
      </Sequence>
      
      <Sequence from={8500} durationInFrames={500}>
        <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', backgroundColor: COLORS.accent }}>
          <div style={{ fontSize: 100, fontFamily: FONT.sans, color: '#000' }}>FIN DE LA TRANSMISIÓN</div>
        </AbsoluteFill>
      </Sequence>
      <Waveform color={COLORS.text} />
    </AbsoluteFill>
  );
};

// ==========================================
// COMPOSICIÓN PRINCIPAL (20 MINUTOS)
// ==========================================
export const UnTioBlancoHipocrita: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.bg }}>
      {/* ACTO 1: 0 a 5 Minutos (Frames 0 - 9000) */}
      <Sequence from={0} durationInFrames={9000}>
        <Acto1 />
      </Sequence>

      {/* ACTO 2: 5 a 10 Minutos (Frames 9000 - 18000) */}
      <Sequence from={9000} durationInFrames={9000}>
        <Acto2 />
      </Sequence>

      {/* ACTO 3: 10 a 15 Minutos (Frames 18000 - 27000) */}
      <Sequence from={18000} durationInFrames={9000}>
        <Acto3 />
      </Sequence>

      {/* ACTO 4: 15 a 20 Minutos (Frames 27000 - 36000) */}
      <Sequence from={27000} durationInFrames={9000}>
        <Acto4 />
      </Sequence>
    </AbsoluteFill>
  );
};
