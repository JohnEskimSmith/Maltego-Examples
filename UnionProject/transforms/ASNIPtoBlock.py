from maltego_trx.maltego import UIM_TYPES
from maltego_trx.entities import Netblock, ASNumber, DNS
from tasks.additions_entities import Company
from tasks.MaltegoLampyre import EnterParamsFake, WriteLog, WriterResult
import tasks.asn_by_ip as module_exec
from maltego_trx.transform import DiscoverableTransform

import ipaddress

def get_network(cidr: str):
    try:
        return ipaddress.IPv4Network(cidr)
    except ipaddress.AddressValueError:
        try:
            return ipaddress.IPv6Network(cidr)
        except ipaddress.AddressValueError:
            return None
    except:
        return None

class EnterParamas_Netblock(EnterParamsFake):
    def __init__(self, ips):
        self.ips = ips


class ASNIPtoBlock(DiscoverableTransform):

    @classmethod
    def create_entities(cls, request, response):
        asnnumber = None
        netblock_record = [request.Value]
        try:
            params = EnterParamas_Netblock(netblock_record)
            rows = WriterResult()
            module_exec.IPandASNmapping().execute(params, rows, WriteLog, None)

            if len(rows.rows) > 0:
                for row in list(filter(lambda x: len(x['Announced_Prefix']) > 0, rows.rows)):
                    _block_result = get_network(row['Announced_Prefix'])
                    if _block_result:
                        ip1, ip2 = _block_result[0], _block_result[-1]
                        _record_str = f"{ip1}-{ip2}"
                        response.addEntity(Netblock, _record_str)
                        label = f"Country: {row['Country']}"
                        response.entities[-1].setLinkLabel(label)

                    if len(row['ASN']) > 2:
                        asnnumber = row['ASN'][2:]
                        response.addEntity(ASNumber, asnnumber)
                        label = f"Country: {row['Country']}"
                        response.entities[-1].setLinkLabel(label)

                    if len(row['ASN_Name']) > 0:

                        if row['Country'].strip() !=  row['ASN_Name']:
                            response.addEntity(Company, row['ASN_Name'])
                            label = f"Country: {row['Country']}"
                            response.entities[-1].setLinkLabel(label)

                    if len(row['Prefix_Description']) > 0:
                        response.addEntity(Company, row['Prefix_Description'])
                        label = f"Country: {row['Country']}"
                        response.entities[-1].setLinkLabel(label)

                    if len(row['rDNS']) > 0:
                        if '.' in row['rDNS']:

                            response.addEntity(DNS, row['rDNS'])
                            if asnnumber:
                                label = f"AS: {asnnumber}"
                                response.entities[-1].setLinkLabel(label)

            for i in response.entities:
                i.setLinkColor("#660066")
        except Exception as e:
            response.addUIMessage("Error: " + str(e), UIM_TYPES["partial"])

