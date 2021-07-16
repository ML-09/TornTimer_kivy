import time
import threading
import requests
import json
import simpleaudio as sa

from kivy.app import App
from kivy.config import Config
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.uix.switch import Switch
from kivy.lang import Builder
#from kivy.clock import Clock
#import kivy.weakmethod

Config.set('graphics', 'width', 320)
Config.set('graphics', 'height', 480)
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

# variabls for for api requests
global arrival_time # 0 if landed, unixtime of "arriving" if flying
arrival_time = 0
global first_api_request
first_api_request = 1

global button_state
button_state = 1

# variables for settings
global settings
settings = dict()
settings["do_ring_arrival"] = 0
settings["advance_arrival"] = 5
settings["do_ring_15m"] = 1
settings["advance_15m"] = 5
settings["do_apirequests"] = 0
settings["apikey"] = "XJwNJPNFIysNXhKH"

# variables for character
global character
character = dict()
character["destination"] = 'Torn'




class MainScreen(Screen):
    def __init__(self, **kwargs):
        self.load_config()
        super(MainScreen, self).__init__(**kwargs)
        self.slider_advance_arrival.value = settings["advance_arrival"]
        self.switcher_arrival.active = settings["do_ring_arrival"]
        self.slider_advance.value = settings["advance_15m"]
        self.switcher_15m.active = settings["do_ring_15m"]

        tt = threading.Timer(0, self.my_callback)
        tt.daemon = True
        tt.start()
        #self.my_callback()

    def btn_press(self):
        global button_state
        print("Кнопка нажата")
        if button_state == 1:
            self.btn_start.text = "Start playing sound"
            button_state = 0
            print(button_state)
        else:
            self.btn_start.text = "Stop playing sound"
            button_state = 1
            print(button_state)

    def slider_arrival_on_value(self, slider_value):
        global settings
        settings["advance_arrival"] = slider_value
        self.save_config()

    def switch_arrival_on_active(self, switch_active):
        global settings
        settings["do_ring_arrival"] = switch_active
        self.save_config()

    def slider_on_value(self, slider_value):
        global settings
        settings["advance_15m"] = slider_value
        self.save_config()

    def switch_15m_on_active(self, switch_active):
        global settings
        settings["do_ring_15m"] = switch_active
        self.save_config()


    def my_callback(self):
        global settings
        global character
        global arrival_time
        global first_api_request

        tt = threading.Timer(1.0, self.my_callback)
        tt.daemon = True
        tt.start()

        self.time_24.text = str(time.strftime("%H:%M:%S", time.localtime()))
        self.time_24_15.text = str(time.strftime("%M:%S", time.gmtime(int((((15*60)- round(time.time()) ) % (15*60)))+1)))


        if (round(time.time()) < arrival_time):
            print("Мы в полете "+ str(arrival_time)+ " " + str(round(time.time())))
            self.time_arrival_24.text = str(time.strftime("%H:%M:%S", time.gmtime((arrival_time - round(time.time())))))
        elif (round(time.time()) > arrival_time):
            print("Давно прилетели "+ str(arrival_time)+ " " + str(round(time.time())))
        else:
            print("Вот прямо сейчас прилетели "+ str(arrival_time)+ " " + str(round(time.time())))
            arrival_time = 0
            self.label_arrival.text = "Arrived to:"
            self.time_arrival_24.text = character["destination"]

        if (self.switcher_15m.active == True):
            temporary_variable = 15
            if ((((15*60)- round(time.time()) ) % (temporary_variable*60)) == (0+int(self.slider_advance.value))):
                wave_obj = sa.WaveObject.from_wave_file("resources/sound.wav")
                play_obj = wave_obj.play()
                play_obj.wait_done()
        if (self.switcher_arrival.active == True) and arrival_time:
            temporary_variable = 15
            print("КОГДА ЗВЕНЕТЬ: "+str(arrival_time - settings["advance_arrival"]))
            if arrival_time - settings["advance_arrival"] == round(time.time()):
                wave_obj = sa.WaveObject.from_wave_file("resources/landing.wav")
                play_obj = wave_obj.play()
                play_obj.wait_done()
                print("Прилетели прилетели")

        # запуск запросов по API о путешествиях каждую 30-ю секунду
        if ((((round(time.time())) % 60) == 30) or (first_api_request == 1)) and settings["do_apirequests"]:
            first_api_request = 0
            print("Запуск Api запроса")
            resp = requests.get('https://api.torn.com/user/2531416?selections=travel&key='+settings["apikey"])
            resp_json = resp.json()
            print(resp_json)

            if 'error' in resp_json:
                self.time_arrival_24.text = "Incorrect API key"
            else:
                resp_json_time_left = resp_json["travel"]["time_left"]
                character["destination"] = str(resp_json["travel"]["destination"])
                if (resp_json_time_left > 0 ):
                    arrival_time = round(resp_json_time_left + time.time())
                    self.label_arrival.text = "Arrival to "+character["destination"]+" in:"
                    self.time_arrival_24.text = str(time.strftime("%H:%M:%S", time.gmtime(resp_json_time_left)))
                else:
                    arrival_time = 0
                    self.label_arrival.text = "Arrived to:"
                    self.time_arrival_24.text = str(character["destination"])

    def save_config(self):
        global settings
        with open('config1.json', 'w') as f:
            json.dump(settings, f)
        print("save config")

    def load_config(self):
        global settings
        print(str(settings["advance_arrival"]))
        with open('config1.json', 'r') as f:
            settings = json.load(f)
        print("loading config")
        print(str(settings["advance_arrival"]))

class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super(SettingsScreen, self).__init__(**kwargs)
        global settings
        self.apikey_input.text = settings["apikey"]
        self.switcher_apirequests.active = settings["do_apirequests"]

    def textinput_on_text(self, input_text):
        global settings
        settings["apikey"] = input_text
        MainScreen.save_config(self)

    def switch_apirequests_on_active(self, switch_active):
        global settings
        settings["do_apirequests"] = switch_active
        MainScreen.save_config(self)

class TornTimerApp(App):
    def build(self):
        Builder.load_file("torntimer2.kv")
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='mainscreen'))
        sm.add_widget(SettingsScreen(name='settingsscreen'))
        return sm

if __name__ == '__main__':
    TornTimerApp().run()