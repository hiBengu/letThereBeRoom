import configparser
from bs4 import BeautifulSoup
import requests
from googletrans import Translator
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes


class TelegramBot():
    def __init__(self):
        print('Telegram Bot')
        self.app = ApplicationBuilder().token("YOUR TOKEN HERE").build()

    async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text(f'Hello {update.effective_user.first_name}')

    def run(self):
        print('Telegram Run')

        self.app.add_handler(CommandHandler("hello", self.hello))
        self.app.run_polling()


class FindRoom():
    def __init__(self, url, target_lang):
        print("Find room init")
        html_text = requests.get(url).text
        self.soup = BeautifulSoup(html_text, 'html.parser')
        self.target_lang = target_lang
        self.translator = Translator()

    def checkIfSentBefore(self, id):
        print('check if seen before')
        return False

    def translateDescription(self, offer_url):
        print('extract and translate description')
        desc_text = ""

        offer_text = requests.get(offer_url).text
        desc_soup = BeautifulSoup(offer_text, 'html.parser')
        desc = desc_soup.find(id='ad_description_text')
        for text in desc.find_all('p'):
            desc_text += text.find(text=True)

        return self.translator.translate(desc_text, src='de').text

    def run(self):
        print("Find room main")
        for offer in self.soup.find_all('div', id=lambda x: x and x.startswith('liste-details-ad-')):
            offer_link = "https://www.wg-gesucht.de" + \
                offer.find('a').get('href')
            offer_id = offer.get('data-id')

            if(offer_id == None or self.checkIfSentBefore(offer_id)):
                continue

            print(offer_link)
            translatedDesc = self.translateDescription(offer_link)
            print(translatedDesc)
            break


class LetThereBeRoom():
    def __init__(self):
        print("Inside Init")
        config = configparser.ConfigParser(interpolation=None)
        config.read('config.ini')

        self.url = config['WEB']['url']
        self.target_lang = config['Translate']['target']

        self.findRoom = FindRoom(self.url, self.target_lang)
        self.telegramBot = TelegramBot()

    def checkNewPostings(self):
        print("Check New Postings")
        self.findRoom.run()

    def translateDesc(self):
        print('Translate Description')

    def sendTelegramRequest(self):
        print("SendTelegramRequest")
        self.telegramBot.run()

    def run(self):
        print("Start Main Process")
        self.checkNewPostings()
        self.sendTelegramRequest()


if __name__ == "__main__":
    letThereBeRoom = LetThereBeRoom()
    letThereBeRoom.run()
