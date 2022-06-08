# Astronomer Vendor Images

The Astronomer ap-vendor repo is a collection of third party components that we vendor and provide through our own supply chain. This gives us more control over when updates are released, and how the software is distributed to our customers.

## Directory layout

Most directories in this repository hold everything needed to build and test one component. Three of the most common files you can find are Dockerfile, version.txt, test.yaml, and trivyignore.

`Dockerfile` is pretty well known. The way the the docker images are named is by prefixing the docker repo and `ap-` (for Astronomer Platform) to the name of the directory. For instance, the directory `grafana` would become `quay.io/astronomer/ap-grafana`.

`version.txt` gives the docker tag for the component. We use [semver](https://semver.org) for all of our tags. Using this file for versions gives us more control over what we want to use as the version. For instance, if we are building software from source inside of a debian container, and that debian container is updated to fix a security vulnerability but the component version does not change, we could potentially run into a tag conflict. Instead, we can increase the prerelease section of the tag to increase the semver compatible version number while still indicating the upstream number.

`test.yaml` allows you to configure the [ap-vendor test suite](https://github.com/astronomer/ap-vendor/blob/bd74b1425f/bin/test.py) to test certain aspects of the image, for instance to verify that the image build defaults to using a certain non-root user with a given uid.

`trivyignore` allows us to ignore CVEs during trivy security scan. This is used sparingly, and ideally should not be used, but sometimes it is necessary to release versions when a CVE exists, or when a CVE does not apply to our environment at all but is present in the base image.

`.circleci` is the standard CircleCI configuration directory. The config file is automatically generated through a python script and jinja2 template. As long as all the image directories follow the conventions outlined above, the config will be generated correctly.

## License

Apache 2.0 with Commons Clause
