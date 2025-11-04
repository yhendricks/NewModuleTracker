from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from .models import PcbTestResult, VoltageMeasurementResult, CurrentMeasurementResult, ResistanceMeasurementResult, FrequencyMeasurementResult, YesNoQuestionResult, InstructionResult, QaSignoff
from batch_app.models import Pcb, Batch
from test_config_type_app.models import TestConfigType, TestStep
from django.contrib.auth.models import User, Group


@login_required
@permission_required('pcb_test_result_app.view_pcbtestresult', raise_exception=True)
def pcb_test_result_list(request):
    """Display list of PCB Test Results with search and filtering"""
    # Get the ordering parameter from the request
    order_by = request.GET.get('order_by', '-test_date')  # Default to descending date

    # Define valid ordering fields to prevent injection
    valid_order_fields = ['test_date', '-test_date', 'pcb__serial_number', '-pcb__serial_number',
                          'technician__username', '-technician__username', 'result', '-result']

    if order_by not in valid_order_fields:
        order_by = '-test_date'  # Default if invalid field provided

    test_results = PcbTestResult.objects.select_related('pcb', 'technician', 'qa_signoff', 'qa_signoff__qa_user').order_by(order_by)

    # Handle search/filter
    search_query = request.GET.get('search', '')
    if search_query:
        test_results = test_results.filter(
            Q(pcb__serial_number__icontains=search_query) |
            Q(technician__username__icontains=search_query) |
            Q(result__icontains=search_query)
        )

    # Filter by PCB if specified
    pcb_id = request.GET.get('pcb_id', '')
    if pcb_id:
        test_results = test_results.filter(pcb_id=pcb_id)

    # Filter by technician if specified
    technician_id = request.GET.get('technician_id', '')
    if technician_id:
        test_results = test_results.filter(technician_id=technician_id)

    # Get all PCBs and technicians for filter dropdowns
    pcbs = Pcb.objects.all().order_by('serial_number')
    technicians = User.objects.filter(groups__name='add_board_bringup_result').distinct().order_by('username')

    context = {
        'test_results': test_results,
        'search_query': search_query,
        'pcb_id': pcb_id,
        'technician_id': technician_id,
        'pcbs': pcbs,
        'technicians': technicians,
        'current_order': order_by,  # Pass current order to template
    }
    return render(request, 'pcb_test_result_app/pcb_test_result_list.html', context)


@login_required
@permission_required('pcb_test_result_app.add_pcbtestresult', raise_exception=True)
def pcb_test_result_create(request):
    """Create a new PCB Test Result - Step 1: Select PCB"""
    if request.method == 'POST':
        pcb_id = request.POST.get('pcb_id')
        try:
            pcb = get_object_or_404(Pcb, id=pcb_id)
            # Redirect to the first step of the test process
            return redirect('pcb_test_execute_steps', pcb_id=pcb.id)
        except Exception as e:
            messages.error(request, f'Error selecting PCB: {str(e)}')
            return redirect('pcb_test_result_create')

    # GET request - show form to select PCB
    batches = Batch.objects.all().prefetch_related('pcbs').order_by('-created_at')

    context = {
        'batches': batches,
    }
    return render(request, 'pcb_test_result_app/pcb_test_select.html', context)


