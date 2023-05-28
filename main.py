import pandas as pd
import unidecode

import socket
import ipaddress
from urllib.parse import urlparse

from rich.prompt import Confirm
from rich import print as rprint
from rich.console import Console
from rich.prompt import Prompt
from rich.padding import Padding

import requests
import tldextract

from wafw00f.main import WAFW00F
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from robo import Robo
from iaas_ips import IAASIp
from time import sleep


class CheckHosting(Robo): # Robo de https://github.com/4rfel/Robo-Selenium.git autor: Rafael dos Santos
    def check_hosting(self, url2check):
        self.go_to_url("https://hostingchecker.com/") # Abrindo o site
        self.wait_until_find_send_keys(By.CSS_SELECTOR, "input#url", url2check) # Preenchendo o campo de URL
        self.wait_until_find_click(By.CSS_SELECTOR, "input.pingsubmit") # Clicando no botão de submit
        host = self.wait_until_find(By.CSS_SELECTOR, ".hcresults > p:nth-child(2) > b:nth-child(1)") # Obtendo o nome do servidor
        max_tries = 5
        tries = 0
        while not host: # Se não conseguir obter o nome do servidor, tentar novamente
            sleep(5)
            self.wait_until_find_click(By.CSS_SELECTOR, "input.pingsubmit")
            host = self.wait_until_find(By.CSS_SELECTOR, ".hcresults > p:nth-child(2) > b:nth-child(1)")
            tries = 1
            if tries == max_tries:
                self.console.print("Não foi possível obter o nome do servidor.", style="bold red")
                return "Não foi possível obter o nome do servidor."

        return host.text



