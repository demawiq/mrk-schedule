from django.shortcuts import render, get_object_or_404, redirect
from .models import Schedule, Group, Teacher, Subject
from django import forms
from django.contrib.auth.decorators import login_required
from datetime import time as dt_time

class ScheduleForm(forms.ModelForm):
    new_subject = forms.CharField(max_length=100, required=False, label="Новый предмет (если нет в списке)")
    new_teacher = forms.CharField(max_length=100, required=False, label="Новый преподаватель 1 (если нет в списке)")
    new_teacher2 = forms.CharField(max_length=100, required=False, label="Новый преподаватель 2 (если нет в списке)")

    class Meta:
        model = Schedule
        fields = ['group', 'subject', 'new_subject', 'teacher', 'new_teacher', 'teacher2', 'new_teacher2', 'day_of_week', 'time', 'end_time', 'room', 'room2', 'note']
        widgets = {
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
            'note': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['subject'].required = False
        self.fields['teacher'].required = False

def get_period_info(lesson):
    hours = [
        (1, dt_time(8, 0), dt_time(8, 45)),
        (2, dt_time(8, 55), dt_time(9, 40)),
        (3, dt_time(9, 50), dt_time(10, 35)),
        (4, dt_time(10, 45), dt_time(11, 30)),
        (5, dt_time(11, 50), dt_time(12, 35)),
        (6, dt_time(12, 45), dt_time(13, 30)),
        (7, dt_time(13, 40), dt_time(14, 25)),
        (8, dt_time(14, 35), dt_time(15, 20)),
        (9, dt_time(15, 40), dt_time(16, 25)),
        (10, dt_time(16, 35), dt_time(17, 20)),
        (11, dt_time(17, 30), dt_time(18, 15)),
        (12, dt_time(18, 25), dt_time(19, 10)),
        (13, dt_time(19, 20), dt_time(20, 5)),
        (14, dt_time(20, 15), dt_time(21, 0)),
    ]
    start = lesson.time
    end = lesson.end_time or start
    lesson_hours = []
    for h_num, h_start, h_end in hours:
        if start < h_end and end > h_start:
            lesson_hours.append(h_num)
    if not lesson_hours:
        return None, []
    first_hour = lesson_hours[0]
    period_num = (first_hour + 1) // 2
    return period_num, lesson_hours

def handle_dynamic_fields(form):
    cleaned_data = form.cleaned_data
    subject = cleaned_data.get('subject')
    new_subject_title = cleaned_data.get('new_subject')
    if new_subject_title:
        subject, _ = Subject.objects.get_or_create(title=new_subject_title)
    teacher = cleaned_data.get('teacher')
    new_teacher_name = cleaned_data.get('new_teacher')
    if new_teacher_name:
        teacher, _ = Teacher.objects.get_or_create(name=new_teacher_name)
    teacher2 = cleaned_data.get('teacher2')
    new_teacher2_name = cleaned_data.get('new_teacher2')
    if new_teacher2_name:
        teacher2, _ = Teacher.objects.get_or_create(name=new_teacher2_name)
    return subject, teacher, teacher2

def public_schedule(request):
    group_id = request.GET.get('group')
    teacher_id = request.GET.get('teacher')
    day_filter = request.GET.get('day')
    groups = Group.objects.all()
    teachers = Teacher.objects.all().order_by('name')
    schedules = Schedule.objects.select_related('group', 'subject', 'teacher', 'teacher2').all().order_by('time')
    
    if group_id:
        schedules = schedules.filter(group_id=group_id)
    if teacher_id:
        schedules = schedules.filter(teacher_id=teacher_id)
    if day_filter:
        schedules = schedules.filter(day_of_week=day_filter)
    
    days = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
    day_names = {'Пн': 'Понедельник', 'Вт': 'Вторник', 'Ср': 'Среда', 'Чт': 'Четверг', 'Пт': 'Пятница', 'Сб': 'Суббота', 'Вс': 'Воскресенье'}
    period_range = range(1, 8)
    schedule_data = {}
    
    active_days = [day_filter] if day_filter else days
    
    for day in active_days:
        day_schedules = schedules.filter(day_of_week=day)
        if day_schedules.exists():
            schedule_data[day] = {'name': day_names[day], 'groups': {}}
            if teacher_id:
                active_groups = Group.objects.filter(id__in=day_schedules.values_list('group_id', flat=True).distinct())
            else:
                active_groups = groups.filter(id=group_id) if group_id else groups
            
            for group in active_groups:
                group_lessons = day_schedules.filter(group=group)
                if group_lessons.exists():
                    grid = {p: {1: None, 2: None, 'is_covered': False, 'colspan': 1} for p in period_range}
                    sorted_lessons = group_lessons.order_by('time')
                    for lesson in sorted_lessons:
                        p_num, lesson_hours = get_period_info(lesson)
                        if p_num and p_num in grid:
                            unique_periods = sorted(list(set((h + 1) // 2 for h in lesson_hours)))
                            start_p = unique_periods[0]
                            num_periods = len(unique_periods)
                            if not grid[start_p]['is_covered']:
                                if num_periods == 1:
                                    for h_num in lesson_hours:
                                        h_in_period = 1 if h_num % 2 != 0 else 2
                                        if not grid[start_p][h_in_period]:
                                            grid[start_p][h_in_period] = lesson
                                else:
                                    grid[start_p][1] = lesson
                                    grid[start_p][2] = lesson
                                    grid[start_p]['colspan'] = num_periods
                                    for next_p in unique_periods[1:]:
                                        if next_p in grid:
                                            grid[next_p]['is_covered'] = True
                    schedule_data[day]['groups'][group] = grid

    return render(request, 'schedule_app/public_schedule.html', {
        'schedule_data': schedule_data, 'groups': groups, 'teachers': teachers,
        'selected_group': int(group_id) if group_id else None,
        'selected_teacher': int(teacher_id) if teacher_id else None,
        'selected_day': day_filter,
        'days_list': [{'code': d, 'name': day_names[d]} for d in days],
        'period_range': period_range
    })

@login_required
def schedule_list(request):
    group_id = request.GET.get('group')
    teacher_id = request.GET.get('teacher')
    day_filter = request.GET.get('day')
    groups = Group.objects.all()
    teachers = Teacher.objects.all().order_by('name')
    schedules = Schedule.objects.select_related('group', 'subject', 'teacher', 'teacher2').all().order_by('time')
    
    if group_id:
        schedules = schedules.filter(group_id=group_id)
    if teacher_id:
        schedules = schedules.filter(teacher_id=teacher_id)
    if day_filter:
        schedules = schedules.filter(day_of_week=day_filter)
    
    days = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
    day_names = {'Пн': 'Понедельник', 'Вт': 'Вторник', 'Ср': 'Среда', 'Чт': 'Четверг', 'Пт': 'Пятница', 'Сб': 'Суббота', 'Вс': 'Воскресенье'}
    period_range = range(1, 8)
    schedule_data = {}
    
    active_days = [day_filter] if day_filter else days
    
    for day in active_days:
        day_schedules = schedules.filter(day_of_week=day)
        if day_schedules.exists():
            schedule_data[day] = {'name': day_names[day], 'groups': {}}
            if teacher_id:
                active_groups = Group.objects.filter(id__in=day_schedules.values_list('group_id', flat=True).distinct())
            else:
                active_groups = groups.filter(id=group_id) if group_id else groups
            
            for group in active_groups:
                group_lessons = day_schedules.filter(group=group)
                if group_lessons.exists():
                    grid = {p: {1: None, 2: None, 'is_covered': False, 'colspan': 1} for p in period_range}
                    sorted_lessons = group_lessons.order_by('time')
                    for lesson in sorted_lessons:
                        p_num, lesson_hours = get_period_info(lesson)
                        if p_num and p_num in grid:
                            unique_periods = sorted(list(set((h + 1) // 2 for h in lesson_hours)))
                            start_p = unique_periods[0]
                            num_periods = len(unique_periods)
                            if not grid[start_p]['is_covered']:
                                if num_periods == 1:
                                    for h_num in lesson_hours:
                                        h_in_period = 1 if h_num % 2 != 0 else 2
                                        if not grid[start_p][h_in_period]:
                                            grid[start_p][h_in_period] = lesson
                                else:
                                    grid[start_p][1] = lesson
                                    grid[start_p][2] = lesson
                                    grid[start_p]['colspan'] = num_periods
                                    for next_p in unique_periods[1:]:
                                        if next_p in grid:
                                            grid[next_p]['is_covered'] = True
                    schedule_data[day]['groups'][group] = grid

    return render(request, 'schedule_app/schedule_list.html', {
        'schedule_data': schedule_data, 'groups': groups, 'teachers': teachers,
        'selected_group': int(group_id) if group_id else None,
        'selected_teacher': int(teacher_id) if teacher_id else None,
        'selected_day': day_filter,
        'days_list': [{'code': d, 'name': day_names[d]} for d in days],
        'period_range': period_range
    })

@login_required
def schedule_add(request):
    error_message = None
    if request.method == 'POST':
        form = ScheduleForm(request.POST)
        if form.is_valid():
            subject, teacher, teacher2 = handle_dynamic_fields(form)
            if not subject or not teacher:
                error_message = "Ошибка: Необходимо выбрать или вписать предмет и основного преподавателя."
            else:
                instance = form.save(commit=False)
                instance.subject = subject
                instance.teacher = teacher
                instance.teacher2 = teacher2
                instance.save()
                return redirect('schedule_list')
    else:
        form = ScheduleForm()
    return render(request, 'schedule_app/schedule_form.html', {'form': form, 'title': 'Добавить занятие', 'error_message': error_message})

@login_required
def schedule_edit(request, pk):
    schedule = get_object_or_404(Schedule, pk=pk)
    error_message = None
    if request.method == 'POST':
        form = ScheduleForm(request.POST, instance=schedule)
        if form.is_valid():
            subject, teacher, teacher2 = handle_dynamic_fields(form)
            if not subject or not teacher:
                error_message = "Ошибка: Необходимо выбрать или вписать предмет и основного преподавателя."
            else:
                instance = form.save(commit=False)
                instance.subject = subject
                instance.teacher = teacher
                instance.teacher2 = teacher2
                instance.save()
                return redirect('schedule_list')
    else:
        form = ScheduleForm(instance=schedule)
    return render(request, 'schedule_app/schedule_form.html', {'form': form, 'title': 'Редактировать занятие', 'error_message': error_message, 'schedule': schedule})

@login_required
def schedule_delete(request, pk):
    schedule = get_object_or_404(Schedule, pk=pk)
    if request.method == 'POST':
        schedule.delete()
        return redirect('schedule_list')
    return render(request, 'schedule_app/schedule_confirm_delete.html', {'schedule': schedule})

@login_required
def teacher_list(request):
    teachers = Teacher.objects.all().order_by('name')
    error_message = None
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            if Teacher.objects.filter(name=name).exists():
                error_message = f"Ошибка: Преподаватель '{name}' уже есть в списке!"
            else:
                Teacher.objects.create(name=name)
                return redirect('teacher_list')
    return render(request, 'schedule_app/teacher_list.html', {'teachers': teachers, 'error_message': error_message})

@login_required
def teacher_edit(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    error_message = None
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            if Teacher.objects.filter(name=name).exclude(pk=pk).exists():
                error_message = f"Ошибка: Преподаватель с именем '{name}' уже существует!"
            else:
                teacher.name = name
                teacher.save()
                return redirect('teacher_list')
    return render(request, 'schedule_app/teacher_form.html', {'teacher': teacher, 'error_message': error_message})

@login_required
def teacher_delete(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    if request.method == 'POST':
        teacher.delete()
        return redirect('teacher_list')
    return render(request, 'schedule_app/teacher_confirm_delete.html', {'teacher': teacher})

@login_required
def subject_list(request):
    subjects = Subject.objects.all().order_by('title')
    error_message = None
    if request.method == 'POST':
        title = request.POST.get('title')
        if title:
            if Subject.objects.filter(title=title).exists():
                error_message = f"Ошибка: Предмет '{title}' уже существует!"
            else:
                Subject.objects.create(title=title)
                return redirect('subject_list')
    return render(request, 'schedule_app/subject_list.html', {'subjects': subjects, 'error_message': error_message})

@login_required
def subject_edit(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    error_message = None
    if request.method == 'POST':
        title = request.POST.get('title')
        if title:
            if Subject.objects.filter(title=title).exclude(pk=pk).exists():
                error_message = f"Ошибка: Предмет с названием '{title}' уже существует!"
            else:
                subject.title = title
                subject.save()
                return redirect('subject_list')
    return render(request, 'schedule_app/subject_form.html', {'subject': subject, 'error_message': error_message})

@login_required
def subject_delete(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    if request.method == 'POST':
        subject.delete()
        return redirect('subject_list')
    return render(request, 'schedule_app/subject_confirm_delete.html', {'subject': subject})

@login_required
def group_list(request):
    groups = Group.objects.all()
    error_message = None
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            if Group.objects.filter(name=name).exists():
                error_message = f"Ошибка: Группа '{name}' уже создана!"
            else:
                Group.objects.create(name=name)
                return redirect('group_list')
    return render(request, 'schedule_app/group_list.html', {'groups': groups, 'error_message': error_message})

@login_required
def group_edit(request, pk):
    group = get_object_or_404(Group, pk=pk)
    error_message = None
    if request.method == 'POST':
        name = request.POST.get('name')
        order = request.POST.get('order')
        if name:
            if Group.objects.filter(name=name).exclude(pk=pk).exists():
                error_message = f"Ошибка: Группа с названием '{name}' уже существует!"
            else:
                group.name = name
                if order:
                    group.order = int(order)
                group.save()
                return redirect('group_list')
    return render(request, 'schedule_app/group_form.html', {'group': group, 'error_message': error_message})

@login_required
def group_delete(request, pk):
    group = get_object_or_404(Group, pk=pk)
    if request.method == 'POST':
        group.delete()
        return redirect('group_list')
    return render(request, 'schedule_app/group_confirm_delete.html', {'group': group})
