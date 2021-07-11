# argocd-aws-secret-plugin
An Argo CD plugin to retrieve secrets from AWS Secrets Manager and inject them into Kubernetes secrets.

The plugin replaces Kubernetes manifest values within angle brackets e.g. `<PLACEHOLDER>` with AWS Secrets, were `PLACEHOLDER` is an AWS SecretId.

### Prerequisites

A Kubernetes Cluster with Argo CD setup.

### Installation

1. Copy plugin binary into a volume mount via init-container then attach volume to `argocd-repo-server` container:

``` argocd-repo-server
containers:
- name: argocd-repo-server
  volumeMounts:
  - name: custom-tools
    mountPath: /usr/local/bin/aws-secret-plugin
    subPath: aws-secret-plugin
volumes:
- name: custom-tools
  emptyDir: {}
initContainers:
- name: download-tools
  image: alpine:3.8
  command: [sh, -c]
  args:
    - >-
      wget -O aws-secret-plugin
      https://github.com/mziyabo/argocd-aws-secret-plugin/releases/download/<RELEASE NAME>/aws-secret-plugin &&
      chmod +x aws-secret-plugin &&
      mv aws-secret-plugin /custom-tools/
  volumeMounts:
    - mountPath: /custom-tools
      name: custom-tools
```

2. Register plugin in Argo CD

Edit `configManagementPlugins` in argocd-cm configmap:

**Configuration with directory:**
This plugin configuration applies for running the plugin against a Kubernetes template directory 

``` argocd-cm
data:
  configManagementPlugins: |-
    - name: aws-secret-plugin
      generate:
        command: ["aws-secret-plugin"]
        args: ["generate", "./"]
```

**Configuration for Helm use:**

``` argocd-cm
configManagementPlugins: |
  - name: aws-secret-plugin-helm
    init:
      command: [sh, -c]
      args: ["helm dependency build"]
    generate:
      command: ["sh", "-c"]
      args: ["helm template . > all.yaml && aws-secret-plugin generate all.yaml"]

```

3. Create IAM Service Account for argocd-repo-server pod:

Attach a Service Account to the `argocd-repo-server` using IAM roles for service accounts to grant **AWS Secrets Manager** permissions [1].

[1] [IAM Roles for Service Accounts](https://docs.aws.amazon.com/eks/latest/userguide/iam-roles-for-service-accounts.html)

### Usage

Before using the plugin in Argo CD follow the setup instructions above. Once the plugin is installed, you can use it 3 ways.

1. From the ArgoCD UI, Select your plugin by selecting New App and then changing **Directory** at the bottom of the form to be `aws-secret-plugin`. In the **ENV** section, add the region from which the secrets are retrieved using the `AWS_DEFAULT_REGION` variable.

2. Apply an Argo CD Application yaml that has `aws-secret-plugin` as the plugin.

```
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: your-application-name
spec:
  destination:
    name: ''
    namespace: default
    server: 'https://kubernetes.default.svc'
  source:
    path: .
    plugin:
      name: argocd-aws-secret-plugin
      env:
        - name: AWS_DEFAULT_REGION
          value: eu-west-1
    repoURL: http://your-repo/
    targetRevision: HEAD
  project: default
```

> Note: The AWS Region environment variable, `AWS_DEFAULT_REGION`, is required to fetch secrets from AWS Secrets Manager.

3. Alternatively you can pass the config-management-plugin flag to the Argo CD CLI app create command:
    `argocd app create you-app-name --config-management-plugin argocd-aws-secret-plugin`

### Release Notes
🚧 Working but Contributions Welcome

### RoadMap
- Support annotations to conditionally ignore processing manifests

### Credits
Similar Project: [IBM Argo CD Vault Plugin](https://github.com/IBM/argocd-vault-plugin)

### License
Apache-2.0
