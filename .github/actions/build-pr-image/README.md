## Build PR Image Action

This Action provides automation for a Docker builder for a PR. An image is then pushed to a given registry.

## Parameters

### Inputs

 * `REGISTRY`: The image registry where the action is pulling from. Images can be found in https://hub.docker.com/?namespace=vaporio
 * `BUILDERIMAGE`: A base image containing the build tool chain
 * `SLIMIMAGE`: A smaller image for deploys
 * `DOCKERFILE`: Name of the Dockerfile. Usually just `Dockerfile`
 * `USERNAME`: Login user for the image registry
 * `PASSWORD`: Password for image registry
 * `IMAGENAME`: Name of the image to push into the registry

### Usage

Since this Action is located in a private repo, a step will checkout this repo with a token so then it can be used
in the next step.

```
# .github/workflows/deploy.yml
name: build
on: ['build']

jobs:
  image_build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          repository: vapor-ware/workflows
          token: ${{ secrets.VIO_REPO_READ }}
          ref: main
          path: vapor-ware-workflows # Checkouts directory path name for the next step

      - uses: ./vapor-ware-workflows/.github/actions/build-pr-image
        with:
          REGISTRY: docker.io
          BUILDERIMAGE: ubuntu:22.04
          SLIMIMAGE: ubuntu:22.04
          DOCKERFILE: Dockerfile
          USERNAME: ${{ secrets.DOCKERHUB_USERNAME }}
          PASSWORD: ${{ secrets.DOCKERHUB_TOKEN }}
          IMAGENAME: my_image
```
