import csv
import pandas as pd

import socket
import ipaddress
import dns.resolver
from urllib.parse import urlparse

from urllib.parse import urlparse
import os

from rich.prompt import Confirm
from rich import print as rprint
from rich.console import Console
from rich.prompt import Prompt
from rich.padding import Padding

import requests
import json
import tldextract

from iaas_ips import IAASIp

from wafw00f.main import WAFW00F


#Something went wrong Invalid URL 'www.example.com': No schema supplied. Perhaps you meant http://www.example.com?

def check_waf(url):
    print("Verificando se o site possui WAF...")
    print(url)

    # Verificando e corrigindo o esquema da URL
    parsed_url = urlparse(url)
    if not parsed_url.scheme:
        url = "http://" + url

    print(url)

    wafw00f_obj = WAFW00F()
    try:
        results = wafw00f_obj.identwaf(url)

        if results:
            num_wafs = len(results)
            clouds = set([result['origin'] for result in results])

            print(f"O site possui {num_wafs} WAF(s) de serviço(s) de cloud: {', '.join(clouds)}")
        else:
            print("O site não possui WAF.")
    except Exception as e:
        print(f"Ocorreu um erro ao verificar o WAF: {str(e)}")


check_waf("http://www.google.com.br")