class WebScan:
    def __init__(self):
        self.console = Console()

        # Título do programa
        self.console.print("======================================================", style="bold blue", justify="center")
        self.console.print("UniWebScan", style="bold blue", justify="center", highlight=True)
        self.console.print("======================================================", style="bold blue", justify="center")
        self.console.print(" ")

        options = FirefoxOptions()
        # options.add_argument("--headless") # Rodar o Firefox em modo headless

        self.CH = CheckHosting(options)


    def check_iaas(self, ip, excel_file):
        nomes_univ = []
        abrev_univ = []

        # Lendo o arquivo excel com os nomes das universidades
        df = pd.read_excel(excel_file)
        nomes_univ = df['univ'].apply(unidecode.unidecode).apply(lambda x: x.lower()).tolist()

        abrev_univ = df['abrev'].tolist()

        # Mudar para lowcase
        abrev_univ = [x.lower() for x in abrev_univ]
        # print(abrev_univ)

        self.console.print("Verificando se o site está hospedado em alguma IaaS...", style="bold blue")
        # Printar lista das IaaS consultadas
        self.console.print("IaaS consultadas:", style="bold blue")
        self.console.print("AWS, GCP, Oracle, Azure, Cloudflare, Akamai", style="bold blue")

        self.console.print(" ")

        iaas_ips = IAASIp()

        # Obtendo os IPs das IaaS estão em JSON
        ips_aws = iaas_ips.ips_aws
        ips_gcp = iaas_ips.ips_gcp
        ips_oracle = iaas_ips.ips_oracle

        ip_address = ipaddress.ip_address(ip) # Convertendo o IP para o formato ipaddress

        # Verificando se é um servidor próprio
        host_from_hostingchecker = self.CH.check_hosting(ip)

        # mudar para lowcase
        low_case_host = unidecode.unidecode(host_from_hostingchecker.lower())
        
        self.console.print(f"Site hospedado em: {host_from_hostingchecker}", style="bold green")

        if (low_case_host in nomes_univ) or (low_case_host in abrev_univ):
            self.console.print("Ou seja, está hospedado em servidor próprio.", style="bold green")
            # Inserir no excel "Servidor próprio"
            # add new row to dataframe
            self.temp_row["onde_hosteado"] = ["Servidor próprio" + " - " + host_from_hostingchecker]

        # Verificando se o IP pertence a alguma IaaS
        elif any(ip_address in ipaddress.ip_network(cidr) for cidr in ips_aws):
            self.console.print("Site hospedado na AWS.", style="bold green")
            # Inserir no excel "AWS"
            self.temp_row["onde_hosteado"] = ["AWS" + " - " + host_from_hostingchecker]

        elif any(ip_address in ipaddress.ip_network(cidr) for cidr in ips_oracle):
            self.console.print("Site hospedado na Oracle.", style="bold green")
            # Inserir no excel "Oracle"
            self.temp_row["onde_hosteado"] = ["Oracle" + " - " + host_from_hostingchecker]

        elif any(ip_address in ipaddress.ip_network(cidr) for cidr in ips_gcp):
            self.console.print("Site hospedado na GCP.", style="bold green")
            # Inserir no excel "GCP"
            self.temp_row["onde_hosteado"] = ["GCP" + " - " + host_from_hostingchecker]

        elif any(ip_address in ipaddress.ip_network(cidr) for cidr in iaas_ips.ips_azure):
            self.console.print("Site hospedado na Azure.", style="bold green")
            # Inserir no excel "Azure"
            self.temp_row["onde_hosteado"] = ["Azure" + " - " + host_from_hostingchecker]

        elif any(ip_address in ipaddress.ip_network(cidr) for cidr in iaas_ips.ips_cloudflare):
            self.console.print("Site hospedado na Cloudflare.", style="bold green")
            # Inserir no excel "Cloudflare"
            self.temp_row["onde_hosteado"] = ["Cloudflare" + " - " + host_from_hostingchecker]

        elif any(ip_address in ipaddress.ip_network(cidr) for cidr in iaas_ips.ips_akamai):
            self.console.print("Site hospedado na Akamai.", style="bold green")
            # Inserir no excel "Akamai"
            self.temp_row["onde_hosteado"] = ["Akamai" + " - " + host_from_hostingchecker]

        else:
            # Fazer por Lookup reverso
            rev_ip = '.'.join(reversed(ip.split(".")))
            url_gpcns = f"https://dns.google/resolve?name={rev_ip}.in-addr.arpa&type=PTR"

            response = requests.get(url_gpcns)
            response_json = response.json()


            if 'Answer' in response_json:
                data = response_json["Answer"][0]["data"]

                if "amazonaws" in data:
                    self.console.print("Site hospedado na AWS.", style="bold green")
                    # Inserir no excel "AWS"
                    self.temp_row["onde_hosteado"] = ["AWS" + " - " + host_from_hostingchecker]

                elif "hwclouds" in data:
                    self.console.print("Site hospedado na Huawei Cloud.", style="bold green")
                    # Inserir no excel "Huawei Cloud"
                    self.temp_row["onde_hosteado"] = ["Huawei Cloud" + " - " + host_from_hostingchecker]

                elif "azure" in data:
                    self.console.print("Site hospedado na Azure.", style="bold green")
                    # Inserir no excel "Azure"
                    self.temp_row["onde_hosteado"] = ["Azure" + " - " + host_from_hostingchecker]




    def check_dns_server(self, url):
        self.console.print("Verificando onde o servidor DNS está hospedado...", style="bold blue")

        dns_name = tldextract.extract(url).domain + '.' + tldextract.extract(url).suffix
        print(dns_name)

        # Usando Google Public DNS
        url_dns = f"https://dns.google/resolve?name={dns_name}&type=AAAA"

        response = requests.get(url_dns)
        response_json = response.json()

        if 'Authority' in response_json:
            authority = response_json['Authority']
            if authority:
                dns_server = authority[0]['data'].split()[0]

                nome = tldextract.extract(url).domain
                if nome in dns_server:
                    self.console.print(f"O servidor DNS está hospedado em servidor próprio - {dns_server}", style="bold green")
                    # Inserir no excel "Servidor próprio"
                    self.temp_row["cloud_dns"] = ["Servidor próprio" + " - " + dns_server]

                else:
                    self.console.print(f"O servidor DNS está hospedado em: {dns_server}", style="bold green")
                    # Inserir no excel "Não próprio"
                    self.temp_row["cloud_dns"] = [dns_server]
            else:
                self.console.print("Não foi possível obter informações sobre o servidor DNS.", style="bold red")

        else:
            self.console.print(f"O servidor DNS está hospedado em servidor próprio", style="bold green")
            # Inserir no excel "Servidor próprio"
            self.temp_row["cloud_dns"] = ["Servidor próprio"]
            


    def check_waf(self, url):
        self.console.print("Verificando se o site possui WAF...", style="bold blue")
        rprint(" ")

        # Check if the URL includes a protocol schema
        parsed_url = urlparse(url)
        if not parsed_url.scheme:
            url = "http://" + url

        wafw00f_obj = WAFW00F(url)

        try:
            results = wafw00f_obj.identwaf()

            if results:
                num_wafs = len(results)

                self.console.print(f"O site possui {num_wafs} WAF(s)", style="bold green")
                rprint(" ")
                self.console.print("WAF(s) identificado(s):", style="bold green")
                for waf in results:
                    self.console.print(waf, style="bold green")

                # Inserir no excel "Possui WAF"
                self.temp_row["tem_waf"] = [1]
                self.temp_row["waf"] = results
            else:
                self.console.print("O site não possui WAF.")
                # Inserir no excel "Não possui WAF"
                self.temp_row["tem_waf"] = [0]

        except Exception as e:
            self.console.print(f"Ocorreu um erro ao verificar o WAF: {str(e)}", style="bold red")



    def verifica_url_brasileira(self, url, csv_file):

        # retorna True se a URL for de uma universidade brasileira
        nomes_universidades = []
        abreviacoes_universidades = []

        nomes_maiusculos = []
        abreviacoes_maiusculos = []

        df = pd.read_excel(csv_file)

        nomes_maiusculos = df['univ'].tolist()
        # Deixar com letras minúsculas
        nomes_universidades = [x.lower() for x in nomes_maiusculos]

        abreviacoes_maiusculos = df['abrev'].tolist()
        # Deixar com letras minúsculas
        abreviacoes_universidades = [x.lower() for x in abreviacoes_maiusculos]

        # Verificando se a URL é de uma universidade brasileira
        domain = tldextract.extract(url).domain

        self.console.print("Verificando se a URL é de uma universidade brasileira...", style="bold blue")



        if domain in nomes_universidades or domain in abreviacoes_universidades:
            self.console.print("Site de universidade brasileira")

            # Printando nome da universidade
            index = abreviacoes_universidades.index(domain)

            self.console.print(f"Nome da universidade: {nomes_maiusculos[index]} ({abreviacoes_maiusculos[index]})", style="bold green")

            # Adiciona url na coluna url no excel
            # Adicionando nome e abreviação da universidade no excel
            if url in self.df_info['urls_univ'].values:
                rprint(" ")
                self.console.print("URL já está no excel", style="bold red")
                include = Prompt.ask("Deseja sobrescrever? (s/n)", choices=["s", "n"])
                if include == "n":
                    exit()
                else:
                    self.df_info = self.df_info[self.df_info.urls_univ != url]

            self.temp_row['urls_univ'] = [url]
            self.temp_row['nome_univ'] = [nomes_maiusculos[index]]
            self.temp_row['sigla_univ'] = [abreviacoes_maiusculos[index]]

            return True

        else:
            self.console.print("Site não é de universidade pública brasileira", style="bold red")
            return False



    def run(self, excel_file, info_excel):

        # Mensagem de boas vindas
        self.console.print("Bem-vindo ao UniWebScan!", style="bold blue", justify="center")
        rprint(" ")
        self.console.print("Este programa tem como objetivo verificar algumas informações sobre um dado site de universidade brasileira. \nAs informações que podem ser obtidas são listadas a seguir:\n", style="bold blue")
        self.console.print("1. Onde o site está hospedado", style="bold blue")
        rprint("  - Se o site está hospedado em alguma das IaaS listadas: AWS, GCP, Azure, Oracle, Cloudflare\n")

        self.console.print("2. Onde o servidor DNS está hospedado", style="bold blue\n")
        rprint(" ")

        self.console.print("3. Se o site possui WAF e qual serviço de cloud está sendo utilizado", style="bold blue")
        rprint(" ")

        # Input do site
        self.console.print("Digite a URL de uma universidade brasileira que deseja escanear EX: https://ufrj.br/")
        self.console.print("Digite 'Sair' para sair do programa.", style="bold red")
        rprint(" ")
        url = Prompt.ask("URL")


        if url == "Sair":
            return

        rprint(f"Site: {url}")
        rprint(" ")

        self.console.print("Verificando se o site é válido...", style="bold blue")

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

        rprint(" ")
        self.df_info = pd.read_excel(info_excel)
        self.temp_row = pd.DataFrame(columns=self.df_info.columns)
        # Verificando se é um site de uma universidade brasileira
        univ_publica = self.verifica_url_brasileira(url, excel_file)

        if univ_publica:
            ip = socket.gethostbyname(urlparse(url).netloc)
            print(f"IP: {ip}\n")

            rprint(" ")
            self.console.print("Inserindo onde o site está hospedado...", style="bold blue")
            self.check_iaas(ip, excel_file)
            rprint(" ")

            rprint(" ")
            self.console.print("Inserindo onde o servidor DNS está hospedado...", style="bold blue")
            self.check_dns_server(url)
            rprint(" ")

            rprint(" ")
            self.console.print("Inserindo informações sobre WAF...", style="bold blue")
            self.check_waf(url)
            rprint(" ")

        else:
            rprint(" ")
            self.console.print("Saindo do programa...", style="bold blue")

        self.df_info = pd.concat([self.df_info, self.temp_row], ignore_index=True)
        print(self.df_info)

        self.df_info.to_excel(info_excel, index=False, sheet_name="Planilha1")

        # with pd.ExcelWriter(info_excel, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
        #     self.df_info.to_excel(writer, index=False, startrow=len(self.df_info), header=False, sheet_name="Template", float_format="%.2f")




info_excel = "info_universidades.xlsx"
excel_file = "universidades.xlsx"
webscan = WebScan()

webscan.run(excel_file, info_excel)
webscan.CH.quit()