@login_required
@permission_required('pcb_test_result_app.add_pcbtestresult', raise_exception=True)
def pcb_test_execute_steps(request, pcb_id):
    """Execute test steps for a specific PCB based on its test configuration"""
    pcb = get_object_or_404(Pcb, id=pcb_id)
    test_config = pcb.batch.test_config_type
    test_steps = test_config.steps.all().order_by('order')

    # If no results exist, create a new test result
    if 'current_test_result_id' not in request.session:
        test_result = PcbTestResult.objects.create(
            pcb=pcb,
            technician=request.user
        )
        request.session['current_test_result_id'] = test_result.id
    else:
        test_result_id = request.session['current_test_result_id']
        try:
            test_result = PcbTestResult.objects.get(id=test_result_id)
        except PcbTestResult.DoesNotExist:
            # If the test result was deleted or session is invalid, create a new one
            test_result = PcbTestResult.objects.create(
                pcb=pcb,
                technician=request.user
            )
            request.session['current_test_result_id'] = test_result.id

    # Process any submitted step before displaying the next one
    if request.method == 'POST':
        step_id = request.POST.get('step_id')
        step = get_object_or_404(TestStep, id=step_id)

        # Process the step result
        if step.step_type == 'VOLTAGE':
            measured_value = request.POST.get('measured_value')
            if measured_value:
                try:
                    measured_value = float(measured_value)
                    passed = step.min_value <= measured_value <= step.max_value
                    VoltageMeasurementResult.objects.create(
                        test_result=test_result,
                        parameter_name=step.parameter_name,
                        measured_value=measured_value,
                        unit=step.unit or 'V',
                        min_value=step.min_value,
                        max_value=step.max_value,
                        passed=passed
                    )
                except ValueError:
                    messages.error(request, f'Invalid voltage value: {measured_value}')
        elif step.step_type == 'CURRENT':
            measured_value = request.POST.get('measured_value')
            if measured_value:
                try:
                    measured_value = float(measured_value)
                    passed = step.min_value <= measured_value <= step.max_value
                    CurrentMeasurementResult.objects.create(
                        test_result=test_result,
                        parameter_name=step.parameter_name,
                        measured_value=measured_value,
                        unit=step.unit or 'A',
                        min_value=step.min_value,
                        max_value=step.max_value,
                        passed=passed
                    )
                except ValueError:
                    messages.error(request, f'Invalid current value: {measured_value}')
        elif step.step_type == 'RESISTANCE':
            measured_value = request.POST.get('measured_value')
            if measured_value:
                try:
                    measured_value = float(measured_value)
                    passed = step.min_value <= measured_value <= step.max_value
                    ResistanceMeasurementResult.objects.create(
                        test_result=test_result,
                        parameter_name=step.parameter_name,
                        measured_value=measured_value,
                        unit=step.unit or 'Ω',
                        min_value=step.min_value,
                        max_value=step.max_value,
                        passed=passed
                    )
                except ValueError:
                    messages.error(request, f'Invalid resistance value: {measured_value}')
        elif step.step_type == 'FREQUENCY':
            measured_value = request.POST.get('measured_value')
            if measured_value:
                try:
                    measured_value = float(measured_value)
                    passed = step.min_value <= measured_value <= step.max_value
                    FrequencyMeasurementResult.objects.create(
                        test_result=test_result,
                        parameter_name=step.parameter_name,
                        measured_value=measured_value,
                        unit=step.unit or 'Hz',
                        min_value=step.min_value,
                        max_value=step.max_value,
                        passed=passed
                    )
                except ValueError:
                    messages.error(request, f'Invalid frequency value: {measured_value}')
        elif step.step_type == 'QUESTION':
            user_answer = request.POST.get('user_answer')
            if user_answer:  # Check if not empty string, None, or False
                user_bool = user_answer.lower() in ['true', '1', 'yes']  # Handle various true values
                required_bool = step.required_answer
                passed = user_bool == required_bool
                YesNoQuestionResult.objects.create(
                    test_result=test_result,
                    question_text=step.question_text,
                    user_answer=user_bool,
                    required_answer=required_bool,
                    passed=passed
                )
        elif step.step_type == 'INSTRUCTION':
            # For instructions, acknowledge completion
            InstructionResult.objects.create(
                test_result=test_result,
                instruction_text=step.instruction_text,
                acknowledged=True  # Instruction is acknowledged when user proceeds to next step
            )

    # Find the next uncompleted step
    completed_step_ids = []

    # Check voltage measurements
    completed_voltage_measurements = test_result.voltage_measurements.values_list('parameter_name', flat=True)
    completed_step_ids.extend(test_steps.filter(
        step_type='VOLTAGE',
        parameter_name__in=completed_voltage_measurements
    ).values_list('id', flat=True))

    # Check current measurements
    completed_current_measurements = test_result.current_measurements.values_list('parameter_name', flat=True)
    completed_step_ids.extend(test_steps.filter(
        step_type='CURRENT',
        parameter_name__in=completed_current_measurements
    ).values_list('id', flat=True))

    # Check resistance measurements
    completed_resistance_measurements = test_result.resistance_measurements.values_list('parameter_name', flat=True)
    completed_step_ids.extend(test_steps.filter(
        step_type='RESISTANCE',
        parameter_name__in=completed_resistance_measurements
    ).values_list('id', flat=True))

    # Check frequency measurements
    completed_frequency_measurements = test_result.frequency_measurements.values_list('parameter_name', flat=True)
    completed_step_ids.extend(test_steps.filter(
        step_type='FREQUENCY',
        parameter_name__in=completed_frequency_measurements
    ).values_list('id', flat=True))

    # Check yes/no questions
    completed_questions = test_result.yes_no_questions.values_list('question_text', flat=True)
    completed_step_ids.extend(test_steps.filter(
        step_type='QUESTION',
        question_text__in=completed_questions
    ).values_list('id', flat=True))

    # Check instructions
    completed_instructions = test_result.instructions.values_list('instruction_text', flat=True)
    completed_step_ids.extend(test_steps.filter(
        step_type='INSTRUCTION',
        instruction_text__in=completed_instructions
    ).values_list('id', flat=True))

    # Get the next step to display
    next_step = test_steps.exclude(id__in=completed_step_ids).order_by('order').first()

    # Check if this is the last step
    is_last_step = len(completed_step_ids) + 1 == test_steps.count()

    # If this is the last step and notes were submitted, save them
    if request.method == 'POST' and is_last_step:
        test_notes = request.POST.get('test_notes', '').strip()
        if test_notes:
            test_result.notes = test_notes
            test_result.save()

    if next_step is None:
        # All steps completed, show the summary page
        # Don't determine result yet, let the user review and submit notes if any
        context = {
            'pcb': pcb,
            'test_result': test_result,
            'total_steps': test_steps.count(),
            'completed_steps': len(completed_step_ids),
            'is_summary_page': True,
        }
        return render(request, 'pcb_test_result_app/pcb_test_execute.html', context)

    # Calculate progress percentage
    total_steps_count = test_steps.count()
    completed_steps_count = len(completed_step_ids)
    progress_percentage = 0
    if total_steps_count > 0:
        progress_percentage = int(((completed_steps_count + 1) / total_steps_count) * 100)

    context = {
        'pcb': pcb,
        'test_result': test_result,
        'current_step': next_step,
        'total_steps': total_steps_count,
        'completed_steps': completed_steps_count,
        'progress_percentage': progress_percentage,
    }
    return render(request, 'pcb_test_result_app/pcb_test_execute.html', context)


