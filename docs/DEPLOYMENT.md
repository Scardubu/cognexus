# Production Deployment

Nexus-OpenAI is designed for a Linux container platform, a single Linux VM, or a managed Kubernetes service. Redis is the recommended production session backend.

## Deployment topology

Minimum production topology:

1. One or more API containers.
2. A private Redis 7 service with authentication and TLS where supported.
3. An OpenTelemetry collector or managed OTLP endpoint.
4. A reverse proxy or managed load balancer that terminates TLS.
5. A secret manager that injects environment variables at runtime.

Do not expose Redis directly to the public internet.

## Docker Compose deployment

Create the environment file:

```bash
cp .env.example .env
```

Generate independent credentials rather than editing template placeholders:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Set production values through a secret manager or a mode-`0600` local environment file:

```dotenv
NEXUS_ENV=production
OPENAI_API_KEY=<provider key from the secret manager>
NEXUS_API_KEY=<independent generated service key>
NEXUS_SESSION_BACKEND=redis
REDIS_URL=rediss://<user>:<password>@<private-redis-host>:6379/0
NEXUS_ALLOW_SQLITE_FALLBACK=false
# Optional; omitted values automatically reuse REDIS_URL in a live Redis deployment.
NEXUS_RATE_LIMIT_STORAGE_URI=
NEXUS_CORS_ORIGINS=https://app.example.com
NEXUS_TRUSTED_HOSTS=api.example.com
# Use the exact reverse-proxy or ingress source IP/CIDR, never a public wildcard.
NEXUS_FORWARDED_ALLOW_IPS=10.0.0.0/24
NEXUS_OTEL_ENABLED=true
OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317
```

Live configuration rejects placeholder credentials, shared OpenAI/service secrets,
wildcard proxy trust, wildcard CORS/hosts, and process-local rate limiting when Redis
sessions are used. Configure Redis with authentication, TLS/private networking,
persistence appropriate to the recovery objective, and `noeviction`.

Start the services:

```bash
docker compose up --build -d
```

Inspect status:

```bash
docker compose ps
docker compose logs --tail=200 nexus
docker compose logs --tail=200 redis
```

Verify from the host:

```bash
curl -f http://localhost:8000/health
curl -f http://localhost:8000/ready
```

Stop safely:

```bash
docker compose down
```

Remove local persistent data only when intentionally resetting the deployment:

```bash
docker compose down -v
```

## Standalone Docker deployment

Build:

```bash
docker build -t nexus-openai:3.3.1 .
```

Run with an environment file:

```bash
docker run --rm \
  --name nexus-openai \
  --env-file .env \
  -p 8000:8000 \
  nexus-openai:3.3.1
```

The image runs as a non-root user and includes a health check.

## Linux VM deployment without Docker

Create a service account and installation directory:

```bash
sudo useradd --system --create-home --shell /usr/sbin/nologin nexus
sudo mkdir -p /opt/nexus-openai /var/lib/nexus-openai /var/log/nexus-openai
sudo chown -R nexus:nexus /opt/nexus-openai /var/lib/nexus-openai /var/log/nexus-openai
```

Copy the repository to `/opt/nexus-openai`, then install as the service account:

```bash
sudo -u nexus python3 -m venv /opt/nexus-openai/.venv
sudo -u nexus /opt/nexus-openai/.venv/bin/python -m pip install --upgrade "pip>=26,<27"
sudo -u nexus /opt/nexus-openai/.venv/bin/python -m pip install -r /opt/nexus-openai/requirements.txt
sudo -u nexus /opt/nexus-openai/.venv/bin/python -m pip check
sudo -u nexus /opt/nexus-openai/.venv/bin/python /opt/nexus-openai/scripts/verify_version.py
```

Create `/etc/nexus-openai.env` with mode `0600`:

```bash
sudo install -m 600 /dev/null /etc/nexus-openai.env
sudo editor /etc/nexus-openai.env
```

Example systemd unit at `/etc/systemd/system/nexus-openai.service`:

```ini
[Unit]
Description=Nexus OpenAI Production API
After=network-online.target redis-server.service
Wants=network-online.target

[Service]
Type=simple
User=nexus
Group=nexus
WorkingDirectory=/opt/nexus-openai
EnvironmentFile=/etc/nexus-openai.env
ExecStart=/opt/nexus-openai/.venv/bin/cognexus-server
Restart=always
RestartSec=5
TimeoutStopSec=30
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/lib/nexus-openai /var/log/nexus-openai

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now nexus-openai
sudo systemctl status nexus-openai
sudo journalctl -u nexus-openai -n 200 --no-pager
```

