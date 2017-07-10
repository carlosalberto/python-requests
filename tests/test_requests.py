from mock import patch, MagicMock
import unittest

import opentracing
import requests
import requests.structures
import requests_opentracing

from dummies import *
from util import PatchedSessionSend


@patch('requests.Session.send', new_callable=PatchedSessionSend)
class TestRequests(unittest.TestCase):
    def test_no_trace(self, send_method):
        tracer = DummyTracer()
        requests_opentracing.init_tracing(tracer, trace_all=False)

        res = requests.get('http://www.google.com')
        self.assertIsNotNone(res)
        self.assertEqual(len(tracer.spans), 0)

    def test_get(self, send_method):
        tracer = DummyTracer()
        requests_opentracing.init_tracing(tracer)

        res = requests.get('http://www.google.com')
        self.assertEqual(len(tracer.spans), 1)
        self.assertEqual(tracer.spans[0].operation_name, 'GET')
        self.assertTrue(tracer.spans[0].is_finished)
        self.assertEqual(tracer.spans[0].tags, {
            'component': 'requests',
            'http.url': 'http://www.google.com/',
            'http.method': 'GET',
            'http.status_code': 200,
            'span.kind': 'client',
            'requests.reason': 'OK',
        })

    def test_start_span_cb(self, send_method):
        tracer = DummyTracer()

        def test_cb(span, request):
            span.operation_name = request.url

        requests_opentracing.init_tracing(tracer, start_span_cb=test_cb)

        res = requests.get('http://www.google.com')
        self.assertEqual(len(tracer.spans), 1)
        self.assertEqual(tracer.spans[0].operation_name, 'http://www.google.com/')
        self.assertTrue(tracer.spans[0].is_finished)
        self.assertEqual(tracer.spans[0].tags, {
            'component': 'requests',
            'http.url': 'http://www.google.com/',
            'http.method': 'GET',
            'http.status_code': 200,
            'span.kind': 'client',
            'requests.reason': 'OK',
        })

    def test_inject_headers(self, send_method):
        tracer = DummyTracer()
        requests_opentracing.init_tracing(tracer)

        with patch.object(tracer, 'inject', auto_spec=True) as inject_method:
            res = requests.get('http://www.google.com')

            self.assertEqual(inject_method.call_count, 1)

            call_args = inject_method.call_args[0]
            self.assertEqual(call_args[1], opentracing.Format.HTTP_HEADERS)
            self.assertTrue(isinstance(call_args[2], 
                                       requests.structures.CaseInsensitiveDict))
