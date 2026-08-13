# -*- coding: utf-8 -*-
"""Reguas de QC para fotografia de imovel tratada (original vs tratada).

Porque existe: a olho nao se distingue "corrigiu a exposicao" de "redesenhou a
sala", e um numero mal calibrado e' pior do que nenhum. Cada regua aqui foi
calibrada contra casos de resposta conhecida, e A CALIBRACAO CORRE SEMPRE antes
dos casos reais. Se falhar, o script recusa-se a imprimir resultados.

Historia, para nao se repetir: a primeira regua de geometria era SSIM sobre a
magnitude do gradiente. Uma LUT por canal, que nao consegue mover um pixel,
pontuou 0,531 nessa regua, o mesmo valor de uma imagem deslocada 12 px. Media
tom e geometria misturados e foi deitada fora.

USO
    python qc_fotos.py <original> <tratada> [<tratada2> ...]
    python qc_fotos.py --pasta <dir_originais> <dir_tratadas>

COMO LER
    geometria  px de deslocamento. ~0 = arquitectura intacta. >2 = a imagem mexeu.
               E' o unico alarme verdadeiro num tratamento de cor.
    detalhe    variancia do laplaciano. So' comparavel a' MESMA escala, por isso
               tudo e' reamostrado para uma grelha comum antes de medir.
    ruido      desvio de (imagem - mediana). Sobe com sharpen agressivo.
    cor        desvio de croma em p99. Mede dominante de cor, nao saturacao.
    blocos     periodicidade a 8 px. So' se le como DELTA entre o antes e o
               depois do mesmo enquadramento: se subir muito, o tratamento
               reforcou compressao. O valor absoluto nao diz de onde veio o
               ficheiro (ver a nota em blocos()).
"""
import os
import sys

import cv2
import numpy as np

# grelha comum: detalhe e ruido dependem da resolucao, portanto nada se mede
# antes de as duas imagens estarem do mesmo tamanho
ESC = (1500, 1000)

# limiares de calibracao: se a regua nao passar nisto, nao presta
CAL_LUT_MAX = 0.80      # uma LUT nao move pixeis, tem de dar ~0
CAL_3PX_MIN = 2.00      # 3 px deslocados tem de ler perto de 3
CAL_12PX_MIN = 9.00     # 12 px deslocados tem de ler perto de 12


def ler(caminho, escala=ESC):
    """Le com suporte a acentos no caminho (imread nao aguenta em Windows)."""
    im = cv2.imdecode(np.fromfile(caminho, np.uint8), cv2.IMREAD_COLOR)
    if im is None:
        return None
    return cv2.resize(im, escala, interpolation=cv2.INTER_AREA) if escala else im


# --------------------------------------------------------------------------
# reguas
# --------------------------------------------------------------------------

def _normalizar(im):
    """Contraste local normalizado: tira exposicao, contraste e balanco.

    E' isto que torna a regua de geometria cega ao tom. Sem este passo, uma
    correccao de cor forte le-se como movimento.
    """
    g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY).astype(np.float32)
    media = cv2.GaussianBlur(g, (0, 0), 8)
    desvio = np.sqrt(np.maximum(cv2.GaussianBlur((g - media) ** 2, (0, 0), 8), 1e-6))
    return np.clip((g - media) / (desvio + 4.0) * 40 + 128, 0, 255).astype(np.uint8)


def geometria(a, b):
    """Deslocamento mediano em pixeis, por fluxo optico. Cego ao tom."""
    f = cv2.calcOpticalFlowFarneback(
        _normalizar(a), _normalizar(b), None,
        pyr_scale=0.5, levels=4, winsize=25,
        iterations=5, poly_n=7, poly_sigma=1.5, flags=0)
    m = np.linalg.norm(f, axis=2)[40:-40, 40:-40]   # a moldura nao e' fiavel
    return float(np.median(m))


def detalhe(im):
    """Variancia do laplaciano. So' comparavel a' mesma escala."""
    g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    return float(cv2.Laplacian(g, cv2.CV_64F).var())


def ruido(im):
    """Desvio do que sobra depois de tirar a mediana. Sobe com sharpen."""
    g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY).astype(np.float32)
    return float((g - cv2.medianBlur(g.astype(np.uint8), 3).astype(np.float32)).std())


def cor(im):
    """Dominante de cor: p99 do desvio maximo de canal face a' luminancia.

    Desfoca-se primeiro para nao apanhar objectos coloridos legitimos; o que
    interessa e' o banho de cor sobre a imagem toda.
    """
    f = cv2.GaussianBlur(im, (0, 0), 12).astype(np.float32)
    lum = f.mean(axis=2, keepdims=True)
    return float(np.percentile(np.abs(f - lum).max(axis=2), 99))


def blocos(im):
    """Blocos de JPEG: diferencas nas fronteiras 8x8 contra as de dentro.

    1,00 = limpo. Acima de 1,05 os blocos veem-se ao ampliar, e e' o sinal de
    que o ficheiro passou por WhatsApp ou por recompressao agressiva.

    !! MEDE-SE EM RESOLUCAO NATIVA, ao contrario das outras reguas. Reamostrar
    desalinha a grelha 8x8 e apaga o que se procura: um ficheiro que mede 1,358
    em nativo leu 1,022 depois de reduzido para a grelha comum. Se aparecer aqui
    uma imagem ja' reamostrada, o numero nao vale nada.

    !! E NAO SERVE PARA IDENTIFICAR A PROVENIENCIA DE UM FICHEIRO. Medido no lote
    do T3: originais de 24 MP deram 1,02 a 1,62 e o lote de WhatsApp deu 1,23 a
    1,50, ou seja as gamas sobrepoem-se. O valor mais alto de todos foi um
    ORIGINAL, um corredor de roupeiros de ripas verticais, porque textura
    repetida perto dos 8 px le-se como bloco. Para decidir se um ficheiro chega
    para o trabalho usa-se a RESOLUCAO, que e' binaria. Este numero serve para
    comparar o MESMO enquadramento antes e depois de um tratamento, mais nada.
    """
    g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY).astype(np.float32)
    d = np.abs(np.diff(g, axis=1))
    col = np.arange(d.shape[1])
    fronteira = d[:, col % 8 == 7].mean()
    dentro = d[:, col % 8 != 7].mean()
    return float(fronteira / (dentro + 1e-6))


