from gmail2notification.messages.builder import build_message


def test_call_train_func_exit():
    data = {
        'date': '08月20日',
        'time': '17時28分',
        'provider': '東急電鉄',
        'station': '駒沢大学駅',
        'enterexit': '出場',
        'email_service': 'train',
    }

    result = build_message('Tester', data)
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
        'email_service': 'train',
    }

    result = build_message('Tester', data)
    assert (
        result
        == 'Train Notification for Tester.\n08月20日 at 17時28分\nEntered 駒沢大学駅'
    )


def test_call_institute_func():
    data = {
        'date': '08月17日 16時50分',
        'enterexit': 'に入室しました',
        'location': '駒沢大学教室',
        'email_service': 'tokyoinstitute',
    }

    result = build_message('Tester', data)
    print(result)
    assert result == '駒沢大学教室 Notification for Tester.\n08月17日 16時50分 に入室しました'


def test_call_bus_func():
    data = {
        'date': '11月20日',
        'time': '15時27分',
        'name': 'タマオアイビーローズ',
        'busname': '渋24',
        'destination': '渋谷駅',
        'boardedat': '成育医療研究センター前',
        'email_service': 'bus',
    }

    result = build_message('Tester', data)
    assert result == "Tester boarded the 渋24 bound for \n渋谷駅 at stop: 成育医療研究センター前\nat 15時27分 on 11月20日"

def test_call_no_function():
    data = {
        'date': '08月20日',
        'time': '17時28分',
        'provider': '東急電鉄',
        'station': '駒沢大学駅',
        'enterexit': '出場',
        'email_service': 'bogus',
    }

    result = build_message('Tester', data)
    assert result is None
