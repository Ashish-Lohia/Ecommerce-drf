import json
from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, CrontabSchedule, IntervalSchedule


class Command(BaseCommand):
    help = "Setup periodic tasks for ecommerce automation"

    def handle(self, *args, **options):
        daily_midnight, _ = CrontabSchedule.objects.get_or_create(
            minute="0",
            hour="0",
            day_of_week="*",
            day_of_month="*",
            month_of_year="*",
        )

        hourly, _ = IntervalSchedule.objects.get_or_create(
            every=1,
            period=IntervalSchedule.HOURS,
        )

        every_30_minutes, _ = IntervalSchedule.objects.get_or_create(
            every=30,
            period=IntervalSchedule.MINUTES,
        )

        every_1_minute, _ = IntervalSchedule.objects.get_or_create(
            every=1,
            period=IntervalSchedule.MINUTES,
        )

        tasks = [
            {
                "name": "Deactivate Expired Coupons",
                "task": "ecommerce.tasks.deactivate_expired_coupons",
                "schedule": daily_midnight,
            },
            {
                "name": "Check Low Stock Products",
                "task": "ecommerce.tasks.check_low_stock_products",
                "schedule": hourly,
            },
            {
                "name": "Generate Sales Analytics",
                "task": "ecommerce.tasks.generate_sales_analytics",
                "schedule": every_1_minute,
            },
            {
                "name": "Cleanup Old Notifications",
                "task": "ecommerce.tasks.cleanup_old_notifications",
                "schedule": daily_midnight,
            },
            {
                "name": "Update Coupon Usage Stats",
                "task": "ecommerce.tasks.update_coupon_usage_stats",
                "schedule": every_30_minutes,
            },
            {
                "name": "Archive Out of Stock Products",
                "task": "ecommerce.tasks.archive_out_of_stock_products",
                "schedule": daily_midnight,
            },
            {
                "name": "Remind Inactive Users",
                "task": "ecommerce.tasks.remind_inactive_users",
                "schedule": daily_midnight,
            },
        ]

        for task_config in tasks:
            schedule = task_config["schedule"]

            schedule_kwargs = {
                "crontab": schedule if isinstance(schedule, CrontabSchedule) else None,
                "interval": (
                    schedule if isinstance(schedule, IntervalSchedule) else None
                ),
            }

            task, created = PeriodicTask.objects.get_or_create(
                name=task_config["name"],
                defaults={
                    "task": task_config["task"],
                    **schedule_kwargs,
                    "enabled": True,
                },
            )

            if not created:
                task.task = task_config["task"]
                task.crontab = schedule_kwargs["crontab"]
                task.interval = schedule_kwargs["interval"]
                task.enabled = True
                task.save()
                status = "Updated"
            else:
                status = "Created"

            self.stdout.write(
                self.style.SUCCESS(f'{status} periodic task: {task_config["name"]}')
            )

        self.stdout.write(
            self.style.SUCCESS("✅ Successfully setup all periodic tasks!")
        )
