import time
import os
import logging

import pwnagotchi
import pwnagotchi.plugins as plugins
import pwnagotchi.ui.faces as faces
import pwnagotchi.ui.fonts as fonts
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK


class Age(plugins.Plugin):
    __author__ = 'HannaDiamond'
    __version__ = '1.0.0'
    __license__ = 'MIT'
    __description__ = 'A plugin that will add age and strength stats based on epochs and trained epochs'

    def __init__(self):
        self.epochs = 0
        self.train_epochs = 0

    def on_loaded(self):
        log_path = '/var/log/pwnagotchi.log'
        # log_path = pwnagotchi.config['main']['log']['path']
        self.load_logs(log_path)


    def on_ui_setup(self, ui):
        ui.add_element('Age', LabeledValue(color=BLACK, label='Age', value='0', position=(ui.width() / 2 + 5, 81),
                                           label_font=fonts.Bold, text_font=fonts.Medium))
        ui.add_element('Strength', LabeledValue(color=BLACK, label='Str', value='0', position=(ui.width() / 2 + 50, 81),
                                           label_font=fonts.Bold, text_font=fonts.Medium))

    def on_unload(self, ui):
        with ui._lock:
            ui.remove_element('Age')
            ui.remove_element('Strength')

    def on_ui_update(self, ui):
        ui.set('Age', str(self.abrev_number(self.epochs)))
        ui.set('Strength', str(self.abrev_number(self.train_epochs)))


    def on_ai_training_step(self, agent, _locals, _globals):
        self.train_epochs += 1
        if self.train_epochs % 100 == 0:
            self.strength_checkpoint(agent)

    def on_epoch(self, agent, epoch, epoch_data):
        self.epochs += 1
        if self.epochs % 100 == 0:
            self.age_checkpoint(agent)

    def abrev_number(self, num):
        num = float('{:.2g}'.format(num))
        magnitude = 0
        while abs(num) >= 1000:
            magnitude += 1
            num /= 1000.0
        return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])

    def age_checkpoint(self, agent):
        view = agent.view()
        view.set('face', faces.HAPPY)
        view.set('status', "Wow, I've lived for " + str(self.abrev_number(self.epochs)) + " epochs!")
        view.update(force=True)
        time.sleep(3)

    def strength_checkpoint(self, agent):
        view = agent.view()
        view.set('face', faces.MOTIVATED)
        view.set('status', "Look at my strength go up! \n"
                           "I've trained for " + str(self.abrev_number(self.train_epochs)) + " epochs")
        view.update(force=True)
        time.sleep(3)

    def load_logs(self, log_path):
        if os.path.exists(log_path):
            with open(log_path, encoding="utf-8") as fp:
                for line in fp:
                    line = line.strip()
                    if line != "" and line[0] != '[':
                        continue
                    parts = line.split(']')
                    if len(parts) < 2:
                        continue
                    if ' training epoch ' in line:
                        self.train_epochs += 1
                    if '[epoch ' in line:
                        self.epochs += 1

