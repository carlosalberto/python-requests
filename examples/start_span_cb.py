import requests

import opentracing
import requests_opentracing


# Your OpenTracing-compatible tracer here.
tracer = opentracing.tracer

def start_span_callback(span, request):
    span.operation_name = 'Foo::%s' % request.method
    span.set_tag('custom.key', 1024)


if __name__ == '__main__':
    # start_span_callback() will be called for each traced request.
    requests_opentracing.init_tracing(tracer, start_span_cb=start_span_callback)

    # Traced as a 'Foo::https://api.github.com/orgs/opentracing'
    # with a custom tag 'custom.key' = 1024
    res = requests.get('https://api.github.com/orgs/opentracing')
    print('%s: %s' % (res.status_code, res.reason))
    print(res.json()['description'])
