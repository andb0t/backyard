def check_auth(username: str, password: str):
    '''This function is called to check if a username /
    password combination is valid.'''
    return username == 'admin' and password == 'secret'


def requires_auth(username, password, required_scopes=None):
    if not check_auth(username, password):
        return None
    return {
        "uid": username
    }
