import pytest
from aiobot import Updater, VkBot, Dispatcher


@pytest.fixture
def dummy_updater(bot_records):
    updater = Updater(**bot_records)
    return updater


def test_updater_init(bot_records):
    updater = Updater(**bot_records)
    assert updater.bot.access_token == bot_records['access_token']
    assert updater.dispatcher.bot == updater.bot


def test_updater_start(dummy_updater):
    pass
