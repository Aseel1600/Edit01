// Despeja a estrutura COMPLETA de uma camada de texto para ficheiro, para depois
// se poder reconstruir por script sem depender de gravar presets a' mao.
//
// Le: animadores, seletores (e as EXPRESSOES, que sao a parte que interessa),
// propriedades animadas, efeitos com todos os valores, e marcadores.
//
// Procura a camada pelo NOME em todas as comps, porque a ponte trabalha por nome
// e nao se pode assumir qual e' a comp activa.

(function () {
    var ALVO = "Sala 29m2";          // <-- nome da camada que FUNCIONA
    var SAIDA = "C:/OpenMontage/tools/ae/estrutura.txt";

    var L = [];
    function p(s) { L.push(s); }

    function gravar() {
        var f = new File(SAIDA);
        f.encoding = "UTF-8";
        f.open("w");
        f.write(L.join("\n"));
        f.close();
    }

    // --- encontrar a camada ---
    var camada = null;
    var compNome = "";
    for (var i = 1; i <= app.project.numItems; i++) {
        var it = app.project.item(i);
        if (!(it instanceof CompItem)) { continue; }
        for (var j = 1; j <= it.numLayers; j++) {
            if (it.layer(j).name === ALVO) {
                camada = it.layer(j);
                compNome = it.name;
                break;
            }
        }
        if (camada !== null) { break; }
    }

    if (camada === null) {
        p("NAO ENCONTREI a camada '" + ALVO + "' em nenhuma comp.");
        p("Comps no projecto:");
        for (var k = 1; k <= app.project.numItems; k++) {
            var x = app.project.item(k);
            if (x instanceof CompItem) {
                p("  - " + x.name + "  (" + x.numLayers + " camadas)");
                for (var m = 1; m <= x.numLayers; m++) { p("      " + x.layer(m).name); }
            }
        }
        gravar();
        alert("Camada nao encontrada. Ver " + SAIDA);
        return;
    }

    p("camada : " + camada.name);
    p("comp   : " + compNome);
    p("inPoint " + camada.inPoint + "   outPoint " + camada.outPoint);
    p("");

    // --- MARCADORES: o suspeito principal ---
    var mk = camada.property("ADBE Marker");
    p("=== MARCADORES (" + mk.numKeys + ") ===");
    for (var mi = 1; mi <= mk.numKeys; mi++) {
        var v = mk.keyValue(mi);
        p("  t=" + mk.keyTime(mi) +
          "  comment='" + v.comment + "'" +
          "  duration=" + v.duration +
          "  label=" + v.label);
    }
    p("");

    // --- EFEITOS e todos os valores ---
    var ef = camada.property("ADBE Effect Parade");
    p("=== EFEITOS (" + ef.numProperties + ") ===");
    for (var e = 1; e <= ef.numProperties; e++) {
        var efx = ef.property(e);
        p("  [" + e + "] " + efx.name + "   matchName=" + efx.matchName);
        for (var q = 1; q <= efx.numProperties; q++) {
            var pr = efx.property(q);
            var linha = "        " + pr.name + "  (" + pr.matchName + ")";
            if (pr.numKeys > 0) {
                linha = linha + "  [" + pr.numKeys + " keyframes]";
            } else if (pr.value !== undefined) {
                linha = linha + " = " + pr.value.toString();
            }
            if (pr.expressionEnabled === true) {
                linha = linha + "\n            EXPR: " + pr.expression.replace(/\n/g, "\n                  ");
            }
            p(linha);
        }
    }
    p("");

    // --- ANIMADORES DE TEXTO: o que faltou no .ffx ---
    var txt = camada.property("ADBE Text Properties");
    var ans = txt.property("ADBE Text Animators");
    p("=== ANIMADORES (" + ans.numProperties + ") ===");
    for (var a = 1; a <= ans.numProperties; a++) {
        var an = ans.property(a);
        p("  [" + a + "] " + an.name + "   matchName=" + an.matchName);

        var sels = an.property("ADBE Text Selectors");
        p("      SELETORES (" + sels.numProperties + "):");
        for (var s = 1; s <= sels.numProperties; s++) {
            var sel = sels.property(s);
            p("        - " + sel.name + "   matchName=" + sel.matchName);
            for (var sp = 1; sp <= sel.numProperties; sp++) {
                var spp = sel.property(sp);
                var l2 = "            " + spp.name + "  (" + spp.matchName + ")";
                if (spp.numKeys > 0) {
                    l2 = l2 + "  [" + spp.numKeys + " keyframes]";
                    for (var kk = 1; kk <= spp.numKeys; kk++) {
                        l2 = l2 + "\n                k" + kk + " t=" + spp.keyTime(kk) +
                             " v=" + spp.keyValue(kk).toString();
                    }
                } else if (spp.value !== undefined) {
                    l2 = l2 + " = " + spp.value.toString();
                }
                if (spp.expressionEnabled === true) {
                    l2 = l2 + "\n                EXPR: " +
                         spp.expression.replace(/\n/g, "\n                      ");
                }
                p(l2);
            }
        }

        var props = an.property("ADBE Text Animator Properties");
        p("      PROPRIEDADES ANIMADAS (" + props.numProperties + "):");
        for (var pp = 1; pp <= props.numProperties; pp++) {
            var pr2 = props.property(pp);
            var l3 = "        - " + pr2.name + "  (" + pr2.matchName + ")";
            if (pr2.numKeys > 0) {
                l3 = l3 + "  [" + pr2.numKeys + " keyframes]";
            } else if (pr2.value !== undefined) {
                l3 = l3 + " = " + pr2.value.toString();
            }
            if (pr2.expressionEnabled === true) {
                l3 = l3 + "\n            EXPR: " +
                     pr2.expression.replace(/\n/g, "\n                  ");
            }
            p(l3);
        }
        p("");
    }

    gravar();
    alert("Estrutura despejada para:\n" + SAIDA);
})();
