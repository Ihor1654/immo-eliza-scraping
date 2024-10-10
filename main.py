from src.pipeline import Pipeline
import time
start_time = time.localtime()
start = time.strftime("%H:%M:%S", start_time)
print(start)
pipeline = Pipeline()
pipeline.run(input('Enter name of csv file that you want to save'))
finish_time = time.localtime()
finish = time.strftime("%H:%M:%S", finish_time)
print(finish)