# -*- coding: utf8 -*-
__author__ = 'sai'

import ipaddress
import time
from pymongo import MongoClient
import itertools


# region Import System Ontology
try:
    from tasks.ontology import (
        Object, Task, Link, Attribute, Header, HeaderCollection, Utils, Field, ValueType, SchemaLink, SchemaObject, Condition, Operations, Macro,
        MacroCollection, Schema, EnterParamCollection, SchemaCollection, GraphMappingFlags, BinaryType, Constants,
        Attributes, IP, Domain, IPToDomain, Netblock, IPToNetblock)

except ImportError as ontology_exception:
    print('...missing or invalid ontology')
    raise ontology_exception
# endregion


# region load Namecoin Ontology
try:
    from tasks.NamecoinOntology import (NamecoinTXnExplorer_in, NamecoinTXid, NamecoinTXidToNamecoinTXid,
                                  NamecoinTXnExplorer_out, NamecoinAddress, NamecoinTXidToAddress,
                                  NamecoinAddressToIP, NamecoinAddressToDomain,
                                  NamecoinDomainExplorer, NamecoinTXidToDomain,
                                  NamecoinTXidToIP)
except ImportError as ontology_exception:
    print('...missing or invalid ontology')
    raise ontology_exception
# endregion


def valid_ip(address):
    """
    Checks if string is a valid ip-address

    :param str address:
    :rtype: bool
    """
    try:
        ipaddress.ip_address(address)
        return True
    except:
        return False


def ip_to_range(record_range: str):
    _ip1, _ip2 = record_range.split('-')
    ip1 = _ip1.strip()
    ip2 = _ip2.strip()
    if valid_ip(ip1) and valid_ip(ip2):
        try:
            if ipaddress.ip_address(ip1) < ipaddress.ip_address(ip2):
                int_ip1 = int(ipaddress.ip_address(ip1))
                int_ip2 = int(ipaddress.ip_address(ip2))
                return [str(ipaddress.ip_address(i)) for i in range(int_ip1, int_ip2+1)]
        except:
            pass


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


def check_range_record(record_range: str):
    check_list = []
    count_true = 4
    if "-" in record_range:
        check_list.append(True)
        try:
            part1, part2 = record_range.split('-')
            check_list.append(True)
            if valid_ip(part1) and valid_ip(part2):
                check_list.append(True)
                if ipaddress.ip_address(part1) < ipaddress.ip_address(part2):
                    check_list.append(True)
        except:
            check_list.append(False)

    return len(check_list) == count_true and all(check_list)



def init_connect_to_mongodb(ip, port, dbname, username=None, password=None):
    """
    :param ip:  ip server MongoDB
    :param port: 27017
    :return: True, if connected, and set value mongoclient - MongoClient
    """
    if username and password:
        connect_string_to = 'mongodb://{}:{}@{}:{}/{}'.format(username, password, ip, port, dbname)
    else:
        connect_string_to = 'mongodb://{}:{}/{}'.format(ip, port, dbname)

    check = False
    count_repeat = 4
    sleep_sec = 1
    check_i = 0

    while not check and check_i < count_repeat:
        try:
            client = MongoClient(connect_string_to, serverSelectionTimeoutMS=60)
            client.server_info()
            check = True
        except Exception as ex:
            print(f"try {check_i}, error:'{str(ex)}', connecting - error, sleep - 1 sec.")
            time.sleep(sleep_sec)
            check_i += 1
        else:
            return client


def not_empty(field: Field):
    return Condition(field, Operations.NotEqual, '')


def return_massive_about_ips(ips, server, user, password, cidr):

    def prepare_row(line):
        _name = return_namecoin(line['clean_name'])
        if _name:
            _result = dict()

            _result['date_time'] = line['clean_datetime_block']
            _result['domain'] = _name['domain']
            _result['namecoin_domain'] = line['clean_name']

            _result['height'] = line['height_block']
            _result['hash_block'] = line['blockhash']
            _result['txid'] = line['txid']
            _result['short_txid'] = line['txid'][:8]

            try:
                _result['operation'] = line['clean_op']
            except:
                pass
            if 'ips' in line:
                for ip in line['ips']:
                    _result_row = _result.copy()
                    _result_row['ip'] = ip.strip()
                    _result_row['Netblock'] = cidr
                    yield _result_row
            else:
                yield _result

    def return_info(search_dict, need_fields):
        rows = db[collection_name_tx].find(search_dict, need_fields)
        massive_all = [row for row in rows]

        _need_block_fields = {'_id': 1, 'height': 1}
        hashs_block = list(set([row['blockhash'] for row in massive_all]))
        _search_filter = {"_id": {"$in": hashs_block}}
        _tmp = db[collection_name_blocks].find(_search_filter, _need_block_fields)
        _cache = {}
        for row in _tmp:
            if row['_id'] not in _cache:
                _cache[row['_id']] = row['height']

        for row in massive_all:
            if row['blockhash'] in _cache:
                row['height_block'] = _cache[row['blockhash']]
            rows_for_table_lampyre = prepare_row(row)
            for _row in rows_for_table_lampyre:
                yield _row

    ip, port = server.split(":")
    dbname = "NamecoinExplorer"
    collection_name_blocks = "Blocks"
    collection_name_tx = "Tx"
    cl_mongo = init_connect_to_mongodb(ip, port, dbname, user, password)
    if cl_mongo:
        db = cl_mongo[dbname]
        search_dict = {"ips": {"$in": ips}}
        need_fields = {'clean_name': 1,
                       'ips': 1,
                       'clean_op': 1,
                        'clean_datetime_block': 1,
                       'blockhash': 1,
                       'txid': 1,
                       '_id': 0}
        for row in return_info(search_dict, need_fields):
            yield row


