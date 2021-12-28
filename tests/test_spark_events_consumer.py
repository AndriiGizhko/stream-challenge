from spark_events_consumer import update_function


def test_update_function_no_updates():
    data = [{'Url': 'url1', 'Timestamp': 1}]
    assert update_function([], {'updated': True, 'data': data}) == {'updated': False, 'data': data}


def test_update_function_state_update():
    state_data = [{'Url': 'url1', 'Timestamp': 1}]
    new_data = [{'Url': 'url2', 'Timestamp': 2}]
    assert update_function([new_data], {'updated': False, 'data': state_data}) == \
           {'updated': True, 'data': [{'Url': 'url2', 'Timestamp': 2}, {'Url': 'url1', 'Timestamp': 1}]}


def test_update_function_state_update_6th_url():
    state_data = [
        {'Url': 'url5', 'Timestamp': 2},
        {'Url': 'url4', 'Timestamp': 2},
        {'Url': 'url3', 'Timestamp': 2},
        {'Url': 'url2', 'Timestamp': 2},
        {'Url': 'url1', 'Timestamp': 1}
    ]
    new_data = [{'Url': 'url6', 'Timestamp': 3}]
    assert update_function([new_data], {'updated': False, 'data': state_data}) == \
           {'updated': True, 'data': [
               {'Url': 'url6', 'Timestamp': 3},
               {'Url': 'url5', 'Timestamp': 2},
               {'Url': 'url4', 'Timestamp': 2},
               {'Url': 'url3', 'Timestamp': 2},
               {'Url': 'url2', 'Timestamp': 2}
           ]}


