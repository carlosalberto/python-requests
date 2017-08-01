from mock import patch
import unittest

import requests
import requests_opentracing

from dummies import *
from util import PatchedSessionSend


@patch('requests.Session.send', new_callable=PatchedSessionSend)
class TestApi(unittest.TestCase):
    def test_init_tracer_none(self, send_method):
        with self.assertRaises(ValueError):
            requests_opentracing.init_tracing(None)

    def test_init(self, send_method):
        tracer = DummyTracer()

        requests_opentracing.init_tracing(tracer)
        self.assertEqual(tracer, requests_opentracing.g_tracer)
        self.assertEqual(True, requests_opentracing.g_trace_all)
        self.assertEqual(None, requests_opentracing.g_start_span_cb)

    def test_init_subtracer(self, send_method):
        tracer = DummyTracer(with_subtracer=True)

        requests_opentracing.init_tracing(tracer)
        self.assertEqual(tracer._tracer, requests_opentracing.g_tracer)
        self.assertEqual(True, requests_opentracing.g_trace_all)
        self.assertEqual(None, requests_opentracing.g_start_span_cb)

    def test_init_trace_all(self, send_method):
        requests_opentracing.init_tracing(DummyTracer(), trace_all=False)
        self.assertEqual(False, requests_opentracing.g_trace_all)

        requests_opentracing.init_tracing(DummyTracer(), trace_all=True)
        self.assertEqual(True, requests_opentracing.g_trace_all)

    def test_init_start_span_cb(self, send_method):
        def test_cb(span, request):
            pass

        requests_opentracing.init_tracing(DummyTracer(), start_span_cb=test_cb)
        self.assertEqual(test_cb, requests_opentracing.g_start_span_cb)

    def test_init_start_span_cb_invalid(self, send_method):
        with self.assertRaises(ValueError):
            requests_opentracing.init_tracing(DummyTracer(),
                                              start_span_cb=object())

    def test_trace_session_none(self, send_method):
        with self.assertRaises(ValueError):
            requests_opentracing.trace_session(None)
