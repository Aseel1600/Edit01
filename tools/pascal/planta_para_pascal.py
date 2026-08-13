# -*- coding: utf-8 -*-
"""Ponte: a nossa geometria (planta marcada a mao) -> Pascal Editor.

Porque e que isto existe
------------------------
A geometria de um imovel sai da planta que o Miguel marca a mao, e vive em tres
ficheiros JSON nossos (`paredes_reais.json`, `vaos_medidos.json`, `layout_px.json`).
O que custou caro no primeiro imovel nao foi renderizar, foi **corrigir**: catorze
rondas de "esta parede esta mal" -> ir ao Paint -> reler tracos -> remendar
coordenadas a mao.

O Pascal Editor (MIT, github.com/pascalorg/editor) resolve essa parte: e um editor
de edificios que corre no browser, com o mesmo modelo de dados que nos ja temos
(parede = start/end/height/thickness; portas e janelas presas a parede por wallId).
Traz um servidor MCP headless, portanto da para construir a cena por codigo, o
Miguel corrige a arrastar, e sai `export_glb` que o Blender importa nativamente.

O que este script NAO faz
-------------------------
Nao substitui o Blender. O render final continua a ser Cycles com HDRI, materiais,
mobiliario e camara animada. Isto trata so de geometria.

Nao usa o `analyze_floorplan_image` deles. Essa ferramenta delega a leitura da
planta no modelo anfitriao, devolve paredes e divisoes mas **nao devolve vaos**, e
e a abordagem que ja testamos e descartamos: a marcacao a mao ganha.

Uso
---
    py -3.11 tools/pascal/planta_para_pascal.py --cliente Luis
    py -3.11 tools/pascal/planta_para_pascal.py --cliente Luis --verificar
"""
import argparse
import json
import os
import sys
import subprocess

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CLIENTES = os.path.join(RAIZ, "projects", "video-service-business", "clients")

# Os mesmos valores da cena Blender. Se um dia divergirem, a maqueta e o editor
# passam a mostrar casas diferentes.
PE_DIREITO, ESP = 2.70, 0.16


# --------------------------------------------------------------------------- #
#  cliente MCP minimo (stdio)
# --------------------------------------------------------------------------- #
class Mcp:
    """Cliente MCP por stdio.

    ⚠️ Por stdio e nao por HTTP de proposito: o servidor HTTP deles guarda UMA
    sessao e responde `Server already initialized` a qualquer segundo cliente,
    portanto uma sonda esquecida numa consola chega para partir o script. Por
    stdio cada execucao arranca o seu proprio servidor e morre com ele.
    """

    def __init__(self, cena=None):
        cmd = ["bunx", "pascal-mcp", "--stdio"]
        if cena:
            cmd += ["--scene", cena]
        self.p = subprocess.Popen(cmd, cwd=os.path.dirname(os.path.abspath(__file__)),
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, text=True, encoding="utf-8",
                                  bufsize=1, shell=(os.name == "nt"))
        self._id = 0
        self._rpc("initialize", protocolVersion="2025-06-18", capabilities={},
                  clientInfo={"name": "planta_para_pascal", "version": "1"})
        self._envia({"jsonrpc": "2.0", "method": "notifications/initialized"})

    def _envia(self, corpo):
        self.p.stdin.write(json.dumps(corpo) + chr(10))
        self.p.stdin.flush()

    def _rpc(self, metodo, **params):
        self._id += 1
        self._envia({"jsonrpc": "2.0", "id": self._id, "method": metodo, "params": params})
        while True:
            linha = self.p.stdout.readline()
            if not linha:
                raise RuntimeError(f"servidor morreu: {self.p.stderr.read()[:500]}")
            linha = linha.strip()
            if not linha.startswith("{"):
                continue
            r = json.loads(linha)
            if r.get("id") == self._id:
                if "error" in r:
                    raise RuntimeError(f"{metodo}: {r['error']}")
                return r.get("result", {})

    def chama(self, nome, **args):
        res = self._rpc("tools/call", name=nome, arguments=args)
        if res.get("isError"):
            raise RuntimeError(f"{nome}: {res.get('content')}")
        sc = res.get("structuredContent")
        if sc is not None:
            return sc
        for c in res.get("content", []):
            if c.get("type") == "text":
                try:
                    return json.loads(c["text"])
                except json.JSONDecodeError:
                    return c["text"]
        return res

    def fecha(self):
        try:
            self.p.stdin.close(); self.p.terminate()
        except Exception:
            pass


