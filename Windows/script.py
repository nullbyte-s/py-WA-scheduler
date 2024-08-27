#! /usr/bin/env python3

import argparse
import base64
import ctypes
import os
import qrcode
import time
from io import BytesIO
from numpy import array
from PIL import Image
from playwright.sync_api import sync_playwright
from pyzbar.pyzbar import decode
from sys import stdout

LF_FACESIZE = 32
STD_OUTPUT_HANDLE = -11


class COORD(ctypes.Structure):
    _fields_ = [("X", ctypes.c_short), ("Y", ctypes.c_short)]


class CONSOLE_FONT_INFOEX(ctypes.Structure):
    _fields_ = [
        ("cbSize", ctypes.c_ulong),
        ("nFont", ctypes.c_ulong),
        ("dwFontSize", COORD),
        ("FontFamily", ctypes.c_uint),
        ("FontWeight", ctypes.c_uint),
        ("FaceName", ctypes.c_wchar * LF_FACESIZE)
    ]


def get_console_font():
    handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
    font = CONSOLE_FONT_INFOEX()
    font.cbSize = ctypes.sizeof(CONSOLE_FONT_INFOEX)
    ctypes.windll.kernel32.GetCurrentConsoleFontEx(
        handle, False, ctypes.pointer(font))

    font_size = font.dwFontSize.Y

    return font_size


def set_console_font(size):
    handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
    font = CONSOLE_FONT_INFOEX()
    font.cbSize = ctypes.sizeof(CONSOLE_FONT_INFOEX)
    font.nFont = 0
    font.dwFontSize.X = 0
    font.dwFontSize.Y = size
    font.FontFamily = 54
    font.FontWeight = 400
    font.FaceName = "Consolas"
    ctypes.windll.kernel32.SetCurrentConsoleFontEx(
        handle, ctypes.c_long(False), ctypes.pointer(font))


def wait_for_element(page, selector, max_attempts=3, sleep_interval=5):
    attempts = 0
    while attempts < max_attempts:
        try:
            element = page.query_selector(selector)
            if element:
                return element
            else:
                time.sleep(sleep_interval)
                attempts += 1
        except Exception as e:
            print(f"Tentativa {attempts + 1} falhou: {e}")
            time.sleep(sleep_interval)
            attempts += 1
    return None


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
                print('██', end='', file=stdout)
            else:
                print('  ', end='', file=stdout)
        original_font_size = get_console_font()
        set_console_font(10)
        print(file=stdout)
        set_console_font(original_font_size)


def send_whatsapp_message(page, phone_number, message):
    page.goto(f"https://web.whatsapp.com/send?phone={phone_number}")

    message_box = wait_for_element(
        page, 'div[tabindex="10"]', max_attempts=10, sleep_interval=2)

    if message_box:
        attempts = 0
        while attempts < 10:
            aria_label = message_box.get_attribute('aria-placeholder')
            if aria_label and "Digite uma mensagem" in aria_label:
                message_box.click()
                message_box.type(message)
                while True:
                    time.sleep(2)
                    current_text = message_box.text_content().strip()
                    if len(current_text) >= len(message):
                        page.keyboard.press("Enter")
                        time.sleep(5)
                        break
                print(f"Mensagem enviada para {phone_number}.")
                return
            time.sleep(2)
            attempts += 1
            print("Falha ao localizar a caixa de mensagem correta.")
    else:
        print("Falha ao localizar a caixa de mensagem.")


def main():
    parser = argparse.ArgumentParser(
        description="Envie mensagens pelo WhatsApp Web através do terminal.")
    parser.add_argument('phone_number', type=str,
                        help='Número de telefone do destinatário (com código do país).')
    parser.add_argument('message', type=str, help='Mensagem a ser enviada.')

    args = parser.parse_args()

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            'user_data_dir', headless=False)
        page = browser.new_page()
        page.goto('https://web.whatsapp.com')

        if wait_for_element(page, 'span[data-icon="chats-filled"]'):
            print("Sessão restaurada com sucesso.")
        else:
            qr_element = wait_for_element(page, 'canvas')
            if not qr_element:
                print("Falha ao carregar o QR code.")
                browser.close()
                exit()

            qr_code_base64 = qr_element.screenshot()
            qr_code_data = base64.b64decode(qr_code_base64)
            qr_code_image = Image.open(BytesIO(qr_code_base64))
            qr_code_data = decode(qr_code_image)

            if qr_code_data:
                qr_code_content = qr_code_data[0].data.decode('utf-8')
                render_qr_code(qr_code_content)
            else:
                print("QR Code não encontrado.")
                browser.close()
                exit()

            if not wait_for_element(page, 'span[data-icon="chats-filled"]', max_attempts=10, sleep_interval=5):
                print("Falha ao autenticar no WhatsApp Web.")
                browser.close()
                exit()

        send_whatsapp_message(page, args.phone_number, args.message)
        browser.close()


if __name__ == '__main__':
    main()
