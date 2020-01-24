from .vk_obj import VkObject
from typing import List, Optional
from enum import Enum
from dataclasses import dataclass
import json
# TODO реализовать возможность выбора библиотеки json


class ButtonColor(Enum):
    """ Возможные цвета кнопок """

    #: Синяя
    PRIMARY = 'primary'
    #: Белая
    DEFAULT = 'default'
    #: Красная
    NEGATIVE = 'negative'
    #: Зелёная
    POSITIVE = 'positive'


class Action:
    def to_dict(self) -> dict:
        return self.__dict__


# TODO добавить __slots__
@dataclass
class TextAction(Action):
    label: str
    type: str = 'text'
    payload: str = None


@dataclass
class OpenLinkAction(Action):
    label: str
    link: str
    type: str = 'open_link'
    payload: str = None


@dataclass
class LocationAction(Action):
    type: str = 'location'
    payload: str = None


@dataclass
class VKPayAction(Action):
    hash: str
    type: str = 'vkpay'
    payload: str = None


@dataclass
class VKAppsAction(Action):
    app_id: int
    owner_id: int
    label: str
    hash: str
    type: str = 'open_app'
    payload: str = None


@dataclass
class Button:
    action: Action
    color: ButtonColor

    def to_dict(self) -> dict:
        return {'action': self.action.to_dict(), 'color': self.color.value}


class Keyboard(VkObject):
    def __init__(self,
                 one_time: bool = False,
                 inline: bool = False,
                 buttons: Optional[List[List[Button]]] = None):
        self.one_time = one_time
        self.buttons = buttons or [[]]
        self.inline = inline

    def add_line(self) -> None:
        if len(self.buttons) < 5:
            self.buttons.append([])
        else:
            raise ValueError('Too many lines.')

    @classmethod
    def get_empty_keyboard(cls) -> str:
        return cls(one_time=True, inline=False).get_keyboard()

    def add_button(self, label: str, color: ButtonColor = ButtonColor.PRIMARY, payload: str = None) -> None:
        current_row = self.buttons[-1]
        if ((self.inline and len(current_row) < 6) or
                (not self.inline and len(current_row) < 10)):
            btn = Button(TextAction(label=label, payload=payload), color)
            current_row.append(btn)
        else:
            raise ValueError('Too many buttons per line. 6 for inline and 10 for non-inline.')

    def _empty_row_or_error(self) -> List[Button]:
        current_row = self.buttons[-1]

        if len(current_row) != 0:
            raise ValueError('This type of button takes the entire width of the line')

        return current_row

    def add_location_button(self, color: ButtonColor = ButtonColor.PRIMARY, payload: str = None) -> None:
        current_row = self._empty_row_or_error()
        btn = Button(LocationAction(payload=payload), color)
        current_row.append(btn)

    def add_vkpay_button(self, hash_string: str, color: ButtonColor = ButtonColor.PRIMARY, payload: str = None) -> None:
        current_row = self._empty_row_or_error()
        btn = Button(VKPayAction(hash_string, payload=payload), color)
        current_row.append(btn)

    def add_vkapps_button(self, app_id: int, owner_id: int, label: str, hash_string: str,
                          color: ButtonColor = ButtonColor.PRIMARY, payload: str = None) -> None:
        current_row = self._empty_row_or_error()
        btn = Button(VKAppsAction(app_id, owner_id, label, hash_string, payload=payload), color)
        current_row.append(btn)

    def _buttons_to_dict(self) -> list:
        btn_list = []
        for row in self.buttons:
            btn_row = []
            for btn in row:
                btn_row.append(btn.to_dict())
            btn_list.append(btn_row)

        return btn_list

    def get_keyboard(self) -> str:
        keyboard = {
            'one_time': self.one_time,
            'inline': self.inline,
            'buttons': self._buttons_to_dict()
        }
        return json.dumps(keyboard)
