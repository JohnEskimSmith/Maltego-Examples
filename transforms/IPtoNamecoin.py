from maltego_trx.maltego import UIM_TYPES
from tasks.namecoin_entities import NamecoinDNS
from tasks.MaltegoLampyre import EnterParamsFake, WriteLog, WriterResult
import tasks.Blockchain_Namecoin_find_by_ip_MongoDB as module_exec
from maltego_trx.transform import DiscoverableTransform


class EnterParamas_IP(EnterParamsFake):
    def __init__(self, ips):
        self.ips = ips



class IPtoNamecoin(DiscoverableTransform):

    @classmethod
    def create_entities(cls, request, response):
        ip_input = request.Value
        try:
            ips = [ip_input]
            params = EnterParamas_IP(ips)
            rows = WriterResult()
            module_exec.NamecoinHistoryIPDomainMongoDB().execute(params, rows, WriteLog, None)
            if len(rows.rows) > 0:
                for row in list(filter(lambda x: len(x['domain']) > 0, rows.rows)):
                    domain_result = row['domain']
                    response.addEntity(NamecoinDNS, domain_result)
                    response.entities[-1].setLinkLabel(str(row['date_time']))
            for i in response.entities:
                i.setLinkColor("#4c6cd0")
        except Exception as e:
            response.addUIMessage("Error: " + str(e), UIM_TYPES["partial"])

        # Write the slider value as a UI message - just for fun
        response.addUIMessage("Slider value is at: " + str(request.Slider))
