from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Q
from .models import TestConfigType, VoltageMeasurement, CurrentMeasurement, YesNoQuestion, ResistanceMeasurement, FrequencyMeasurement


@login_required
@permission_required('test_config_type_app.view_testconfigtype', raise_exception=True)
def test_config_type_list(request):
    """Display list of Test Config Types with search and pagination"""
    test_configs = TestConfigType.objects.all().order_by('name')
    
    # Handle search/filter
    search_query = request.GET.get('search', '')
    if search_query:
        test_configs = test_configs.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(test_configs, 10)  # Show 10 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'test_configs': page_obj,
        'search_query': search_query,
    }
    return render(request, 'test_config_type_app/test_config_type_list.html', context)


@login_required
@permission_required('test_config_type_app.add_testconfigtype', raise_exception=True)
def test_config_type_create(request):
    """Create a new Test Config Type"""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        
        # Check if name already exists
        if TestConfigType.objects.filter(name__iexact=name).exists():
            messages.error(request, 'A Test Config Type with this name already exists.')
            return redirect('test_config_type_list')
        
        test_config = TestConfigType.objects.create(name=name, description=description)
        
        # Create associated measurements and questions from form data
        create_associated_measurements(test_config, request.POST)
        
        messages.success(request, f'Test Config Type "{test_config.name}" created successfully.')
        return redirect('test_config_type_list')
    
    return redirect('test_config_type_list')


@login_required
@permission_required('test_config_type_app.change_testconfigtype', raise_exception=True)
def test_config_type_update(request, pk):
    """Update an existing Test Config Type"""
    test_config = get_object_or_404(TestConfigType, pk=pk)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        
        # Check if name already exists (excluding current item)
        if TestConfigType.objects.filter(name__iexact=name).exclude(pk=pk).exists():
            messages.error(request, 'A Test Config Type with this name already exists.')
            return redirect('test_config_type_list')
        
        test_config.name = name
        test_config.description = description
        test_config.save()
        
        # Update associated measurements and questions
        # First, clear all existing related measurements
        test_config.voltage_measurements.all().delete()
        test_config.current_measurements.all().delete()
        test_config.yes_no_questions.all().delete()
        test_config.resistance_measurements.all().delete()
        test_config.frequency_measurements.all().delete()
        
        # Then create new ones from form data
        create_associated_measurements(test_config, request.POST)
        
        messages.success(request, f'Test Config Type "{test_config.name}" updated successfully.')
        return redirect('test_config_type_list')
    
    # Return JSON for modal
    if request.GET.get('format') == 'json':
        # Get all related measurements
        voltage_measurements = [{
            'id': vm.id,
            'parameter_name': vm.parameter_name,
            'min_value': vm.min_value,
            'max_value': vm.max_value,
            'unit': vm.unit
        } for vm in test_config.voltage_measurements.all()]
        
        current_measurements = [{
            'id': cm.id,
            'parameter_name': cm.parameter_name,
            'min_value': cm.min_value,
            'max_value': cm.max_value,
            'unit': cm.unit
        } for cm in test_config.current_measurements.all()]
        
        yes_no_questions = [{
            'id': qn.id,
            'question_text': qn.question_text,
            'required_answer': qn.required_answer
        } for qn in test_config.yes_no_questions.all()]
        
        resistance_measurements = [{
            'id': rm.id,
            'parameter_name': rm.parameter_name,
            'min_value': rm.min_value,
            'max_value': rm.max_value,
            'unit': rm.unit
        } for rm in test_config.resistance_measurements.all()]
        
        frequency_measurements = [{
            'id': fm.id,
            'parameter_name': fm.parameter_name,
            'min_value': fm.min_value,
            'max_value': fm.max_value,
            'unit': fm.unit
        } for fm in test_config.frequency_measurements.all()]
        
        return JsonResponse({
            'id': test_config.id,
            'name': test_config.name,
            'description': test_config.description,
            'voltage_measurements': voltage_measurements,
            'current_measurements': current_measurements,
            'yes_no_questions': yes_no_questions,
            'resistance_measurements': resistance_measurements,
            'frequency_measurements': frequency_measurements
        })
    
    return redirect('test_config_type_list')


