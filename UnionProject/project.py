import sys
import transforms

from maltego_trx.registry import register_transform_function, register_transform_classes
from maltego_trx.server import app, application
from maltego_trx.handler import handle_run
from tasks.namecoin_entities import keys_for_parse_enterparams

def restore_only_need_enteparams(arguments):
    sys_argv_replaced = arguments[:4]
    _tmp = arguments[4:]
    part_params = ''.join(_tmp)
    attrs_for_param = keys_for_parse_enterparams[sys.argv[2]]
    for k, v in attrs_for_param.items():
        if k in part_params:
            try:
                sub_data = part_params.split('#')[v]
                sys_argv_replaced.append(sub_data)
            except:
                pass
    if len(sys_argv_replaced) >= 5:
        return sys_argv_replaced

# register_transform_function(transform_func)
register_transform_classes(transforms)

# reparse sys.argv
sys_argv_replaced = restore_only_need_enteparams(sys.argv)

# try to send replaces args to Maltego parser
if sys_argv_replaced:
    handle_run(__name__, sys_argv_replaced, app)

