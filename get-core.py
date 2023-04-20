from kubernetes import client, config
import os

def get_cpu_cores(deployment_name):
    # Load Kubernetes configuration from default location
    config.load_kube_config()

    # Create a Kubernetes API client
    api_instance = client.AppsV1Api()

    # Get the deployment object
    try:
        deployment = api_instance.read_namespaced_deployment(deployment_name, "default")
    except client.rest.ApiException as e:
        print("Error getting deployment: %s\n" % e)
        return

    # Get the pod selector labels from the deployment
    selector = deployment.spec.selector.match_labels

    # Create a Kubernetes API client for pods
    api_instance = client.CoreV1Api()

    # Get the pods that match the selector
    try:
        pods = api_instance.list_namespaced_pod("default", label_selector=selector)
    except client.rest.ApiException as e:
        print("Error getting pods: %s\n" % e)
        return

    # Print the CPU core(s) on which each container is running
    for pod in pods.items:
        print("Pod %s:" % pod.metadata.name)
        for container in pod.spec.containers:
            container_name = container.name
            try:
                # Get the logs for the container
                pod_logs = api_instance.read_namespaced_pod_log(name=pod.metadata.name,
                                                                namespace="default",
                                                                container=container_name)
                # Extract the CPU core number from the logs
                cpu_core = pod_logs.split()[-1].decode()
                print("Container %s is running on CPU core %s" % (container_name, cpu_core))
            except client.rest.ApiException as e:
                print("Error getting logs for container %s in pod %s: %s" % (container_name, pod.metadata.name, e))

# Example usage: Get the CPU cores for a deployment named "my-deployment"
get_cpu_cores("my-deployment")
