import execjs
import base64

get_hex = '''
    function getHex(a) {    
        return {
            str: a["substring"](4),
            hex: a["substring"](0, 4)["split"]("").reverse().join("")
        }
    }
'''
get_dec = '''
    function getDec(a) {
        var b = parseInt(a, 16).toString();
        return {
            pre: b["substring"](0, 2)["split"](""),
            tail: b["substring"](2)["split"]("")
        }
    }
'''
sub_str = '''
    function substr(a, b) {
        var c = a["substring"](0, b[0])
          , d = a["substr"](b[0], b[1]);
        return c + a["substring"](b[0])["replace"](d, "")
    }
'''
get_pos = '''
    function getPos(a, b) {
        return b[0] = a.length - b[0] - b[1],
        b
    }
'''


def js2py_main(a):
    if a == 'Null':
        return 0
    else:
        get_hex_run = execjs.compile(get_hex)
        get_dec_run = execjs.compile(get_dec)
        sub_str_run = execjs.compile(sub_str)
        get_pos_run = execjs.compile(get_pos)
        b = get_hex_run.call('getHex', a)
        c = get_dec_run.call('getDec', b['hex'])
        d = sub_str_run.call('substr', b['str'], c['pre'])
        e = get_pos_run.call('getPos', d, c['tail'])
        atob = sub_str_run.call('substr', d, e)
        url = base64.b64decode(atob).decode("utf-8", "ignore")
        return url


if __name__ == '__main__':
    a = '''ed51Ly9tdw6WelnZpZGVvMTEubWVpdHVkYXRhLmNvbS81ZWFkOWVmNGUxNWU1b2ozY3Iyd2RyNDczN19IMjY0XzFfNmYxZWRlOTNhY2Y0M19IMjY0XzRfNzBjNDI3OWRjMDhlMBDNV5tiNS5tcDQ='''
    print(js2py_main(a))

