---
name: acestep
description: Music generation for video production — background beds, jingles, mood tracks. Use when generating music, soundtracks, or a music bed for a video. Triggers include background music, soundtrack, jingle, music generation, musical composition. NOTE the working path is the ElevenLabs MCP, not a local model — read the top of this skill before writing any command.
---

# Music generation

> 🔴 **Este ficheiro estava errado até 2026-08-10.** Prometia *"open-source music generation
> (MIT license) via `tools/music_gen.py`, runs on RunPod serverless"* com
> `RUNPOD_API_KEY` e `RUNPOD_ACESTEP_ENDPOINT_ID`. **Nada disso corresponde ao que existe.**
> Quem seguisse os exemplos à letra apanhava um ficheiro inexistente, e depois um 401.
> O que está abaixo é o que funciona de facto, verificado nesse dia.

## O que usar: o MCP `generate_music`

```
mcp__ElevenLabs_Player__generate_music
  prompt            : descrição do estilo (ver "Escrever o prompt")
  duration_seconds  : duração exacta em segundos
  instrumental      : true  ← quase sempre, para cama de música
  title             : nome curto
```

Corre na **subscrição** do utilizador, não na chave do `.env`. Gera **e toca** a faixa.

⚠️ **A chave `ELEVENLABS_API_KEY` do `.env` está MORTA** (401 em `/v1/music`, `/v1/voices` e
`/v1/user`). A `FAL_KEY` também. **As credenciais boas vivem nos MCP**, não no `.env`.

⚠️ **O MCP devolve o caminho do ficheiro por expandir** (`${user_config.output_dir}\...`).
Se precisares do ficheiro em disco para montar, conta com procurá-lo ou pedi-lo ao utilizador.

### A ferramenta em `tools/audio/music_gen.py`

Existe, mas **é um invólucro da API ElevenLabs** (`https://api.elevenlabs.io/v1/music`) e
depende da chave morta. Não é ACE-Step, não é RunPod, não é local. O caminho na versão antiga
desta skill (`tools/music_gen.py`) também estava errado. Classe `MusicGen`, `name="music_gen"`,
campos `prompt` (obrigatório) e `duration_seconds`. **Não a uses enquanto a chave estiver morta.**

## ❌ ACE-Step local: testado e reprovado

A 10/08/2026 correu-se ACE-Step 1.5 XL SFT local no Maestro, 60 s instrumental, contra uma
faixa ElevenLabs com o mesmo briefing. **O Miguel ouviu e reprovou.** Os pesos foram apagados
(5,85 GB); o código do Maestro em `models/TTS/ace_step*` ficou.

Se algum dia se voltar a tentar, a invocação certa pelo CLI do Maestro é:

```json
{
  "settings_version": 2.57,
  "model_type": "ace_step_v1_5_xl_sft",
  "prompt": "[instrumental]",
  "alt_prompt": "<o estilo vai AQUI>",
  "duration_seconds": 60,
  "num_inference_steps": 30,
  "guidance_scale": 7.0,
  "scheduler_type": "euler",
  "seed": 42
}
```

⚠️ No ACE-Step o **`prompt` é a LETRA** e o **`alt_prompt` é o ESTILO**. `prompt` vazio é
rejeitado com *"Prompt cannot be empty"*; para instrumental usa-se `[instrumental]`.
Saída: WAV 48 kHz estéreo com a duração exacta pedida.

## 🔴 O que NÃO existe pelo caminho que funciona

A versão antiga desta skill documentava capacidades que o MCP **não tem**. Não as prometas:

| prometido antes | realidade |
|---|---|
| `--preset corporate-bg` etc. | ❌ não há presets; põe o estilo no texto |
| `--bpm 120 --key "D Major"` | ❌ não há campos; escreve "around 120 BPM" no prompt |
| `--seed 42` | ❌ **não há seed**, portanto não há repetibilidade |
| `--cover --reference x.mp3` | ❌ não há style transfer |
| `--extract vocals` | ❌ não há separação de stems |
| `--brand <name>` | ❌ não existe |

➡️ **A ausência de seed é a limitação que mais custa:** não dá para variar uma coisa e
atribuir-lhe a diferença. Iterar é gerar outra vez e ouvir.

## Escrever o prompt

Isto **transfere** para qualquer motor e é a parte que valia a pena guardar.

**Camadas a incluir:** género, emoção, instrumentos, timbre, época, produção, e se é
instrumental. Métricas como BPM entram como texto, já que não há campo.

**Bom:** *"Slow melancholic piano ballad, intimate female vocal, warm strings building to a
powerful chorus, studio-polished production"*
**Mau:** *"Sad song"*

**Princípios:**

1. **Específico bate vago.** Descreve instrumentos, humor e produção.
2. **Sem contradições.** Não peças "cordas clássicas" e "metal" ao mesmo tempo.
3. **Repetir reforça prioridade.**
4. **Prompt esparso dá mais liberdade ao modelo;** prompt detalhado constrange.
5. **Diz o que NÃO queres.** Foi assim que se travou o piano.

### 🔒 Regra da casa, para música nossa

**Chill electro. NADA de piano.** Duas faixas de piano foram reprovadas seguidas.
E para cama sob narração, o prompt deve pedir explicitamente **energia constante, sem build,
sem drop, sem pancadas de trailer**, senão a faixa compete com a voz.

**Faixa nova por cliente, nunca repetida entre clientes.**

## Integração em vídeo

**Duração:** planear as durações das cenas primeiro, a partir do guião de voz, e pedir a
música com a duração exacta.

**Mistura:** cama de música a **10-20%** sob narração.

```tsx
<Audio src={staticFile('voiceover.mp3')} volume={1} />
<Audio src={staticFile('bg-music.mp3')} volume={0.15} />
```

Ver `RETOQUE-FINAL.md` para os alvos de entrega: **−16 LUFS** no 16:9, **−14** nos Reels,
true peak **≤ −1 dBTP**.

## Quando NÃO usar isto

- **Narração e voz** → ver a regra de voz PT-PT; TTS não é geração de música
- **Efeitos sonoros** → `mcp__ElevenLabs_Player__generate_sound_effect`
- **Separação de stems** → não existe por aqui; procurar ferramenta dedicada
