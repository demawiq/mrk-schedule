from schedule_app.models import Group

group_order = [
    "5К9091", "5К9191", "5К9491", "4К9091", "4К9191", "4К9491", "3К9091", "3К9191", "2К9091", "2К9191",
    "5К9391", "5К9392", "5К9393", "4К9391", "4К9392", "4К9393", "4К9394", "3К9391", "3К9392", "3К9393",
    "3К9394", "3К9311", "2К9391", "2К9392", "2К9393", "2К9394", "5К9591", "5К9592", "5К9691", "5К9291",
    "5К9791", "4К9591", "4К9592", "4К9691", "4К9291", "3К9591", "3К9592", "3К9691", "3К9291", "2К9591",
    "2К9491", "5К9341", "5К9342", "4К9341", "4К9342", "3К9341", "3К9342", "2К9341"
]

for index, name in enumerate(group_order):
    Group.objects.filter(name=name).update(order=index)

# For any groups not in the list, they will have order 0 (default) or we can set them to a high number
max_order = len(group_order)
Group.objects.exclude(name__in=group_order).update(order=max_order)

print("Group ordering updated successfully.")
