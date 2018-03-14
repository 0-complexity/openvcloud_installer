# Grafana application

## Generate dashboards

If you want to edit dashboards, you need to regenerate them from template.

We provide default templates, you can probably skip this step.


## Install configuration

- Add ConfigMap datasource and dashboards:
```bash
kubectl create configmap grafana-provisioning-datasources --from-file=provisioning/datasources
kubectl create configmap grafana-provisioning-dashboards --from-file=provisioning/dashboards
kubectl create configmap grafana-dashboards --from-file=sources/templates
```

## Deployment

- Run `kubectl create -f grafana-service.yaml`
- Run `kubectl create -f grafana-deployment.yaml`

