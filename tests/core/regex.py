from gmail2line.core import matching
from gmail2line.core.patterns.jpn.regex import train


def test_train():
    test_str = '09月10日　15時54分\n' 'SOMENAMEさん\n' '「東急電鉄・駒沢大学駅」を入場されました。\n'

    result = matching.find_matches(test_str, train)
    print(result)
    assert result['date'] == '09月10日'
    assert result['time'] == '15時54分'
    assert result['name'] == 'SOMENAME'
    assert result['provider'] == '東急電鉄'
    assert result['station'] == '駒沢大学駅'
    assert result['enterexit'] == '入場'
