import time
from datetime import datetime, timedelta
import schedule
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.alert import Alert
from datetime import datetime
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, ElementNotInteractableException,TimeoutException,ElementClickInterceptedException
import undetected_chromedriver as uc
import random
import pyotp  
import re
import string
import pdfkit

sk = "GZRTONRWG5QTOYJTMFRGMOJRGM3WIZJQ"  # Substitua pelo seu código secreto correto

def datasuperior(data1: str, data2: str) -> bool: #data 1 é data da última movimentação, data2 é a data limite do escopo
    """
    Verifica se data1 é menor ou igual a data2.

    Parâmetros:
    - data1 (str): Data no formato "DD/MM/AAAA" que será comparada.
    - data2 (str): Outra data no formato "DD/MM/AAAA" para comparação.

    Retorna:
    - bool: Retorna True se data1 for menor ou igual a data2, caso contrário, False.
    """
    dt1 = datetime.strptime(data1, "%d/%m/%Y")
    dt2 = datetime.strptime(data2, "%d/%m/%Y")
    print(data1,data2)
    # Comparando as datas
    if dt1 >= dt2:
        print('maior,igual')
        return True
    else:
        print('menor')
        return False
    
def registrarsucesso(mensagem: str, txt='encontrado/encontrado.txt'):
    data_hoje = datetime.today().strftime("%d/%m/%Y")
    with open(txt, "a", encoding="utf-8") as file:
        file.write(f'{mensagem} {data_hoje}\n')

def consultarsucesso(processo,txt='encontrado/encontrado.txt'):
    resultado = False
    try:
        with open(txt, "r", encoding="utf-8") as arquivo:
            for linha in arquivo:
                if processo in linha:    
                    print(linha.strip())  # strip() remove espaços e quebras de linha extras  
                    resultado = True  
                    break
    except FileNotFoundError:
        pass
    return resultado

def registrarconsulta(mensagem: str, txt='consultados/consultados.txt'):
    
    processo = mensagem.strip().split(' ')[0]  # Extrai o processo
    atualizado = False  # Flag para verificar se foi substituído

    # Lê todas as linhas do arquivo
    novas_linhas = []
    
    try:
        with open(txt, "r", encoding="utf-8") as file:
            linhas = file.readlines()
            
            #print(linhas)
        # Atualiza a linha se o processo já existir
        
        for linha in linhas:
            if processo in linha:  # Se a linha começa com o processo
                novas_linhas.append(mensagem + "\n")  # Substitui a linha
                atualizado = True
                print('substituido')
            else:
                novas_linhas.append(linha)  # Mantém as outras linhas
    except FileNotFoundError:
        pass
    
    # Se não encontrou o processo, adiciona a nova mensagem
    if not atualizado:
        novas_linhas.append(mensagem + "\n")

    # Escreve o arquivo atualizado
    with open(txt, "w", encoding="utf-8") as file:
        file.writelines(novas_linhas)
        
def consultarconsulta(processo,txt='consultados/consultados.txt'):
    resultado = False
    data_atual = datetime.now().strftime("%d/%m/%Y")
    try:
        with open(txt, "r", encoding="utf-8") as arquivo:
            for linha in arquivo:
                if processo in linha:    
                    if data_atual in linha: 
                        resultado = True
                    print(linha.strip())  # strip() remove espaços e quebras de linha extras    
                    break
    except FileNotFoundError:
        pass
    return resultado
    

