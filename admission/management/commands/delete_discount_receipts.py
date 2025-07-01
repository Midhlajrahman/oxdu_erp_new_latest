from django.core.management.base import BaseCommand
from admission.models import FeeReceipt

class Command(BaseCommand):
    help = 'Delete all FeeReceipt objects with note="Discount Applied" or note="Discount".'

    def handle(self, *args, **options):
        count_applied = FeeReceipt.objects.filter(note="Discount Applied").count()
        count_discount = FeeReceipt.objects.filter(note="Discount").count()
        FeeReceipt.objects.filter(note__in=["Discount Applied", "Discount"]).delete()
        total = count_applied + count_discount
        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {total} discount FeeReceipt(s) ("Discount Applied": {count_applied}, "Discount": {count_discount}).')) 