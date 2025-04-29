from core.base import BaseModel
from core.choices import PAYMENT_STATUS

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MaxValueValidator
from django.core.validators import MinValueValidator
from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse_lazy
from django.utils import timezone


class Transaction(BaseModel):
    transaction_type = models.CharField(max_length=7, choices=[("RECEIPT", "RECEIPT"), ("PAYMENT", "PAYMENT"), ("JV", "JV")])
    payment_method = models.CharField(max_length=4, choices=[("BANK", "BANK"), ("CASH", "CASH")], verbose_name="Payment Method", null=True)
    branch = models.ForeignKey('branches.Branch', on_delete=models.CASCADE, null=True)
    date = models.DateField(default=timezone.now)
    main_account = models.ForeignKey('accounting.Account', on_delete=models.PROTECT, related_name="main_acc")
    opposite_account = models.ForeignKey('accounting.Account', on_delete=models.PROTECT, related_name="opp_acc")

    voucher_no = models.CharField(max_length=50, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    # cash
    document_no = models.CharField(max_length=30, null=True, blank=True)
    document_date = models.DateField(null=True, blank=True)
    is_denomination = models.BooleanField(default=False)
    denomination = models.JSONField(null=True)
    # bank
    cheque_no = models.CharField(max_length=20, null=True, blank=True, verbose_name="Chq/DD No.")
    cheque_date = models.DateField(null=True, blank=True, verbose_name="Chq/DD Date.")
    cheque_name = models.CharField(max_length=50, null=True, blank=True)
    transfer_method = models.CharField(max_length=20, choices=[("Online", "Online"), ("UPI", "UPI")], null=True, blank=True)
    #
    reference = models.CharField(max_length=15, choices=[("against", "Against Reference"), ("not_applicable", "Not Applicable")])
    narration = models.TextField(null=True, blank=True)
    remark = models.TextField(null=True, blank=True)

    def __str__(self):
        direction = "credited to" if self.transaction_type == "RECEIPT" else "debited from"
        counterparty = "from" if self.transaction_type == "RECEIPT" else "to"
        date_str = self.date.strftime('%d/%m/%Y') if self.date else "No Date"

        return f"{self.amount} {direction} {self.main_account} {counterparty} {self.opposite_account} on {date_str}"

    class Meta(BaseModel.Meta):
        unique_together = ("transaction_type", "voucher_no")

    def get_update_url(self):
        if self.transaction_type == 'RECEIPT':
            if self.payment_method == 'BANK':
                return reverse_lazy("transactions:bank_receipt_update", kwargs={'pk': self.pk})
            return reverse_lazy("transactions:cash_receipt_update", kwargs={'pk': self.pk})
        else:
            if self.payment_method == 'BANK':
                return reverse_lazy("transactions:bank_payment_update", kwargs={'pk': self.pk})
            return reverse_lazy("transactions:cash_payment_update", kwargs={'pk': self.pk})


class TransactionItem(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to={'model__in': ('saleinvoice', 'purchase')}, verbose_name="Type", null=True)
    object_id = models.PositiveIntegerField(null=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Transaction Entry"
        verbose_name_plural = "Transaction Entries"

    def save(self, *args, **kwargs):
        if self.content_object:
            if self.content_type.model == 'saleinvoice' and hasattr(self.content_object, 'received'):
                self.content_object.received += self.amount
                self.content_object.save(update_fields=['received'])
            elif self.content_type.model == 'purchase' and hasattr(self.content_object, 'paid'):
                self.content_object.paid += self.amount
                self.content_object.save(update_fields=['paid'])

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.transaction.amount -= self.amount
        self.transaction.save(update_fields=['amount'])
        if self.content_object:
            if self.content_type.model == 'saleinvoice' and hasattr(self.content_object, 'received'):
                self.content_object.received -= self.amount
                self.content_object.save(update_fields=['received'])
            elif self.content_type.model == 'purchase' and hasattr(self.content_object, 'paid'):
                self.content_object.paid -= self.amount
                self.content_object.save(update_fields=['paid'])
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.content_object} - {self.amount}"


def next_expense_no():
    max_expense_no = Expense.objects.aggregate(models.Max("expense_no"))["expense_no__max"]
    if max_expense_no in (None, ""):
        expense_no = 1
    else:
        expense_no = int(max_expense_no) + 1
    return str(expense_no).zfill(4)


class Expense(BaseModel):
    branch = models.ForeignKey('branches.Branch', on_delete=models.CASCADE, null=True)
    expense_no_regex = RegexValidator(regex=r'^\d{4,}$', message="Expense number must be at least 4 digits.")
    is_gst = models.BooleanField(default=False)
    expense_category = models.ForeignKey('accounting.Account', on_delete=models.CASCADE)
    expense_no = models.CharField(max_length=30, default=next_expense_no, validators=[expense_no_regex])
    bill_date = models.DateField(default=timezone.now)
    party = models.ForeignKey('accounting.Account', verbose_name="Party A/C", on_delete=models.CASCADE, null=True, blank=True, related_name="party_expenses")
    discount_percentage = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, validators=[MaxValueValidator(100), MinValueValidator(0)])
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    auto_round_off = models.BooleanField("Round Off", default=False, null=True, blank=True)
    round_off_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    taxable_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_tax_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    items_discount_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sub_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='paid')

    def __str__(self):
        if self.party:
            return f"{self.expense_category.name} - {self.party.name} - {self.expense_no}"
        return f"{self.expense_category.name} - {self.expense_no}"

    def calculate_total(self):
        # Get all associated ExpenseItem instances
        expense_items = self.expenseitem_set.all()

        # Sum up the line_total of all ExpenseItem instances
        subtotal = sum(item.line_total for item in expense_items)

        self.discount_amount = self.discount_amount or 0
        self.round_off = self.round_off or 0

        # Calculate the total after applying the discount
        total_after_discount = subtotal - self.discount_amount + self.round_off

        return total_after_discount

    def save(self, *args, **kwargs):
        if not self.pk:
            super().save(*args, **kwargs)
        self.grand_total = self.calculate_total()
        super().save(*args, **kwargs)


