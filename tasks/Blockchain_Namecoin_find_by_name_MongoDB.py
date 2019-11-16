# -*- coding: utf8 -*-
__author__ = 'sai'

import time
from pymongo import MongoClient


# region Import System Ontology
try:
    from tasks.ontology import (
        Object, Task, Link, Attribute, Header, HeaderCollection, Utils, Field, ValueType, SchemaLink, SchemaObject, Condition, Operations, Macro,
        MacroCollection, Schema, EnterParamCollection, SchemaCollection, GraphMappingFlags, BinaryType, Constants,
        Attributes, IP, Domain, IPToDomain)

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


def init_connect_to_mongodb(ip, port, dbname, username=None, password=None):
    """
    :param ip:  ip server MongoDB
    :param port: 27017
    :return: True, if connected, and set value mongoclient - MongoClient
    """
    if username and password:
        connect_string_to = f'mongodb://{username}:{password}@{ip}:{port}/{dbname}'
    else:
        connect_string_to = f'mongodb://{ip}:{port}/{dbname}'

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
            print(f"try {check_i}, error:'{str(ex)}' connecting - error, sleep - 1 sec.")
            time.sleep(sleep_sec)
            check_i += 1
        else:
            return client


def not_empty(field: Field):
    return Condition(field, Operations.NotEqual, '')


def return_massive_about_domains(domains, server, user, password):

    def prepare_row(line):
        _name = return_namecoin(line['clean_name'])
        if _name:
            _result = dict()

            _result['date_time'] = line['clean_datetime_block']
            _result['domain'] = _name['domain'].strip()
            _result['namecoin_domain'] = line['clean_name'].strip()

            _result['height'] = line['height_block']
            _result['hash_block'] = line['blockhash']
            _result['txid'] = line['txid']
            _result['short_txid'] = line['txid'][:8]
            try:
                _result['operation'] =  line['clean_op'].strip()
            except:
                pass
            if 'ips' in line:
                for ip in line['ips']:
                    _result_row = _result.copy()
                    _result_row['ip'] = ip.strip()
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

    if ':' in server:
        ip, port = server.split(":")
    else:
        # try default
        ip = server
        port = '27017'

    dbname = "NamecoinExplorer"
    collection_name_blocks = "Blocks"
    collection_name_tx = "Tx"
    cl_mongo = init_connect_to_mongodb(ip, port, dbname, user, password)
    if cl_mongo:
        db = cl_mongo[dbname]
        _domains = [return_namecoin(domain) for domain in domains]
        search_list = [el['namecoin_domain'] for el in _domains]
        search_dict = {"clean_name":{"$in": search_list}}
        need_fields = {'clean_name': 1,
                       'ips': 1,
                       'clean_op':1,
                        'clean_datetime_block': 1,
                       'blockhash': 1,
                       'txid': 1,
                       '_id': 0}
        for line in return_info(search_dict, need_fields):
            yield line


def return_namecoin(namedomain):
    if namedomain.endswith(".bit"):
        return {'domain': namedomain, 'namecoin_domain': f"d/{namedomain[:-4]}"}
    elif namedomain.startswith('d/'):
        return {'domain': namedomain[2:]+'.bit', 'namecoin_domain': namedomain}


class NamecoinDomainIP(metaclass=Schema):
    name = 'Namecoin schema: Domain and IP'
    Header = NamecoinDomainExplorer

    SchemaIP = SchemaObject(IP, mapping={IP.IP: Header.ip})
    SchemaDomain = SchemaObject(Domain, mapping={Domain.Domain: Header.domain})

    SchemaIPToDomain = IPToDomain.between(
        SchemaIP, SchemaDomain,
        mapping={IPToDomain.Resolved: Header.date_time},
        conditions=[not_empty(Header.domain), not_empty(Header.ip)])


class NamecoinDomainExtended(metaclass=Schema):
    name = 'Namecoin schema: Extended schema interpretation'
    Header = NamecoinDomainExplorer

    SchemaIP = SchemaObject(IP, mapping={IP.IP: Header.ip})
    SchemaDomain = SchemaObject(Domain, mapping={Domain.Domain: Header.domain})
    SchemaTxid = SchemaObject(NamecoinTXid, mapping={NamecoinTXid.txid: Header.txid,
                                                     NamecoinTXid.txid_short: Header.short_txid})

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


class NamecoinHistoryDomainIPMongoDB(Task):

    def __init__(self):
        super().__init__()
        self.info, self.error, self.result, self.api, self.api_key = [None] * 5

    def get_id(self):
        return '151b0d5e-6e3b-489d-b482-701774690ca4'

    def get_display_name(self):
        return 'Explore Namecoin names(MongoDB)'

    def get_category(self):
        return "Blockchain:\nNamecoin"

    def get_description(self):
        return 'Return history Namecoin name\n\nEnter parameters "d/example or example.bit'

    def get_weight_function(self):
        return 'domains'

    def get_headers(self):
        return HeaderCollection(NamecoinDomainExplorer)

    def get_schemas(self):
        return SchemaCollection(NamecoinDomainIP, NamecoinDomainExtended)

    def get_graph_macros(self):
        return MacroCollection(
            Macro(name='Namecoin Schema: Explore domains', mapping_flags=[GraphMappingFlags.Completely],
                  schemas=[NamecoinDomainIP]))

    def get_enter_params(self):
        ep_coll = EnterParamCollection()
        ep_coll.add_enter_param('domains', 'Namecoin domain', ValueType.String, is_array=True, required=True,
                                value_sources=[Attributes.System.Domain],
                                description='Namecoin name, e.g.:\nd/example'
                                            '\nexample.bit')
        ep_coll.add_enter_param('server', 'Host with MongoDB', ValueType.String, is_array=False, required=True,
                                default_value="68.183.0.119:27017")
        ep_coll.add_enter_param('usermongodb', 'user', ValueType.String, is_array=False, required=True,
                                default_value="anonymous")
        ep_coll.add_enter_param('passwordmongodb', 'password', ValueType.String, is_array=False, required=True,
                                default_value="anonymous")
        return ep_coll

    def execute(self, enter_params, result_writer, log_writer, temp_dir=None):
        server = enter_params.server
        user = enter_params.usermongodb
        password = enter_params.passwordmongodb

        domains = set([d.strip().lower() for d in enter_params.domains])

        log_writer.info("Number of Namecoins:{}".format(len(domains)))
        result_lines = return_massive_about_domains(domains, server, user, password)
        i = 1
        for line in sorted(result_lines,  key=lambda line: line['date_time']):
            log_writer.info('ready:{}.\t{}'.format(i, line['domain']))
            fields_table = NamecoinDomainExplorer.get_fields()
            tmp = NamecoinDomainExplorer.create_empty()
            for field in fields_table:
                if field in line:
                    tmp[fields_table[field]] = line[field]
            result_writer.write_line(tmp, header_class=NamecoinDomainExplorer)
            i += 1
