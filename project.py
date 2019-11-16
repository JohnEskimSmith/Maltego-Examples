import sys
import transforms

from maltego_trx.registry import register_transform_function, register_transform_classes
from maltego_trx.server import app, application
from maltego_trx.handler import handle_run

# register_transform_function(transform_func)
register_transform_classes(transforms)
log_file = open('log.txt', 'a')
log_file.write('|'.join(sys.argv))
log_file.write('\n')
log_file.close()
handle_run(__name__, sys.argv, app)

