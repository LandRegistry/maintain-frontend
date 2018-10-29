import os
# RULES OF CONFIG:
# 1. No region specific code. Regions are defined by setting the OS environment variables appropriately to build up the
# desired behaviour.
# 2. No use of defaults when getting OS environment variables. They must all be set to the required values prior to the
# app starting.
# 3. This is the only file in the app where os.environ should be used.

# For logging
LOG_LEVEL = os.environ['LOG_LEVEL']
AUDIT_API_URL = os.environ['AUDIT_API_URL']

# For health route
COMMIT = os.environ['COMMIT']

# Search API URL
SEARCH_API_URL = os.environ['SEARCH_API_URL']

# Session API URL
SESSION_API_URL = os.environ['SESSION_API_URL']

# Geoserver URL
GEOSERVER_URL = os.environ['GEOSERVER_URL']

# Static Content
STATIC_CONTENT_URL = os.environ['STATIC_CONTENT_URL']

# Feedback url
FEEDBACK_URL = os.environ['FEEDBACK_URL']

# Contact Us url
CONTACT_US_URL = os.environ['CONTACT_US_URL']

# OS Terms and Conditions Link (displayed on copyright message on map pages)
OS_TERMS_CONDITIONS_LINK = os.environ['OS_TERMS_CONDITIONS_LINK']

# Create cookies with secure flag
SESSION_COOKIE_SECURE = True

# Base layer API key and view name
MASTERMAP_API_KEY = os.environ['MASTERMAP_API_KEY']
MAP_BASE_LAYER_VIEW_NAME = os.environ['MAP_BASE_LAYER_VIEW_NAME']

# Maintain API URL
MAINTAIN_API_URL = os.environ['MAINTAIN_API_URL']

# Storage API
STORAGE_API_URL = os.environ['STORAGE_API_URL']

# LLC1 API 'generate' endpoint
LLC1_API_URL = os.environ['LLC1_API_URL']

# Local Authority API URL
LA_API_URL = os.environ['LA_API_URL']

# Report API
REPORT_API_BASE_URL = os.environ['REPORT_API_BASE_URL']

# This APP_NAME variable is to allow changing the app name when the app is running in a cluster. So that
# each app in the cluster will have a unique name.
APP_NAME = os.environ['APP_NAME']

# SECRET_KEY used for CSRF protection
SECRET_KEY = os.environ['SECRET_KEY']

NOTIFICATION_API_URL = os.environ['NOTIFICATION_API_URL']

NOTIFY_TWO_FACTOR_AUTH_TEMPLATE_ID = os.environ['NOTIFY_TWO_FACTOR_AUTH_TEMPLATE_ID']
NOTIFY_PAYMENT_LINK_TEMPLATE_ID = os.environ['NOTIFY_PAYMENT_LINK_TEMPLATE_ID']

# SEARCH_LOCAL_LAND_CHARGE_API_URL for search service viewing
SEARCH_LOCAL_LAND_CHARGE_API_URL = os.environ['SEARCH_LOCAL_LAND_CHARGE_API_URL']

# MAX_HEALTH_CASCADE used for cascading health checks
MAX_HEALTH_CASCADE = os.environ['MAX_HEALTH_CASCADE']
DEPENDENCIES = {"Search API": os.environ['SEARCH_API_ROOT'],
                "Local Authority API": os.environ['LA_API_ROOT'],
                "Session API": os.environ['SESSION_API_ROOT'],
                "Maintain API": os.environ['MAINTAIN_API_ROOT'],
                "LLC1 API": os.environ['LLC1_API_ROOT'],
                "Audit API": os.environ['AUDIT_API_ROOT'],
                "Report API": os.environ['REPORT_API_BASE_URL'],
                "LLCS Search API": os.environ['SEARCH_LOCAL_LAND_CHARGE_API_URL']}

# Default page size for pagination
DEFAULT_PAGE_SIZE = os.environ['DEFAULT_PAGE_SIZE']

# Timeout for geoserver tokens
GEOSERVER_TIMEOUT = int(os.environ['GEOSERVER_TIMEOUT'])

WFS_SERVER_URL = os.environ['WFS_SERVER_URL']
WMTS_SERVER_URL = os.environ['WMTS_SERVER_URL']

EXPIRED_REPORT_KEY = os.environ['EXPIRED_REPORT_KEY']
EXPIRED_REPORT_BUCKET = os.environ['EXPIRED_REPORT_BUCKET']

# Source Information Limit for LA Admins
SOURCE_INFORMATION_LIMIT = os.environ['SOURCE_INFORMATION_LIMIT']

# Schema version to use when forming charge
SCHEMA_VERSION = "7.0"

ENABLE_TWO_FACTOR_AUTHENTICATION = os.environ['ENABLE_TWO_FACTOR_AUTHENTICATION'] == 'True'

LOGCONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            '()': 'maintain_frontend.extensions.JsonFormatter'
        },
        'audit': {
            '()': 'maintain_frontend.extensions.JsonAuditFormatter'
        }
    },
    'filters': {
        'contextual': {
            '()': 'maintain_frontend.extensions.ContextualFilter'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'filters': ['contextual'],
            'stream': 'ext://sys.stdout'
        },
        'audit_console': {
            'class': 'logging.StreamHandler',
            'formatter': 'audit',
            'filters': ['contextual'],
            'stream': 'ext://sys.stdout'
        }
    },
    'loggers': {
        'maintain_frontend': {
            'handlers': ['console'],
            'level': LOG_LEVEL
        },
        'audit': {
            'handlers': ['audit_console'],
            'level': 'INFO'
        }
    }
}
