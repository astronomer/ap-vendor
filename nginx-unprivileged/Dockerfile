FROM nginxinc/nginx-unprivileged:1.21.4
USER root

# address CVE-2021-43618
# upstream (as of upstream tag 1.21.4) not yet updating libgmp10
RUN apt-get update && apt-get install libgmp10 -y

USER nginx
