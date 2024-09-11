def get_concatenation(params):
    path = ''
    if params is not None:
        for key, value in params.items():
            if path == '':
                path = '?'
            if path != '?':
                path = path + "&"
            if value is None:
                pass
            elif isinstance(value, list):
                for i in value:
                    path = path + key + "=" + str(i) + "&"
                path = path.rstrip('&')
            elif value != '':
                path = path + key + "=" + str(value)
    return path

if __name__ == '__main__':
    data = {
        "limit": 20,
        "loginUsernameSearchText": None,
        "verificationState": ["VERIFIED", "KYC_VERIFIED", "CRYPTO_VERIFIED"],
    }
    print(get_concatenation(data))