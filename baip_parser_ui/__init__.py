"""BAIP Parser web user interface.

"""
import flask
from flask.ext.autoindex import AutoIndex
from flask.ext.silk import Silk

from logga.log import log
import baip_parser
# import baip_parser.exception


app = flask.Flask(__name__)
silk = Silk(app)
app.config.from_object('config')

# Load the Parser config.
#try:
#    conf_file = app.config['MUNGER_CONF_FILE']
#    conf = baip_parser.XpathGen(conf_file=conf_file)
#except baip_parser.exception.MungerConfigError as e:
#    log.error(str(e))

staging_index = AutoIndex(app,
                          browse_root=app.config['STAGING_DIR'],
                          add_url_rules=False)

ready_index = AutoIndex(app,
                        browse_root=app.config['READY_DIR'],
                        add_url_rules=False)

from baip_parser_ui import views
