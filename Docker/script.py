import argparse
import base64
import os
import qrcode
import sys
import time
from io import BytesIO
from multiprocessing import Process
from numpy import array
from PIL import Image
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyzbar.pyzbar import decode


def print_with_animation(interval):
    animation = ['⣾', '⣷', '⣯', '⣟', '⡿', '⢿', '⣻', '⣽']
    index = 0
    while True:
        print('\033[K', end=' ')
        print(f"\033[96m{animation[index]}\033[0m", end='\r')
        time.sleep(interval)
        index = (index + 1) % len(animation)


def print_progress_bar(completed, total, length=10):
    progress = int(length * completed / total)
    bar = '■' * progress + '□' * (length - progress)
    sys.stdout.write(f'\r[{bar}]')
    sys.stdout.flush()


def wait_for_element(driver, by, value, max_attempts=10, sleep_interval=5):
    attempts = 0
    animation_interval = 0.75
    animation_process = Process(
        target=print_with_animation, args=(animation_interval,))
    animation_process.start()

    try:
        while attempts < max_attempts:
            try:
                element = WebDriverWait(driver, sleep_interval).until(
                    EC.presence_of_element_located((by, value))
                )
                return element
            except Exception:
                time.sleep(sleep_interval)
                attempts += 1
        return None
    finally:
        animation_process.terminate()
        animation_process.join()


def render_qr_code(data):
    if not hasattr(Image, 'Resampling'):
        Image.Resampling = Image

    qr = qrcode.QRCode(
        version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=1, border=1)
    qr.add_data(data)
    qr.make(fit=True)
    image = qr.make_image(fill_color=(0, 0, 0), back_color=(255, 255, 255))
    image_array = array(image.getdata())

    width = image.size[0]
    height = image.size[1]

    offset = 0
    while image_array[offset * width + offset][0] == 255:
        offset += 1

    scale = 1
    while image_array[(offset + scale) * width + (offset + scale)][0] == 0:
        scale += 1

    image = image.resize((width // scale, height // scale),
                         Image.Resampling.NEAREST)
    image_array = array(image.getdata())
    width = image.size[0]
    height = image.size[1]

    for i in range(height):
        for j in range(width):
            if image_array[i * width + j][0] < 128:
                print('██', end='', file=sys.stdout)
            else:
                print('  ', end='', file=sys.stdout)
        sys.stdout.flush()
        print(file=sys.stdout)


def send_whatsapp_message(page, phone_number, message):
    page.get(f"https://web.whatsapp.com/send?phone={phone_number}")

    message_box = wait_for_element(
        page, By.CSS_SELECTOR, 'div[aria-label="Digite uma mensagem"][contenteditable="true"]', max_attempts=10, sleep_interval=6)

    if message_box:
        attempts = 0

        while attempts < 10:
            aria_label = message_box.get_attribute('aria-placeholder')
            if aria_label and "Digite uma mensagem" in aria_label:
                page.execute_script("arguments[0].focus();", message_box)
                print("Preparando envio...")
                print_progress_bar(0, 10)
                time.sleep(2)

                for i, line in enumerate(message.split('\n')):
                    message_box.send_keys(line)
                    message_box.send_keys(Keys.SHIFT, Keys.RETURN)
                    print_progress_bar(i + 1, len(message.split('\n')))
                    time.sleep(1)

                # os.system('clear')
                sys.stdout.flush()

                while True:
                    time.sleep(2)
                    current_text = message_box.text
                    if current_text.strip() == message.strip():
                        send_button = wait_for_element(
                            page, By.CSS_SELECTOR, 'span[data-icon="send"]')
                        send_button.click()
                        WebDriverWait(page, 10).until(
                            lambda d: message_box.text == "")
                        time.sleep(10)
                        break

                print(f"\nMensagem enviada para {phone_number}.")
                return

            time.sleep(2)
            attempts += 1
            print("\nFalha ao localizar a caixa de mensagem correta.")
    else:
        print("Falha ao localizar a caixa de mensagem.")


def main():
    parser = argparse.ArgumentParser(
        description="Envie mensagens pelo WhatsApp Web através do terminal.")
    parser.add_argument('phone_number', type=str,
                        help='Número de telefone do destinatário (com código do país).')
    parser.add_argument('--message', type=str, help='Mensagem a ser enviada.')
    parser.add_argument(
        '--file', type=str, help='Caminho para o arquivo de texto contendo a mensagem.')

    args = parser.parse_args()

    message = args.message
    if args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            message = f.read()

    if not message:
        print("Erro: nenhuma mensagem fornecida.")
        exit(1)

    user_data_dir = './User_Data'

    if not os.path.exists(user_data_dir):
        os.makedirs(user_data_dir)

    display = Display(visible=0, size=(1280, 720))
    display.start()

    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f"--user-data-dir={user_data_dir}")

    service = Service('/usr/bin/chromedriver')
    driver = webdriver.Chrome(service=service, options=options)
    driver.get('https://web.whatsapp.com')

    qr_element = wait_for_element(driver, By.TAG_NAME, 'canvas')

    if qr_element:
        qr_code_base64 = driver.execute_script(
            "return arguments[0].toDataURL('image/png').substring(22);", qr_element)
        qr_code_image = Image.open(BytesIO(base64.b64decode(qr_code_base64)))
        qr_code_data = decode(qr_code_image)

        if qr_code_data:
            qr_code_content = qr_code_data[0].data.decode('utf-8')
            render_qr_code(qr_code_content)
        else:
            print("QR Code não encontrado.")
            driver.quit()
            exit()

        if not wait_for_element(driver, By.CSS_SELECTOR, 'span[data-icon="chats-filled"]', max_attempts=10, sleep_interval=5):
            print("Falha ao autenticar no WhatsApp Web.")
            driver.quit()
            exit()

        print("Sessão restaurada com sucesso.")
    else:
        if wait_for_element(driver, By.CSS_SELECTOR, 'span[data-icon="chats-filled"]'):
            print("Sessão restaurada com sucesso.")
        else:
            print("Falha ao carregar o QR code.")
            driver.quit()
            display.stop()
            exit()

    send_whatsapp_message(driver, args.phone_number, message)

    driver.quit()
    display.stop()


if __name__ == '__main__':
    main()
