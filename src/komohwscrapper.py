from bs4 import BeautifulSoup
import json
import requests


class KOMOHWScrapper:
    """
    web scrapper for Republic of Korea Ministry of Health and Welfare
    @http://ncv.kdca.go.kr/
    """

    BASE_URL = "http://ncv.kdca.go.kr/content/"
    MY_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) " \
                    "Chrome/88.0.4324.192 Safari/537.36 "

    VACCINATION_MENU = "0201"

    # common headers
    HEADERS = {
        "USER-AGENT": MY_USER_AGENT
    }

    @staticmethod
    def __get_menu_params(menu):
        return {
            "menu_cd": menu
        }

    @staticmethod
    def __get_class_attr(class_name):
        return {
            'class': class_name
        }

    @staticmethod
    def __get_id_attr(class_name):
        return {
            'id': class_name
        }

    def __parse_table_header(self, tr_item):
        return list(map(lambda x: x.get_text(), tr_item))

    def __parse_table_item(self, tr_item):
        title = tr_item.find('th', attrs={'scope':'row'}).get_text()
        items = list(map(lambda x: x.get_text(), tr_item.find_all('td', attrs={'class': 'd_num'})))
        items.extend(
            list(map(lambda x: x.get_text(), tr_item.find_all('td', attrs={'class': 'ta_r'})))
        )
        return {
            "title": title,
            "data": items
        }

    def __parse_content_tables(self, content_tables):
        result = []
        for table in content_tables:
            description = table.find('caption').find('span', attrs=self.__get_class_attr('hdn')).get_text()

            heads = list(map(
                lambda x: self.__parse_table_header(x.find_all('th', attrs={'scope': 'col'})),
                table.find('thead').find_all('tr')
            ))

            items = list(map(
                lambda x: self.__parse_table_item(x),
                table.find('tbody').find_all('tr')
            ))

            result.append({
                "description": description,
                "items": items
            })

        return result

    def get_vaccination_status(self):
        url = f"{self.BASE_URL}/vaccination.html"
        res = requests.get(url, headers=self.HEADERS, params=self.__get_menu_params(self.VACCINATION_MENU))
        soup = BeautifulSoup(res.content, 'html.parser', from_encoding='utf8')
        content_html = soup.find('div', attrs=self.__get_class_attr('content'))

        date = content_html.find('span', attrs=self.__get_class_attr('t_date')).get_text()
        content_titles = list(
            map(lambda x: x.get_text(), content_html.find_all('h4', attrs=self.__get_class_attr('s_title_0'))))
        content_tables = content_html.find_all('div', attrs=self.__get_class_attr('data_table tbl_scrl_mini'))

        contents = self.__parse_content_tables(content_tables)

        return {
            "last_update": date,
            "content_title": content_titles,
            "data": contents
        }


scrapper = KOMOHWScrapper()
scrap_result = scrapper.get_vaccination_status()
print(json.dumps(scrap_result, indent=2, default=str, ensure_ascii=False))
