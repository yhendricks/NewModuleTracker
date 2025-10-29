from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Q
from .models import TestConfigType, TestStep


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
        
        # Create associated steps from form data
        create_associated_steps(test_config, request.POST)
        
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
        
        # Update associated steps
        # First, clear all existing related steps
        test_config.steps.all().delete()
        
        # Then create new ones from form data
        create_associated_steps(test_config, request.POST)
        
        messages.success(request, f'Test Config Type "{test_config.name}" updated successfully.')
        return redirect('test_config_type_list')
    
    # Return JSON for modal
    if request.GET.get('format') == 'json':
        # Get all related steps
        steps = [{
            'id': step.id,
            'step_type': step.step_type,
            'order': step.order,
            'parameter_name': step.parameter_name,
            'min_value': step.min_value,
            'max_value': step.max_value,
            'unit': step.unit,
            'question_text': step.question_text,
            'required_answer': step.required_answer,
            'instruction_text': step.instruction_text,
        } for step in test_config.steps.all()]
        
        return JsonResponse({
            'id': test_config.id,
            'name': test_config.name,
            'description': test_config.description,
            'steps': steps
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


def create_associated_steps(test_config, post_data):
    """Helper function to create associated steps from POST data"""
    # Get all step-related field indices to determine the sequence
    step_indices = set()
    
    # Collect all step indices from the form data
    for key in post_data.keys():
        if key.startswith('step_type_'):
            index = key.split('_')[-1]
            step_indices.add(index)
    
    # Sort indices to maintain order
    sorted_indices = sorted(step_indices, key=int)
    
    # Create steps based on the order they appear
    for i, idx in enumerate(sorted_indices, start=1):
        step_type = post_data.get(f'step_type_{idx}')
        
        if step_type == 'VOLTAGE':
            param_name = post_data.get(f'voltage_param_name_{idx}')
            min_val = post_data.get(f'voltage_min_{idx}')
            max_val = post_data.get(f'voltage_max_{idx}')
            unit = post_data.get(f'voltage_unit_{idx}', 'V')
            
            if param_name and min_val not in [None, ''] and max_val not in [None, '']:
                try:
                    min_val = float(min_val)
                    max_val = float(max_val)
                    TestStep.objects.create(
                        test_config=test_config,
                        step_type=step_type,
                        order=i,
                        parameter_name=param_name,
                        min_value=min_val,
                        max_value=max_val,
                        unit=unit
                    )
                except ValueError:
                    # Skip invalid values
                    pass
                    
        elif step_type == 'CURRENT':
            param_name = post_data.get(f'current_param_name_{idx}')
            min_val = post_data.get(f'current_min_{idx}')
            max_val = post_data.get(f'current_max_{idx}')
            unit = post_data.get(f'current_unit_{idx}', 'A')
            
            if param_name and min_val not in [None, ''] and max_val not in [None, '']:
                try:
                    min_val = float(min_val)
                    max_val = float(max_val)
                    TestStep.objects.create(
                        test_config=test_config,
                        step_type=step_type,
                        order=i,
                        parameter_name=param_name,
                        min_value=min_val,
                        max_value=max_val,
                        unit=unit
                    )
                except ValueError:
                    # Skip invalid values
                    pass
                    
        elif step_type == 'RESISTANCE':
            param_name = post_data.get(f'resistance_param_name_{idx}')
            min_val = post_data.get(f'resistance_min_{idx}')
            max_val = post_data.get(f'resistance_max_{idx}')
            unit = post_data.get(f'resistance_unit_{idx}', 'Ω')
            
            if param_name and min_val not in [None, ''] and max_val not in [None, '']:
                try:
                    min_val = float(min_val)
                    max_val = float(max_val)
                    TestStep.objects.create(
                        test_config=test_config,
                        step_type=step_type,
                        order=i,
                        parameter_name=param_name,
                        min_value=min_val,
                        max_value=max_val,
                        unit=unit
                    )
                except ValueError:
                    # Skip invalid values
                    pass
                    
        elif step_type == 'FREQUENCY':
            param_name = post_data.get(f'frequency_param_name_{idx}')
            min_val = post_data.get(f'frequency_min_{idx}')
            max_val = post_data.get(f'frequency_max_{idx}')
            unit = post_data.get(f'frequency_unit_{idx}', 'Hz')
            
            if param_name and min_val not in [None, ''] and max_val not in [None, '']:
                try:
                    min_val = float(min_val)
                    max_val = float(max_val)
                    TestStep.objects.create(
                        test_config=test_config,
                        step_type=step_type,
                        order=i,
                        parameter_name=param_name,
                        min_value=min_val,
                        max_value=max_val,
                        unit=unit
                    )
                except ValueError:
                    # Skip invalid values
                    pass
        
        elif step_type == 'QUESTION':
            question_text = post_data.get(f'question_text_{idx}')
            required_answer = post_data.get(f'question_required_{idx}')
            
            if question_text:
                required_bool = required_answer == 'true' or required_answer == 'True' or required_answer == '1'
                TestStep.objects.create(
                    test_config=test_config,
                    step_type=step_type,
                    order=i,
                    question_text=question_text,
                    required_answer=required_bool
                )
        
        elif step_type == 'INSTRUCTION':
            instruction_text = post_data.get(f'instruction_text_{idx}')
            
            if instruction_text:
                TestStep.objects.create(
                    test_config=test_config,
                    step_type=step_type,
                    order=i,
                    instruction_text=instruction_text
                )