# --------------------------------------------------------------------------- #
#  leitura da nossa geometria
# --------------------------------------------------------------------------- #
def carrega(cliente):
    base = os.path.join(CLIENTES, cliente, "build", "3d")
    sys.path.insert(0, base)                       # para as regras dos vaos
    from vaos_regras import dims_vao, especie_vao

    def le(nome):
        with open(os.path.join(base, nome), encoding="utf-8") as f:
            return json.load(f)

    layout = le("layout_px.json")
    S = layout["escala"]
    div = layout["divisoes"]
    x0 = min(r[0] for r in div.values())
    y0 = min(r[1] for r in div.values())
    # ⚠️ o mesmo referencial da cena Blender: Y invertido, senao a casa sai em espelho
    P = lambda x, y: ((x - x0) / S, -(y - y0) / S)
    return base, S, P, le("paredes_reais.json"), le("vaos_medidos.json"), dims_vao, especie_vao


def extremos(p, P):
    """parede em pixel -> (inicio, fim) em metros"""
    if p["tipo"] == "h":
        return P(p["a"], p["c"]), P(p["b"], p["c"])
    return P(p["c"], p["a"]), P(p["c"], p["b"])


def parede_do_vao(v, paredes):
    """(indice da parede, contido) para um vao.

    ⚠️ Diferenca real entre os dois modelos: no nosso, um vao pode atravessar o
    fim de uma parede e o vazio ate a seguinte, porque o corte booleano so tira o
    que la estiver. No Pascal um vao vive DENTRO de uma parede. Aconteceu com a
    porta do closet do Luis (430->504, com a parede a acabar em 454). Em vez de o
    perder em silencio, escolhe-se a parede de maior sobreposicao e assinala-se.
    """
    melhor, area = None, 0
    for i, p in enumerate(paredes):
        if p["tipo"] != v["tipo"] or abs(p["c"] - v["c"]) > 2:
            continue
        sobrep = min(v["fim"], p["b"]) - max(v["ini"], p["a"])
        if sobrep > area:
            melhor, area = i, sobrep
    if melhor is None:
        return None, False
    p = paredes[melhor]
    contido = p["a"] - 2 <= v["ini"] and v["fim"] <= p["b"] + 2
    return melhor, contido


# --------------------------------------------------------------------------- #
#  construcao
# --------------------------------------------------------------------------- #
def constroi(cliente, saida):
    base, S, P, paredes, vaos, dims_vao, especie_vao = carrega(cliente)
    m = Mcp()

    cena = m.chama("get_scene")
    nivel = next(n["id"] for n in cena["nodes"].values() if n["type"] == "level")
    print(f"[pascal] nivel {nivel}")

    ids = []
    for p in paredes:
        (ax, ay), (bx, by) = extremos(p, P)
        r = m.chama("create_wall", levelId=nivel, start=[ax, ay], end=[bx, by],
                    thickness=ESP, height=PE_DIREITO)
        ids.append(r["wallId"])
    print(f"[pascal] {len(ids)} paredes criadas")

    postos, orfaos, parciais = 0, [], []
    for v in vaos:
        i, contido = parede_do_vao(v, paredes)
        if i is None:
            orfaos.append(v)
            continue
        if not contido:
            parciais.append(v)
        larg, alt, z0 = dims_vao(v)
        esp = especie_vao(v)
        # ⚠️ `position` e NORMALIZADO (0 a 1) ao longo da parede, nao metros.
        # Em metros o servidor rejeita com "Too big: expected number to be <=1".
        p = paredes[i]
        pos = min(1.0, max(0.0, ((v["ini"] + v["fim"]) / 2 - p["a"]) / (p["b"] - p["a"])))
        if esp in ("janela", "correr"):
            m.chama("add_window", wallId=ids[i], position=pos,
                    width=larg, height=alt, sillHeight=z0)
        else:
            m.chama("add_door", wallId=ids[i], position=pos, width=larg, height=alt)
        postos += 1
    print(f"[pascal] {postos} de {len(vaos)} vaos colocados")
    if orfaos:
        print(f"[pascal] AVISO: {len(orfaos)} sem parede nenhuma: {orfaos}")
    for v in parciais:
        print(f"[pascal] AVISO: vao atravessa o fim da parede, colocado na de maior "
              f"sobreposicao: {v}")

    val = m.chama("validate_scene")
    print(f"[pascal] validate_scene -> {json.dumps(val)[:300]}")

    os.makedirs(saida, exist_ok=True)
    cena = m.chama("export_json", pretty=True)
    alvo = os.path.join(saida, f"{cliente.lower()}_pascal.json")
    with open(alvo, "w", encoding="utf-8") as f:
        f.write(cena["json"] if isinstance(cena, dict) else str(cena))
    print(f"[pascal] cena -> {alvo}  ({os.path.getsize(alvo)/1024:.0f} KB)")

    try:
        glb = m.chama("export_glb")
        print(f"[pascal] export_glb -> {json.dumps(glb)[:200]}")
    except Exception as e:
        print(f"[pascal] AVISO: export_glb falhou: {e}")
    return alvo


