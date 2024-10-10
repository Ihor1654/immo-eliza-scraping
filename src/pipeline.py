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
        self.link_creator.create_final_dict()
        self.link_creator.to_json_file
    
    def scrap_data(self):
        
        self.scraper.run_as(self.scraper.get_full_raw_data_set())
        self.scraper.raw_data_to_json()
        return self.scraper.houses_raw_data_dict
    

    def prepare_data(self):
        self.scraper.clean_up_all_data()
        self.dictionary_list_for_transfer = self.scraper.houses_cleaned_data_list
    

    def save_to_csv(self,filepath :str ):
        pass
        

    def run(self,filepath):
        self.colect_links()
        self.scrap_data()
        self.prepare_data()
        self.save_to_csv(filepath)
        



