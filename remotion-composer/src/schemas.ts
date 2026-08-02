import { z } from 'zod';

export const EvidenceItemSchema = z.object({
  id: z.string().min(1),
  type: z.enum(['image', 'video']),
  src: z.string().min(1),
  chapter: z.string().optional(),
  startFrame: z.number().int().nonnegative().optional(),
  durationFrames: z.number().int().positive().optional(),
  durationSeconds: z.number().positive().optional(),
  trimStartSeconds: z.number().nonnegative().default(0),
  trimEndSeconds: z.number().positive().optional(),
  fit: z.enum(['cover', 'contain']).default('cover'),
  position: z.string().default('center'),
  caption: z.string().optional(),
  kicker: z.string().optional(),
  source: z.string().optional(),
  timestamp: z.string().optional(),
  muted: z.boolean().default(true),
  volume: z.number().min(0).max(1).default(0),
  playbackRate: z.number().positive().default(1),
  emphasis: z.enum(['normal', 'hard', 'glitch']).default('normal'),
});

export const UnTioBlancoHipocritaPropsSchema = z.object({
  jobId: z.string().optional(),
  title: z.string().default('UN TÍO BLANCO HIPÓCRITA'),
  subtitle: z.string().optional(),
  evidenceStartFrame: z.number().int().nonnegative().default(90),
  evidenceGapFrames: z.number().int().nonnegative().default(10),
  defaultImageDurationSeconds: z.number().positive().default(3.5),
  defaultVideoDurationSeconds: z.number().positive().default(5),
  evidences: z.array(EvidenceItemSchema).default([]),
});

export type UnTioBlancoHipocritaProps = z.input<
  typeof UnTioBlancoHipocritaPropsSchema
>;

export type ParsedEvidenceItem = z.output<typeof EvidenceItemSchema>;
export type ParsedProps = z.output<typeof UnTioBlancoHipocritaPropsSchema>;
