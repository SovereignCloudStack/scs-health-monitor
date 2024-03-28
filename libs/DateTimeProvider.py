from datetime import datetime, timezone

class DateTimeProvider:
    @staticmethod
    def get_current_utc_time():
        return datetime.now(timezone.utc)
    