@login_required
@permission_required('pcb_test_result_app.view_pcbtestresult', raise_exception=True)
def pcb_test_results_by_pcb(request, pcb_serial_number):
    """Display all test results for a specific PCB"""
    pcb = get_object_or_404(Pcb, serial_number=pcb_serial_number)
    test_results = PcbTestResult.objects.filter(pcb=pcb).order_by('-test_date')

    context = {
        'pcb': pcb,
        'test_results': test_results,
    }
    return render(request, 'pcb_test_result_app/pcb_test_results_by_pcb.html', context)


@login_required
@permission_required('pcb_test_result_app.view_pcbtestresult', raise_exception=True)
def pcb_test_result_detail(request, pk):
    """View details of a specific PCB Test Result"""
    test_result = get_object_or_404(PcbTestResult, pk=pk)

    # Get QA signoff if it exists
    try:
        qa_signoff = test_result.qa_signoff
    except QaSignoff.DoesNotExist:
        qa_signoff = None

    # Check if all tests have passed
    all_tests_passed = True

    # Check voltage measurements
    total_voltage = test_result.voltage_measurements.count()
    passed_voltage = test_result.voltage_measurements.filter(passed=True).count()
    if passed_voltage != total_voltage:
        all_tests_passed = False

    # Check current measurements
    total_current = test_result.current_measurements.count()
    passed_current = test_result.current_measurements.filter(passed=True).count()
    if passed_current != total_current:
        all_tests_passed = False

    # Check resistance measurements
    total_resistance = test_result.resistance_measurements.count()
    passed_resistance = test_result.resistance_measurements.filter(passed=True).count()
    if passed_resistance != total_resistance:
        all_tests_passed = False

    # Check frequency measurements
    total_frequency = test_result.frequency_measurements.count()
    passed_frequency = test_result.frequency_measurements.filter(passed=True).count()
    if passed_frequency != total_frequency:
        all_tests_passed = False

    # Check yes/no questions
    total_questions = test_result.yes_no_questions.count()
    passed_questions = test_result.yes_no_questions.filter(passed=True).count()
    if passed_questions != total_questions:
        all_tests_passed = False

    # Check instructions
    total_instructions = test_result.instructions.count()
    passed_instructions = test_result.instructions.filter(acknowledged=True).count()
    if passed_instructions != total_instructions:
        all_tests_passed = False

    context = {
        'test_result': test_result,
        'qa_signoff': qa_signoff,
        'can_qa_signoff': request.user.groups.filter(name='qa_signoff_board_bringup_result').exists() or request.user.is_superuser,
        'all_tests_passed': all_tests_passed,
        'test_counts': {
            'voltage': {'total': total_voltage, 'passed': passed_voltage},
            'current': {'total': total_current, 'passed': passed_current},
            'resistance': {'total': total_resistance, 'passed': passed_resistance},
            'frequency': {'total': total_frequency, 'passed': passed_frequency},
            'questions': {'total': total_questions, 'passed': passed_questions},
            'instructions': {'total': total_instructions, 'passed': passed_instructions},
        }
    }
    return render(request, 'pcb_test_result_app/pcb_test_result_detail.html', context)


