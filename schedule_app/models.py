from django.db import models

class Teacher(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="ФИО преподавателя")

    def __str__(self):
        return self.name

class Subject(models.Model):
    title = models.CharField(max_length=100, unique=True, verbose_name="Название предмета")

    def __str__(self):
        return self.title

class Group(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Название группы")
    order = models.IntegerField(default=0, verbose_name="Порядок сортировки")

    class Meta:
        ordering = ['order', 'name']
        verbose_name = "Группа"
        verbose_name_plural = "Группы"

    def __str__(self):
        return self.name

class Schedule(models.Model):
    DAYS_OF_WEEK = [
        ('Пн', 'Понедельник'),
        ('Вт', 'Вторник'),
        ('Ср', 'Среда'),
        ('Чт', 'Четверг'),
        ('Пт', 'Пятница'),
        ('Сб', 'Суббота'),
        ('Вс', 'Воскресенье'),
    ]
    group = models.ForeignKey(Group, on_delete=models.CASCADE, verbose_name="Группа")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name="Предмет")
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='schedules_1', verbose_name="Преподаватель 1")
    teacher2 = models.ForeignKey(Teacher, on_delete=models.SET_NULL, related_name='schedules_2', blank=True, null=True, verbose_name="Преподаватель 2")
    day_of_week = models.CharField(max_length=10, choices=DAYS_OF_WEEK, verbose_name="День недели")
    time = models.TimeField(verbose_name="Время начала")
    end_time = models.TimeField(verbose_name="Время окончания", blank=True, null=True)
    room = models.CharField(max_length=20, blank=True, null=True, verbose_name="Кабинет 1")
    room2 = models.CharField(max_length=20, blank=True, null=True, verbose_name="Кабинет 2")
    note = models.TextField(blank=True, null=True, verbose_name="Заметка")

    class Meta:
        # unique_together = ('group', 'day_of_week', 'time') # Removed to allow sub-lessons
        verbose_name = "Занятие"
        verbose_name_plural = "Занятия"

    def __str__(self):
        return f"{self.group} - {self.subject} ({self.day_of_week} {self.time})"
