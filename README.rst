####################
Requests Opentracing
####################

This package enables distributed tracing for the Python requests library.

Installation
============

Run the following command:

    $ pip install requests_opentracing

Getting started
===============

Tracing a `requests` client requires setting up an OpenTracing-compatible tracer, and calling `init_tracing` to set up the tracing wrappers. See the examples directory for several different approaches.

.. code-block:: python

    import requests
    import requests_opentracing

    requests_opentracing.init_tracing(tracer)

    # Traced as a GET operation, as by default the method
    # is used as operation name.
    res = requests.get('https://api.github.com/orgs/opentracing')

    # Traced as a GET operation too.
    session = Session()
    res = session.get('https://api.github.com/orgs/opentracing/repos')

    # Prepared requests are traced as well.
    req = requests.Request('GET', 'https://api.github.com/orgs/opentracing')
    session.send(session.prepare_request(req))

It's possible to trace only specific Session objects:

.. code-block:: python

    requests_opentracing.init_tracing(tracer, trace_all=False)

    session = Session()
    requests_opentracing.trace_session(session)

    # Only requests executed through this session will
    # be traced.
    session.get('https://api.github.com/orgs/opentracing')

It's also possible to specify a callback to be invoked when a new Span is created, thus allowing the user to override the `Span.operation_name`, or setting additional `Span` tags:

.. code-block:: python

    def my_start_span_cb(span, request):
        span.operation_name = 'Cache-%s' % request.method
        span.set_tag('component', 'cache') # Override the component tag
        span.set_tag('custom', 'true') # Additional custom tag.

    requests_opentracing.init_tracing(tracer, my_start_span_cb=start_span_cb)

Further information
===================

If you’re interested in learning more about the OpenTracing standard, please visit `opentracing.io`_ or `join the mailing list`_. If you would like to implement OpenTracing in your project and need help, feel free to send us a note at `community@opentracing.io`_.

.. _opentracing.io: http://opentracing.io/
.. _join the mailing list: http://opentracing.us13.list-manage.com/subscribe?u=180afe03860541dae59e84153&id=19117aa6cd
.. _community@opentracing.io: community@opentracing.io

