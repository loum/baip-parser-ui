CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'

ALLOWED_EXTENSIONS = set(['xls', 'xlsx'])

# Munger staging directory on the server.
STAGING_DIR = '/var/tmp/baip-parser/staging'

# Munger ready directory on the server.
READY_DIR = '/var/tmp/baip-parser/ready'

# Define the location of the Munger configuration file.
PARSER_CONF_FILE = 'baip_parser_ui/tests/files/parser.conf'
