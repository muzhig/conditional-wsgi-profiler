# Thanks to @mitsuhiko
# 90% code is taken from https://github.com/mitsuhiko/werkzeug/blob/master/werkzeug/contrib/profiler.py

import sys
import time
import os
from cProfile import Profile
from pstats import Stats



class ConditionalProfilerMiddleware(object):
    def __init__(self, app, stream=None, sort_by=('time', 'calls'), profile_dir=None, prefilter=None, postfilter=None, line_profiler_args=[], line_profiler_kwargs={}):
        self._app = app
        self._stream = stream or sys.stdout
        self._sort_by = sort_by
        self._profile_dir = profile_dir
        self._prefilter = prefilter
        self._postfilter = postfilter
        self.line_profiler = None
        if line_profiler_args or line_profiler_kwargs:
            from line_profiler import LineProfiler
            self.line_profiler = LineProfiler(*line_profiler_args, **line_profiler_kwargs)
        if self._profile_dir and not os.path.isdir(self._profile_dir):
            os.makedirs(self._profile_dir)

    def __call__(self, environ, start_response):
        response_body = []

        if self._prefilter and not self._prefilter(environ):
            return self._app(environ, start_response)

        def catching_start_response(status, headers, exc_info=None):
            start_response(status, headers, exc_info)
            return response_body.append

        def runapp():
            appiter = self._app(environ, catching_start_response)
            response_body.extend(appiter)
            if hasattr(appiter, 'close'):
                appiter.close()

        p = self.line_profiler or Profile()
        start = time.time()
        p.runcall(runapp)
        body = b''.join(response_body)
        elapsed = time.time() - start

        if not self._postfilter or self._postfilter(environ, body, elapsed):

            if self._profile_dir is not None:
                prof_filename = os.path.join(self._profile_dir, '%06dms.%s.prof' % (elapsed * 1000.0, environ.get('PATH_INFO').strip('/').replace('/', '.') or 'root',))
                p.dump_stats(prof_filename)
            else:
                stats = Stats(p, stream=self._stream)
                stats.sort_stats(*self._sort_by)

                self._stream.write('-' * 80)
                self._stream.write('\nPATH: %r\n' % environ.get('PATH_INFO'))
                stats.print_stats()
                self._stream.write('-' * 80 + '\n\n')

        return [body]
