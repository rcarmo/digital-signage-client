import os, sys, platform, logging.config
from utils import get_config, path_for

try:
    settings
except NameError:
    try:
        settings = get_config(path_for(os.path.join('..','etc','config.json')))
    except Exception as e:
        print >> sys.stderr, ("Error while loading configuration file" % locals())
        sys.exit(2)
        logging.config.dictConfig(dict(settings.logging))
        log = logging.getLogger()
        log.info("Logging configured.")
