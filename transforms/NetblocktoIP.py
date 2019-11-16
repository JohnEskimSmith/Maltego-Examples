from maltego_trx.maltego import UIM_TYPES
from maltego_trx.entities import IPAddress
from tasks.MaltegoLampyre import EnterParamsFake, WriteLog, WriterResult
import tasks.Blockchain_Namecoin_find_by_netmask_MongoDB as module_exec
from maltego_trx.transform import DiscoverableTransform


class EnterParamas_Netblock(EnterParamsFake):
    def __init__(self, netblock):
        self.netblock = netblock


class NetblocktoIP(DiscoverableTransform):

    @classmethod
    def create_entities(cls, request, response):
        netblock = request.Value
        try:
            netblock = [netblock]
            params = EnterParamas_Netblock(netblock)
            rows = WriterResult()
            module_exec.NamecoinHistoryNetblockMongoDB().execute(params, rows, WriteLog, None)
            if len(rows.rows) > 0:
                for row in list(filter(lambda x: len(x['ip']) > 0, rows.rows)):
                    ip_result = row['ip']
                    response.addEntity(IPAddress, ip_result)
                    label = f"{row['date_time']}, {row['domain']}"
                    response.entities[-1].setLinkLabel(label)
            for i in response.entities:
                i.setLinkColor("#4c6cd0")
        except Exception as e:
            response.addUIMessage("Error: " + str(e), UIM_TYPES["partial"])

        # Write the slider value as a UI message - just for fun
        response.addUIMessage("Slider value is at: " + str(request.Slider))
