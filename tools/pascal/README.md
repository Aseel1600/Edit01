# Ponte planta ↔ Pascal Editor

**Feita 29/07/2026.** Liga a nossa geometria (planta marcada à mão → JSON) ao
[Pascal Editor](https://github.com/pascalorg/editor), um editor de edifícios 3D open
source (MIT) que corre no browser.

## Para que serve

No primeiro imóvel (Luís, Pinhal do General) o que custou caro **não foi renderizar,
foi corrigir**: catorze rondas de "esta parede está mal" → ir ao Paint → reler traços
vermelhos → remendar coordenadas à mão.

Esta ponte troca esse ciclo por: nós geramos a cena, o Miguel **arrasta a parede no
browser**, e a correção volta para os JSON que alimentam o Blender.

## Estado: PROVADO ponta a ponta

Testado contra o modelo do Luís, que é o caso de teste perfeito porque já sabemos qual
é o resultado certo.

| Verificação | Resultado |
|---|---|
| Paredes exportadas | 28 de 28 |
| Vãos exportados | 15 de 15 |
| **Comprimento total de parede** | **99,67 m dos dois lados, diferença 0,000 m** |
| Larguras dos vãos | todas iguais |
| `validate_scene` do Pascal | `valid: true`, zero erros |
| **Regresso: paredes** | **28 de 28 idênticas** |
| Regresso: vãos | 14 de 15 idênticos (o 15.º é um caso conhecido, ver abaixo) |
| Correção simulada (parede arrastada 0,5 m) | chegou ao nosso lado como 41 px, e 0,5 m = 41,5 px |
| Ficheiro produzido recarrega no servidor deles | sim, `valid: true` |

## Como se usa

```bash
py -3.11 tools/pascal/planta_para_pascal.py --cliente Luis
```

Constrói a cena e grava `tools/pascal/cenas/luis_pascal.json`. Depois:

```bash
py -3.11 tools/pascal/planta_para_pascal.py --cliente Luis --voltar --escrever
```

Lê a cena, prova que o que volta é o que saiu, e grava `paredes_reais.NOVO.json` e
`vaos_medidos.NOVO.json` ao lado dos originais. **Não substitui nada sem `--escrever`**,
e mesmo assim escreve para `.NOVO.json`: a substituição é decisão de quem está a ver.

## Instalação (já feita nesta máquina)

```bash
npm i -g bun                      # bun 1.3.14
cd tools/pascal && bun add @pascal-app/mcp @pascal-app/core
```

## O que NÃO faz, e é preciso saber

**Não substitui o Blender.** O Pascal é WebGPU em tempo real, para editar. O produto
continua a ser Cycles com HDRI, materiais, mobiliário e câmara animada. Isto trata só de
geometria: paredes, portas e janelas.

**Não usa o `analyze_floorplan_image` deles.** Essa ferramenta delega a leitura da planta
no modelo anfitrião, devolve paredes e divisões mas **não devolve vãos**, e é a
abordagem que já testámos e descartámos. A marcação à mão do Miguel ganha.

**O `export_glb` não funciona headless.** Responde
`GLB export requires the Three.js renderer, which is browser-only`. Não faz falta: a
troca é em JSON e nós já construímos a partir de JSON.

**O `save_scene` falha** nesta instalação (`this.withWriteTransaction` indefinido), o que
quer dizer que a base SQLite partilhada com o editor não arranca. **A passagem para o
browser faz-se pelo ficheiro JSON**, não pela base. ⚠️ Ainda **não foi verificado** que o
editor no browser importa este JSON tal e qual; é o passo seguinte se se quiser usar a
sério.

## Armadilhas que já custaram tempo

**O `position` que a ferramenta ACEITA não é o `position` que o nó GUARDA.** O
`add_window` quer um `t` normalizado de 0 a 1; o nó guarda
`[distância em metros ao longo da parede, cota do centro, desvio]`. Confundir os dois põe
todos os vãos no sítio errado **sem dar erro nenhum**.

**O servidor HTTP guarda UMA sessão** e responde `Server already initialized` a qualquer
segundo cliente. Uma sonda esquecida numa consola chega para partir tudo. Por isso a
ponte fala **stdio**: cada execução arranca o seu servidor e morre com ele.

**O `create_wall` devolve `{"wallId": ...}`**, não `id` nem `nodeId`.

**Um vão nosso pode atravessar o fim de uma parede; um vão do Pascal não.** No nosso
modelo o corte booleano só tira o que lá estiver, portanto a porta do closet do Luís
(430→504, com a parede a acabar em 454) funciona. No Pascal um vão vive **dentro** de uma
parede. A ponte escolhe a parede de maior sobreposição e **assinala em vez de perder em
silêncio**. É a única diferença nos 15 vãos, e é conhecida.

**A consola do Windows é cp1252** e rebenta com emoji nos `print`.

## Onde vivem as regras

As regras dos vãos (largura, altura, peitoril) estão em
`clients/<cliente>/build/3d/vaos_regras.py`, **um módulo sem `bpy`**, porque são precisas
em três sítios: o corte booleano na parede, a caixilharia, e esta ponte, que corre fora do
Blender. Escritas em mais do que um sítio, basta mexer numa para o caixilho deixar de
encaixar no buraco.
