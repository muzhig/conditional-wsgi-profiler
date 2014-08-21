import sys
import time
import os
from cProfile import Profile
from pstats import Stats



class ProfilerMiddleware(object):
    def __init__(self, app, stream=None, sort_by=('time', 'calls'), profile_dir=None, filter_func=None, dump_filter_func=None):
        self._app = app
        self._stream = stream or sys.stdout
        self._sort_by = sort_by
        self._restrictions = restrictions
        self._profile_dir = profile_dir
        self._filter_func = filter_func
        self._dump_filter_func = dump_filter_func
        if self._profile_dir and not os.path.isdir(self._profile_dir):
            os.makedirs(self._profile_dir)

    def __call__(self, environ, start_response):
        response_body = []

        if self._filter_func and not self._filter_func(environ):
            return self._app(environ, start_response)

        def catching_start_response(status, headers, exc_info=None):
            start_response(status, headers, exc_info)
            return response_body.append

        def runapp():
            appiter = self._app(environ, catching_start_response)
            response_body.extend(appiter)
            if hasattr(appiter, 'close'):
                appiter.close()

        p = Profile()
        start = time.time()
        p.runcall(runapp)
        body = b''.join(response_body)
        elapsed = time.time() - start

        if not self._dump_filter_func or self._dump_filter_func(environ, body, elapsed):

            if self._profile_dir is not None:
                prof_filename = os.path.join(self._profile_dir, '%06dms.%s.prof' % (elapsed * 1000.0, environ.get('PATH_INFO').strip('/').replace('/', '.') or 'root',))
                p.dump_stats(prof_filename)
            else:
                stats = Stats(p, stream=self._stream)
                stats.sort_stats(*self._sort_by)

                self._stream.write('-' * 80)
                self._stream.write('\nPATH: %r\n' % environ.get('PATH_INFO'))
                stats.print_stats(*self._restrictions)
                self._stream.write('-' * 80 + '\n\n')

        return [body]

