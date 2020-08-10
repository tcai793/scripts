import memobird_agent
from datetime import datetime


class Paper(memobird_agent.Document):
    def __init__(self, hostname):
        self._empty = True
        super().__init__()

        # Add header
        timestr = datetime.now().strftime('%Y/%m/%d %H:%M:%S %Z')
        super().add_text("From: " + hostname, bold=1)
        super().add_text("Time: " + timestr, bold=1)
        super().add_text()

    def new_module(self, module_name):
        if not self._empty:
            # This document has content, append module footer
            super().add_sticker(42)

        self._empty = False

        return super().add_text(module_name, font_size=2)

    def add_text(self, text='\n', bold=0, font_size=1, underline=0):
        self._empty = False
        return super().add_text(text=text, bold=bold, font_size=font_size, underline=underline)

    def add_picture(self, path):
        self._empty = False
        return super().add_picture(path)

    def add_qrcode(self, text='\n'):
        self._empty = False
        return super().add_qrcode(text=text)

    def add_sticker(self, sticker_id=0):
        self._empty = False
        return super().add_sticker(sticker_id=sticker_id)

    def is_empty(self):
        return self._empty

    def print(self, smart_guid, user_id, to_user_id=0):
        # Do not print the document if it is empty
        if self._empty:
            return None

        # Append document footer and print
        super().add_sticker(41)
        return super().print(smart_guid, user_id, to_user_id=to_user_id)
