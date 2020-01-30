from typing import Callable, Optional, List
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
    def __init__(self, handlers: List[BaseHandler] = (), name: str = None):
        self.name = name
        self.handlers = handlers

    def __hash__(self):
        if self.name is None:
            return id(self)
        else:
            return hash(self.name)

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __repr__(self):
        return f'<State: {self.name=}, {self.handlers=}>'


class FsmHandler(BaseHandler):
    END_STATE = State(name='FSM_END_STATE')

    def __init__(self,
                 entry_points: State,
                 fallbacks: State,
                 allow_reentry: bool = False):
        self.entry_points = entry_points
        self.fallbacks = fallbacks
        self.allow_reentry = allow_reentry

        self.conversations = {}

    def get_state(self, user):
        return self.conversations.get(user, self.entry_points)

    def check_update(self, update) -> bool:
        # TODO peer_id, user_id и chat_id - разные вещи, надо это учитывать
        if update.type != VkEventType.MESSAGE_NEW:
            return False
        else:
            user = update.message.peer_id
            current_state = self.get_state(user)
            handlers_per_user = []
            handlers_per_user.extend(current_state.handlers)

            if current_state != self.entry_points and self.allow_reentry:
                handlers_per_user.extend(self.entry_points.handlers)

            handlers_per_user.extend(self.fallbacks.handlers)

            for handler in handlers_per_user:
                if handler.check_update(update):
                    BaseHandler.set_current(handler)
                    return True

    def handle_update(self, update: Update, bot: VkBot) -> Optional[State]:
        # TODO здесь хорошо сделать через StatesGroup просто изменение состояния, без поиска
        # current_state = State.get_current()
        handler = BaseHandler.get_current()
        new_state = handler.handle_update(update, bot)
        if new_state is not None and new_state != self.END_STATE:
            self.conversations[update.message.peer_id] = new_state
        elif new_state == self.END_STATE:
            del self.conversations[update.message.peer_id]
        return
