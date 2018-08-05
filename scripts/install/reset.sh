kubectl delete deploy --all --namespace default -l app!=qa
kubectl delete configmap --all --namespace default
kubectl delete secret --all --namespace default
kubectl delete service --all --namespace default -l name!=qa
kubectl delete statefulset --all --namespace default
