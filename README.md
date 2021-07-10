# argocd-aws-secret-plugin
An Argo CD plugin to retrieve secrets from AWS Secrets Manager and inject them into Kubernetes secrets

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
      https://github.com/mziyabo/argocd-aws-secret-plugin/releases/download/v1.0.0-alpha/aws-secret-plugin &&
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

Attach a Service Account to the `argocd-repo-server` using IAM roles for service accounts to grant **AWS Secrets Manager** permissions.

Follow [1] to achieve the above:

[1] https://docs.aws.amazon.com/eks/latest/userguide/iam-roles-for-service-accounts.html: IAM roles for service accounts


### Usage

Before using the plugin in Argo CD you must follow the steps to install the plugin to your Argo CD instance. Once the plugin is installed, you can use it 3 ways.

1. Select your plugin via the UI by selecting New App and then changing Directory at the bottom of the form to be aws-secret-plugin.

2. Apply a Argo CD Application yaml that has aws-secret-plugin as the plugin.

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
    repoURL: http://your-repo/
    targetRevision: HEAD
  project: default
```

3. Alternatively you can pass the config-management-plugin flag to the Argo CD CLI app create command:
    `argocd app create you-app-name --config-management-plugin argocd-aws-secret-plugin`

### Release Notes:
🚧 wip

### License:
Apache-2.0