import requests

import opentracing
import requests_opentracing


# Your OpenTracing-compatible tracer here.
tracer = opentracing.tracer

if __name__ == '__main__':
    # By default, init_tracing() traces all requests.
    requests_opentracing.init_tracing(tracer)

    # Traced as a GET command, including http information
    # such as status code, url, and method.
    res = requests.get('https://api.github.com/orgs/opentracing')
    print('%s: %s' % (res.status_code, res.reason))
    print(res.json()['description'])