def verifica(cliente, caminho):
    """Compara o que saiu do Pascal com os nossos numeros. E o unico teste que conta."""
    base, S, P, paredes, vaos, dims_vao, _ = carrega(cliente)
    with open(caminho, encoding="utf-8") as f:
        cena = json.load(f)
    nos = cena["nodes"].values()
    pw = [n for n in nos if n["type"] == "wall"]
    pj = [n for n in nos if n["type"] == "window"]
    pd = [n for n in nos if n["type"] == "door"]

    print(f"contagens   nossas: {len(paredes)} paredes, {len(vaos)} vaos")
    print(f"            pascal: {len(pw)} paredes, {len(pj)} janelas + {len(pd)} portas "
          f"= {len(pj)+len(pd)} vaos")

    # comprimento total de parede, que apanha erros de escala e de eixo trocado
    def comp(a, b):
        return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5
    nosso = sum(comp(*extremos(p, P)) for p in paredes)
    deles = sum(comp(w["start"], w["end"]) for w in pw)
    print(f"comprimento total de parede   nosso {nosso:7.2f} m   pascal {deles:7.2f} m   "
          f"diferenca {abs(nosso-deles):.3f} m")

    largs_n = sorted(round(dims_vao(v)[0], 2) for v in vaos)
    largs_p = sorted(round(n.get("width", 0), 2) for n in pj + pd)
    print(f"larguras dos vaos iguais? {'SIM' if largs_n == largs_p else 'NAO'}")
    if largs_n != largs_p:
        print(f"   nossas: {largs_n}")
        print(f"   pascal: {largs_p}")


