<!--
Thank you for contributing to astronomer/ap-vendor!

When you push to any branch, CI will run:
- build all images
- security scan all images

When your change is merged to master:
- build all images
- security scan all images
- any images where the version is not published to Dockerhub, then publish
-->

**Which issue this PR fixes**:

<!-- if applicable, otherwise just delete the header -->

**Summary of changes**:

<!-- required -->

**Which images are updated by this PR?**:

<!-- required -->

- [ ] alertmanager
- [ ] curator
- [ ] elasticsearch-exporter
- [ ] grafana
- [ ] kube-state
- [ ] nginx
- [ ] pgbouncer
- [ ] prisma
- [ ] redis
- [ ] statsd-exporter
- [ ] elasticsearch
- [ ] fluentd
- [ ] kibana
- [ ] kubed
- [ ] nginx-es
- [ ] pgbouncer-exporter
- [ ] prometheus
- [ ] registry

**Checklist** (required)

Place an '[x]' (no spaces) in all applicable fields. Please remove unrelated fields.

- [ ] version.txt is updated in the changed image(s)

If a security scan fails for an unchanged image...

- [ ]  a fix has been applied OR...
- [ ]  an [issue](<!-- link to the issue -->) has been created

<!--
Please give it a shot to fix any security issue, even if unrelated to your change.
-->

If adding a new image:

- [ ] the directory has the same name you intend it to be published as, less a preceding "ap-"
- [ ] the directory includes a file "version.txt", with content 0.0.0
- [ ] the directory includes a file "cve-whitelist.yaml", which may be empty
- [ ] the file .github/PULL_REQUEST_TEMPLATE.md is updated to include the image in the checklist
- [ ] execute the script .circleci/generate_circleci_config.py, commit changes to .circleci/config.yml

**Additional notes for your reviewer**:
