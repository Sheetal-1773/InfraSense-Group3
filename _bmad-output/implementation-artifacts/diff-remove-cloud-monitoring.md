---
status: complete
updated: 2026-08-18
---

# Focused diff — spec-remove-cloud-monitoring.md

Scope: remove cloud (Azure + AWS) monitoring; run local + simulated only.

## Deleted files
- `health-analytics-platform/infrastructure/azure_setup.py` — Azure provisioning script (VMs, VNet, NSG, PostgreSQL, Load Balancer) REMOVED
- `health-analytics-platform/infrastructure/aws_setup.py` — AWS provisioning script (EC2, RDS, ALB/NLB, VPC) REMOVED
- `health-analytics-platform/scripts/verify_azure_e2e.py` — Azure E2E verifier REMOVED

## health-analytics-platform/prometheus.yml

Before:
```yaml
global:
  external_labels:
    cloud_provider: 'azure'
# ... jobs: prometheus, node-exporter, infrasense-backend, postgres-exporter,
#     mysql-exporter, application-metrics,
#     azure-vms (azure_sd_configs + relabel cloud_provider=azure),
#     azure-postgres (azure_sd_configs + relabel cloud_provider=azure),
#     azure-load-balancer (static, cloud_provider=azure),
#     local-mock
```

After:
```yaml
global:
  external_labels:
    cloud_provider: 'local'
# ... jobs: prometheus, node-exporter, infrasense-backend, postgres-exporter,
#     mysql-exporter, application-metrics, local-mock
# azure-vms, azure-postgres, azure-load-balancer jobs DELETED
```

## health-analytics-platform/docker-compose.yml
- `CLOUD_PROVIDER=azure` → `CLOUD_PROVIDER=local` (backend service)

## health-analytics-platform/.env.example
- Azure block REMOVED: `AZURE_SUBSCRIPTION_ID`, `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`, `AZURE_RESOURCE_GROUP`, `AZURE_LOCATION`, `INFRA_VM_COUNT`

## backend/app/services/data_sources/base.py
- `cloud_provider` property: `return "azure"` → `return "local"`

## backend/app/services/data_source_manager.py
- `self.cloud_provider = os.getenv("CLOUD_PROVIDER", "azure")` → `..., "local")`

## backend/app/services/data_sources/prometheus_adapter.py
- `return os.getenv("CLOUD_PROVIDER", "azure")` → `..., "local")`

## backend/app/services/data_sources/otel_adapter.py
- `return os.getenv("CLOUD_PROVIDER", "azure")` → `..., "local")`
- `get_network_metrics` PromQL metric names renamed from `azure_load_balancer_*` to `load_balancer_*` (6 queries): `lb_request_count`, `lb_response_time`, `lb_4xx_count`, `lb_5xx_count`, `lb_healthy_hosts`, `lb_unhealthy_hosts`

## backend/app/routers/components.py
- `os.getenv("CLOUD_PROVIDER", "azure")` → `"local"` (3 sites: discover provider, discover cloud_provider, infrastructure summary cloud_provider)
- `by_provider = {"azure": 0, "local": 0, "simulated": 0, "prometheus": 0}` → `{"local": 0, "simulated": 0, "prometheus": 0}`
- `elif source == "azure": by_provider["azure"] += 1` branch DELETED

## src/pages/Components.tsx
- `SOURCE_MAPPING`: `azure: 'azure'` entry REMOVED
- `type SourceFilter = 'all' | 'local' | 'simulated' | 'azure'` → `'all' | 'local' | 'simulated'`
- Filter dropdown: `<option value="azure">Azure</option>` REMOVED

## src/pages/Dashboard.tsx
- `sourceBreakdown` color mapping: `source === 'azure' ? '#0078D4' :` branch REMOVED