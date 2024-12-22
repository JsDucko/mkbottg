import requests
from data.config import CRYPTOBOT_API_KEY

class CryptoBot:
    def __init__(self):
        self.url = 'https://pay.crypt.bot/api/'
        self.token = {'Crypto-Pay-API-Token': CRYPTOBOT_API_KEY}

    def get_rate(self, cryptocurrency: str) -> float:
        response = requests.get(
            f'{self.url}getExchangeRates', headers=self.token)
        currency_data = response.json()['result']
        print(response.json()['result'])

        for rate in currency_data:
            if rate['source'] == cryptocurrency.upper() and rate['target'] == 'RUB':
                print(f"Rate в функции гет рейт: {rate}")
                return float(rate['rate'])
        return 0

    def create_bill(self, cryptocurrency: str, total: int) -> list:
        rate = self.get_rate(cryptocurrency)

        if rate == 0:
            raise ValueError(f"Не удалось найти курс обмена для криптовалюты {cryptocurrency}")

        #print(f"Total: {total}")
        #print(f"Rate в функции крейт билл: {rate}")

        amount = str(total / rate)
        
        #print(f"Amount: {amount}")

        result = list()
        params = {'asset': f'{cryptocurrency}',
                'amount': amount}
        response = requests.get(
            f'{self.url}createInvoice', params, headers=self.token)
        result.append(response.json()['result']['invoice_id'])
        result.append(response.json()['result']['pay_url'])
        return result

    # Проверка оплаты счёта Crypto
    def get_bill_status(self, id: str) -> str:
        params = {'invoice_ids': id}
        response = requests.get(
            f'{self.url}getInvoices', params, headers=self.token)
        return response.json()['result']['items'][0]['status']