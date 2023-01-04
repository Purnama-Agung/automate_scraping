import hashlib
import json
import math
import random
import re
import time
import os
import subprocess as sub
import requests
from datetime import datetime

from src.html_parser import HtmlParser
from src.browser import get_browser_chrome
from lib.logger import Logger
from lib.helper import create_path
from src.proxies import get_proxy

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from pyvirtualdisplay import Display


class Eperolehan_catalogue:
    def __init__(self):
        self.logger = Logger(name=self.__class__.__name__)
        self.url = "https://www.eperolehan.gov.my/e-catalogue"
        self.base_path = '/Path/Dir/{}'.format(datetime.now().strftime('%Y%m%d'))
        self.parser = HtmlParser()
        self.browser = None
        self.display = None
        self.category = None
        self.jenama = None

    def get_index(self, cat=None, jenama=None, start_page=None, end_page=None):
        url = self.url
        status = True
        while status:
            try:
                self.display = Display(visible=False, size=(1366, 768))
                self.display.start()
                category = cat
                sub_category = jenama

                self.browser = get_browser_chrome(proxy=True, files='proxy_cloud.json')
                self.browser.get(url)
                WebDriverWait(self.browser, 30).until(EC.invisibility_of_element_located(
                    (By.CLASS_NAME, 'div.ui-panel.ui-widget.ui-widget-content.ui-corner-all')))

                # CLICK CATEGORY
                time.sleep(random.uniform(0.5, 0.9))
                cat_terperinci = self.browser.find_elements(By.CSS_SELECTOR, 'tr.ui-datagrid-row td.ui-datagrid-column a')[int(category)]
                category_name = self.browser.find_elements(By.CSS_SELECTOR, 'tr.ui-datagrid-row td.ui-datagrid-column')[int(category)].find_elements(By.CSS_SELECTOR, 'tr td')[0].text.strip()
                self.category = re.sub('\W+', '_', category_name).upper()
                self.logger.log(f'systems start from index - click catalagoue {self.category}')
                cat_terperinci.click()
                time.sleep(6)

                # CLICK JENAMA
                WebDriverWait(self.browser, 30).until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'table > tbody > tr:nth-child(3) > td > span > table > tbody')))
                self.browser.find_element(By.CSS_SELECTOR, '#_publicCatalogue_WAR_NGePportlet_\:form\:catalogueTabId\:j_idt38 > div.ui-selectonemenu-trigger.ui-state-default.ui-corner-right').click()
                time.sleep(0.5)
                sub_jenama = self.browser.find_elements(By.CSS_SELECTOR, '#_publicCatalogue_WAR_NGePportlet_\:form\:catalogueTabId\:j_idt38_panel > div > ul > li')
                if int(sub_category) == 0:
                    self.jenama = 'all'.upper()
                elif int(sub_category) > 0 & int(sub_category) <= int(len(sub_jenama)):
                    sub_category_name = sub_jenama[int(sub_category)].text.strip()
                    self.jenama = re.sub('\W+', '_', sub_category_name).upper()
                    self.logger.log(f'INDEX: [{self.category}] choice jenama {self.jenama}')
                    sub_jenama[int(sub_category)].click()
                else:
                    self.logger.log(f'INDEX: [{self.category}] only have {int(len(sub_jenama))} jenama | Systems Exit')
                    status = False
                    raise

                # CLICK CARI
                time.sleep(random.uniform(0.5, 0.9))
                self.browser.find_elements(By.CSS_SELECTOR, '.ui-button.ui-widget.ui-state-default.ui-corner-all.ui-button-text-only')[-1].click()

                time.sleep(6)
                try:
                    items = self.browser.find_element(By.XPATH, '//*[@id="_publicCatalogue_WAR_NGePportlet_:form:catalogueTabId:resultpl"]/table/tbody/tr/td[2]/label')
                    total_items = re.sub("\s[A-z]tem.*", "", items.text.strip())
                    total_pages = int(math.ceil(int(total_items) / 9))
                except:
                    total_pages = '1'

                self.logger.log(f"INDEX: [{self.category}/{self.jenama}] Total Page {total_pages}")

                if not start_page:
                    page_start = 1
                else:
                    page_start = int(start_page)

                if not end_page:
                    page_end = int(total_pages)
                else:
                    if int(end_page) >= int(total_pages):
                        page_end = int(total_pages)
                    else:
                        page_end = int(end_page)

                self.logger.log(f"INDEX: [{self.category}/{self.jenama}] Start from page {page_start} to {page_end}")
                for index_page in range(int(page_start), int(page_end) + 1):
                    self.logger.log(f'INDEX: [{self.category}/{self.jenama}] Loop page {index_page}')
                    time.sleep(1)
                    self.get_paging(index_page, page_end)

                    total_details = self.browser.find_elements(By.CSS_SELECTOR, '.ui-datagrid-row .ui-datagrid-column a')
                    path_file = f"{self.base_path}/{self.category}/{self.jenama}/page_{index_page}"

                    out = "find {} -type f | wc -l".format(path_file)
                    total_file = sub.check_output(out, stderr=sub.STDOUT, shell=True, close_fds=True)
                    total_file = str(total_file.decode('utf-8')).strip()
                    if "No such file" in total_file:
                        total_file = re.sub('.*\n(.*)', '\g<1>', total_file).strip()
                    self.logger.log(f"INDEX: [{self.category}/{self.jenama}] total file details {len(total_details)} in page {index_page}")

                    # cek total file and total details
                    if str(int(total_file) - 2) != str(len(total_details)):
                        file_exists = os.path.isfile("{}/{}.html".format(path_file, index_page))
                        if not file_exists:
                            path = create_path(path_file)
                            with open("{}/index_{}.html".format(path, index_page), 'w+') as f:
                                f.write(self.browser.page_source)
                        self.get_details(index_page, path_file, total_details)

                status = False
                self.logger.log(f"INDEX: [{self.category}/{self.jenama}] finish and successfully get data")
            except Exception as e:
                self.logger.log(e)
                raise
            finally:
                self.browser.quit()
                self.display.stop()

    def get_paging(self, index_page, page_end):
        nextPage = True
        while nextPage:
            time.sleep(2)
            if int(page_end) == 1:
                pg = '1'
            else:
                page_actual = self.browser.find_element(By.CSS_SELECTOR,
                              'span.ui-paginator-page.ui-state-default.ui-state-active.ui-corner-all').text
                pg = re.sub(r'[\W]+', '', page_actual).strip()

            self.logger.log("INDEX: [{}/{}] - page actualy {} page loop {}".format(self.category, self.jenama, pg, index_page))
            page_of_lists = self.browser.find_elements(By.CSS_SELECTOR, '.ui-paginator-pages span')
            page_lists = [page_list.text for page_list in page_of_lists]
            if pg != str(index_page):
                page_option = self.browser.find_element(By.CSS_SELECTOR, 'div.ui-paginator.ui-paginator-bottom.ui-widget-header.ui-corner-bottom')
                self.browser.execute_script("arguments[0].scrollIntoView();", page_option)
                time.sleep(1)
                if str(index_page) not in page_lists:
                    time.sleep(3)
                    self.logger.log(f"INDEX: [{self.category}/{self.jenama}] - next page before page {index_page}")
                    page_of_lists[-1].click()
                    time.sleep(2)
                else:
                    self.logger.log(f"INDEX: [{self.category}/{self.jenama}] - click page {index_page}")
                    page_of_lists[page_lists.index(str(index_page))].click()
                    time.sleep(2)
            else:
                self.logger.log("INDEX: [{}/{}] - next page stop".format(self.category, self.jenama))
                nextPage = False

    def get_details(self, index_page, path, total_details):
        try:
            for details in range(0, int(len(total_details))):
                WebDriverWait(self.browser, 30).until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, '#_publicCatalogue_WAR_NGePportlet_\:form\:catalogueTabId\:resultpl > table > tbody > tr > td:nth-child(2)')))
                time.sleep(2)
                detail = self.browser.find_elements(By.CSS_SELECTOR, ".ui-datagrid-row .ui-datagrid-column div a")[details]
                detail_name = re.sub('\W+', '_', detail.text.strip())
                detail_name_hash = f'{int(details) + 1}_{hashlib.md5(detail_name.encode("utf-8")).hexdigest()}'
                file_exists = os.path.isfile("{}/{}.html".format(path, detail_name_hash))
                if not file_exists:
                    self.logger.log(f'DETAILS: [{self.category}/{self.jenama}] new file')
                    detail.click()
                    WebDriverWait(self.browser, 30).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, '#_publicCatalogue_WAR_NGePportlet_\:form\:publicCatalogDetPageId > table')))
                    time.sleep(0.5)
                    html_details = self.browser.page_source
                    with open("{}/{}.html".format(path, str(detail_name_hash)), 'w+') as f:
                        f.write(html_details)

                    # CREATE JSON FILE
                    detail_parse = self.parse_details(html_details)
                    img_path = create_path(f'{path}/img')
                    img_url = detail_parse['img_url']
                    if 'http' in img_url:
                        self.img_downloader(img_url, detail_name_hash, img_path)
                        self.logger.log(
                            f'DETAILS: [{self.category}/{self.jenama}] saved image {detail_name_hash}.jpg')
                    else:
                        self.logger.log(
                            f'DETAILS: [{self.category}/{self.jenama}] no image')
                        pass
                    detail_parse['img_path'] = '{}/{}.jpg'.format(img_path, detail_name_hash)

                    json_path = f'{path}/index_{str(index_page)}.json'
                    json_exists = os.path.isfile(json_path)
                    if not json_exists:
                        with open(json_path, 'w+') as create_new:
                            create_new.write(json.dumps([detail_parse]))
                        self.logger.log(
                            f'DETAILS : {self.category}/{self.jenama} create json file index_{index_page}.json')
                    else:
                        with open(json_path, 'r') as read_only:
                            all_data = json.loads(read_only.read())
                            read_only.close()

                        with open(json_path, 'w') as append_new:
                            data_append = all_data + [detail_parse]
                            append_new.write(json.dumps(data_append))
                            append_new.close()
                        self.logger.log(
                            f'DETAILS: [{self.category}/{self.jenama}] append json to file index_{index_page}.json')

                    log_path = create_path(f"{self.base_path}/{self.category}/{self.jenama}/")
                    with open(f"{log_path}/filename_{self.jenama}", 'a') as f2:
                        with open(f"{log_path}/filename_{self.jenama}", 'r') as f1:
                            data = f1.readlines()
                            if detail_name_hash not in data:
                                f2.write(f'{self.category}/{self.jenama}/page_{index_page}/{detail_name_hash} | {detail_name.encode("utf-8").decode("utf-8")}')
                                self.logger.log(
                                    f'DETAILS: [{self.category}/{self.jenama}] saved {detail_name_hash}.html')
                            else:
                                self.logger.log(
                                    f'DETAILS: [{self.category}/{self.jenama}] name log {detail_name_hash} exists')
                    kembali = self.browser.find_element(By.CSS_SELECTOR, '#_publicCatalogue_WAR_NGePportlet_\:form\:j_idt8')
                    self.browser.execute_script("arguments[0].scrollIntoView();", kembali)
                    kembali.click()
                    time.sleep(0.5)
                else:
                    self.logger.log(
                        f'DETAILS: [{self.category}/{self.jenama}] exists file {detail_name_hash}.html')
        except:
            raise

    def parse_details(self, html):
        try:
            temp = dict()
            table1 = self.parser.bs4_parser(html, '.liferay-faces-bridge-body table[style="width: 100%;"]')[0]
            items_title = table1.select('tr')[0].select('td')
            if len(items_title) > 2:
                item_title = items_title[2].text.strip()
                img = items_title[1].text.strip()
                temp['img_url'] = img
            else:
                item_title = items_title[1].text.strip()
                img = items_title[0].select('img')[0].get('src')
                temp['img_url'] = f'https://www.eperolehan.gov.my{img}'
            temp['item_title'] = item_title

            table_rows = table1.find_all('tr')
            data_null = []
            if len(table_rows) == 16:
                kod_item = table1.select('tr')[1].select('td')[0].select('span')[1].text.strip()
                harga_item = table1.select('tr')[3].select('td')[0].select('span')[0].text.strip()
                detail_item_key = table1.select('tr')[4].find_all('td')
                detail_item_val = table1.select('tr')[5].find_all('td')
                detail_item_key_1 = table1.select('tr')[6].find_all('td')
                detail_item_val_1 = table1.select('tr')[7].find_all('td')
                maklumat_tambahan_key = table1.select('tr')[8].find_all('td')[0].text.strip()
                maklumat_tambahan_key = re.sub('\W+$', '', maklumat_tambahan_key).replace(' ', '_').lower()
                maklumat_tambahan_val = table1.select('tr')[8].find_all('td')[1].text.strip()

                maklumat_pembekal = table1.select('tr')[9]
                table_maklumat_pembekal_title = re.sub('\W+', '_', maklumat_pembekal.select('.ui-panel-title')[0].text.strip()).lower()
                table_maklumat = maklumat_pembekal.select('table')[0]
                for k, v in enumerate(table_maklumat.find_all('tr')):
                    rows = v.find_all('td')
                    key = '{}'.format(re.sub('\W+', '_', rows[0].text.strip()).lower())
                    val = rows[1].text.strip()
                    if key == '':
                        data_null.append(val)
                    else:
                        temp['{}_{}'.format(table_maklumat_pembekal_title, key)] = val
            else:
                kod_item = table1.select('tr')[2].select('td')[0].select('span')[1].text.strip()
                harga_item = table1.select('tr')[4].select('td')[0].select('span')[0].text.strip()
                detail_item_key = table1.select('tr')[5].find_all('td')
                detail_item_val = table1.select('tr')[6].find_all('td')
                detail_item_key_1 = table1.select('tr')[7].find_all('td')
                detail_item_val_1 = table1.select('tr')[8].find_all('td')
                maklumat_tambahan_key = table1.select('tr')[9].find_all('td')[0].text.strip()
                maklumat_tambahan_key = re.sub('\W+$', '', maklumat_tambahan_key).replace(' ', '_').lower()
                maklumat_tambahan_val = table1.select('tr')[9].find_all('td')[1].text.strip()

                maklumat_pembekal = table1.select('tr')[10]
                table_maklumat_pembekal_title = re.sub('\W+', '_', maklumat_pembekal.select('.ui-panel-title')[
                    0].text.strip()).lower()
                table_maklumat = maklumat_pembekal.select('table')[0]
                for k, v in enumerate(table_maklumat.find_all('tr')):
                    rows = v.find_all('td')
                    key = '{}'.format(re.sub('\W+', '_', rows[0].text.strip()).lower())
                    val = rows[1].text.strip()
                    if key == '':
                        data_null.append(val)
                    else:
                        temp['{}_{}'.format(table_maklumat_pembekal_title, key)] = val

            for detail_item_keys, detail_item_vals in zip(detail_item_key, detail_item_val):
                detail_key = re.sub('\W+$', '', detail_item_keys.text.strip())
                detail_key = re.sub('\W+', '_', detail_key).lower()
                detail_val = detail_item_vals.text.strip()
                if detail_key or detail_val != '':
                    temp[detail_key] = detail_val

            for detail_item_keys_1, detail_item_vals_1 in zip(detail_item_key_1, detail_item_val_1):
                detail_key_1 = re.sub('\W+$', '', detail_item_keys_1.text.strip())
                detail_key_1 = re.sub('\W+', '_', detail_key_1).lower()
                detail_val_1 = detail_item_vals_1.text.strip()
                if detail_key_1 or detail_val_1 != '':
                    temp[detail_key_1] = detail_val_1

            temp['kod_item'] = kod_item
            temp['harga_item'] = harga_item
            temp[maklumat_tambahan_key] = maklumat_tambahan_val
            alamat_syarikat = temp[f'{table_maklumat_pembekal_title}_alamat_syarikat']
            temp[f'{table_maklumat_pembekal_title}_alamat_syarikat'] = alamat_syarikat.join(data_null)
        except:
            raise
        return temp

    def img_downloader(self, img_url, hash, path):
        try:
            proxy = None
            item = get_proxy(files='proxy_cloud.json')
            address = item['address']
            port = int(item['port'])

            if address and port:
                proxy = {'http': '{}:{}'.format(address, port), 'https': '{}:{}'.format(address, port),
                         'ssl': '{}:{}'.format(address, port), 'socks': '{}:{}'.format(address, port),
                         'ftp': '{}:{}'.format(address, port)}

            session = requests.get(img_url, proxies=proxy)
            if session.status_code == 200:
                with open(f'{path}/{hash}.jpg', 'wb') as f:
                    f.write(session.content)
        except:
            raise
