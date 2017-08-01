from functools import wraps

import opentracing
import requests


g_tracer = None
g_trace_all = True
g_start_span_cb = None


def init_tracing(tracer, trace_all=True, start_span_cb=None):
    '''
    Set our tracer for requests instrumentation. Tracer objects
    from the OpenTracing django/flask/pyramid libraries can be
    passed as well.

    :param tracer: the tracer object.
    :param trace_all: If True, all requests are automatically traced.
        Else, explicit tracing on Session objects is required.
    :param start_span_cb: The callback function invoked when
        a new Span is created, having the Span and the request object
        as arguments. Can be used to set the operation name or set
        custom tags.
    '''
    global g_tracer, g_trace_all, g_start_span_cb

    if hasattr(tracer, '_tracer'):
        tracer = tracer._tracer

    if tracer is None:
        raise ValueError('tracer')

    if start_span_cb is not None and not callable(start_span_cb):
        raise ValueError('start_span_cb')

    g_tracer = tracer
    g_trace_all = trace_all
    g_start_span_cb = start_span_cb

    if trace_all:
        _patch_session_send()


def trace_session(session):
    '''
    Marks a Session to be traced. All requests executed
    through this object will be traced.
    '''
    if session is None:
        raise ValueError('session')

    send_method = session.send

    @wraps(send_method)
    def tracing_send(request, **kwargs):
        return _call_send(None, send_method, request, **kwargs)

    session.send = tracing_send


def _patch_session_send():
    send_method = requests.Session.send

    @wraps(send_method)
    def tracing_send(self, request, **kwargs):
        return _call_send(self, send_method, request, **kwargs)

    requests.Session.send = tracing_send


def _call_send(self, send, request, **kwargs):
    span = g_tracer.start_span(request.method)

    g_tracer.inject(span.context,
                    opentracing.Format.HTTP_HEADERS,
                    request.headers)

    span.set_tag('component', 'requests')
    span.set_tag('span.kind', 'client')
    span.set_tag('http.url', request.url)
    span.set_tag('http.method', request.method)

    # Invoke our callback after the headers/tags have been set,
    # so the user can override them if needed.
    if g_start_span_cb is not None:
        g_start_span_cb(span, request)

    try:
        if self is None: # bound method.
            result = send(request, **kwargs)
        else: # unbound method, pass self.
            result = send(self, request, **kwargs)

    except Exception as exc:
        span.set_tag('error', 'true')
        span.set_tag('error.object', exc)
        span.finish()
        raise

    span.set_tag('http.status_code', result.status_code)
    span.set_tag('requests.reason', result.reason)
    span.finish()

    return result