@login_required
@permission_required('pcb_test_result_app.change_pcbtestresult', raise_exception=True)
def pcb_test_result_update(request, pk):
    """Update an existing PCB Test Result"""
    test_result = get_object_or_404(PcbTestResult, pk=pk)

    # Handle AJAX request for JSON data
    if request.GET.get('format') == 'json':
        data = {
            'id': test_result.id,
            'notes': test_result.notes,
        }
        return JsonResponse(data)

    if request.method == 'POST':
        notes = request.POST.get('notes', '')

        try:
            test_result.notes = notes
            test_result.save()

            # Clear existing results
            test_result.voltage_measurements.all().delete()
            test_result.current_measurements.all().delete()
            test_result.resistance_measurements.all().delete()
            test_result.frequency_measurements.all().delete()
            test_result.yes_no_questions.all().delete()
            test_result.instructions.all().delete()

            # Process measurement results
            process_measurement_results(test_result, request.POST)

            # Process yes/no question results
            process_yes_no_question_results(test_result, request.POST)

            # Process instruction results
            process_instruction_results(test_result, request.POST)

            # Determine overall result
            determine_overall_result(test_result)

            messages.success(request, f'Test Result for PCB "{test_result.pcb.serial_number}" updated successfully.')
            return redirect('pcb_test_result_detail', pk=test_result.pk)
        except Exception as e:
            messages.error(request, f'Error updating test result: {str(e)}')
            return redirect('pcb_test_result_list')

    # GET request - show form with existing data
    # Get all PCBs for the dropdown
    pcbs = Pcb.objects.all().order_by('serial_number')

    context = {
        'test_result': test_result,
        'pcbs': pcbs,
    }
    return render(request, 'pcb_test_result_app/pcb_test_result_update.html', context)


