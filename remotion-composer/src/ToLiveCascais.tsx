import React from "react";
import { AbsoluteFill, OffthreadVideo, staticFile } from "remotion";
import { PropertyLabels, PropertyLabelSpec } from "./components/PropertyLabel";

/**
 * ToLive Cascais / Diogo Alves (RE/MAX) · camada de legendas.
 *
 * ⚠️ **Esta composicao NAO remonta o filme.** O filme ja vem montado do
 * `_montar.py` em ffmpeg, com os 29 planos, as transicoes, os dois logotipos, a
 * musica e o cartao final. Aqui ele entra como um unico `OffthreadVideo` e so se
 * lhe acrescentam as legendas por cima.
 *
 * ⚠️ Porque assim e nao a remontar tudo em Remotion: sao 29 planos e a montagem ja
 * estava aprovada. Remonta-la seria repetir trabalho e arriscar diferencas de
 * timing; assim a unica coisa que muda entre a versao aprovada e esta e a legenda.
 *
 * ⚠️ Porque Remotion e nao ffmpeg para as legendas: a caixa tem desfoque REAL do
 * video por baixo (`backdrop-filter`) e curvas de aceleracao. Em ffmpeg isso obriga
 * a `geq`, avaliado pixel a pixel por fotograma, e o render caiu para 4,3 KB/s numa
 * peca anterior, ou seja horas.
 *
 * ⚠️ O audio vem do proprio ficheiro; nao se acrescenta `Audio` nenhum.
 *
 * Os tempos vieram de `_build/tempos.json`, calculado a reproduzir a cadeia de
 * `xfade` da montagem. Nao sao estimativas.
 */

const FPS = 60;   // ⚠️ 02/08: o filme passou a 60 fps (ver `_upscale.py`)
const s = (seg: number) => Math.round(seg * FPS);

/**
 * Uma legenda por batida, nao por plano: 19 em 29 planos. Os planos de servico e os
 * angulos repetidos do exterior passam sem texto, para a peca respirar.
 *
 * ⚠️ **Duas correccoes do Miguel a 02/08:**
 *  1. **Cinco legendas falavam de PAVIMENTO** (tres delas em marmore). Eram fieis: as
 *     linhas descritivas da brochura sao quase todas sobre pavimentos, porque a brochura
 *     e uma ficha tecnica. Mas um filme nao deve herdar a repeticao de uma ficha tecnica,
 *     e o chao e a coisa menos vendavel de um empreendimento com spa, rooftop e
 *     penthouse. Foram trocadas por frases do PROPRIO promotor (as aberturas de seccao)
 *     e por caracteristicas que vendem. So fica o pavimento da suite master, porque esse
 *     DISTINGUE: e madeira contra o marmore do resto.
 *  2. **As legendas ficavam pouco tempo.** Comecavam 0,7 s depois do plano entrar e saiam
 *     0,5 s antes; com 14 fotogramas de entrada e 14 de saida na animacao, numa batida de
 *     3,4 s sobrava pouco mais de 1 s de leitura plena. Agora entram 0,35 s depois e saem
 *     0,25 s antes, o que devolve ~0,6 s a cada uma.
 *
 * ⚠️ Textos verificados contra a brochura (`clients/Diogo Alves/LEGENDAS.md`). Tres
 * regras que vieram de la:
 *  · o "ou similar" dos acabamentos nao se endurece numa promessa nossa;
 *  · o LEED e PRE-certificacao, portanto nao aparece;
 *  · nenhuma legenda afirma o que a brochura nao diz (nao ha "piscina aquecida").
 */
const LABELS: PropertyLabelSpec[] = [
  { start: s(0.35), end: s(5.65), eyebrow: "Cascais", title: "A 500 metros da Baía" },
  { start: s(6.25), end: s(10.05), eyebrow: "Antigo Cinema Oxford", title: "Um marco da vila, reconvertido" },
  { start: s(23.85), end: s(28.15), eyebrow: "No centro de Cascais", title: "Mercado da Vila e Parque Marechal Carmona a passos", align: "right" },
  { start: s(36.05), end: s(40.35), eyebrow: "Receção e lounge", title: "Desde já, sinta-se em casa" },
  { start: s(40.95), end: s(45.75), eyebrow: "Piscina interior", title: "E jacuzzi", align: "right" },
  { start: s(46.35), end: s(49.65), eyebrow: "Spa", title: "Duche revestido a mármore" },
  { start: s(50.25), end: s(54.05), eyebrow: "Sala de massagem", title: "No spa, o conforto não conhece estações", align: "right" },
  { start: s(54.65), end: s(58.45), eyebrow: "Spa", title: "Sauna e banho turco" },
  { start: s(59.05), end: s(62.85), eyebrow: "Lifestyle & wellbeing", title: "Ginásio equipado", align: "right" },
  { start: s(63.45), end: s(66.25), eyebrow: "Estação de bicicletas", title: "Com espaço de manutenção" },
  { start: s(66.85), end: s(69.65), eyebrow: "Sala de entrega", title: "Para receber encomendas", align: "right" },
  { start: s(73.15), end: s(75.95), eyebrow: "Espaço pet", title: "Bancada equipada" },
  { start: s(76.55), end: s(81.85), eyebrow: "Rooftop", title: "Piscina e espaço gourmet", align: "right" },
  { start: s(82.45), end: s(86.75), eyebrow: "T3 e penthouses T4", title: "Cozinha integrada equipada" },
  { start: s(97.15), end: s(101.45), eyebrow: "Varanda gourmet", title: "Bancada e lava-loiça", align: "right" },
  { start: s(102.05), end: s(106.35), eyebrow: "Suíte master", title: "Pavimento flutuante em madeira" },
  { start: s(111.35), end: s(114.65), eyebrow: "Casa de banho master", title: "Bancada esculpida", align: "right" },
  { start: s(115.25), end: s(120.05), eyebrow: "Penthouse", title: "Terraço com piscina e pérgola" },
  { start: s(120.65), end: s(125.95), eyebrow: "Hidromassagem", title: "Com vista mar", align: "right" },
  // ⚠️ o plano de fecho (a mulher a abrir os cortinados) fica SEM legenda, por
  // decisao do Miguel: e a imagem que fecha a peca e o texto so lhe roubava atencao.
];

export const ToLiveCascais: React.FC = () => (
  <AbsoluteFill style={{ backgroundColor: "#000" }}>
    <OffthreadVideo src={staticFile("diogo/filme.mp4")} />
    <PropertyLabels labels={LABELS} />
  </AbsoluteFill>
);
