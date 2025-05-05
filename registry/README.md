## Docker Registry

This is our build of the docker registry (github.com/docker/distribution)

### Version

This version mechanism was changed from following the ap-vendor version to following the upstream build version on 2025-04-09, shortly after registry 3.0.0 was released. This caused a backwards bump from 3.21 (the version of alpine that was used in ap-base) to 3.0.0 (the version of docker/distribution). Be aware of this if you are sorting versions of this component, because higher semver versions do not necessarily mean newer builds of the component. More details can be found here: <https://github.com/astronomer/ap-vendor/pull/943>