@login_required
@permission_required('pcb_test_result_app.delete_pcbtestresult', raise_exception=True)
def pcb_test_result_delete(request, pk):
    """Delete a PCB Test Result"""
    test_result = get_object_or_404(PcbTestResult, pk=pk)

    if request.method == 'POST':
        # Form submitted from modal, proceed with deletion without additional confirmation
        # since we already validate in the frontend modal
        test_result_notes = test_result.notes
        test_result.delete()
        messages.success(request, f'Test Result for PCB "{test_result.pcb.serial_number}" deleted successfully.')
        return redirect('pcb_test_result_list')

    return redirect('pcb_test_result_list')


def process_measurement_results(test_result, post_data):
    """Process measurement results from POST data"""
    # Process voltage measurements
    voltage_count = int(post_data.get('voltage_count', 0))
    for i in range(voltage_count):
        param_name = post_data.get(f'voltage_param_name_{i}')
        measured_value = post_data.get(f'voltage_measured_{i}')
        min_value = post_data.get(f'voltage_min_{i}')
        max_value = post_data.get(f'voltage_max_{i}')
        unit = post_data.get(f'voltage_unit_{i}', 'V')

        if param_name and measured_value not in [None, ''] and min_value not in [None, ''] and max_value not in [None, '']:
            try:
                measured_value = float(measured_value)
                min_value = float(min_value)
                max_value = float(max_value)
                passed = min_value <= measured_value <= max_value

                VoltageMeasurementResult.objects.create(
                    test_result=test_result,
                    parameter_name=param_name,
                    measured_value=measured_value,
                    unit=unit,
                    min_value=min_value,
                    max_value=max_value,
                    passed=passed
                )
            except ValueError:
                # Skip invalid values
                pass

    # Process current measurements
    current_count = int(post_data.get('current_count', 0))
    for i in range(current_count):
        param_name = post_data.get(f'current_param_name_{i}')
        measured_value = post_data.get(f'current_measured_{i}')
        min_value = post_data.get(f'current_min_{i}')
        max_value = post_data.get(f'current_max_{i}')
        unit = post_data.get(f'current_unit_{i}', 'A')

        if param_name and measured_value not in [None, ''] and min_value not in [None, ''] and max_value not in [None, '']:
            try:
                measured_value = float(measured_value)
                min_value = float(min_value)
                max_value = float(max_value)
                passed = min_value <= measured_value <= max_value

                CurrentMeasurementResult.objects.create(
                    test_result=test_result,
                    parameter_name=param_name,
                    measured_value=measured_value,
                    unit=unit,
                    min_value=min_value,
                    max_value=max_value,
                    passed=passed
                )
            except ValueError:
                # Skip invalid values
                pass

    # Process resistance measurements
    resistance_count = int(post_data.get('resistance_count', 0))
    for i in range(resistance_count):
        param_name = post_data.get(f'resistance_param_name_{i}')
        measured_value = post_data.get(f'resistance_measured_{i}')
        min_value = post_data.get(f'resistance_min_{i}')
        max_value = post_data.get(f'resistance_max_{i}')
        unit = post_data.get(f'resistance_unit_{i}', 'Ω')

        if param_name and measured_value not in [None, ''] and min_value not in [None, ''] and max_value not in [None, '']:
            try:
                measured_value = float(measured_value)
                min_value = float(min_value)
                max_value = float(max_value)
                passed = min_value <= measured_value <= max_value

                ResistanceMeasurementResult.objects.create(
                    test_result=test_result,
                    parameter_name=param_name,
                    measured_value=measured_value,
                    unit=unit,
                    min_value=min_value,
                    max_value=max_value,
                    passed=passed
                )
            except ValueError:
                # Skip invalid values
                pass

    # Process frequency measurements
    frequency_count = int(post_data.get('frequency_count', 0))
    for i in range(frequency_count):
        param_name = post_data.get(f'frequency_param_name_{i}')
        measured_value = post_data.get(f'frequency_measured_{i}')
        min_value = post_data.get(f'frequency_min_{i}')
        max_value = post_data.get(f'frequency_max_{i}')
        unit = post_data.get(f'frequency_unit_{i}', 'Hz')

        if param_name and measured_value not in [None, ''] and min_value not in [None, ''] and max_value not in [None, '']:
            try:
                measured_value = float(measured_value)
                min_value = float(min_value)
                max_value = float(max_value)
                passed = min_value <= measured_value <= max_value

                FrequencyMeasurementResult.objects.create(
                    test_result=test_result,
                    parameter_name=param_name,
                    measured_value=measured_value,
                    unit=unit,
                    min_value=min_value,
                    max_value=max_value,
                    passed=passed
                )
            except ValueError:
                # Skip invalid values
                pass


