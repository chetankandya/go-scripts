from kubernetes import client, config

# Get deployment name from command line argument
deployment_name = input("Enter the name of the deployment: ")

# Load kubeconfig file
config.load_kube_config()

# Create a Kubernetes client
api_instance = client.AppsV1Api()

# Get the deployment object
try:
    deployment = api_instance.read_namespaced_deployment(deployment_name, "default")
except client.exceptions.ApiException as e:
    if e.status == 404:
        print(f"Deployment {deployment_name} not found.")
    else:
        print(f"Error occurred: {e}")
    exit()

# Get the pod selector labels from the deployment
selector = deployment.spec.selector.match_labels

# Create a Kubernetes client for getting pod information
api_instance = client.CoreV1Api()

# Get the pods that match the selector
pods = api_instance.list_namespaced_pod("default", label_selector=selector)

# Print the CPU core(s) on which each container is running
for pod in pods.items:
    print(f"Pod {pod.metadata.name}:")
    for container in pod.spec.containers:
        logs = api_instance.read_namespaced_pod_log(pod.metadata.name, "default", container=container.name)
        print(f"Container {container.name} is running on CPU core {logs}")
