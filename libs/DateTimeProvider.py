from datetime import datetime, timezone, timedelta

class DateTimeProvider:
    @staticmethod
    def get_current_utc_time():
        return datetime.now(timezone.utc)
    def calc_totDur(context, start, stop) -> timedelta | None:
        totDur = None
        if not start:
            context.logger.log_error("no start time found")
            return totDur
        elif not stop: 
            context.logger.log_error("could not get stop time")
            return totDur
        else:           
            try:
                totDur = stop - start
                context.logger.log_info(f"total duration {totDur}")
            except:
                context.logger.log_error("could not calc time delta")
        return totDur
