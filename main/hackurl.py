def hackurl(url):
    scheme, x, rest = url.partition('://')
    netloc, x, path = rest.partition('/')
    host, x, port = netloc.partition(':')
    x, y, octet = host.rpartition('.')
    newport = str(int(octet) + 20000)
    return scheme + '://172.29.74.183:' + newport + '/' + path


if __name__ == '__main__':
    testurl = 'http://10.0.0.3:5000/jobs'
    print "test input:  " + testurl
    print "test output: " + hackurl(testurl)
