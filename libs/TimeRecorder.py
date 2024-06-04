import time

class TimeRecorder:
    @staticmethod
    def record_time(func, on_success=None, on_fail=None, *args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            end_time = time.time()
            duration = end_time - start_time
            if on_success:
                on_success(duration)
            return result
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            if on_fail:
                on_fail(duration, e)
            raise
        