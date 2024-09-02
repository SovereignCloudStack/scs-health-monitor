#!bash

set -e

trap "exit" SIGINT SIGTERM

SCRIPT_DIR=$(dirname $(readlink -f "$0"))

### Build

podman build -t scshm-runner -f "$SCRIPT_DIR/Containerfile.runner" "$SCRIPT_DIR/"



### Run

cd "$SCRIPT_DIR"

if [[ -z "$KUBECONFIG" ]]; then
    echo "There is no KUBECONFIG env var set, so skipping Kubernetes kubeconfig mount."
    echo "No Kubernetes tests will be able to run, if there's no kubeconfig in the image."
    echo
    KUBECONFIG_MOUNT=""
else
    if [[ ! -f "$KUBECONFIG" ]]; then
        echo "$KUBECONFIG is not a file, aborting"
        exit
    fi

    # Make path absolute
    KUBECONFIG=$(readlink -f "$KUBECONFIG")

    echo "Using $KUBECONFIG as kubeconfig in the container"
    echo
    KUBECONFIG_MOUNT="-v ${KUBECONFIG}:/kubeconfig:ro,Z"
fi

if [[ -z "$CLOUDS_YAML" ]]; then
    echo "CLOUDS_YAML env var is not set, so no OpenStack clouds.yaml is mounted into the container."

    if [[ -f "./clouds.yaml" ]]; then
        echo "There's a clouds.yaml file in the root directory of the project, so this one will be used."
    fi

    echo
    CLOUDSYAML_MOUNT=""
else
    if [[ ! -f "$CLOUDS_YAML" ]]; then
        echo "$CLOUDS_YAML is not a file, aborting"
        exit
    fi

    # Make path absolute
    CLOUDS_YAML=$(readlink -f "$CLOUDS_YAML")

    echo "Using $CLOUDS_YAML as clouds.yaml in the container"
    echo
    CLOUDSYAML_MOUNT="-v ${CLOUDS_YAML}:/data/clouds.yaml:ro,Z"
fi

if [[ -z "$KUBECONFIG_MOUNT" && ( -z "$CLOUDSYAML_MOUNT" && ! -f "clouds.yaml" ) ]]; then
    echo "You have neither a Kubeconfig nor a clouds.yaml for the runner container - no action possible"
    exit
fi

podman run -ti ${KUBECONFIG_MOUNT} ${CLOUDSYAML_MOUNT} -v ${SCRIPT_DIR}:/data/:rw,Z \
  --userns=keep-id:uid=1000,gid=1000 \
  --network=host \
  scshm-runner:latest
