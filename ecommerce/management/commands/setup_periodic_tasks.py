from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, CrontabSchedule, IntervalSchedule


class Command(BaseCommand):
    help = "Setup periodic tasks for ecommerce automation"

    def handle(self, *args, **options):
        # Create schedules
        daily_midnight, _ = CrontabSchedule.objects.get_or_create(
            minute=0,
            hour=0,
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
                "schedule": daily_midnight,
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
        ]

        for task_config in tasks:
            task, created = PeriodicTask.objects.get_or_create(
                name=task_config["name"],
                defaults={
                    "task": task_config["task"],
                    "crontab": (
                        task_config.get("schedule")
                        if isinstance(task_config["schedule"], CrontabSchedule)
                        else None
                    ),
                    "interval": (
                        task_config.get("schedule")
                        if isinstance(task_config["schedule"], IntervalSchedule)
                        else None
                    ),
                    "enabled": True,
                },
            )

            status = "Created" if created else "Updated"
            self.stdout.write(
                self.style.SUCCESS(f'{status} periodic task: {task_config["name"]}')
            )

        self.stdout.write(self.style.SUCCESS("Successfully setup all periodic tasks!"))
