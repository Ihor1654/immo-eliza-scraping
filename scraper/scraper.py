from bs4 import BeautifulSoup
import json
from requests import Session
import httpx
import asyncio
from src.link_creator import RunThread




class Scraper():
    """
    
    """






    def __init__(self) -> None:
        self.headers = {"User-Agent":'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:130.0) Gecko/20100101 Firefox/130.0'}
        self.json_path = 'houselinks_for_postcode.json'
        self.timeout = httpx.Timeout(50.0)
        self.semaphore = asyncio.Semaphore(10)
        self.link_dict = {}
        self.houses_raw_data_dict = {}
        self.old_links_counter = 0
        self.problem_with_json_list = []
        self.houses_cleaned_data_list = []

    def upload_data_from_json(self, filepath : str = ''):
        if filepath == '':
            filepath = self.json_path
        with open(filepath,'r') as f:
            self.link_dict = json.load(f)
        return self.link_dict
    
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

    async def get_house_raw_data(self,link,session):
        while True:
            try:
                resp = await session.get(link, headers=self.headers, timeout = self.timeout)
                if resp.status_code == 200:
                    print(f'Collecting data from {link}')
                    soup = BeautifulSoup(resp._content,'html.parser')
                    window_classifier = str(soup.find_all('script', attrs={'type':'text/javascript'})[1])
                    window_classifier = window_classifier.replace('<script type="text/javascript">','').replace('</script>',"").strip().replace('window.classified = ','').strip(';')
                    try:
                        raw_data_dict = json.loads(window_classifier)
                        del raw_data_dict['customers']
                        del raw_data_dict['premiumProjectPage']
                        del raw_data_dict['media']
                    except json.JSONDecodeError as e:
                        print(f'something wrong with Json\n{e}')
                        print(window_classifier)
                        self.problem_with_json_list.append(link)
                        break

                    self.houses_raw_data_dict[link] = raw_data_dict
                    break
                elif resp.status_code == 404:
                    print(f'{link} doesn\'t exist')
                    self.old_links_counter +=1
                    break
                else:
                    print(f"Failed with status code {resp.status_code} for {link}")
            except httpx.TimeoutException:
                print(f'Request time out for {link}')


    async def get_house_raw_data_for_pc(self,key):
        async with self.semaphore:
            async with httpx.AsyncClient() as session:
                tasks = [asyncio.create_task(self.get_house_raw_data(link,session)) for link in self.link_dict[key]]
                resp = await asyncio.gather(*tasks)


    async def get_full_raw_data_set(self):
        tasks = [asyncio.create_task(self.get_house_raw_data_for_pc(key)) for key in self.link_dict.keys()]
        resp = await asyncio.gather(*tasks)
    
    def clean_up_house_data(self,house_raw_dict : dict, link : str):
        my_dict = {'link':f"{link}",}
        if not house_raw_dict["flags"]["isLifeAnnuitySale"]:
            my_dict['property_id'] = house_raw_dict["id"]
            my_dict['locality_name'] = house_raw_dict["property"]["location"]["locality"] 
            my_dict['postal_code'] = house_raw_dict["property"]["location"]["postalCode"]
            my_dict['price'] = house_raw_dict["price"]["mainValue"]
            my_dict['type_of_property'] = house_raw_dict["property"]["type"]
            my_dict['subtype_of_property'] = house_raw_dict["property"]["subtype"]
            my_dict['living_area'] = house_raw_dict["property"]["netHabitableSurface"]
            if house_raw_dict["transaction"]["sale"]["isFurnished"] is None:
                my_dict['furnished'] = None
            elif house_raw_dict["transaction"]["sale"]["isFurnished"] == True:
                my_dict['furnished'] = 1
            elif house_raw_dict["transaction"]["sale"]["isFurnished"] == False:
                my_dict['furnished'] = 0
            if house_raw_dict["property"]["fireplaceExists"]:
                my_dict['open_fire'] = 1
            else:
                my_dict['open_fire'] = 0
            if house_raw_dict["property"]["hasTerrace"] is None:
                my_dict['terrace_surface'] = 'null'
            elif house_raw_dict["property"]["hasTerrace"] == True:
                my_dict['terrace_surface'] = house_raw_dict["property"]["terraceSurface"]
            else:
                print(house_raw_dict["property"]["terraceSurface"])
            if house_raw_dict["property"]["hasGarden"]:
                my_dict['garden'] = house_raw_dict["property"]["gardenSurface"]
            else:
                my_dict["garden"] = 'null'
            try:
                if house_raw_dict["property"]["building"]["facadeCount"] is None:
                    my_dict['facades'] = 0
                else:
                    my_dict['facades'] = house_raw_dict["property"]["building"]["facadeCount"]
            except:
                    my_dict["facades"] = None
            if house_raw_dict["property"]["hasSwimmingPool"] is None or house_raw_dict["property"]["hasSwimmingPool"] == 'null':
                my_dict['swimming_pool'] = 0
            else:
                my_dict['swimming_pool'] = 1
        
            try:
                my_dict['land_area'] = house_raw_dict["property"]["land"]["surface"]
            except:
                #ADD CHECK IF ITS INT
                my_dict['land_area'] = None
            try:
                my_dict['equipped_kitchen'] = house_raw_dict["property"]["kitchen"]["type"]
            except:
                my_dict['equipped_kitchen'] = None
            try:
                my_dict["state_of_building"] = house_raw_dict["property"]["building"]["condition"]
            except:
                my_dict["state_of_building"] = None
            my_dict['type_of_sale'] = house_raw_dict["transaction"]["type"]
        if len(my_dict) > 1:
            #print(my_dict)
            return my_dict
        else:
            return None

    def clean_up_all_data(self):
        with open('data/raw_data_houses.json','r') as file:
            goal_dict = json.load(file)
        for key,dicti in goal_dict.items():
            cleand_dict = self.clean_up_house_data(dicti,key)
            if cleand_dict is not None:
                self.houses_cleaned_data_list.append(cleand_dict)
        return self.houses_cleaned_data_list

                
             
    
    def raw_data_to_json(self,filename : str = 'data/raw_data_houses.json'):
        with open(filename,'w') as file:
            json.dump(self.houses_raw_data_dict,file,ensure_ascii=False)

