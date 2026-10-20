# Optional CUDA runtime for Phase09 latency work

The preserved reference container uses the CPU image. This CUDA configuration
reserves one NVIDIA GPU and offloads24layers. An initial8layer readiness load used
about1.1GB;24layers then loaded successfully atabout2.1GB,leavingabout1.8GBfree.
This was one capacity adjustment before timed observations,not a layer sweep. The laptop
has4GBVRAM;the existing GGUF is5.126GB,so complete GPU placement is not assumed.
Startup logs and actual requests verified GPU loading and faster execution;see
[measured results and limits](../plans/2026-10-20-phase09-latency-results.md).

The official linux/amd64 image is pinned to manifest
`sha256:f66a5229a3e0586339d16155e9fe09c37834d7a7f4134bbdee7360b5a1f2546d`.
Its compressed layers total2,594,107,748bytes(~2.42GiB);a pull may reuse local
layers. No GGUF download,copy or project dependency change is needed. Driver596.36
detects the RTX3050Laptop. Docker DeviceRequests and actual offload were verified.

This configuration uses localhost18088 and a distinct container;the existing CPU
container on18087 is preserved. It mounts only the existing model root read-only,
refuses to create a missing host directory,and never pulls an image implicitly.
Context8192,one slot,output768 and8CPUthreads match the previous runtime. Record
the actual CUDA build/template before comparing;do not assume builds match by tag.

Validate without starting or downloading anything:

```powershell
$env:MODELS_DIR='C:/Coding-projects/bintanong_workspace/MODELS'
docker compose -f docker/bintu-cuda.compose.yaml config
```

After the repository's download authorization boundary is satisfied:

```powershell
docker compose -f docker/bintu-cuda.compose.yaml pull --policy always bintu_cuda
docker compose -f docker/bintu-cuda.compose.yaml up -d --pull never bintu_cuda
docker logs bintanong-p09-cuda-latency
```

Verify actual GPU offload,VRAM use,`http://127.0.0.1:18088/health` and `/props`
before using the runner's `--url http://127.0.0.1:18088`. The CUDA container is
currently running;the CPU reference is stopped intact to free RAM. The runner's
default URL remains18087,so the explicit18088 flag is required for CUDA.
Keep guards and timing budgets fixed. To return to the preserved CPU runtime:

```powershell
docker compose -f docker/bintu-cuda.compose.yaml stop bintu_cuda
docker start bintanong-p07-router-offline
```

Official references:[llama.cpp Docker](https://github.com/ggml-org/llama.cpp/blob/master/docs/docker.md),
[server options](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md),
[Compose GPU reservations](https://docs.docker.com/compose/how-tos/gpu-support/).
