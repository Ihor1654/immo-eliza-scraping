import threading
import asyncio
import json
import httpx
from bs4 import BeautifulSoup
class RunThread(threading.Thread):
    """
    Class inheritance from threading.Thread and creates thread for coroutine
    :properties:
    coro
    result
    :methods:
    run()
    get_postcode_dict()
    
    """
    def __init__(self, coro):
        self.coro = coro
        self.result = None
        super().__init__()

    def run(self)-> None:
        """
            Method run the coroutine
        """
        self.result = asyncio.run(self.coro)

class LinkCreator():
    """
    Class that creates a dictionary with all postcodes of Belgium as keys and lists, which contain from 0 to 20 house links, as values.    
    :properties:
    special_char_dict
    headers
    postcode_dict
    link_dict
    failed_links_list
    final_postcode_dict
    timeout
    semaphore
    :methods:
    run_as()
    get_postcode_dict()
    get_link_dict()
    get_houselinks_for_pcode()
    if_link_is_goed()
    check_all_links()
    create_final_dict()
    to_json_file()
    """
    def __init__(self) -> None:
        self.special_char_dict = { 
                    'é':'e',
                    'è':'e',
                    "ê":'e',
                    'ë':'e',
                    'à':'a',
                    'â':'a',
                    'ù':'u',
                    'û':'u',
                    'ü':'u',
                    'î':'i',
                    'ï':'i',
                    'ô':'o',
                    'ç':'c',
                    ' ':'-',
                    'saint':'st',
                    'sint':'st'
                    }
        self.headers = {"User-Agent":'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:130.0) Gecko/20100101 Firefox/130.0'}
        self.postcode_dict = {}
        self.link_dict={}
        self.failed_links_list = []
        self.final_postcode_dict = {}
        self.timeout = httpx.Timeout(50.0)
        self.semaphore = asyncio.Semaphore(10) 

    def run_as(self,coro)->None:
        """
            Method checks if there is a running loop if it so, creates and run thread with coroutine, otherwise run corutine in a loop
            :param: coro, coroutien function
        """
        try:
            global_loop = asyncio.get_running_loop()
        except  RuntimeError:
            global_loop = None
        if global_loop and global_loop.is_running():
            thread = RunThread(coro)
            thread.start()
            thread.join()
            return thread.result
        else:
            print('Starting new event loop')
            return asyncio.run(coro)

    def get_postcode_dict(self):
        """
        Method that creates a dictionary with all postcodes of Belgium as keys and name of area as the value, and cleans up the city name by removing spaces and non-ASCII characters.
        Method creates this dictionary from a postal_codes.json file containing data for all regions of Belgium.
        :param: None
        :return: None
        """
        with open('data/postal-codes.json','r') as file:
            dictinary  = json.load(file)
            for i in dictinary:
                if i['mun_name_nl']:
                    self.postcode_dict[i['postcode']] = i['mun_name_nl'].lower()
                    for char in self.special_char_dict.keys():
                        self.postcode_dict[i['postcode']] = self.postcode_dict[i['postcode']].replace(char,self.special_char_dict[char])  
                elif i['mun_name_de']:
                    self.postcode_dict[i['postcode']] = i['mun_name_de'].lower()
                    for char in self.special_char_dict.keys():
                        self.postcode_dict[i['postcode']] = self.postcode_dict[i['postcode']].replace(char,self.special_char_dict[char])    
                elif i['mun_name_fr']:
                    self.postcode_dict[i['postcode']] = i['mun_name_fr'].lower()
                    for char in self.special_char_dict.keys():
                        self.postcode_dict[i['postcode']] = self.postcode_dict[i['postcode']].replace(char,self.special_char_dict[char])  

    def get_link_dict(self):
        """
        Method that creates a dictionary with all postcodes of Belgium as keys and a search result link from Immoweb for each postcode as the value.
        :param: None
        :return: dict link_dict the resulting dictionary
        """
        for key in self.postcode_dict.keys():
            self.link_dict[key] = f'https://www.immoweb.be/en/search/house-and-apartment/for-sale/{self.postcode_dict[key]}/{key}?countries=BE&page=1&orderBy=relevance'
        return self.link_dict
    
    def get_houselinks_for_pcode(self,content):
        """
            Method that scrapes all house links from a search result link on Immoweb for a specific postcode.
            :params: str content, The content of the response to a request for a search result link.
            :return: list link_list, contains from 0 to 20 house links.
        """
        link_list= []
        try:
            soup = BeautifulSoup(content,'html.parser')
            for elem in soup.find_all('a',attrs= {"class":"card__title-link"}):
                if elem.get('href').find('new-real-estate-project-apartments') == -1 and elem.get('href').find('new-real-estate-project-houses') == -1 :
                    link_list.append(elem.get('href'))

        except Exception as e:
            print(e)
        if len(link_list) <= 30 :
            return []
        elif len(link_list) ==60:
            return(link_list[:15])
        elif len(link_list) >=40:
            return link_list[:10]
        else:
            return link_list[:-30]
    
    async def if_link_is_goed(self,link, session, key):
        """
        Method coroutine that makes a request to Immoweb, checks if the search link is valid, and if so, adds the result of get_houselinks_for_pcode to the final_postcode_dict and returns True, otherwise returns False and adds link to failed_links_list.
        :param: str link, link for specific post code
        :param: AsyncClient, instance of web client 
        :param: str key, postcode as a string
        :return: bool, True if link is valid, otherwise False.
        """
        async with self.semaphore:
            while True:
                try:
                    resp = await session.get(link, headers=self.headers, timeout=self.timeout)
                    if resp.status_code == 200:
                        #print(f"Success for {link}")
                        self.final_postcode_dict[key] = self.get_houselinks_for_pcode(resp.content)
                        return True
                    else:
                        #print(f"Failed with status code {resp.status_code} for {link}")
                        self.failed_links_list.append(link)
                        return False
                except httpx.TimeoutException:
                    print(f"Request timed out for {link}")
                 
    async def check_all_links(self):
        """
        Method coroutine that runs the asynchronous if_link_is_good coroutines and returns a list of booleans for each coroutine.
        :return: list resp, list that contain bool for all links in link_dict
        """
        async with httpx.AsyncClient() as session:
            tasks = [asyncio.create_task(self.if_link_is_goed(link,session,key)) for key,link in self.link_dict.items()]
            resp = await asyncio.gather(*tasks)
            return resp
        
    def create_final_dict(self):
        """
        Method that runs all the necessary steps to create the final_postcode_dict.
        :param: None
        :return: None 
        """
        self.get_postcode_dict()
        self.get_link_dict()
        res = self.run_as(self.check_all_links())
        #print(res.count(True))
        #print(res.count(False))
    
    def to_json_file(self, filepath : str = 'data/links/houselinks_for_postcode.json')-> None:
        """
            Method creates json file with filepath name 
            :param: str filepath, the name of file; houselinks_for_postcode.json by default
            :return: None
        """
        with open(filepath,mode='w',encoding='utf8') as write_file:
            json.dump(self.final_postcode_dict,write_file,ensure_ascii=False)