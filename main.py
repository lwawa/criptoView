import flet as ft
import yfinance as yf
import json
import requests
from flet import (
    Text,
    Column,
    Row,
    TextField,
    MainAxisAlignment,
    ElevatedButton,
    colors,
    UserControl,
    Container,
    border,
    IconButton,
    icons
)

def getPrice(ticker_symbol):
    ticker_data = yf.Ticker(ticker_symbol)
    tickerPrice = float(ticker_data.history(period='1d')['Close'][0])
    return tickerPrice

def getValid(ticker_symbol):
    if not yf.Ticker(ticker_symbol).history(period='1d').empty:
        return True
    else:
        return False

def getCotacao():
    request = requests.get('https://economia.awesomeapi.com.br/last/USD-BRL')
    reqJson = request.json()
    cotacaoDolar = reqJson["USDBRL"]["bid"]
    return cotacaoDolar

class Ticker(UserControl):
    def __init__(self, simbolo ,nome):
        super().__init__
        self.simbolo = simbolo
        self.nome = nome

class TickerManager:
    def __init__(self, file_path):
        self.file_path = file_path
        self.tickers = self.load_tickers()

    def load_tickers(self):
        try:
            with open(self.file_path, 'r') as file:
                tickers_data = json.load(file)
                tickers = [Ticker(item['simbolo'], item['nome']) for item in tickers_data]
                return tickers
        except FileNotFoundError:
            return []

    def save_tickers(self):
        with open(self.file_path, 'w') as file:
            tickers_data = [{'simbolo': ticker.simbolo, 'nome': ticker.nome} for ticker in self.tickers]
            json.dump(tickers_data, file, indent=4)

    def create_ticker(self, simbolo, nome):
        if any(ticker.simbolo == simbolo for ticker in self.tickers):
            print("Erro: Já existe um ticker com este símbolo.")
            return
        else:
            ticker = Ticker(simbolo, nome)
            self.tickers.append(ticker)
            self.save_tickers()

    def update_ticker(self, simbolo, novo_nome):
        for ticker in self.tickers:
            if ticker.simbolo == simbolo:
                ticker.nome = novo_nome
                self.save_tickers()
                return True
        return False

    def delete_ticker(self, simbolo):
        self.tickers = [ticker for ticker in self.tickers if ticker.simbolo != simbolo]
        self.save_tickers()

def main(page: ft.Page):
    
    manager = TickerManager("tickers.json")

    def addTicker(e):
        falha = False
        if not simboloCadastro.value:
            simboloCadastro.error_text = "Por favor, insira um simbolo"
            falha = True
        else:
            simboloCadastro.error_text = ""
        if not nomeCadastro.value:
            nomeCadastro.error_text = "Por favor, insira um nome"
            falha = True
        else:
            nomeCadastro.error_text = ""
        if not falha:            
            if getValid(simboloCadastro.value):
                manager.create_ticker(simboloCadastro.value, nomeCadastro.value)
                simboloCadastro.value = ""
                nomeCadastro.value = ""
            else:
                simboloCadastro.error_text = "Simbolo não existente"
            
        updateTicker()
        page.update()

    def buttonUpdate(e):
        updateTicker()
        page.update()
        
    def updateTicker():
        tickerList = []
        ticker_space.controls.clear()
        for ticker in manager.load_tickers():
            def deleteTicker(e):
                manager.delete_ticker(ticker.simbolo)
                updateTicker()
                page.update()
            tickerDolar = getPrice(ticker.simbolo) 
            tickerReal = tickerDolar * float(getCotacao())
            tickerDolarText = Text(value='$' + '{:.2f}'.format(tickerDolar), text_align=ft.TextAlign.LEFT, expand=1)
            tickerRealText = Text(value='$' + '{:.2f}'.format(tickerReal), text_align=ft.TextAlign.LEFT, expand=1)
            ticker_space.controls.append(
                Container(
                Row(
                [
                    Container(
                        Text(ticker.simbolo + "/" + ticker.nome), 
                        width=300,
                    ),
                    tickerDolarText,
                    tickerRealText,
                    Row(
                        [
                            IconButton(
                            icons.DELETE_OUTLINE,
                            tooltip="Delete",
                            on_click=deleteTicker,
                            icon_color=colors.AMBER
                            ),
                        ],
                        alignment=MainAxisAlignment.END,         
                    )
                ],
                alignment=MainAxisAlignment.START,
                ),
            )
            )
        return tickerList
    
    page.title = "Conversor de cripto"
    lableCadastro = Text(value="Cadastro de Ticker", text_align=ft.TextAlign.LEFT)
    simboloCadastro = TextField(label="Adicione o símbolo do seu ticker", text_align=ft.TextAlign.LEFT)
    nomeCadastro = TextField(label="Adicione o nome para o seu ticker", text_align=ft.TextAlign.LEFT, expand=1)
    rt_button = ElevatedButton(
        text="Registrar ticker", 
        bgcolor=colors.BLACK,
        color=colors.AMBER_500,
        height=60,
        on_click=addTicker
        )
    tickerCadastro = Row(
                   [
                       simboloCadastro,
                       nomeCadastro,
                       rt_button
                   ],
                   alignment=MainAxisAlignment.START,
               )
    
    ticker_space = Column()
    updateTicker()
    
    ticker_header = Container(
        Row(
            [
                Container(
                    Row(
                    [
                        Text("Icone/Nome")    
                    ],
                    alignment=MainAxisAlignment.CENTER,
                    ),
                    alignment=ft.alignment.center,
                    border=border.only(bottom = border.BorderSide(2, colors.BLACK26), right = border.BorderSide(2, colors.BLACK26)),
                    width=300,
                    margin=0
                ),
                Container(
                    Row(
                        [
                            Text(value="Valor em dolar", text_align=ft.TextAlign.CENTER, )      
                        ],
                        alignment=MainAxisAlignment.CENTER,
                    ),
                    alignment=ft.alignment.center,
                    border=border.only(bottom = border.BorderSide(2, colors.BLACK26)),
                    expand=1
                ),
                Container(
                    Row(
                        [
                            Text(value="Valor em real", text_align=ft.TextAlign.CENTER,)      
                        ],
                        alignment=MainAxisAlignment.CENTER,
                    ),
                    alignment=ft.alignment.center,
                    border=border.only(bottom = border.BorderSide(2, colors.BLACK26), left= border.BorderSide(2, colors.BLACK26)),
                    expand=1
                ),
                Container(
                    IconButton(
                            icons.REFRESH_OUTLINED,
                            tooltip="Delete",
                            icon_color=colors.AMBER,
                            on_click = buttonUpdate
                            ),
                    alignment=ft.alignment.center_right,
                    border=border.only(bottom = border.BorderSide(2, colors.BLACK26), left = border.BorderSide(2, colors.BLACK26)),
                    width=50,
                )
            ],
            spacing=0
        ),
        margin=0,
        height=50
    )
    
    page.add(
        Column(
            [
               Row(
                   [
                       lableCadastro
                   ],
                   alignment=MainAxisAlignment.START,
               ),
               tickerCadastro,
               Container(
                   Column(
                       [
                           ticker_header,
                           ticker_space,
                       ],
                       alignment=MainAxisAlignment.CENTER,
                       spacing=0
                    ),
                    alignment=ft.alignment.center,
                    bgcolor=colors.BLACK12,
                    border=ft.border.all(2, colors.BLACK26),
                    margin=0,
               )
            ],
            alignment=MainAxisAlignment.START,
        )
    )

ft.app(target=main)