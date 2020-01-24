from typing import List, Optional
import datetime
from enum import Enum


class VkObject:
    @classmethod
    def from_dict(cls, data: dict):
        if not data:
            return None

        return data

    def __hash__(self) -> int:
        def _hash(obj) -> int:
            buf: int = 0
            if isinstance(obj, list):
                for item in obj:
                    buf += _hash(item)
            elif isinstance(obj, dict):
                for dict_key, dict_value in obj.items():
                    buf += hash(dict_key) + _hash(dict_value)
            else:
                try:
                    buf += hash(obj)
                except TypeError:  # Skip unhashable objects
                    pass
            return buf

        result = 0
        for key, value in sorted(self.__dict__.items()):
            result += hash(key) + _hash(value)

        return result

    def __eq__(self, other: 'VkObject') -> bool:
        return isinstance(other, self.__class__) and hash(other) == hash(self)


class Geo(VkObject):
    pass


class Action(VkObject):
    pass


class Attachment(VkObject):
    pass


class ClientInfo(VkObject):
    pass


# TODO сделать датакласс
class Message(VkObject):
    def __init__(self,
                 msg_id: int,
                 date: int,
                 peer_id: int,
                 from_id: int,
                 text: str,
                 ref: str = None,
                 ref_source: str = None,
                 attachments: list = None,
                 important: bool = None,
                 geo: Geo = None,
                 payload: str = None,
                 # keyboard: Keyboard = None,
                 fwd_messages: List['Message'] = None,
                 reply_message: 'Message' = None,
                 action: Action = None):

        self.msg_id = msg_id
        self.date = datetime.datetime.fromtimestamp(float(date))
        self.peer_id = peer_id
        self.from_id = from_id
        self.text = text
        self.ref = ref
        self.ref_source = ref_source
        self.attachments = attachments
        self.important = important
        self.geo = geo
        self.payload = payload
        # self.keyboard = keyboard
        self.fwd_messages = fwd_messages
        self.reply_message = reply_message
        self.action = action

    @classmethod
    def from_dict(cls, data: dict) -> Optional['Message']:
        if not data:
            return None

        new_data = {
            'msg_id': data.get('id'),
            'date': data.get('date'),
            'peer_id': data.get('peer_id'),
            'from_id': data.get('from_id'),
            'text': data.get('text'),
            'ref': data.get('ref'),
            'ref_source': data.get('ref_source'),
            'important': data.get('important'),
            'payload': data.get('payload'),
            'geo': Geo.from_dict(data.get('geo')),
            # 'keyboard': Keyboard.from_dict(data.get('keyboard', None)),
            'attachments': [Attachment.from_dict(attachment) for attachment in data.get('attachments')],
            'action': Action.from_dict(data.get('action')),
            'reply_message': Message.from_dict(data.get('reply_message')),
            'fwd_messages': [Message.from_dict(msg) for msg in data.get('fwd_messages')]
        }

        return cls(**new_data)


class VkEventType(Enum):
    MESSAGE_NEW = 'message_new'
    MESSAGE_REPLY = 'message_reply'
    MESSAGE_EDIT = 'message_edit'

    MESSAGE_TYPING_STATE = 'message_typing_state'

    MESSAGE_ALLOW = 'message_allow'

    MESSAGE_DENY = 'message_deny'

    PHOTO_NEW = 'photo_new'

    PHOTO_COMMENT_NEW = 'photo_comment_new'
    PHOTO_COMMENT_EDIT = 'photo_comment_edit'
    PHOTO_COMMENT_RESTORE = 'photo_comment_restore'

    PHOTO_COMMENT_DELETE = 'photo_comment_delete'

    AUDIO_NEW = 'audio_new'

    VIDEO_NEW = 'video_new'

    VIDEO_COMMENT_NEW = 'video_comment_new'
    VIDEO_COMMENT_EDIT = 'video_comment_edit'
    VIDEO_COMMENT_RESTORE = 'video_comment_restore'

    VIDEO_COMMENT_DELETE = 'video_comment_delete'

    WALL_POST_NEW = 'wall_post_new'
    WALL_REPOST = 'wall_repost'

    WALL_REPLY_NEW = 'wall_reply_new'
    WALL_REPLY_EDIT = 'wall_reply_edit'
    WALL_REPLY_RESTORE = 'wall_reply_restore'

    WALL_REPLY_DELETE = 'wall_reply_delete'

    BOARD_POST_NEW = 'board_post_new'
    BOARD_POST_EDIT = 'board_post_edit'
    BOARD_POST_RESTORE = 'board_post_restore'

    BOARD_POST_DELETE = 'board_post_delete'

    MARKET_COMMENT_NEW = 'market_comment_new'
    MARKET_COMMENT_EDIT = 'market_comment_edit'
    MARKET_COMMENT_RESTORE = 'market_comment_restore'

    MARKET_COMMENT_DELETE = 'market_comment_delete'

    GROUP_LEAVE = 'group_leave'

    GROUP_JOIN = 'group_join'

    USER_BLOCK = 'user_block'

    USER_UNBLOCK = 'user_unblock'

    POLL_VOTE_NEW = 'poll_vote_new'

    GROUP_OFFICERS_EDIT = 'group_officers_edit'

    GROUP_CHANGE_SETTINGS = 'group_change_settings'

    GROUP_CHANGE_PHOTO = 'group_change_photo'

    VKPAY_TRANSACTION = 'vkpay_transaction'


class Update(VkObject):
    # Бот пока сфокусирован на сообщениях пока
    allow_event_types = [VkEventType.MESSAGE_NEW, VkEventType.MESSAGE_EDIT, VkEventType.MESSAGE_REPLY]

    def __init__(self,
                 upd_type: str,
                 message: dict,
                 group_id: int,
                 client_info: ClientInfo = None,
                 event_id: int = None):

        self.type = upd_type
        self.message = message
        self.group_id = group_id
        self.event_id = event_id
        self.client_info = client_info

    @classmethod
    def from_dict(cls, data: dict):
        if not data:
            return None

        try:
            upd_type = VkEventType(data['type'])
        except ValueError:
            upd_type = data['type']

        if upd_type not in cls.allow_event_types:
            return VkEvent(data)

        new_data = {
            'upd_type': upd_type,
            'message': Message.from_dict(data['object'].get('message')),
            'client_info': ClientInfo.from_dict(data['object'].get('client_info')),
            'group_id': data.get('group_id'),
            'event_id': data.get('event_id')
        }

        return cls(**new_data)


class VkEvent(VkObject):

    def __init__(self, raw_event: dict):
        try:
            self.type = VkEventType(raw_event['type'])
        except ValueError:
            self.type = raw_event['type']

        self.object = raw_event['object']
