import requests
import json

class IAASIp:
    def __init__(self):
        self.ips_aws = self.obter_ips_aws()
        self.ips_gcp = self.obter_ips_gcp()
        self.ips_oracle = self.obter_ips_oracle()
        self.ips_azure = self.obter_ips_azure()
        self.ips_cloudflare = self.obter_ips_cloudflare()
        self.ips_akamai = self.obter_ips_akamai()

    def obter_ips_aws(self):
        url = 'https://ip-ranges.amazonaws.com/ip-ranges.json'
        response = requests.get(url)
        data = response.json()

        ips_aws = set()

        for prefix in data['prefixes']:
            if 'ip_prefix' in prefix:
                ips_aws.add(prefix['ip_prefix'])

        return ips_aws

    def obter_ips_gcp(self):
        url = 'https://www.gstatic.com/ipranges/cloud.json'
        response = requests.get(url)
        data = response.json()

        ips_gcp = set()

        for prefix in data['prefixes']:
            if 'ipv4Prefix' in prefix:
                ips_gcp.add(prefix['ipv4Prefix'])

        return ips_gcp

    def obter_ips_oracle(self):
        url = 'https://docs.cloud.oracle.com/en-us/iaas/tools/public_ip_ranges.json'
        response = requests.get(url)
        data = response.json()

        ips_oracle = set()

        for region in data['regions']:
            for cidr_block in region['cidrs']:
                ips_oracle.add(cidr_block['cidr'])

        return ips_oracle
    
    def obter_ips_azure(self):
        ips_azure = set() 

        url = 'https://download.microsoft.com/download/7/1/D/71D86715-5596-4529-9B13-DA13A5DE5B63/ServiceTags_Public_20230522.json'
        response = requests.get(url)
        data = response.json()

        # para cada bloco, adicionar os ips na lista
        for value in data['values']:
            
            for prefix in value["properties"]['addressPrefixes']:
                ips_azure.add(prefix)
        
        return ips_azure
    

    def obter_ips_cloudflare(self):
        ips_cloudflare = set()

        url = 'https://www.cloudflare.com/ips-v4'
        response = requests.get(url)
        data = response.text.splitlines()

        for ip in data:
            ips_cloudflare.add(ip)

        url = 'https://www.cloudflare.com/ips-v6'
        response = requests.get(url)
        data = response.text.splitlines()

        for ip in data:
            ips_cloudflare.add(ip)

        return ips_cloudflare
    

    def obter_ips_akamai(self):
        ips_akamai = set()

        url = 'https://raw.githubusercontent.com/SecOps-Institute/Akamai-ASN-and-IPs-List/master/akamai_ip_cidr_blocks.lst'
        response = requests.get(url)
        data = response.text.splitlines()

        for ip in data:
            ips_akamai.add(ip)
        
        return ips_akamai



# Teste
ips = IAASIp()
# print("AWS IPs:", ips.ips_aws)

