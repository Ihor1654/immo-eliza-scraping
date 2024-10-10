import json
from .link_creator import LinkCreator
from scraper.scraper import Scraper
import csv









class Pipeline():
    def __init__(self) -> None:
        self.scraper = Scraper()
        self.link_creator = LinkCreator()
        self.dictionary_list_for_transfer = None
    
    def colect_links(self):
        print('Collecting links...')
        self.link_creator.create_final_dict()
        #print(self.link_creator.final_postcode_dict)
        self.link_creator.to_json_file()
        
    def scrap_data(self):
        print('Scraping_data')
        self.scraper.upload_data_from_json()
        self.scraper.run_as(self.scraper.get_full_raw_data_set())
        self.scraper.raw_data_to_json()
        print(f'All data scraped\n Number of records: {len(self.scraper.houses_raw_data_dict)}')
        return self.scraper.houses_raw_data_dict
    

    def prepare_data(self):
        data_list = self.scraper.clean_up_all_data()
        self.dictionary_list_for_transfer = data_list
    

    def save_to_csv(self,filepath :str ):
        with open (filepath,'w',newline='') as file:
            field_names = [key for key in self.dictionary_list_for_transfer[1].keys()]
            writer = csv.DictWriter(file,fieldnames=field_names,)
            self.dictionary_list_for_transfer.insert(0,{f'{key}': f"{key}" for key in field_names} )
            for dict in self.dictionary_list_for_transfer:
                writer.writerow(dict)

    def run(self,filepath):
        self.colect_links()
        a = self.scrap_data()
        print(len(a))
        self.prepare_data()
        self.save_to_csv(filepath)
        



