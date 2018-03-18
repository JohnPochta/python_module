from urllib3 import *
import certifi
import xml.etree.cElementTree as ET
from xml.dom import minidom
import re


class Bug:
    def __init__(self, input_file, output_file, depth):
        self.depth = depth
        self.input_file = input_file
        self.output_file = output_file
        self.https = PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where(),timeout=10.0)  # якась хуйня шоб можна було робити хітровиєбані рекуести)
    def xml_input_reader(self, path_to_file):  # чєтаєм входной фаіл
        output = []
        mydoc = minidom.parse(path_to_file)
        urls = mydoc.getElementsByTagName('url')
        for elem in urls:
            output.append(elem.childNodes[0].nodeValue)
        return output

    def page_reader(self, url):
        try:
            page = self.https.request('GET', url).data.decode('utf-8')
            # кароче собираю їбать явні емаіли
            emails = set(re.findall('([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)', str(page)))
            # кароче собираю їбать неявні емаіли і об'єдную множини
            emails = emails | (
            set(re.findall('([a-zA-Z0-9_.+-]+\s?(?:\(at\)|\[at\])\s?[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)', str(page))))
            # сабираю ссилки
            set_of_urls_on_page = set(
                re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', str(page)))
        except:
            emails = set()
            set_of_urls_on_page = set()
        return [emails, set_of_urls_on_page]

    @property
    def scrub_emails(self):
        emails = set()
        start_urls_dataset = self.xml_input_reader(self.input_file)  # прочитали входной фаіл
        visited_urls_dataset = set()  # тут будуть записуватись сторінки на яких ми вже були, шоб не лазити туди по 100 раз
        temporary_urls_dataset = set()
        temporary_urls_dataset |= set(
            start_urls_dataset)  # тут будуть записуватись сторінки на які ми збираємось сходити в наступному ходу йопта=)
        temp = set()
        # розберешся кароч)))0
        for i in range(self.depth):
            temp = set()
            for url in temporary_urls_dataset:
                emails = emails | self.page_reader(url)[0]
                visited_urls_dataset.add(url)
                temp |= (self.page_reader(url)[1] - visited_urls_dataset) - set(temporary_urls_dataset)
            temporary_urls_dataset = set()
            temporary_urls_dataset |= temp  # це опєрация об'єднання. Я юзаю її, а не =, того шо якшо юзати =, то присвоїть указатєль на присваюємий обьєкт, а це , сама понімаєш хуйня полічіцо
        # тут ми пишем xml-фаіл
        # кароч тут якісь ахуєвші свєрхтєхнології: https://stackoverflow.com/questions/3605680/creating-a-simple-xml-file-using-python
        root = ET.Element("root")
        doc = ET.SubElement(root, "doc")
        for email in emails:
            ET.SubElement(doc, "email").text = email
        tree = ET.ElementTree(root)
        tree.write(self.output_file)
