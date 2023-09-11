from gmail2line.messages import common
from gmail2line.messages import message_builder
from gmail2line.messages.message_builder import *


def test_call_train_func_exit():
    data = {
        'date': '08月20日',
        'time': '17時28分',
        'provider': '東急電鉄',
        'station': '駒沢大学駅',
        'enterexit': '出場',
        'notifier': 'train',
    }

    result = common.call_function('Tester', data)
    assert (
        result
        == 'Train Notification for Tester.\n08月20日 at 17時28分\nExited 駒沢大学駅'
    )


def test_call_train_func_entered():
    data = {
        'date': '08月20日',
        'time': '17時28分',
        'provider': '東急電鉄',
        'station': '駒沢大学駅',
        'enterexit': '入場',
        'notifier': 'train',
    }

    result = common.call_function('Tester', data)
    assert (
        result
        == 'Train Notification for Tester.\n08月20日 at 17時28分\nEntered 駒沢大学駅'
    )


def test_call_institute_func():
    data = {
        'date': '08月17日 16時50分',
        'enterexit': 'に入室しました',
        'location': '駒沢大学教室',
        'notifier': 'tokyoinstitute',
    }

    result = common.call_function('Tester', data)
    print(result)
    assert result == '駒沢大学教室 Notification for Tester.\n08月17日 16時50分 に入室しました'


def test_call_no_function():
    data = {
        'date': '08月20日',
        'time': '17時28分',
        'provider': '東急電鉄',
        'station': '駒沢大学駅',
        'enterexit': '出場',
        'notifier': 'bogus',
    }

    result = common.call_function('Tester', data)
    assert result is None
