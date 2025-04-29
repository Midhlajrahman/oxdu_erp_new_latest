from .models import Employee


def generate_employee_id():
    # Filter out employees where `employee_id` is None and where the employee is inactive
    employee_ids = [int(employee.employee_id) for employee in Employee.objects.exclude(employee_id__isnull=True).filter(is_active=True)]

    # If there are no valid employee IDs, start with "0001"
    if not employee_ids:
        next_employee_id = "0001"
    else:
        # Get the maximum employee ID and increment it by 1
        max_employee_id = max(employee_ids)
        next_employee_id = str(max_employee_id + 1).zfill(4)

    return next_employee_id