def grouper(count, iterable, fillvalue=None):
    """
    :param count: length of subblock
    :param iterable: array of data
    :param fillvalue: is fill value in last chain
    :return:
    grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx"
    """
    args = [iter(iterable)] * count
    result = []
    for element in itertools.zip_longest(fillvalue=fillvalue, *args):
        tmp = filter(lambda y: y is not None, element)
        result.append(list(tmp))
    return result


def return_namecoin(namedomain):
    if namedomain.endswith(".bit"):
        return {'domain': namedomain,
                'namecoin_domain': "d/{}".format(namedomain[:-4])}
    elif namedomain.startswith('d/'):
        return {'domain': namedomain[2:]+'.bit',
                'namecoin_domain': namedomain}


class NamecoinDomainIPBlock(metaclass=Schema):
    name = f'Namecoin schema: Netblock, IP {Constants.RIGHTWARDS_ARROW} Domain'
    Header = NamecoinDomainExplorer

    SchemaIP = SchemaObject(IP, mapping={IP.IP: Header.ip})
    SchemaDomain = SchemaObject(Domain, mapping={Domain.Domain: Header.domain})

    SchemaBlock = SchemaObject(Netblock, mapping={Netblock.Netblock: Header.Netblock})


    Connection = IPToNetblock.between(SchemaIP, SchemaBlock, {}, [Condition(Header.ip, Operations.NotEqual, ''),
                                                            Condition(Header.Netblock, Operations.NotEqual, '')])

    SchemaIPToDomain = IPToDomain.between(
        SchemaIP, SchemaDomain,
        mapping={IPToDomain.Resolved: Header.date_time},
        conditions=[not_empty(Header.domain), not_empty(Header.ip)])


class NamecoinDomainBlocksExtended(metaclass=Schema):
    name = f'Namecoin schema: Netblock, IP {Constants.RIGHTWARDS_ARROW} Domain (ext.)'
    Header = NamecoinDomainExplorer

    SchemaIP = SchemaObject(IP, mapping={IP.IP: Header.ip})
    SchemaDomain = SchemaObject(Domain, mapping={Domain.Domain: Header.domain})
    SchemaTxid = SchemaObject(NamecoinTXid, mapping={NamecoinTXid.txid: Header.txid,
                                                     NamecoinTXid.txid_short: Header.short_txid})

    SchemaBlock = SchemaObject(Netblock, mapping={Netblock.Netblock: Header.Netblock})

    Connection = IPToNetblock.between(SchemaIP, SchemaBlock , {}, [Condition(Header.ip, Operations.NotEqual, ''),
                                                            Condition(Header.Netblock, Operations.NotEqual, '')])

    SchemaIPToDomain = IPToDomain.between(
        SchemaIP, SchemaDomain,
        mapping={IPToDomain.Resolved: Header.date_time},
        conditions=[not_empty(Header.domain), not_empty(Header.ip)])

    SchemaTxidToDomain = NamecoinTXidToDomain.between(
        SchemaTxid, SchemaDomain,
        mapping={NamecoinTXidToDomain.DateTime: Header.date_time},
        conditions=[not_empty(Header.domain)])

    SchemaTxidToIP = NamecoinTXidToIP.between(
            SchemaTxid, SchemaIP,
            mapping={NamecoinTXidToIP.DateTime: Header.date_time},
            conditions=[not_empty(Header.domain), not_empty(Header.ip)])


# for version - if netblock record like "195.32.16.0/24"


