import socket
from maltego_trx.maltego import UIM_TYPES
from maltego_trx.entities import IPAddress
import tasks.Blockchain_Namecoin_find_by_name_MongoDB as module_exec
from maltego_trx.transform import DiscoverableTransform
from tasks.MaltegoLampyre import EnterParamsFake, WriteLog, WriterResult

class EnterParamas_Domain(EnterParamsFake):
    def __init__(self, domains):
        self.domains = domains



class NamecointoIP(DiscoverableTransform):

    @classmethod
    def create_entities(cls, request, response):
        dns_name = request.Value
        try:
            namecoin_domains = [dns_name]
            params = EnterParamas_Domain(namecoin_domains)
            rows = WriterResult()
            module_exec.NamecoinHistoryDomainIPMongoDB().execute(params, rows, WriteLog, None)
            if len(rows.rows) > 0:
                for row in list(filter(lambda x: len(x['ip']) > 0, rows.rows)):
                    ip_address = row['ip']
                    response.addEntity(IPAddress, ip_address)
                    response.entities[-1].setLinkLabel(str(row['date_time']))
            for i in response.entities:
                i.setLinkColor("#4c6cd0")
        except socket.error as e:
            response.addUIMessage("Error: " + str(e), UIM_TYPES["partial"])