@login_required
@permission_required('test_config_type_app.delete_testconfigtype', raise_exception=True)
def test_config_type_delete(request, pk):
    """Delete a Test Config Type"""
    test_config = get_object_or_404(TestConfigType, pk=pk)
    
    # Check if confirmation name matches
    confirm_name = request.POST.get('confirm_name', '')
    if confirm_name != test_config.name:
        messages.error(request, 'Confirmation name does not match. Deletion cancelled.')
        return redirect('test_config_type_list')
    
    test_config_name = test_config.name
    test_config.delete()
    messages.success(request, f'Test Config Type "{test_config_name}" deleted successfully.')
    return redirect('test_config_type_list')


@login_required
@permission_required('test_config_type_app.view_testconfigtype', raise_exception=True)
def test_config_type_detail(request, pk):
    """View details of a specific Test Config Type"""
    test_config = get_object_or_404(TestConfigType, pk=pk)
    context = {
        'test_config': test_config
    }
    return render(request, 'test_config_type_app/test_config_type_detail.html', context)


def create_associated_measurements(test_config, post_data):
    """Helper function to create associated measurements and questions from POST data"""
    # Process voltage measurements
    voltage_count = int(post_data.get('voltage_count', 0))
    for i in range(voltage_count):
        param_name = post_data.get(f'voltage_param_name_{i}')
        min_val = post_data.get(f'voltage_min_{i}')
        max_val = post_data.get(f'voltage_max_{i}')
        unit = post_data.get(f'voltage_unit_{i}', 'V')
        
        if param_name and min_val is not None and max_val is not None:
            try:
                min_val = float(min_val)
                max_val = float(max_val)
                VoltageMeasurement.objects.create(
                    test_config=test_config,
                    parameter_name=param_name,
                    min_value=min_val,
                    max_value=max_val,
                    unit=unit
                )
            except ValueError:
                # Skip invalid values
                pass

    # Process current measurements
    current_count = int(post_data.get('current_count', 0))
    for i in range(current_count):
        param_name = post_data.get(f'current_param_name_{i}')
        min_val = post_data.get(f'current_min_{i}')
        max_val = post_data.get(f'current_max_{i}')
        unit = post_data.get(f'current_unit_{i}', 'A')
        
        if param_name and min_val is not None and max_val is not None:
            try:
                min_val = float(min_val)
                max_val = float(max_val)
                CurrentMeasurement.objects.create(
                    test_config=test_config,
                    parameter_name=param_name,
                    min_value=min_val,
                    max_value=max_val,
                    unit=unit
                )
            except ValueError:
                # Skip invalid values
                pass

    # Process yes/no questions
    question_count = int(post_data.get('question_count', 0))
    for i in range(question_count):
        question_text = post_data.get(f'question_text_{i}')
        required_answer = post_data.get(f'question_required_{i}')
        
        if question_text and required_answer is not None:
            required_bool = required_answer == 'true' or required_answer == 'True' or required_answer == '1'
            YesNoQuestion.objects.create(
                test_config=test_config,
                question_text=question_text,
                required_answer=required_bool
            )

    # Process resistance measurements
    resistance_count = int(post_data.get('resistance_count', 0))
    for i in range(resistance_count):
        param_name = post_data.get(f'resistance_param_name_{i}')
        min_val = post_data.get(f'resistance_min_{i}')
        max_val = post_data.get(f'resistance_max_{i}')
        unit = post_data.get(f'resistance_unit_{i}', 'Ω')
        
        if param_name and min_val is not None and max_val is not None:
            try:
                min_val = float(min_val)
                max_val = float(max_val)
                ResistanceMeasurement.objects.create(
                    test_config=test_config,
                    parameter_name=param_name,
                    min_value=min_val,
                    max_value=max_val,
                    unit=unit
                )
            except ValueError:
                # Skip invalid values
                pass

    # Process frequency measurements
    frequency_count = int(post_data.get('frequency_count', 0))
    for i in range(frequency_count):
        param_name = post_data.get(f'frequency_param_name_{i}')
        min_val = post_data.get(f'frequency_min_{i}')
        max_val = post_data.get(f'frequency_max_{i}')
        unit = post_data.get(f'frequency_unit_{i}', 'Hz')
        
        if param_name and min_val is not None and max_val is not None:
            try:
                min_val = float(min_val)
                max_val = float(max_val)
                FrequencyMeasurement.objects.create(
                    test_config=test_config,
                    parameter_name=param_name,
                    min_value=min_val,
                    max_value=max_val,
                    unit=unit
                )
            except ValueError:
                # Skip invalid values
                pass