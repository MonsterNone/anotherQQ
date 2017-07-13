def save(requests_cookie_jar):
    cookie_dict = {}
    for i in requests_cookie_jar.list_domains():
        cookie = requests_cookie_jar.get_dict(i)
        cookie_dict[str(cookie)] = i
    with open('./cookies.txt', 'w') as a:
        a.write(str(cookie_dict))


def get(cookie_jar):
    with open('bot/cookies.txt') as a:
        data = eval(a.read())
    for i in data:
        domain = data[i]
        i = eval(i)
        for j in i:
            cookie_jar.set(j, i[j], **{'domain': domain})
    return cookie_jar
