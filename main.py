# --- 1. I TUOI DATI TELEGRAM IN CHIARO (Sostituisci i testi tra virgolette) ---

import time
import requests
import re
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# --- I TUOI DATI TELEGRAM (Metti i tuoi codici veri qui tra le virgolette) ---
BOT_TOKEN = os.environ['TELEGRAM_TOKEN']
CHAT_ID = os.environ['TELEGRAM_ID']

def invia_notifica(testo):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": testo, "parse_mode": "HTML"}
    try:
        r = requests.post(url, json=payload, timeout=10)
        print(f"📡 Invio Telegram: {r.status_code}")
    except Exception as e:
        print(f"❌ Errore Telegram: {e}")

def monitor_mase():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        print("🔍 Apertura pagina MASE...")
        driver.get("https://www.bonusveicolielettrici.mase.gov.it/veicolielettriciBeneficiario/#/plafond")
        time.sleep(15)
        
        elementi = driver.find_elements(By.TAG_NAME, "p") + driver.find_elements(By.TAG_NAME, "div")
        testo_trovato = ""
        for el in elementi:
            if "residuo" in el.text.lower():
                testo_trovato = el.text
                break
        
        if not testo_trovato:
            print("⚠️ Parola 'residuo' non trovata.")
            return
        
        parte_finale = testo_trovato.lower().split("residuo")[1]
        numeri = re.findall(r'\d+', parte_finale.replace('.', '').replace(',', ''))
        
        if numeri:
            valore = float(numeri[0])
            print(f"💰 Valore attuale: {valore} €")

            if valore >= 10000:
                print("🚨 SOGLIA SUPERATA! Invio allarme vero...")
                # Qui ora è impostato per mandarti la cifra esatta!
                messaggio = f"🚨 <b>FONDI DISPONIBILI!</b> 🚨\n\nIl residuo è salito a: <b>{valore} €</b>\n\nCorri a prenotare la Dacia!\n👉 <a href='https://www.bonusveicolielettrici.mase.gov.it'>CLICCA QUI PER IL MASE</a>"
                invia_notifica(messaggio)
            else:
                print("Fondi ancora sotto la soglia. Aspetto...")

    except Exception as e:
        print(f"❌ Errore: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    monitor_mase()
