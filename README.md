Conditional WSGI Profiler
=========================

WSGI profiler for high load production machines. It could help in determining bottleneck which appears only on production environment. You can apply it as regular WSGI middleware.


Conditioning is based on two filter functions:

1. **prefilter**, which is applied to request environment to decide **whether profile or not**. If returns False then profiling isn't done and this request would be processed as usual without any overhead. Purpose of this filter is having more control on overhead added by profiling by applying it to a controlled portion of traffic.
```python
    def prefilter(env):
        return True
```
2. **postfilter**, which is called after profiling to decide **whether dump profiling stats or not**. This filter grants you a control over what and how frequently write to the disk. This allows you to not overwhelm your disks or IO.
```python
    def postfilter(env, body, elapsed):
        return True
```

Example
-------

```python
    # wsgi.py
    application = ... # your regular wsgi app declaration
    
    from conditional_wsgi_profiler import ConditionalProfilerMiddleware
    import random
    application = ConditionalProfilerMiddleware(
       application,
       profile_dir='profiled',
       prefilter=lambda env: random.random() <= 0.01,  # profile 1% of traffic randomly
       postfilter=lambda env, body, elapsed: elapsed > 0.5,
    )
```

Line_profiler is supported
-------

1. Install line_profiler (https://github.com/rkern/line_profiler)
```pip install line_profiler```

2. pass _line_profiler_args_ and _line_profiler_kwargs_ keyword arguments to middleware fabric:
```application = ConditionalProfilerMiddleware(application, line_profiler_args=[func1, func2, func3]```

3. Dumped stats files are actually pickled LineStats objects. You can print them with a command:
```python -m line_profiler <dump_file_name>```


