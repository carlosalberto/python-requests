import requests

import opentracing
import requests_opentracing


# Your OpenTracing-compatible tracer here.
tracer = opentracing.tracer

if __name__ == '__main__':
    requests_opentracing.init_tracing(tracer, trace_all=False)

    # Only trace requests done through this Session object.
    session = requests.Session()
    requests_opentracing.trace_session(session)

    # Traced as a GET command.
    res = session.get('https://api.github.com/orgs/opentracing')
    print('%s: %s' % (res.status_code, res.reason))
    print(res.json()['description'])

    # NOT traced.
    res = requests.get('https://api.github.com/orgs/opentracing/repos')
    print('%s: %s' % (res.status_code, res.reason))
    print('Repos: %s' % len(res.json()))
