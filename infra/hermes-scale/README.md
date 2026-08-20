# Hermes scale configs

Planning session: `cse_01PrUJjvaENr4zTMsM1UB4Bb`

These files do not purchase GPUs, VPS plans, or API credits.

```
Users → https://hermestudios.com  (Hostinger VPS, services/hermes-api)
      → INFERENCE_BASE_URL        (NVIDIA vLLM or hosted OpenAI-compatible API)
Mac   → OpenMontage + LM Studio   (studio only, never the public hot path)
```

| Phase | Env | Compose |
|-------|-----|---------|
| 0 prove traffic | `env/inference-hosted.env.example` + `env/gateway.env.example` | Hostinger `services/hermes-api/docker-compose.yml` |
| 1 ~50 in-flight | `env/inference-nvidia.env.example` (`TENSOR_PARALLEL_SIZE=2`) | `compose/docker-compose.vllm.yml` |
| 2 450–550 in-flight | same NVIDIA env (`TENSOR_PARALLEL_SIZE=8`) | same compose, 8-GPU box (or two boxes) |
| AMD cost-play | `env/inference-amd.env.example` | `compose/docker-compose.vllm-amd.yml` |

Mac: `env/mac-studio.env.example` plus `services/hermes-api/cloudflared.yml.example`.

GPU node TLS (optional, private network preferred): `Caddyfile.gpu-node`.
