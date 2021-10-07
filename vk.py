import vk_api
import requests
import os
import time
import sys
from enum import Enum, auto
from datetime import datetime


class ApiFetcher:

    club_domain = "sch2086_11m"
    count = 10
    stop_words = ["физик", "дз", "домашн", ]

    def __init__(self, login, password):
        self.login = login
        self.password = password
        self.api = None

    def set_club(new_club_domain):
        self.club_domain = new_club_domain

    def auth(self):
        session = vk_api.VkApi(self.login, self.password)
        session.auth()
        self.api = session.get_api()
    
    def check_post_text(self, text):
        return any(map(lambda word: word in text, self.stop_words))
    
    @staticmethod
    def first_passing(func, arr):
        for item in arr:
            if func(item):
                return item

    def get_post(self):
        if self.api is None:
            raise Exception("Api hasn't initialized (probably auth failed)")
        for post in self.api.wall.get(domain=self.club_domain, count=self.count)["items"]:
            if self.check_post_text(post["text"]):
                return post    

        raise Exception(f"Couldn't find specific post in last {self.count}  posts")

        

class PostParser: 
    
    def __init__(self):
        pass

    def parse(self, post):
        text = post["text"]
        image_atts = filter(lambda att: att["type"] == "photo", post["attachments"])
        images = []
        for att in image_atts:
            image = att["photo"]["sizes"][-1]["url"]
            images.append(image)   
        date = post["date"]
        return text, images, date



class VkImageDownloader:
    def __init__(self):
        pass

    def download(self, url, output):
        if url:
            image_fname = "placehoder.jpg"
            with open(output + "/" + image_fname, "wb") as f:
                f.write(requests.get(url).content)
        else:
            print(f"invalid url: {url}")

class FileManager:
    def __init__(self, output_dir):
        self.output_dir = output_dir
    
    def init_dir(self):
        os.makedirs(self.output_dir, exist_ok=True)

    def save_post(self, text, date):
        formatted_date = datetime.fromtimestamp(date).strftime("%Y-%m-%d %H:%M:%S")
        content = f"Post ({formatted_date})\n {text}"
        fname = "post_placeholder.txt"
        with open(self.output_dir + "/" + fname, "w", encoding="utf-8") as f:
            f.write(content)

class PollState(Enum):
    Start = auto()
    Mainloop = auto()
    End = auto()


class StateManager:
    def __init__(self):
        self.current_state = PollState.Start
    
    def change_state(self, new_state):
        self.current_state = new_state
    
    
class Poll:
    def __init__(self, login, password, output, rate):
        self.login = login
        self.password = password
        self.rate = rate
        self.fetcher = ApiFetcher(self.login, self.password)
        self.post_parser = PostParser()
        self.file_manager = FileManager(output)
        self.state_manager = StateManager()
        self.image_downloader = VkImageDownloader()

    def start(self):
        print("Polling started")
        print("Logging in...")
        self.fetcher.auth()
        self.file_manager.init_dir()
        self.state_manager.change_state(PollState.Mainloop)
    
    def poll(self):
        print("fetching results...")
        post = self.fetcher.get_post()
        text, images, date = self.post_parser.parse(post)
        for image_url in images: self.image_downloader.download(image_url, self.file_manager.output_dir)
        self.file_manager.save_post(text, date)
        # self.state_manager.change_state(PollState.End)

    def end(self):
        print("Polling stopped")
    
    def mainloop(self):
        
        current_state = self.state_manager.current_state
        running = True
        # print("curr state:", current_state)
        while running:
            try:
                if current_state is PollState.Start:
                    self.start()
                elif current_state is PollState.Mainloop:
                    self.poll()
                    time.sleep(self.rate)
                elif current_state is PollState.End:
                    self.end()
                    running = False
                else:
                    raise Exception(f"Invalid Poll State {state_manager.current_state}")
                current_state = self.state_manager.current_state
                
            except KeyboardInterrupt:
                current_state = PollState.End
            except Exception as e:
                print("Poll fetched abnormally")
                print(e)
                print("To stop polling press ctrl-c")



