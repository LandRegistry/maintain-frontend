FROM hmlandregistry/dev_base_python_flask:3

RUN yum install -y postgresql-devel && \
    yum install -y geos

ADD package.json /tmp/nodejs/package.json
RUN yum install -y nodejs fontconfig openssl && \
    pip3 install jasmine nodejs && \
    git config --global url."https://github.com/".insteadOf git@github.com: && \
    git config --global url."https://".insteadOf git:// && \
    npm install --prefix /tmp/nodejs

ADD requirements_test.txt requirements_test.txt
ADD requirements.txt requirements.txt
RUN pip3 install -q -r requirements.txt && \
    pip3 install -q -r requirements_test.txt

ENV APP_NAME="maintain-frontend" \
    LOG_LEVEL="DEBUG" \
    COMMIT="LOCAL" \
    PYTHONUNBUFFERED="yes" \
    SEARCH_API_URL="search-api:8080" \
    SEARCH_API_ROOT="http://search-api:8080" \
    LA_API_URL="http://local-authority-api:8080" \
    LA_API_ROOT="http://local-authority-api:8080" \
    SESSION_API_URL="http://llc-session-api:8080/v1.0/sessions" \
    SESSION_API_ROOT="http://llc-session-api:8080" \
    MAINTAIN_API_URL="http://maintain-api:8080/v1.0/maintain" \
    MAINTAIN_API_ROOT="http://maintain-api:8080" \
    STORAGE_API_URL="http://storage-api:8080/v1.0/storage" \
    LLC1_API_URL="http://llc1-document-api:8080/v1.0/generate" \
    LLC1_API_ROOT="http://llc1-document-api:8080" \
    AUDIT_API_URL="http://audit-stub-api:8080/v1" \
    AUDIT_API_ROOT="http://audit-stub-api:8080" \
    STATIC_CONTENT_URL="https://localhost:8080/static" \
    OS_TERMS_CONDITIONS_LINK="https://www.ordnancesurvey.co.uk/about/governance/policies/hm-land-registry-local-land-searches-service.html" \
    GEOSERVER_URL="https://localhost:8080" \
    GEOSERVER_TIMEOUT="3600" \
    MASTERMAP_API_KEY="REDACTED" \
    MAP_BASE_LAYER_VIEW_NAME="hybrid_bng" \
    SECRET_KEY=thisisasecretkey \
    MAX_HEALTH_CASCADE=6 \
    DEFAULT_PAGE_SIZE=10 \
    WFS_SERVER_URL="https://wfs.viaeuropa.uk.com" \
    WMTS_SERVER_URL="https://atlas1.viaeuropa.uk.com/viaeuropa" \
    EXPIRED_REPORT_KEY="thisisareportkey" \
    EXPIRED_REPORT_BUCKET="llc-expired-reports" \
    SOURCE_INFORMATION_LIMIT=8 \
    FEEDBACK_URL="https://www.google.com" \
    CONTACT_US_URL="https://help.landregistry.gov.uk/app/contactus_LLC" \
    REPORT_API_BASE_URL="http://report-api:8080" \
    NOTIFICATION_API_URL=http://notification-api:8080 \
    NOTIFY_TWO_FACTOR_AUTH_TEMPLATE_ID=atemplateid \
    ENABLE_TWO_FACTOR_AUTHENTICATION="False" \
    NOTIFY_PAYMENT_LINK_TEMPLATE_ID=atemplateid \
    NODE_PATH=/tmp/nodejs/node_modules \
    PATH=$PATH:/tmp/nodejs/node_modules/.bin \
    SEARCH_LOCAL_LAND_CHARGE_API_URL="http://search-local-land-charge-api:8080"
