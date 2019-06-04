#!/usr/bin/python3
#
# Copyright 2019 Stan S
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# You may contact Stan S via electronic mail with the address vfpro777@yahoo.com


import kivy
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.graphics.context_instructions import PushMatrix, PopMatrix, Rotate
from kivy.app import App
from kivy.uix.filechooser import FileChooserListView
from kivy.config import Config
from kivy.core.window import Window
from kivy.clock import Clock

import os
from pathlib import Path



class TopBuildWidget(Widget):
    def __init__(self, *args, **kwargs):
        super(TopBuildWidget, self).__init__(**kwargs)

        with self.canvas:
            pass

        with self.canvas.before:
            # you can use this to add instructions rendered before
            #PushMatrix()
            pass
            
        with self.canvas.after:
            # you can use this to add instructions rendered after
            #PopMatrix()
            pass


class MyCustomImageWidget(Widget):
    def __init__(self, filepath, *args, **kwargs):
        super(MyCustomImageWidget, self).__init__(**kwargs)

        with self.canvas:
        
            self.bg = Image(source=filepath)
            
            self.allow_stretch = True
            self.keep_ratio = True
            self.size_hint_y = None
            self.size_hint_x = None
            self.bg.size = Window.size

        with self.canvas.before:
            # you can use this to add instructions rendered before
            #PushMatrix()
            self.rotation = Rotate(angle=0, origin=self.bg.center)
            pass
            
        with self.canvas.after:
            # you can use this to add instructions rendered after
            #PopMatrix()
            pass
            
    def on_press(self, *args):
        self.rotation.angle += 90


class MyFolderChooser(Widget):
    def __init__(self, superparent, *args, **kwargs):
        super(MyFolderChooser, self).__init__(**kwargs)
        # filter added. Since windows will throw error on sys files
        self.fclv = FileChooserListView(path='/', 
        size_hint_x=0.3, size_hint_y=0.4, dirselect=True,
        filters= [lambda folder, filename: not filename.endswith('.sys') ])

        with self.canvas:
             self.bg =  self.fclv
             self.bg.size = Window.size
        
        self.superparent = superparent
 
        self.add_widget(self.fclv)
        self.buttonselectfolder = Button(text='Select folder', 
            size=(Window.width, 40), size_hint=(None, None))
        
        
        self.buttonselectfolder.bind(on_press=self.on_submit)
        self.add_widget(self.buttonselectfolder)
        
    def on_submit(self, *args):
    
        selection = self.fclv.selection[0]
        if os.path.isdir(selection):
            self.stored_folder = selection
        elif os.path.isfile(selection):
            self.stored_folder = str(Path(selection).parent)
        self.load_images(self.stored_folder)
 
    def load_images(self, f):
    
        folder = f
        ext = (".jpg",".gif",".bmp",".tif",".png",".tga",".webp")
        filename = False

        if os.path.isdir(folder):
            directory = folder
        else:
            directory = "."

        images = []
        self.images = images

        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.lower().endswith(ext):
                    images.append(os.path.abspath(os.path.join(root, file)))
        index = 0
        if filename:
            try:
                index = images.index(os.path.abspath(filename))
            except ValueError:
                pass    
                
        Window.remove_widget(self)

        cw = MyCustomImageWidget(directory)
        Window.add_widget(cw)
        self.superparent.customwidget = cw   # needed for the Window keybindings
        self.superparent.topwidget = cw      # now MyCustomImageWidget is on top
        
        if len(self.images) >= 1:
            cw.bg.source=self.images[0]

class MyImageApp(App):

    def build(self):
        self.index = 0
        self.popup = Popup(title='Usage:', content=Label(
            text='Press "f" on the keyboard to find a directory with images\n' + \
            'Press "r" to rotate an image'),auto_dismiss=True)
        self.popup.open()
        Clock.schedule_once(self.popup.dismiss, 5)
        
        Window.bind(on_key_down=self._on_keyboard_down)
        
        self.topwidget = TopBuildWidget()
        return self.topwidget
        
    def _on_keyboard_down(self, keyboard, x, keycode, text, modifiers):
        
        # don't allow the r key, left, or right arrow key just yet until folder is chosen
        if not hasattr(self, 'customwidget') and not text == 'f':
            print ('MyCustomImageWidget not created yet,' + \
                ' press on keyboard f and locate image directory')
            return False
        
        if text == 'r':
            self.customwidget.on_press()

        elif keycode == 79: # keyboard right arrow
            self.index += 1
            if self.index >= len(self.folderpicker.images):
                self.index = 0
            self.customwidget.bg.source=self.folderpicker.images[self.index]

        elif keycode == 80: # keyboard left arrow
            self.index -= 1
            if self.index == -1:
                self.index += len(self.folderpicker.images)
            self.customwidget.bg.source=self.folderpicker.images[self.index]
            
        elif text == 'f':
            Window.remove_widget(self.topwidget)
            Window.clearcolor = (0, 0, 0, 0)
            self.folderpicker = MyFolderChooser(self)
            Window.add_widget(self.folderpicker)
        return True

if __name__ == '__main__':
    MyImageApp().run()

