import os
import time
import requests
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# --- CONFIGURAZIONE VARIABILI (DA GITHUB SECRETS) ---
BOT_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_ID')

def invia_notifica(testo):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": testo, "parse_mode": "HTML"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Errore invio Telegram: {e}")

def monitor_mase():
    # Configurazione Chrome per ambiente Linux (GitHub Actions)
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
        
        # Aspettiamo che la pagina carichi i dati (15 secondi per sicurezza su server remoto)
        time.sleep(15)
        
        # Cerchiamo il testo che contiene il residuo
        elementi = driver.find_elements(By.TAG_NAME, "p") + driver.find_elements(By.TAG_NAME, "div")
        
        testo_trovato = ""
        for el in elementi:
            if "residuo" in el.text.lower():
                testo_trovato = el.text
                break
        
        if not testo_trovato:
            print("⚠️ Parola 'residuo' non trovata. Screenshot salvato.")
            driver.save_screenshot("error_screenshot.png")
            return

        print(f"✅ Testo individuato: {testo_trovato}")
        
        # Estrazione valore numerico dopo la parola 'residuo'
        parte_finale = testo_trovato.lower().split("residuo")[1]
        numeri = re.findall(r'\d+', parte_finale.replace('.', '').replace(',', ''))
        
        if numeri:
            valore = float(numeri[0])
            print(f"💰 Valore estratto: {valore} €")

            if valore >= 1000:
                messaggio = (
                    f"🚨 <b>FONDI DISPONIBILI!</b> 🚨\n\n"
                    f"Il residuo è di: <b>{valore} €</b>\n"
                    f"Vai subito qui: <a href='https://www.bonusveicolielettrici.mase.gov.it'>PORTALE MASE</a>"
                )
                invia_notifica(messaggio)
            else:
                print("Fondi ancora sotto la soglia. Nessun allarme inviato.")

    except Exception as e:
        print(f"❌ Errore durante l'esecuzione: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    monitor_mase()