class eproc:
    def __init__(self,tempfiles):
        
        ###
        self.tempfiles = tempfiles
        options = uc.ChromeOptions()
        #options.add_argument("--headless")  # Executa o navegador sem abrir a janela
        options.add_argument("--disable-gpu")  # Desativa a GPU para melhorar a velocidade no modo headless
        options.add_argument("--start-minimized")  # Inicia o navegador minimizado
        options.add_argument("user-data-dir=C:/Users/ian/AppData/Local/Google/Chrome/User Data")
        options.add_argument("--profile-directory=Profile 3")  # <-- Adicione "--" antes
        options.add_argument('--disable-popup-blocking')  # Desativa bloqueio de pop-ups
        options.add_experimental_option('prefs', {
            "download.default_directory": f'{tempfiles}',
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True #It will not show PDF directly in chrome
        })
        self.driver = uc.Chrome(options=options)
                # Obtém a resolução da tela principal
        screen_width = self.driver.execute_script("return screen.width")
        screen_height = self.driver.execute_script("return screen.height")

        # Move a janela para a segunda tela (a maioria dos setups usa a segunda tela começando após a largura da primeira)
        self.driver.set_window_position(screen_width + 10, 0)  # Move para a direita
        self.driver.set_window_size(screen_width, screen_height)  # Define o tamanho como tela cheia
        
    def digitarlentamente(self,item,texto):
        for string in list(texto):
            time.sleep(random.uniform(0.2, 1))
            item.send_keys(string)
                
    def logareproc(self):
        self.driver.get('https://eproc1.tjto.jus.br/eprocV2_prod_1grau/externo_controlador.php?acao=principal')
        
        time.sleep(2)
        
        try:
            # Tentar capturar o alerta
            alert = Alert(self.driver)
            alert.accept()  # Aceita o alerta (caso seja uma caixa de confirmação)
        except:
            print("Nenhum alerta encontrado.")
            
        if self.driver.current_url != 'https://eproc1.tjto.jus.br/eprocV2_prod_1grau/externo_controlador.php?acao=principal':
            print('alterou')
            
        else:
            #entrar com login e senha
            login = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located ((By.ID, 'txtUsuario')))
            login.send_keys('TO004052')#AUTOR DO PROCESSO
            #self.digitarlentamente(login,texto='TO004052')
            
            senha = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located ((By.ID, 'pwdSenha')))
            senha.send_keys('R4103792014s@')#AUTOR DO PROCESSO
            #self.digitarlentamente(senha,texto='R4103792014s@')
            
            
            entrar = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located ((By.NAME, 'sbmEntrar')))
            
            entrar.click()
            
            sk = "HBSDGNJWGY3TENRVHBRGENBYGFRGKOBS"  # Substitua pelo seu código secreto correto
            totp = pyotp.TOTP(sk)  
            code = totp.now()
            
            try:
                senha = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located ((By.ID, 'txtAcessoCodigo')))
                senha.send_keys(code)
                
                #btnValidar
                validar = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located ((By.ID, 'btnValidar')))
                validar.click()
            except:
                print('não cobrou código')
            
            hintclose = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located ((By.ID, 'hint-close')))
            hintclose.click()
        
    def consultarprocesso(self,numprocess):
        padrao_data_hora = re.compile(r"\b\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}\b")

        pesquisa = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located ((By.ID, 'txtNumProcessoPesquisaRapida')))
        pesquisa.send_keys(numprocess) #'0002465-31.2022.8.27.2702'
        pesquisa.send_keys(Keys.ENTER)
        
    def passardepagina(self):
        try:
            proximapag = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located ((By.ID, "lnkInfraProximaPaginaSuperior")))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", proximapag)
            time.sleep(0.5)
            proximapag.click()
            return True
        
        except Exception as e:
            print(e)
            return False
            
    def procuraralvara(self):
        relacao = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located ((By.XPATH, "//*[contains(text(), 'Relação de processos')]")))
        relacao.click()
        classe = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located ((By.ID, "selClasseProcesso")))
        classe.click()
        
        select = Select(classe)

        # Seleciona a opção pelo valor
        select.select_by_value("0000014559")
        
        hoje = datetime.today()
        self.data_hoje = hoje.strftime('%d/%m/%Y')
        
        #Até quantos dias iremos olhar para trás
        dais = hoje - timedelta(days=1) 

        # Formatar a data no formato ddmmyyyy
        self.data_ontem = dais.strftime('%d/%m/%Y')
        '''
        #dataInicioField
        datainiciofield = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located ((By.NAME, "dataInicioField"))).send_keys(data_ontem)
        datafimfield = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located ((By.NAME, "dataFimField"))).send_keys(data_hoje)
        '''
        
        buscar = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located ((By.ID, "btnBuscas")))
        buscar.click()
        time.sleep(7)
        
        #filtrar por mais recentes
        recentes = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located ((By.CSS_SELECTOR, '[title="Ordenar Data/Hora Ult. Evento Descendente"]'))).click()
        time.sleep(7)
    
    def procuraralvara2(self):
    
        #lnkInfraProximaPaginaSuperior
        
        # Parte fixa do href
        parte_fixa = "controlador.php?acao_origem=relatorio_processo_procurador_listar&acao_retorno=relatorio_processo_procurador_listar&acao=processo_selecionar&num_processo="

        # Busca todos os links <a> cujo href comece com a parte fixa
        links = self.driver.find_elements(By.XPATH, f'//a[starts-with(@href, "{parte_fixa}")]')
        
        #print(f"Encontrados {len(links)} links para clicar.")

        # Salva a aba original
        padrao_data_hora = re.compile(r"\b\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}\b")
        
        # Clica em cada link encontrado
        for link in links:
            try:
                textoproc = link.text  # Obtém o texto dentro do <a> // o número do processo
            except: 
                continue
            
            #vamos procurar a última movimentação no processo
            avo_tr = link.find_element(By.XPATH, "./ancestor::tr[1]")  # Encontra o avô <tr>
            #print(ultimo_tr.get_attribute('outerHTML'))  # Printando o último <tr> (tio)
            
            ultimamov = str(avo_tr.get_attribute('outerHTML')).split('<td>')[-3]
            ultimamov = ultimamov.replace('</td>','')
            ultimamov = ultimamov.split(' ')[0]
            verificardata = datasuperior(ultimamov,self.data_ontem)
            if verificardata == False:
                self.driver.quit()   
                break
                 
                
            #print(f'abrindo {texto}')
            consulta = consultarconsulta(textoproc) #consultar se já verificamos o processo hoje
            consulta2 = consultarsucesso(textoproc) #consulta se não já foi registrado alvará
            
            if consulta == True or consulta2 == True: #se já foi verificado
                continue
            
            link.send_keys(Keys.CONTROL + Keys.RETURN)  # Windows
            time.sleep(0.3)
            abas = self.driver.window_handles
            
            self.driver.switch_to.window(abas[-1])
            data_atual = datetime.now().strftime("%d/%m/%Y")
            registrarconsulta(f'{textoproc} {data_atual}')
            
            #Procura o último evento
            try:
                trs = WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, "//tr[starts-with(@id, 'trEvento')]")))
            except:
                print('página não carregada')
                continue
            
            if trs:
                ultimo_tr = max(trs, key=lambda tr: int(tr.get_attribute("id").replace("trEvento", "")))
                ultimoevento = str(ultimo_tr.get_attribute('id')).replace('trEvento','')
                
                elemento = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located ((By.ID, f'{ultimo_tr.get_attribute('id')}')))
                todos_os_filhos = elemento.find_elements(By.XPATH, ".//*")

                # Percorre e imprime as tags e atributos dos filhos
                for filho in todos_os_filhos:
                    #print(f"Tag: {filho.tag_name}, Atributos: {filho.get_attribute('outerHTML')}")
                     texto = filho.text.strip()
                     correspondencias = padrao_data_hora.findall(texto)  # Procura datas no texto do elemento
                     if correspondencias != []:
                         dataultimoevento = correspondencias[0] #data da última movimentação
                         break
                
            #procurar alvará e verificar se é ação contra o INSS
            html_content = self.driver.page_source
            if "INSS - INSTITUTO NACIONAL DO SEGURO SOCIAL" in html_content:
                try:
                    # Aguarda até que o <label> com o texto "Expedido Alvará" esteja presente
                    label_element = WebDriverWait(self.driver, 1).until(EC.presence_of_element_located((By.XPATH, "//label[@class='infraEventoDescricao' and text()='Expedido Alvará']")))

                    # Sobe dois níveis: pai -> avô
                    avo_element = label_element.find_element(By.XPATH, "./../..")  # Primeiro ../ sobe para o pai, segundo ../ sobe para o avô
                    eventoalvara = str(avo_element.get_attribute('id')).replace('trEvento','')
                    
                    todos_os_filhos = avo_element.find_elements(By.XPATH, ".//*")

                    # Percorre e imprime as tags e atributos dos filhos
                    for filho in todos_os_filhos:
                        #print(f"Tag: {filho.tag_name}, Atributos: {filho.get_attribute('outerHTML')}")
                        texto = filho.text.strip()
                        correspondencias = padrao_data_hora.findall(texto)  # Procura datas no texto do elemento
                        if correspondencias != []:
                            dataalvara = correspondencias[0] #data da última movimentação
                            break
                        
                    print(eventoalvara,dataalvara)
                    netos = WebDriverWait(avo_element, 10).until(EC.presence_of_all_elements_located((By.XPATH, ".//descendant::*[@class='infraLinkDocumento']")))
                    netos[0].click()
                    
                    self.driver.switch_to.window(self.driver.window_handles[-1])
                    time.sleep(2)
                    html_content = self.driver.page_source
                    letras_aleatorias = ''.join(random.choices(string.ascii_letters, k=14))

                    # Defina o caminho para salvar o arquivo HTML
                    with open(f"alvarainss/{letras_aleatorias}.html", "w", encoding="utf-8") as file:
                        file.write('<meta charset="UTF-8">')
                        file.write(html_content)
                        
                    with open("alvarainss/cadastros.txt", "a", encoding="utf-8") as file:
                        file.write(f'informações:{textoproc} {eventoalvara} {dataalvara}/{letras_aleatorias}.html\n')

                    registrarsucesso(textoproc)
                    # Volta
                    self.driver.close() 
                    self.driver.switch_to.window(self.driver.window_handles[-1])
                        
                except Exception as e: 
                    pass
                
            else:
                
                try:
                    # Aguarda até que o <label> com o texto "Expedido Alvará" esteja presente
                    avo_element = WebDriverWait(self.driver, 1).until(EC.presence_of_element_located((By.XPATH, "//td[contains(., 'Alvará Pago')]/ancestor::tr")))
                    eventoalvara = str(avo_element.get_attribute('id')).replace('trEvento','')
                    
                    todos_os_filhos = avo_element.find_elements(By.XPATH, ".//*")

                    # Percorre e imprime as tags e atributos dos filhos
                    for filho in todos_os_filhos:
                        #print(f"Tag: {filho.tag_name}, Atributos: {filho.get_attribute('outerHTML')}")
                        texto = filho.text.strip()
                        correspondencias = padrao_data_hora.findall(texto)  # Procura datas no texto do elemento
                        if correspondencias != []:
                            dataalvara = correspondencias[0] #data da última movimentação
                            break
                        
                    #print(eventoalvara,dataalvara)
                    netos = WebDriverWait(avo_element, 10).until(EC.presence_of_all_elements_located((By.XPATH, ".//descendant::*[@class='infraLinkDocumento']")))
                    netos[0].click()
                    
                    self.driver.switch_to.window(self.driver.window_handles[-1])
                    time.sleep(2)
                    html_content = self.driver.page_source
                    letras_aleatorias = ''.join(random.choices(string.ascii_letters, k=14))
                    # Se o conteúdo for um PDF
                    if '/data-mimetype="pdf"' in html_content:
                        print('baixar pdf')
                        self.driver.save_screenshot(f"alvaraoutros/{letras_aleatorias}.png")
                        terminacao = 'png'
                        
                    else:    
                        terminacao = 'html'
                        # Defina o caminho para salvar o arquivo HTML
                        with open(f"alvaraoutros/{letras_aleatorias}.html", "w", encoding="utf-8") as file:
                            file.write('<meta charset="UTF-8">')
                            file.write(html_content)
                            
                    with open("alvaraoutros/cadastros.txt", "a", encoding="utf-8") as file:
                        file.write(f'informações:{textoproc} {eventoalvara} {dataalvara}/{letras_aleatorias}.{terminacao}\n')
                    # Volta
                    registrarsucesso(textoproc)
                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[-1])
                    
                except Exception as e: 
                    pass
                
            #time.sleep(1)  # Espera o 1 segundo
            print('informações',textoproc,ultimoevento,dataultimoevento)

            # Volta
            self.driver.close()
            self.driver.switch_to.window(abas[0])
            

def consultaralvaraseproc():  
    x = eproc(r'C:\Users\ian\Downloads')
    x.logareproc()
    #x.consultarprocesso('0002465-31.2022.8.27.2702')
    page = 1
    x.procuraralvara()
    while True:
        x.procuraralvara2()
        a = x.passardepagina()
        page = page + 1
        print(f'página:{page}')
        time.sleep(10)
        if a != True:
            print('encerrando')
            break


nn = input('a ou d')

if nn == 'a':
    consultaralvaraseproc()
else:
    # Agendando a tarefa para rodar às 00:05
    schedule.every().day.at("00:05").do(consultaralvaraseproc)

    # Loop para rodar o agendamento
    while True:
        schedule.run_pending()  # Verifica se há tarefas agendadas para rodar
        time.sleep(30)  # Espera 1 minuto antes de verificar novamente