Put Nginx, Caddy, or a managed load balancer in front of `127.0.0.1:8000` and require HTTPS.
Set `NEXUS_HOST=127.0.0.1`, `NEXUS_PORT=8000`, `NEXUS_WORKERS=2`, and
`NEXUS_FORWARDED_ALLOW_IPS=127.0.0.1` in `/etc/nexus-openai.env`. The launcher applies
those validated values consistently. Multi-worker operation requires Redis sessions and
shared Redis-backed rate limits.

## Managed container platforms

Use these settings on ECS, Cloud Run, Azure Container Apps, Render, Fly.io, Railway, or Kubernetes:

- Container port: `8000`
- Liveness path: `/health`
- Readiness path: `/ready`
- Startup grace period: at least 30 seconds
- Minimum memory: 512 MiB; 1 GiB recommended
- Writable volume only if SQLite is used
- Redis reachable over a private network, configured with authentication/TLS and `noeviction`
- Secrets injected from the platform secret manager and rejected when placeholders are detected
- Exact proxy source CIDRs configured through `NEXUS_FORWARDED_ALLOW_IPS`
- Shared Redis rate-limit storage for multiple workers or replicas
- At least two replicas only when using Redis sessions; Cognexus uses a bounded Redis lease to preserve same-session ordering across replicas

## Kubernetes probes

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 20
readinessProbe:
  httpGet:
    path: /ready
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 10
```

## CI/CD

`.github/workflows/ci.yml` runs linting, type checking, unit tests, and the dry-run smoke test. `.github/workflows/docker.yml` builds and optionally publishes the image to GitHub Container Registry.

Required GitHub configuration:

1. Enable Actions for the repository.
2. Grant workflow permissions to read repository contents and write packages if publishing images.
3. Protect the production branch and require the CI workflow.
4. Use an environment approval gate for production deployment jobs added by your hosting platform.

No OpenAI key is required for the default CI checks because the smoke test uses dry-run mode.

## Rollback

Keep immutable image tags based on the Git commit SHA. To roll back:

```bash
docker pull ghcr.io/OWNER/REPOSITORY:PREVIOUS_SHA
docker tag ghcr.io/OWNER/REPOSITORY:PREVIOUS_SHA nexus-openai:rollback
docker compose up -d --no-deps nexus
```

For a managed platform, redeploy the previous immutable image digest. Verify `/health`, `/ready`, one dry-run-equivalent test environment request, logs, and error-rate metrics before declaring recovery.

## Kubernetes deployment

A hardened baseline is provided in `deploy/kubernetes/`. It includes:

- a restricted namespace and non-root service account;
- two replicas with zero-unavailable rolling updates;
- startup, liveness, and readiness probes;
- CPU/memory requests and limits;
- a horizontal pod autoscaler and disruption budget;
- read-only root filesystems, dropped capabilities, and runtime-default seccomp;
- explicit ingress/egress network policy;
- ConfigMap defaults and a non-applied secret example.

Before deployment, replace the image reference and create `cognexus-secrets` through External Secrets, Sealed Secrets, or the platform secret manager. A direct command for a controlled test namespace is:

```bash
kubectl create namespace cognexus --dry-run=client -o yaml | kubectl apply -f -
kubectl -n cognexus create secret generic cognexus-secrets \
  --from-literal=OPENAI_API_KEY="${OPENAI_API_KEY}" \
  --from-literal=NEXUS_API_KEY="${NEXUS_API_KEY}" \
  --from-literal=REDIS_URL="${REDIS_URL}" \
  --from-literal=NEXUS_CORS_ORIGINS="https://app.example.com" \
  --from-literal=NEXUS_TRUSTED_HOSTS="api.example.com" \
  --from-literal=OTEL_EXPORTER_OTLP_ENDPOINT="${OTEL_EXPORTER_OTLP_ENDPOINT}"
```

Edit `deploy/kubernetes/deployment.yaml` or use a Kustomize overlay to set the immutable image digest, then apply:

```bash
kubectl apply -k deploy/kubernetes
kubectl -n cognexus rollout status deployment/cognexus
kubectl -n cognexus get pods,svc,hpa,pdb
```

Label only namespaces allowed to call the API:

```bash
kubectl label namespace YOUR_INGRESS_NAMESPACE cognexus-ingress=true
```

The sample network policy permits outbound DNS, HTTPS, Redis, and OTLP while blocking cloud link-local metadata ranges. Adapt it to the exact managed Redis and collector destinations when the cluster supports narrower egress controls.

## Automated deployment verification

Run static container and Kubernetes verification before applying manifests:

```bash
python scripts/verify_deployment.py
```

After deployment, probe the live service and authenticated deterministic recommendation path:

```bash
python scripts/verify_deployment.py \
  --base-url https://cognexus.example.com \
  --api-key "${NEXUS_API_KEY}"
```

The same verifier is available through `.github/workflows/deployment-verification.yml`. A release is not promoted when readiness, critical synthetic behavior, Redis/session topology, image scanning, or rollback evidence is missing.
