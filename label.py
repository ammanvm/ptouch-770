#!/usr/bin/python3

from PIL import Image, ImageFont, ImageDraw
import os, sys, subprocess, argparse
import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class MyWindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        Gtk.Window.__init__(self, title="Label", application=app)
        self.lines = 0
        self.entries = []
        self.text = []
        self.unprintable = 20
        self.height = 84  # 12mm tape (tested)
        self.rim = 5
        self.font = "FreeSansBold.ttf"
        self.set_border_width(10)
        self.max_height = self.height + self.unprintable
        self.outfile = "/tmp/out.pbm"
        self.out = os.path.abspath(self.outfile)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        for i in range(6):
            entry = Gtk.Entry()
            entry.connect("changed", self.on_text_changed)
            vbox.pack_start(entry, False, False, 0)
            self.entries.append(entry)

        fonts = ["FreeSans.ttf", "FreeSans-Bold.ttf"]
        fonts_combo = Gtk.ComboBoxText()
        fonts_combo.set_entry_text_column(0)
        for currency in fonts:
            fonts_combo.append_text(currency)
        vbox.pack_start(fonts_combo, False, False, 0)

        self.image = Gtk.Image()
        self.image.set_from_file(self.outfile)
        vbox.pack_start(self.image, False, False, 0)

        self.button = Gtk.Button.new_with_label("Print")
        self.button.connect("clicked", self.on_click_me_clicked)
        vbox.pack_start(self.button, False, False, 0)

        self.add(vbox)

    def on_text_changed(self, entry):
        self.lines = 0
        self.text = []
        # Count the number of lines
        for entry in self.entries:
            if (entry.get_text() != ""):
                self.text.append(entry.get_text())
                self.lines = self.lines + 1

        fontsize = int(round(self.height / self.lines, 0))

        font = ImageFont.truetype(self.font, fontsize)

        # Determine the height in pixels based on letter "A"
        # rather than the actual text so as to not have varying
        # text heights just because some lines contain letters
        # such as "A, g" that have a different height
        text_unused_width, text_height = font.getsize("A")

        # Determine the longest line
        max_width = 0
        for line in self.text:
            text_width, text_unused_height = font.getsize(line)
            width = text_width + self.rim * 2
            if (width > max_width):
                max_width = width

        image = Image.new("1", (max_width, self.max_height), 0)
        draw = ImageDraw.Draw(image)

        text_x = self.rim
        text_y = self.unprintable - text_height
        for line in self.text:
            text_y = text_y + text_height * 0.9
            draw.text((text_x, text_y), line, fill=255, font=font)
        image.save(self.out)
        self.image.set_from_file(self.outfile)

    def on_click_me_clicked(self, button):
        tool = os.path.abspath(os.path.join(os.path.dirname(__file__), "ptouch-770-write"))
        subprocess.run(["sudo", tool, self.out], check=True)

class MyApplication(Gtk.Application):

    def __init__(self):
        Gtk.Application.__init__(self)

    def do_activate(self):
        win = MyWindow(self)
        win.show_all()

    def do_startup(self):
        Gtk.Application.do_startup(self)


app = MyApplication()
exit_status = app.run(sys.argv)
sys.exit(exit_status)