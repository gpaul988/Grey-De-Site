from django_cron import CronJobBase, Schedule
from tasks import check_all_subscriptions, check_monthly_subscriptions, check_yearly_subscriptions

class SubscriptionCheckJob(CronJobBase):
    RUN_EVERY_MINS = 1440  # Runs once per day

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = "subscriptions.check_all"

    def do(self):
        check_all_subscriptions()
        check_monthly_subscriptions()
        check_yearly_subscriptions()