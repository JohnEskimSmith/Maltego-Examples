from maltego_trx.maltego import UIM_TYPES
from maltego_trx.entities import IPAddress
from tasks.namecoin_entities import NamecoinDNS
from tasks.MaltegoLampyre import EnterParamsFake, WriteLog, WriterResult
import tasks.Blockchain_Namecoin_find_by_netmask_MongoDB as module_exec
from maltego_trx.transform import DiscoverableTransform


class EnterParamas_Netblock(EnterParamsFake):
    def __init__(self, blocks):
        self.blocks = blocks


class NetblocktoIP(DiscoverableTransform):

    @classmethod
    def create_entities(cls, request, response):

        netblock_record = [request.Value]
        try:
            params = EnterParamas_Netblock(netblock_record)
            rows = WriterResult()
            module_exec.NamecoinHistoryNetblockMongoDB().execute(params, rows, WriteLog, None)

            if len(rows.rows) > 0:
                for row in list(filter(lambda x: len(x['ip']) > 0, rows.rows)):
                    ip_result = row['ip']
                    response.addEntity(IPAddress, ip_result)
                    label = f"{row['date_time']}, {row['domain']}"
                    response.entities[-1].setLinkLabel(label)
                    response.addEntity(NamecoinDNS, row['domain'])
                    response.entities[-1].setLinkLabel(row['ip'])
            for i in response.entities:
                i.setLinkColor("#4c6cd0")
        except Exception as e:
            response.addUIMessage("Error: " + str(e), UIM_TYPES["partial"])

