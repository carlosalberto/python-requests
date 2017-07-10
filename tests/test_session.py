from mock import patch
import unittest

import requests
import requests_opentracing

from dummies import *
from util import PatchedSessionSend


@patch('requests.Session.send', new_callable=PatchedSessionSend)
class TestSession(unittest.TestCase):
    def test_no_trace(self, send_method):
        tracer = DummyTracer()
        requests_opentracing.init_tracing(tracer, trace_all=False)

        session = requests.Session()
        res = session.get('http://www.google.com/')
        self.assertIsNotNone(res)
        self.assertEqual(len(tracer.spans), 0)

    def test_trace_all(self, send_method):
        tracer = DummyTracer()
        requests_opentracing.init_tracing(tracer, trace_all=True)

        session = requests.Session()
        res = session.post('http://www.google.com/', {})
        self.assertIsNotNone(res)
        self.assertEqual(len(tracer.spans), 1)
        self.assertEqual(tracer.spans[0].operation_name, 'POST')
        self.assertTrue(tracer.spans[0].is_finished)
        self.assertEqual(tracer.spans[0].tags, {
            'component': 'requests',
            'http.url': 'http://www.google.com/',
            'http.method': 'POST',
            'http.status_code': 200,
            'span.kind': 'client',
            'requests.reason': 'OK',
        })

    def test_get(self, send_method):
        tracer = DummyTracer()
        requests_opentracing.init_tracing(tracer, trace_all=False)

        session = requests.Session()
        requests_opentracing.trace_session(session)

        res = session.get('http://www.google.com/')
        self.assertIsNotNone(res)
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

    def test_get_error(self, send_method):
        tracer = DummyTracer()
        requests_opentracing.init_tracing(tracer, trace_all=False)

        session = requests.Session()
        requests_opentracing.trace_session(session)
        send_method.exception = ValueError
        call_exc = None

        try:
            session.get('http://www.google.com/')
        except ValueError as exc:
            call_exc = exc

        self.assertIsNotNone(call_exc)
        self.assertEqual(len(tracer.spans), 1)
        self.assertEqual(tracer.spans[0].operation_name, 'GET')
        self.assertTrue(tracer.spans[0].is_finished)
        self.assertEqual(tracer.spans[0].tags, {
            'component': 'requests',
            'http.url': 'http://www.google.com/',
            'http.method': 'GET',
            'span.kind': 'client',
            'error': 'true',
            'error.object': call_exc,
        })

    def test_send(self, send_method):
        tracer = DummyTracer()
        requests_opentracing.init_tracing(tracer, trace_all=False)

        session = requests.Session()
        requests_opentracing.trace_session(session)

        req = requests.Request('GET', 'http://www.google.com')
        res = session.send(req.prepare())
        self.assertIsNotNone(res)
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

    def test_send_error(self, send_method):
        tracer = DummyTracer()
        requests_opentracing.init_tracing(tracer, trace_all=False)

        session = requests.Session()
        requests_opentracing.trace_session(session)

        req = requests.Request('GET', 'http://www.google.com')
        send_method.exception = ValueError
        call_exc = None

        try:
            session.send(req.prepare())
        except ValueError as exc:
            call_exc = exc

        self.assertIsNotNone(call_exc)
        self.assertEqual(len(tracer.spans), 1)
        self.assertEqual(tracer.spans[0].operation_name, 'GET')
        self.assertTrue(tracer.spans[0].is_finished)
        self.assertEqual(tracer.spans[0].tags, {
            'component': 'requests',
            'http.url': 'http://www.google.com/',
            'http.method': 'GET',
            'span.kind': 'client',
            'error': 'true',
            'error.object': call_exc,
        })
