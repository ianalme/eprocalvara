import schedule
import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import openpyxl
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, ElementNotInteractableException,TimeoutException,ElementClickInterceptedException
import os
import undetected_chromedriver as uc
import random
from datetime import datetime, timedelta
import glob
import shutil 
import pyautogui
import math
from openpyxl import load_workbook
import pdfplumber
import re
import requests
import pdfkit
from PIL import Image
from pathlib import Path
from xhtml2pdf import pisa

url = "https://app.advbox.com.br/api/v1/"

def convert_html_to_pdf(dir, output):
    with open(dir, 'r') as html_file:
        html_content = html_file.read()
    with open(output, 'wb') as pdf_file:
        pisa_status = pisa.CreatePDF(html_content, dest=pdf_file)

def comparar_datas(data_str, dias):
    # Converte a string para o formato de data (DD/MM/YYYY)
    data_informada = datetime.strptime(data_str, "%d/%m/%Y")
    
    # Obtém a data atual
    data_atual = datetime.today()
    
    # Calcula a diferença entre as datas
    diferenca = (data_atual - data_informada).days
    
    # Verifica se a diferença é maior ou igual ao número de dias fornecido
    if diferenca >= dias:
        return True
    else:
        return False

    
def adicionar_cadastrada(variavel, caminho_arquivo, mensagem = 'cadastrada'):
    try:
        # Abre o arquivo para leitura
        with open(caminho_arquivo, 'r') as arquivo:
            linhas = arquivo.readlines()

        # Abre o arquivo para escrita (irá sobrescrever o arquivo original)
        with open(caminho_arquivo, 'w') as arquivo:
            for linha in linhas:
                # Se a linha contém a variável, adiciona #cadastrada ao final da linha
                if variavel in linha:
                    arquivo.write(linha.strip() + f' #{mensagem}\n')
                else:
                    arquivo.write(linha)
        
        print(f"Processo concluído. Processo'{variavel}' foi cadastrado")
    except:
        pass
        
def verificarprocessoalvaraid(processoid):
    verificar = False # Ou seja, não há, em teoria, o levantamento de alvará
    endpoint = f'history/{processoid}'
    requestfrom = f'{url}{endpoint}'
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer 9MYNc02X36oGZCRIYSscbmusjRRBV6niFXrZWTochCCThVgdWFPGyLrazLf9",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    
    tentativas = 0
    while True:
        
        if tentativas == 2:
            break
        
        response = requests.get(requestfrom, headers=headers)
        if response.status_code == 200:
            resposta = response.json()
            data = resposta['data']
            for a in data:
                #print(a)
                if 'LEVANTAR ALVARÁ' in a['task']:
                    verificar = True
                    print('alvará levantado!')
                    break
            #print(resposta['data'])
            break
        
        else:
            time.sleep(30)
            tentativas =+ 1
            print(f"Erro {response.status_code}: {response.text}")  # Exibe erro se houver
            
    return verificar

def verificarprocessoalvara(processo):
    verificar = False # em teoria, o alvará ainda não foi levantado
    endpoint = 'lawsuits'
    requestfrom = f'{url}{endpoint}'
    params = {"process_number": processo}
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer 9MYNc02X36oGZCRIYSscbmusjRRBV6niFXrZWTochCCThVgdWFPGyLrazLf9",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    
    tentativas = 0
    while True:
        
        if tentativas == 2:
            break
        
        response = requests.get(requestfrom, headers=headers, params=params)
        if response.status_code == 200:
            resposta = response.json()
            data = resposta['data'][0]
            print('\n')
            verificar = verificarprocessoalvaraid(data['id'])
            
            break
        
        else:
            time.sleep(30)
            tentativas =+ 1
            print(f"Erro {response.status_code}: {response.text}")  # Exibe erro se houver
            
    return verificar

def lerbaixados(dir,caminhodirdoc = Path(__file__).parent.resolve().as_posix()):
    lista = []
    hoje = datetime.today()
    # Adicionando um dia
    amanha = hoje + timedelta(days=5)
    # Se for sábado (5) ou domingo (6), empurra para segunda-feira
    if amanha.weekday() in [5, 6]:
        amanha += timedelta(days=(7 - amanha.weekday()))
        
    hoje = hoje.strftime("%d/%m/%Y")
    amanha = amanha.strftime("%d/%m/%Y")  # Maiúsculo "Y" para ano com 4 dígitos

        
    with open(f'{dir}/cadastros.txt', "r", encoding="utf-8") as file:
        linhas = file.readlines()  # Cada linha vira um item da lista
        for a in linhas:
            
            if '#cadastrada' in a or "#erro" in a:
                continue
            
            line = (a.split(' '))
            arquivo = line[-1].split('/')[-1]
            arquivo = arquivo.replace('\n','')
            processo = line[0].replace('informações:','')
            '''
            check = verificarprocessoalvara(processo)
            
            if check == True:
                print('já verificado')
                
            if check == False:
                print('não verificado')
            '''    
            lista.append({'processo':processo,'informacoes':a,'datah':hoje,'dataf':amanha,'documentos':[f'{caminhodirdoc}/{dir}/{arquivo}']})
    #print(lista)
    return lista

