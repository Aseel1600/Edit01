/**
 * Standalone Remotion entry point for the "Milo goes to space" short.
 *
 * The shared src/index.tsx pulls in every composition in the repo, and several
 * of those load Google Fonts at import time — which hard-fails in offline /
 * network-restricted render environments. This entry registers only CatSpace
 * and vendors its font from public/, so it renders with no external requests.
 */
import { Composition, registerRoot } from "remotion";
import { CatSpace, TOTAL_FRAMES } from "./CatSpace";

const CatSpaceRoot: React.FC = () => (
  <Composition
    id="CatSpace"
    component={CatSpace}
    durationInFrames={TOTAL_FRAMES}
    fps={30}
    width={1080}
    height={1920}
  />
);

registerRoot(CatSpaceRoot);
