# Used only for kubernetes initContainer tasks

# Inherit dockerize and RDS certificates from ap-base
FROM quay.io/astronomer/ap-base:3.18.6-2

RUN apk add --no-cache curl  shadow

# update astro user and group
RUN usermod -u 101 astro && groupmod -g 101 astro

# Must always run as non-root
# 101 is astro user, SecurityContextConstraint requires numeric uids
USER 101