class cadastrartarefa:
    def __init__(self,dicionario,caminhotxt,tarefa:str):
        self.caminhotxt = caminhotxt
        self.dicionario = dicionario
        self.tarefa = tarefa
        path_wkhtmltopdf = r"C:\Users\T-GAMER\Documents\wkhtmltopdf\bin\wkhtmltopdf.exe"
        self.confightmltopdf = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

    def startdriver(self):
        options = uc.ChromeOptions()
        #options.add_argument("--headless")  # Executa o navegador sem abrir a janela
        #options.add_argument("--disable-gpu")  # Desativa a GPU para melhorar a velocidade no modo headless
        #options.add_argument(f'user-data-dir=C:\\Users\\ian\\AppData\\Local\\Google\\Chrome\\User Data')
        options.add_argument("accept-language=en-US,en;q=0.9,pt-BR;q=0.8,pt;q=0.7")
        
        #options.add_argument(f'user-data-dir=C:\\Users\\ian\\AppData\\Local\\Google\\Chrome\\User Data')
        #options.add_argument('profile-directory=Profile 3')
        
        #options.add_argument('--incognito')  # Habilita o modo anônimo
        options.add_argument('--disable-blink-features=AutomationControlled')  # Desabilita a detecção do WebDriver
        options.add_experimental_option('prefs', {
            "download.prompt_for_download": False,
            "download.directory_upgrade": True
        })
        self.driver = uc.Chrome(options=options)
        self.driver.execute_script('Object.defineProperty(navigator, "webdriver", {get: () => undefined})')
        
    def acessarsite(self):
        self.startdriver()
        
        self.driver.get('https://app.advbox.com.br/login')
        
        element = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.NAME, "email")))
        element.send_keys('gestaodiaselima@diaselima.net')
        
        element = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.NAME, "password")))
        element.send_keys('Edric2014@')
        element.send_keys(Keys.ENTER)
        #element = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Entrar']")))
        #element.click()
        print('entrou no advbox')
        time.sleep(7)
        #inserir tarefa
        for a in self.dicionario:
            
            datah = a['datah'].replace('/','')
            dataf = a['dataf'].replace('/','')
            print(dataf,datah)
            processo = a['processo']
            
            element = WebDriverWait(self.driver, 2).until(EC.presence_of_element_located((By.XPATH, '//a[@href="posts/create"]')))
            element.click()
        
            element = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//span[text()='Nome do cliente ou número do processo']")))
            element.click()
            
            wait = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/span/span/span[1]/input')))
            wait.send_keys(processo)
            
            time.sleep(5)
            
            wait.send_keys(Keys.RETURN)
            
            #Quem vai trabalhar nesta tarefa?
            try:
                
                element = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Quem vai trabalhar nesta tarefa?']")))
                element.click()
            
            except:
                print('erro',processo)
                adicionar_cadastrada(processo,f'{self.caminhotxt}/cadastros.txt','erro')
                self.driver.get('https://app.advbox.com.br/')
                continue
            
            wait = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '/html/body/span/span/span[1]/input')))
            wait.send_keys('tavana')
            time.sleep(3)
            wait.send_keys(Keys.RETURN)
            
            #O que essa pessoa irá fazer?
            element = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//span[text()='O que essa pessoa irá fazer?']")))
            element.click()
            
            wait = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '/html/body/span/span/span[1]/input')))
            wait.send_keys(self.tarefa)
            
            time.sleep(3)
            wait.send_keys(Keys.RETURN)
            
            #urgent
            info = a['informacoes']
            line = info.split(' ')
            dataexp = line[2]
            verificar = comparar_datas(dataexp,60) #verificar se há mais de 60 dias durante as duas datas
            
            if verificar == True:
                urgencia = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.NAME, "important")))
                urgencia.click()
            else:
                urgencia = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.NAME, "urgent")))
                urgencia.click()
                
            campo = self.driver.find_element(By.XPATH, '//textarea[@placeholder="Adicione um comentário. Use @ para mencionar."]')
            campo.send_keys(a['informacoes'])
            
            time.sleep(1)
            
            elemento = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.NAME, 'date')))
            elemento.click()
            #data1 = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[8]/div/form/div[7]/div/input')))
            elemento.send_keys(datah)
            
            elemento = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.NAME, 'date_deadline')))
            elemento.click()
            #date_deadline         
            time.sleep(1)
            #data2 = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[8]/div/form/div[9]/div/input')))
            elemento.send_keys(dataf)
            # Agora, procure pelo elemento
            file_input = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input.simple-upload-file')))
            diretorio = Path(__file__).parent.resolve().as_posix()
            saida = f"{diretorio}/kitpdf/saida.pdf"
            
            for b in a['documentos']:
                if 'html' in b:
                    
                    print(b)
                    try:
                        pdfkit.from_file(b, saida, configuration=self.confightmltopdf)
                    except Exception as e:
                        print(e)
                        
                elif 'png' in b:
                    imagem = Image.open(b)
                    imagem_rgb = imagem.convert("RGB")
                    imagem_rgb.save(saida)
                    
                if 'pdf' in b:
                    shutil.copy2(b, saida)
                    
                file_input.send_keys(saida)
                time.sleep(6)
                os.remove(saida)
                
            # Depois de interagir com o elemento, volte para o conteúdo principal
            time.sleep(1)
            
            #Criar nova tarefa
            element = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Criar nova tarefa']")))
            element.click()
            adicionar_cadastrada(processo,f'{self.caminhotxt}/cadastros.txt')
            #Fechar
            element = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.close[title='Fechar']")))
            element.click()
        
    def sair(self):
        try:
            self.driver.quit()
        except:
            print('já encerrado')
            
            
#a = cadastrartarefa([{'processo':'','datah':'08/11/2024','dataf':'09/11/2024',documentos':[r'C:\Users\ian\Downloads\carta-concessao-beneficio.pdf']}])

pastas = ['alvarainss','alvaraoutros']

for a in pastas:
    caminho = a
    tarefa = 'alvará expedido'

    if 'alvaraoutros' in caminho:
        tarefa = 'valores disponíveis'
    else:
        tarefa = 'alvará expedido'
        
        
    lista = lerbaixados(caminho)
    if lista != []:
        x = cadastrartarefa(lista,caminho,tarefa)
        x.acessarsite()
        x.sair()