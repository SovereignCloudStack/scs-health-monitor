class Formatter:
    @staticmethod
    def format_date_time(dt):
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")