# --------------------------------------------------------------------------- #
#  regresso: cena do Pascal -> a nossa geometria
# --------------------------------------------------------------------------- #
def importa(cliente, caminho, escrever=False):
    """Le uma cena do Pascal e devolve-a no NOSSO formato.

    E este o caminho que interessa: o Miguel corrige a arrastar no editor, grava,
    e a correcao volta para os JSON que alimentam o Blender. Por omissao escreve
    ficheiros `*.NOVO.json` ao lado dos originais; nao substitui nada sem `--escrever`.
    """
    base, S, P, paredes_o, vaos_o, dims_vao, _ = carrega(cliente)
    layout = json.load(open(os.path.join(base, "layout_px.json"), encoding="utf-8"))
    div = layout["divisoes"]
    x0 = min(r[0] for r in div.values())
    y0 = min(r[1] for r in div.values())
    # inverso exacto de P
    px = lambda X: X * S + x0
    py = lambda Y: -Y * S + y0

    cena = json.load(open(caminho, encoding="utf-8"))
    nos = cena["nodes"]
    paredes, por_id = [], {}
    for n in nos.values():
        if n.get("type") != "wall":
            continue
        (sx, sy), (ex, ey) = n["start"], n["end"]
        if abs(sy - ey) <= abs(sx - ex):                     # horizontal
            p = {"tipo": "h", "c": round(py(sy)),
                 "a": round(min(px(sx), px(ex))), "b": round(max(px(sx), px(ex)))}
        else:
            p = {"tipo": "v", "c": round(px(sx)),
                 "a": round(min(py(sy), py(ey))), "b": round(max(py(sy), py(ey)))}
        por_id[n["id"]] = p
        paredes.append(p)

    vaos = []
    for n in nos.values():
        t = n.get("type")
        if t not in ("window", "door"):
            continue
        p = por_id.get(n.get("wallId"))
        if p is None:
            print(f"[import] AVISO: vao sem parede conhecida, ignorado: {n.get('id')}")
            continue
        larg = float(n.get("width", 0.9))
        # ⚠️ O `position` GUARDADO no no nao e o `position` que a ferramenta
        # `add_window` ACEITA. A ferramenta quer um t normalizado (0 a 1); o no
        # guarda [distancia em metros ao longo da parede, cota do centro, desvio].
        # Confundir os dois poe todos os vaos no sitio errado sem dar erro nenhum.
        along = float(n["position"][0]) if isinstance(n.get("position"), list)             else float(n.get("position", 0.5)) * (p["b"] - p["a"]) / S
        centro = p["a"] + along * S
        meia = larg * S / 2
        v = {"tipo": p["tipo"], "c": p["c"],
             "ini": round(centro - meia), "fim": round(centro + meia),
             "larg_m": round(larg, 2)}
        # as flags recuperam-se do tipo de no e da altura: a entrada e a unica
        # porta com 2,30 m, e e assim que dims_vao a distingue
        if t == "window":
            v["janela"] = True
        elif abs(float(n.get("height", 2.05)) - 2.30) < 0.02:
            v["entrada"] = True
        vaos.append(v)

    if escrever:
        for nome, dados in (("paredes_reais", paredes), ("vaos_medidos", vaos)):
            alvo = os.path.join(base, f"{nome}.NOVO.json")
            with open(alvo, "w", encoding="utf-8") as f:
                json.dump(dados, f, indent=1, ensure_ascii=False)
            print(f"[import] {alvo}")
    return paredes, vaos


def compara_ida_e_volta(cliente, caminho):
    """Prova o ciclo completo: o que volta tem de ser o que saiu."""
    base, S, P, paredes_o, vaos_o, dims_vao, _ = carrega(cliente)
    paredes_n, vaos_n = importa(cliente, caminho)

    def chave_p(p):
        return (p["tipo"], p["c"], p["a"], p["b"])

    def chave_v(v):
        return (v["tipo"], v["c"], v["ini"], v["fim"], round(v["larg_m"], 2),
                bool(v.get("janela")), bool(v.get("entrada")))

    op, np_ = sorted(map(chave_p, paredes_o)), sorted(map(chave_p, paredes_n))
    ov, nv = sorted(map(chave_v, vaos_o)), sorted(map(chave_v, vaos_n))

    print(f"paredes  saiu {len(op)}  voltou {len(np_)}   iguais? "
          f"{'SIM' if op == np_ else 'NAO'}")
    if op != np_:
        for a, b in zip(op, np_):
            if a != b:
                print(f"   saiu {a}   voltou {b}")
    print(f"vaos     saiu {len(ov)}  voltou {len(nv)}   iguais? "
          f"{'SIM' if ov == nv else 'NAO'}")
    if ov != nv:
        so, sn = set(ov), set(nv)
        for x in sorted(so - sn):
            print(f"   perdido: {x}")
        for x in sorted(sn - so):
            print(f"   novo   : {x}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--cliente", required=True)
    ap.add_argument("--saida", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "cenas"))
    ap.add_argument("--verificar", action="store_true",
                    help="so compara a cena ja exportada com a nossa geometria")
    ap.add_argument("--voltar", action="store_true",
                    help="le a cena do Pascal e prova que volta igual ao que saiu")
    ap.add_argument("--escrever", action="store_true",
                    help="com --voltar, grava paredes_reais.NOVO.json e vaos_medidos.NOVO.json")
    a = ap.parse_args()
    alvo = os.path.join(a.saida, f"{a.cliente.lower()}_pascal.json")
    if a.voltar:
        compara_ida_e_volta(a.cliente, alvo)
        if a.escrever:
            importa(a.cliente, alvo, escrever=True)
    else:
        if not a.verificar:
            alvo = constroi(a.cliente, a.saida)
        verifica(a.cliente, alvo)
