package main

import (
    "context"
    "flag"
    "fmt"
    "os"
    "path/filepath"

 

    "k8s.io/apimachinery/pkg/api/errors"
    "k8s.io/apimachinery/pkg/apis/meta/v1"
    "k8s.io/apimachinery/pkg/fields"
    "k8s.io/client-go/kubernetes"
    "k8s.io/client-go/tools/clientcmd"
)

 

func main() {
    // Get deployment name from command line argument
    deploymentName := flag.String("deployment", "", "Name of the deployment")
    flag.Parse()

 

    // Check if deployment name was provided
    if *deploymentName == "" {
        fmt.Println("Please provide a deployment name using the -deployment flag")
        os.Exit(1)
    }

 

    // Get path to kubeconfig file
    kubeconfig := filepath.Join(os.Getenv("HOME"), ".kube", "config")

 

    // Create a Kubernetes client using the kubeconfig file
    config, err := clientcmd.BuildConfigFromFlags("", kubeconfig)
    if err != nil {
        panic(err)
    }
    clientset, err := kubernetes.NewForConfig(config)
    if err != nil {
        panic(err)
    }

 

    // Get the deployment object
    deployment, err := clientset.AppsV1().Deployments("default").Get(context.TODO(), *deploymentName, v1.GetOptions{})
    if err != nil {
        if errors.IsNotFound(err) {
            fmt.Printf("Deployment %s not found\n", *deploymentName)
        } else {
            panic(err)
        }
    } else {
        // Get the pod selector labels from the deployment
        selector := deployment.Spec.Selector.MatchLabels

 

        // Get the pods that match the selector
        podList, err := clientset.CoreV1().Pods("default").List(context.TODO(), v1.ListOptions{
            LabelSelector: fields.SelectorFromSet(selector).String(),
        })
        if err != nil {
            panic(err)
        }

 

        // Print the CPU core(s) on which each container is running
        for _, pod := range podList.Items {
            fmt.Printf("Pod %s:\n", pod.ObjectMeta.Name)
            for _, container := range pod.Spec.Containers {
                podStats, err := clientset.CoreV1().Pods(pod.ObjectMeta.Namespace).GetLogs(pod.ObjectMeta.Name, &v1.PodLogOptions{
                    Container: container.Name,
                }).Stream(context.Background())
                if err != nil {
                    panic(err)
                }
                buf := make([]byte, 2048)
                _, err = podStats.Read(buf)
                if err != nil {
                    panic(err)
                }
                fmt.Printf("Container %s is running on CPU core %s\n", container.Name, string(buf))
            }
        }
    }
}