def process_yes_no_question_results(test_result, post_data):
    """Process yes/no question results from POST data"""
    question_count = int(post_data.get('question_count', 0))
    for i in range(question_count):
        question_text = post_data.get(f'question_text_{i}')
        user_answer = post_data.get(f'question_user_answer_{i}')
        required_answer = post_data.get(f'question_required_{i}')

        if question_text and user_answer is not None and required_answer is not None:
            try:
                user_bool = user_answer == 'true' or user_answer == 'True' or user_answer == '1'
                required_bool = required_answer == 'true' or required_answer == 'True' or required_answer == '1'
                passed = user_bool == required_bool

                YesNoQuestionResult.objects.create(
                    test_result=test_result,
                    question_text=question_text,
                    user_answer=user_bool,
                    required_answer=required_bool,
                    passed=passed
                )
            except ValueError:
                # Skip invalid values
                pass


def process_instruction_results(test_result, post_data):
    """Process instruction results from POST data"""
    instruction_count = int(post_data.get('instruction_count', 0))
    for i in range(instruction_count):
        instruction_text = post_data.get(f'instruction_text_{i}')
        acknowledged = post_data.get(f'instruction_acknowledged_{i}')

        if instruction_text and acknowledged is not None:
            try:
                ack_bool = acknowledged == 'true' or acknowledged == 'True' or acknowledged == '1'

                InstructionResult.objects.create(
                    test_result=test_result,
                    instruction_text=instruction_text,
                    acknowledged=ack_bool
                )
            except ValueError:
                # Skip invalid values
                pass


def determine_overall_result(test_result):
    """Determine the overall test result based on individual measurements and questions"""
    # Get all measurement results
    voltage_results = test_result.voltage_measurements.all()
    current_results = test_result.current_measurements.all()
    resistance_results = test_result.resistance_measurements.all()
    frequency_results = test_result.frequency_measurements.all()
    question_results = test_result.yes_no_questions.all()
    instruction_results = test_result.instructions.all()

    # Check if any results failed
    all_passed = True

    # Check measurements
    for result in list(voltage_results) + list(current_results) + list(resistance_results) + list(frequency_results):
        if not result.passed:
            all_passed = False
            break

    # Check questions
    if all_passed:
        for result in question_results:
            if not result.passed:
                all_passed = False
                break

    # Check instructions
    if all_passed:
        for result in instruction_results:
            if not result.acknowledged:
                all_passed = False
                break

    # Update test result
    if all_passed:
        test_result.result = PcbTestResult.PASSED
    else:
        test_result.result = PcbTestResult.FAILED

    test_result.save()


@login_required
@permission_required('pcb_test_result_app.add_pcbtestresult', raise_exception=True)
def pcb_test_complete(request, pk):
    """Complete the test after summary view"""
    test_result = get_object_or_404(PcbTestResult, pk=pk)

    if request.method == 'POST':
        # Get notes from the summary page
        test_notes = request.POST.get('test_notes', '').strip()
        if test_notes:
            test_result.notes = test_notes
            test_result.save()

        # Determine overall result
        determine_overall_result(test_result)

        # Clear the session variable
        if 'current_test_result_id' in request.session:
            del request.session['current_test_result_id']

        messages.success(request, f'Test for PCB "{test_result.pcb.serial_number}" completed successfully.')
        return redirect('pcb_test_result_detail', pk=test_result.pk)

    # If not POST, return to the list
    return redirect('pcb_test_result_list')


# Call the function to create the group
# create_pcb_test_result_management_group()  # Commented out until the function is properly defined
