FROM quay.io/keycloak/keycloak:25.0.1

# Setting the build parameter for the database:
ENV KC_DB=postgres

# Add all other build parameters needed, for example enable health and metrics:
ENV KC_HEALTH_ENABLED=true
ENV KC_METRICS_ENABLED=true
# https://www.keycloak.org/server/logging
ENV KC_LOG_LEVEL=INFO
# or DEBUG

# https://stackoverflow.com/questions/75323566/how-to-enable-features-like-token-exchange-in-keycloak-from-command-line
ENV JAVA_TOOL_OPTIONS="-Dkeycloak.profile.feature.admin_fine_grained_authz=enabled -Dkeycloak.profile.feature.token_exchange=enabled"

# To be able to use the image with the Keycloak Operator, it needs to be optimized, which requires Keycloak's build step:
# RUN /opt/keycloak/bin/kc.sh build

ENTRYPOINT [ "/opt/keycloak/bin/kc.sh", "start-dev", "--verbose" ]