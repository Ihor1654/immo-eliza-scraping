import json
from .link_creator import LinkCreator
from scraper.scraper import Scraper
import csv









class Pipeline():
    """
        Class pipeline that gathers functionality and returns a ready dataset.
    :parameters:
    scraper
    link_creator
    dictionary_list_for_transfer
    """
    def __init__(self) -> None:
        '''
            Constructor of the class that creates instances of Scraper and LinkCreator, as well as an empty dictionary for future CSV transfer.
        '''
        self.scraper = Scraper()
        self.link_creator = LinkCreator()
        self.dictionary_list_for_transfer = None
    
    def colect_links(self):
        """
            Method that collects all necessary links and saves them to a JSON file using an instance of LinkCreator.
        """
        print('Collecting links...')
        self.link_creator.create_final_dict()
        #print(self.link_creator.final_postcode_dict)
        self.link_creator.to_json_file()
        
    def scrap_data(self):
        """
            Method that scrapes data for all links from the JSON file created with collect_links, writes the data to a JSON file, and returns houses_raw_data_dict using instance of Scraper.
            :return: dict houses_raw_data_dict, a dictionary with raw data.
        """

        print('Scraping_data')
        self.scraper.upload_data_from_json()
        self.scraper.run_as(self.scraper.get_full_raw_data_set())
        self.scraper.raw_data_to_json()
        print(f'All data scraped\n Number of records: {len(self.scraper.houses_raw_data_dict)}')
        return self.scraper.houses_raw_data_dict

    def prepare_data(self):
        """
            Method that cleans up all data and adds a list with all data to the dictionary_list_for_transfer property.
        """
        data_list = self.scraper.clean_up_all_data()
        self.dictionary_list_for_transfer = data_list
    
    def save_to_csv(self,filepath :str ):
        """
            Method that takes the path to the future file and saves cleaned data in CSV format.
            :params filepath: str path to the future file
        """
        with open ('data/'+filepath,'w',newline='') as file:
            field_names = [key for key in self.dictionary_list_for_transfer[1].keys()]
            writer = csv.DictWriter(file,fieldnames=field_names,)
            self.dictionary_list_for_transfer.insert(0,{f'{key}': f"{key}" for key in field_names} )
            for dict in self.dictionary_list_for_transfer:
                writer.writerow(dict)

    def run(self,filepath):
        """
        Method that gathers all steps together
        """
        self.colect_links()
        a = self.scrap_data()
        self.prepare_data()
        self.save_to_csv(filepath)
        



