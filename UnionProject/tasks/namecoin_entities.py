# -*- coding: utf8 -*-
__author__ = 'sai'
NamecoinDNS = "sai.NamecoinName"
NamecoinAddress = "sai.Address"
NamecoinTX = "sai.TX"

keys_for_parse_enterparams = {"IPtoNamecoin": {"ipv4-address": 0},
                              "NamecointoIP": {"fqdn": 0},
                              "NetblocktoIP": {"ipv4-range": 0},
                              "ASNIPtoBlock": {"ipv4-address": 0}}


ip_blocked_list = ["127.0.0.1"]
# TODO need dev func. for check private or not ip address - easily