# --------------------------------------------------------------------------
# calibracao: corre SEMPRE, e manda o script abaixo se falhar
# --------------------------------------------------------------------------

def calibrar(base):
    """Prova a regua de geometria contra casos de resposta conhecida."""
    print("=== CALIBRACAO ===")
    print("  %-38s %8s %8s" % ("caso", "lido", "esperado"))

    ident = geometria(base, base.copy())
    print("  %-38s %8.2f %8s" % ("identidade", ident, "~0"))

    lut = np.clip(((np.arange(256) / 255.0) ** 0.6) * 255, 0, 255).astype(np.uint8)
    tonal = base.copy()
    for c in range(3):
        tonal[:, :, c] = cv2.LUT(base[:, :, c], lut)
    v_lut = geometria(base, tonal)
    print("  %-38s %8.2f %8s" % ("LUT forte, gama 0,6", v_lut, "~0"))

    def deslocar(px):
        M = np.float32([[1, 0, px], [0, 1, 0]])
        return cv2.warpAffine(base, M, ESC, borderMode=cv2.BORDER_REPLICATE)

    v3 = geometria(base, deslocar(3))
    print("  %-38s %8.2f %8s" % ("deslocado 3 px", v3, "~3"))
    v12 = geometria(base, deslocar(12))
    print("  %-38s %8.2f %8s" % ("deslocado 12 px", v12, "~12"))

    falhas = []
    if v_lut > CAL_LUT_MAX:
        falhas.append("a LUT deu %.2f px, logo a regua NAO e' cega ao tom" % v_lut)
    if v3 < CAL_3PX_MIN:
        falhas.append("3 px leram %.2f, logo a regua nao ve movimento pequeno" % v3)
    if v12 < CAL_12PX_MIN:
        falhas.append("12 px leram %.2f, logo a regua satura" % v12)

    if falhas:
        print("\n  🔴 CALIBRACAO FALHOU. Nao ha numeros para ler:")
        for f in falhas:
            print("     - " + f)
        return False

    print("\n  ok: a regua ve movimento e ignora tom.\n")
    return True


# --------------------------------------------------------------------------

def avaliar(orig_p, tratadas):
    o = ler(orig_p)
    if o is None:
        print("nao consegui ler %s" % orig_p)
        return 1

    if not calibrar(o):
        return 1

    nat_o = ler(orig_p, escala=None)     # blocos so' se le em nativo
    ho, wo = nat_o.shape[:2]

    print("=== %s (%dx%d) ===" % (os.path.basename(orig_p), wo, ho))
    cab = "  %-30s %7s %9s %9s %8s %7s %7s"
    print(cab % ("ficheiro", "racio", "geometria", "detalhe", "ruido", "cor", "blocos"))
    print("  " + "-" * 84)
    print(cab % ("(original)", "%7.3f" % (wo / ho), "", "%9.0f" % detalhe(o),
                 "%8.2f" % ruido(o), "%7.1f" % cor(o), "%7.3f" % blocos(nat_o)))

    for p in tratadas:
        im, nat = ler(p), ler(p, escala=None)
        if im is None or nat is None:
            print("  %-30s  (nao consegui ler)" % os.path.basename(p)[:30])
            continue
        h, w = nat.shape[:2]
        aviso = "  <-- recortada, a geometria nao vale" if abs(w / h - wo / ho) > 0.02 else ""
        print(cab % (os.path.basename(p)[:30], "%7.3f" % (w / h),
                     "%9.2f" % geometria(o, im), "%9.0f" % detalhe(im),
                     "%8.2f" % ruido(im), "%7.1f" % cor(im), "%7.3f" % blocos(nat)) + aviso)

    print("\n  geometria ~0 = arquitectura intacta. >2 = a imagem mexeu.")
    print("  !! so' e' valida entre imagens do MESMO enquadramento. Uma tratada ja'")
    print("     recortada para 16:9 da' um numero grande que e' o corte, nao um defeito.")
    print("  detalhe e ruido comparam-se entre linhas, nunca entre execucoes.")
    print("  blocos: le-se a DIFERENCA para o original, nao o valor absoluto.")
    return 0


def por_pasta(dir_orig, dir_trat):
    """Emparelha por prefixo do nome, que e' como os tratamentos costumam sair."""
    if not (os.path.isdir(dir_orig) and os.path.isdir(dir_trat)):
        print("uma das pastas nao existe")
        return 1
    tratadas = os.listdir(dir_trat)
    saida = 0
    for f in sorted(os.listdir(dir_orig)):
        base = os.path.splitext(f)[0]
        pares = [os.path.join(dir_trat, t) for t in tratadas if t.startswith(base)]
        if not pares:
            continue
        saida |= avaliar(os.path.join(dir_orig, f), pares)
        print()
    return saida


def main(argv):
    if len(argv) >= 4 and argv[1] == "--pasta":
        return por_pasta(argv[2], argv[3])
    if len(argv) >= 3:
        return avaliar(argv[1], argv[2:])
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
