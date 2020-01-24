from typing import Callable, Dict, List, Optional
from .bot import VkBot
from .objects import Update, VkEventType
from .utils import ContextInstanceMixin


class BaseHandler(ContextInstanceMixin):
    def check_update(self, update) -> bool:
        pass

    def handle_update(self, update: Update, bot: VkBot):
        pass


# TODO передавать сразу пользователя и сообщение через ContextVar
class Handler(BaseHandler):
    def __init__(self, callback: Callable, update_type: VkEventType):
        self.callback = callback
        self.update_type = update_type

    def check_update(self, update: Update) -> bool:
        if update.type == self.update_type:
            return True
        else:
            return False
        # return update['type'] == self.update_type

    def handle_update(self, update: Update, bot: VkBot) -> Optional[int]:
        return self.callback(update, bot)


class CommandHandler(Handler):
    def __init__(self, command: str, callback: Callable, **kwargs):
        update_type = kwargs.get('update_type', VkEventType.MESSAGE_NEW)
        super().__init__(callback, update_type)
        self.command = command

    @staticmethod
    def _get_command_from_update(update) -> str:
        # TODO сделать свой тип
        # Stupid search
        return update.message.text.split()[0][1:]  # /(cmd) some text maybe

    def check_update(self, update) -> bool:
        if super(CommandHandler, self).check_update(update):
            if self._get_command_from_update(update) == self.command:
                return True
        else:
            return False


class MessageHandler(Handler):
    def __init__(self, callback: Callable):
        super(MessageHandler, self).__init__(callback, update_type=VkEventType.MESSAGE_NEW)


class EditMessageHandler(Handler):
    def __init__(self, callback: Callable):
        super(EditMessageHandler, self).__init__(callback, update_type=VkEventType.MESSAGE_EDIT)


class ReplyMessageHandler(Handler):
    def __init__(self, callback: Callable):
        super(ReplyMessageHandler, self).__init__(callback, update_type=VkEventType.MESSAGE_REPLY)


class State(ContextInstanceMixin):
    # TODO StatesGroup и объединить в них все состояния, точки входа, выхода и т.д.
    pass


class FsmHandler(BaseHandler):
    END = -1

    def __init__(self,
                 entry_points: List[Handler],
                 states: Dict[State, List[Handler]],
                 fallbacks: List[Handler],
                 allow_reentry: bool = False):
        self.entry_points = entry_points
        self.states = states
        self.fallbacks = fallbacks
        self.allow_reentry = allow_reentry

        self.conversations = {}

    def check_update(self, update) -> bool:
        # TODO peer_id, user_id и chat_id - разные вещи, надо это учитывать
        if update.type != VkEventType.MESSAGE_NEW:
            return False
        else:
            user = update.message.peer_id
            handlers_per_user = []
            if user in self.conversations:
                current_state = self.conversations.get(user)
                # TODO похоже и не надо
                State.set_current(current_state)

                handlers_per_user.extend(self.states.get(current_state))
                handlers_per_user.extend(self.fallbacks)

            if (user not in self.conversations) or self.allow_reentry:
                handlers_per_user.extend(self.entry_points)

            for handler in handlers_per_user:
                if handler.check_update(update):
                    self.set_current(self)
                    return True

    def handle_update(self, update: Update, bot: VkBot) -> Optional[int]:
        # TODO здесь хорошо сделать через StatesGroup просто изменение состояния, без поиска
        # current_state = State.get_current()
        handler = self.get_current()
        new_state = handler.handle_update(update, bot)
        if new_state is not None and new_state != self.END:
            self.conversations[update.message.peer_id] = new_state
        else:
            del self.conversations[update.message.peer_id]
        return
