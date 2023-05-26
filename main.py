import socket
import ipaddress
from rich.prompt import Confirm
from urllib.parse import urlparse
import os

from rich import print as rprint
from rich.console import Console
from rich.prompt import Prompt
from rich.padding import Padding

import requests
import json
import tldextract

from iaas_ips import IAASIp

class WebScan:
    def __init__(self):
        self.console = Console()

        # Título do programa
        self.console.print("======================================================", style="bold blue", justify="center")
        self.console.print("UniWebScan", style="bold blue", justify="center", highlight=True)
        self.console.print("======================================================", style="bold blue", justify="center")
        self.console.print(" ")


    def check_iaas(self, ip):

        iaas_ips = IAASIp()

        # Obtendo os IPs das IaaS estão em JSON
        ips_aws = iaas_ips.ips_aws
        ips_gcp = iaas_ips.ips_gcp
        ips_oracle = iaas_ips.ips_oracle

        ip_address = ipaddress.ip_address(ip) # Convertendo o IP para o formato ipaddress

        # Verificando se o IP pertence a alguma IaaS
        if any(ip_address in ipaddress.ip_network(cidr) for cidr in ips_aws):
            self.console.print("Site hospedado na AWS.", style="bold green")
        elif any(ip_address in ipaddress.ip_network(cidr) for cidr in ips_oracle):
            self.console.print("Site hospedado na Oracle.", style="bold green")
        elif any(ip_address in ipaddress.ip_network(cidr) for cidr in ips_gcp):
            self.console.print("Site hospedado na GCP.", style="bold green")
        elif any(ip_address in ipaddress.ip_network(cidr) for cidr in iaas_ips.ips_azure):
            self.console.print("Site hospedado na Azure.", style="bold green")
        elif any(ip_address in ipaddress.ip_network(cidr) for cidr in iaas_ips.ips_cloudflare):
            self.console.print("Site hospedado na Cloudflare.", style="bold green")
        else:
            rprint("O IP não pertence a nenhuma IaaS.")


    def verifica_url_brasileira(self, url):
        ext = tldextract.extract(url)
        if ext.suffix == 'br':
            return True
        else:
            return False


    def run(self):

        sair = False
        
        # Mensagem de boas vindas
        self.console.print("Bem-vindo ao UniWebScan!", style="bold blue", justify="center")
        rprint(" ")
        self.console.print("Este programa tem como objetivo verificar algumas informações sobre um dado site de universidade brasileira. \nAs informações que podem ser obtidas são listadas a seguir:\n", style="bold blue")
        self.console.print("1. Onde o site está hospedado", style="bold blue")
        rprint("  - Se o site está hospedado em alguma das IaaS listadas: AWS, GCP, Azure, Oracle, Cloudflare\n")

        self.console.print("2. Onde o servidor DNS está hospedado", style="bold blue\n")
        rprint("  - Se o servidor DNS está hospedado em alguma das IaaS listadas: AWS, GCP, Azure, Oracle, Cloudflare\n")
        rprint(" ")
        
        # Input do site
        url = Prompt.ask("Digite a URL de uma universidade brasileira que deseja escanear ou digite 'Sair' para sair.", default="https://www.unicamp.br/")    
        if url == "Sair":
            return
        
        rprint(f"Site: {url}")
        rprint(" ")

        # Verificando se é um site válido
        try:
            result = urlparse(url)
            if not all([result.scheme, result.netloc]):
                rprint("URL inválida.")
                return
            
            else:
                rprint("URL válida.")

        except:
            rprint("URL inválida.")
            return

        while sair == False:
            # Obtendo o IP do site
            ip = socket.gethostbyname(urlparse(url).netloc)
            print(f"IP: {ip}\n")

            # Selecionar o que deseja fazer: obter onde o site está ou onde o servidor DNS está
            self.console.print("Qual informação sobre o site deseja obter:", style="bold blue")
            self.console.print("1. Onde está hospedado", style="bold purple")
            self.console.print("2. Onde o servidor DNS está hospedado", style="bold purple")
            self.console.print("3. Sair", style="bold red")

            opcao = Prompt.ask("Digite o número da opção desejada.", choices=["1", "2", "3"])

            if opcao == "1":
                rprint(" ")
                # Verifica se o IP é de alguma IaaS
                self.check_iaas(ip)

            elif opcao == "3":
                sair = True
                rprint("Saindo...")
                return
            
            # Verifica se quer saber outra informação
            self.console.print(" ")
            self.console.print("Deseja verificar outra informação sobre o site?", style="bold blue")
            opcao = Prompt.ask("Digite 's' para sim ou 'n' para não.", choices=["s", "n"])

            if opcao == "n":
                sair = True
                rprint("Saindo...")
                return
            


WebScan().run()