class Item(BaseModel):
    expense_category = models.ForeignKey('accounting.Account', on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=128, unique=True)
    hsn_or_sac = models.CharField(max_length=50, verbose_name="HSN/SAC Code", null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Price")
    tax_included = models.BooleanField(default=False, verbose_name="Tax Included", choices=[(True, "Including Tax"), (False, "Excluding Tax")])
    price_with_out_tax = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.name

    def calculate_price_without_tax(self):
        if not self.tax:
            raise ValueError("Tax information is required to calculate price without tax.")

        tax_rate = self.tax / 100  # Convert tax rate from percentage to decimal
        if self.tax_included:
            # Calculate price without tax when tax is included
            self.price_with_out_tax = self.price / (1 + tax_rate)
        else:
            # Set price without tax equal to price directly
            self.price_with_out_tax = self.price
        return self.price_with_out_tax

    def save(self, *args, **kwargs):
        self.calculate_price_without_tax()
        super().save(*args, **kwargs)


class ExpenseItem(models.Model):
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percentage = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, validators=[MaxValueValidator(100), MinValueValidator(0)])
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tax = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    line_total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.expense} - {self.item}"

    def save(self, *args, **kwargs):
        # Calculate base total (quantity * unit_price)
        base_total = self.quantity * self.unit_price

        # Calculate discount amount if discount_percentage is set
        if self.discount_percentage:
            self.discount_amount = (base_total * self.discount_percentage) / 100
        else:
            self.discount_amount = self.discount_amount or 0  # Default to 0 if not set

        # Subtract discount from base total
        discounted_total = base_total - self.discount_amount

        # Calculate tax amount if tax is set
        if self.tax:
            tax_rate = self.tax.rate / 100  # Convert tax rate from percentage to decimal
            self.tax_amount = discounted_total * tax_rate
        else:
            self.tax_amount = 0  # Default to 0 if no tax is applied

        # Calculate final line total
        self.line_total = discounted_total + self.tax_amount

        super().save(*args, **kwargs)