class NamecoinHistoryNetblockMongoDB(Task):

    def __init__(self):
        super().__init__()
        self.info, self.error, self.result, self.api, self.api_key = [None] * 5

    def get_id(self):
        return 'a5000127-45fc-4ed8-9cc0-a99299d92bf3'

    def get_display_name(self):
        return 'Explore Namecoin Netblock(MongoDB)'

    def get_category(self):
        return "Blockchain:\nNamecoin"

    def get_description(self):
        return 'Return history Namecoin Netblock\n\nEnter parameters 195.123.245.0/24'

    def get_weight_function(self):
        return 'blocks'

    def get_headers(self):
        return HeaderCollection(NamecoinDomainExplorer)

    def get_schemas(self):
        return SchemaCollection(NamecoinDomainIPBlock, NamecoinDomainBlocksExtended)

    def get_graph_macros(self):
        return MacroCollection(
            Macro(name=f'Namecoin Schema: Netblock, IP {Constants.RIGHTWARDS_ARROW} Domain', mapping_flags=[GraphMappingFlags.Completely],
                  schemas=[NamecoinDomainIPBlock]))

    def get_enter_params(self):
        ep_coll = EnterParamCollection()
        ep_coll.add_enter_param('blocks', 'Netblocks', ValueType.String, is_array=True, required=True, value_sources=[
                    Netblock.Netblock], description='netblock in CIDR notation\nexample: 91.243.80.0/24')
        ep_coll.add_enter_param('server', 'Host with MongoDB', ValueType.String, is_array=False, required=True,
                                default_value="68.183.0.119:27017")
        ep_coll.add_enter_param('usermongodb', 'user', ValueType.String, is_array=False, required=True,
                                default_value="anonymous")
        ep_coll.add_enter_param('passwordmongodb', 'password', ValueType.String, is_array=False, required=True,
                                default_value="anonymous")
        return ep_coll

    def execute(self, enter_params, result_writer, log_writer, temp_dir=None):

        def return_result_canonical_notation_netblocks(set_of_netblocks, settings):
            server, user, password = settings
            i = 1
            group_count = 1000
            result = []
            for cidr in set_of_netblocks:
                need_network = get_network(cidr)
                if need_network:
                    blocks_ips = grouper(group_count, map(str, need_network))

                    for ips in blocks_ips:
                        # return all document
                        _result_lines = return_massive_about_ips(ips, server, user, password, cidr)
                        check_ip_cidr = lambda row: ipaddress.ip_address(row['ip']) in need_network
                        result_lines = filter(check_ip_cidr, _result_lines)
                        result.extend(list(result_lines))
                    log_writer.info('ready:{}.\t{}'.format(i, cidr))
                    i += 1
            return result

        def return_result_maltego_range_notation_netblocks(set_of_netblocks, settings):
            server, user, password = settings
            result = []
            i = 1
            group_count = 1000
            array_ip = []
            # array_ip = [ip for block in set_of_netblocks for ip in ip_to_range(block) if valid_ip(ip)] # ideal variant
            for block in set_of_netblocks:
                array_sub_block_ip = ip_to_range(block)
                if array_sub_block_ip:
                    array_ip.extend(array_sub_block_ip)
            if not len(array_ip) > 0:
                return []

            blocks_ips = grouper(group_count, map(str, array_ip))
            cidr = ''
            for ips in blocks_ips:
                _result_lines = return_massive_about_ips(ips, server, user, password, cidr)
                check_ip_cidr = lambda row: row['ip'] in array_ip
                result_lines = filter(check_ip_cidr, _result_lines)
                try:
                    result.extend(list(result_lines))
                except:
                    pass
            return result

        # enter params

        netblock_enter_params = set(enter_params.blocks)

        array_of_enter_params = {'canonical_notation': [],
                                 'maltego_notation': []}
        array_of_enter_params ['canonical_notation']= list(filter(get_network, netblock_enter_params))
        array_of_enter_params['maltego_notation'] = list(filter(check_range_record, netblock_enter_params))

        settings = [enter_params.server,
                    enter_params.usermongodb,
                    enter_params.passwordmongodb]
        result = []

        if len(array_of_enter_params ['canonical_notation']) > 0:
            sub_result = return_result_canonical_notation_netblocks(array_of_enter_params ['canonical_notation'],
                                                                    settings)
            result.extend(sub_result)

        if len(array_of_enter_params['maltego_notation']) > 0:
            sub_result = return_result_maltego_range_notation_netblocks(array_of_enter_params ['maltego_notation'],
                                                                        settings)
            result.extend(sub_result)

        for line in sorted(result,  key=lambda line: line['date_time']):
            fields_table = NamecoinDomainExplorer.get_fields()
            tmp = NamecoinDomainExplorer.create_empty()
            for field in fields_table:
                if field in line:
                    tmp[fields_table[field]] = line[field]
            result_writer.write_line(tmp, header_class=NamecoinDomainExplorer)

