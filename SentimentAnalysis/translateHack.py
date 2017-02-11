#coding=utf-8

import requests
import unicodedata

def translate(text, to_language='en', language='auto'):
    """
    Return the translation using google translate
    you must shortcut the language you define (French = fr, English = en, Spanish = es, etc...)
    if you don't define anything it will detect it or use english by default
    Example:
    print(translate("salut tu vas bien?", "en"))
    > hello you alright?
    :param text: the text to translate
    :param to_language: the language to translate to
    :param language: the language to translate from
    """
    # The
    before_trans = 'class="t0">'
    link = 'http://translate.google.com/m?hl={}&sl={}&q={}'.format(
        to_language, language, text.replace(' ', "+"))
    response = requests.get(link)
    html_code = response.text
    result = html_code[html_code.find(before_trans) + len(before_trans):]
    result = result.split('<')[0]
    return result.encode('utf-8')


