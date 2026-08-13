import { AbsoluteFill, Img, staticFile } from "remotion";
import { PropertyLabels, PropertyLabelSpec } from "./components/PropertyLabel";

/**
 * Composicao de PROVA do `PropertyLabel`, so para confirmar o desenho.
 *
 * ⚠️ O fundo e uma fotografia real e nao um gradiente: o `backdrop-filter` so se
 * ve sobre detalhe. Num fundo liso o desfoque existe e nao se nota, e nao provava
 * nada.
 */
const LABELS: PropertyLabelSpec[] = [
  { start: 0, end: 60, eyebrow: "T4 · Esmoriz", title: "208 m² de área bruta", align: "left" },
  { start: 70, end: 130, eyebrow: "Quartos", title: "Roupeiro embutido", align: "right" },
  { start: 140, end: 200, title: "Garagem", align: "left" },
];

export const PropertyLabelDemo: React.FC = () => (
  <AbsoluteFill>
    <Img src={staticFile("_label_bg.jpg")} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
    <PropertyLabels labels={LABELS} />
  </AbsoluteFill>
);
