# This file is the entry point.
# First we import the app object, which will get initialised as we do it. Then import methods we're about to use.
from maintain_frontend.app import app
from maintain_frontend.extensions import register_extensions
from maintain_frontend.blueprints import register_blueprints
from maintain_frontend.exceptions import register_exception_handlers
from maintain_frontend.filters import register_filters

# Now we register any extensions we use into the app
register_extensions(app)
# Register the exception handlers
register_exception_handlers(app)
# Register filters for use in Jinja templates
register_filters(app)
# Finally we register our blueprints to get our routes up and running.
register_blueprints(app)
