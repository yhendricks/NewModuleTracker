from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth.models import User
from .models import Module, ATPReport, ESSReport
from module_config_type_app.models import ModuleConfigType

@login_required
@permission_required('module_app.view_module', raise_exception=True)
def module_list(request):
    """Display list of Modules with search and pagination"""
    modules = Module.objects.select_related('module_config', 'technician').all().order_by('-created_at')
    
    # Handle search/filter
    search_query = request.GET.get('search', '')
    if search_query:
        modules = modules.filter(
            Q(name__icontains=search_query) |
            Q(serial_number__icontains=search_query) |
            Q(module_config__name__icontains=search_query)
        )
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        modules = modules.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(modules, 10)  # Show 10 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get all possible statuses for filter dropdown
    status_choices = Module.STATUS_CHOICES
    
    context = {
        'modules': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'status_choices': status_choices,
    }
    return render(request, 'module_app/module_list.html', context)

@login_required
@permission_required('module_app.add_module', raise_exception=True)
def module_create(request):
    """Create a new Module"""
    if request.method == 'POST':
        name = request.POST.get('name')
        config_id = request.POST.get('module_config_id')
        serial_number = request.POST.get('serial_number', '')
        technician_id = request.POST.get('technician_id')
        
        # Get the module config and technician
        module_config = get_object_or_404(ModuleConfigType, pk=config_id)
        technician = get_object_or_404(User, pk=technician_id) if technician_id else None
        
        # Check if name already exists
        if Module.objects.filter(name__iexact=name).exists():
            messages.error(request, 'A Module with this name already exists.')
            return redirect('module_list')
        
        from django.utils import timezone
        module = Module.objects.create(
            name=name,
            module_config=module_config,
            serial_number=serial_number,
            technician=technician,
            created_at=timezone.now()
        )
        messages.success(request, f'Module "{module.name}" created successfully.')
        return redirect('module_list')
    
    # Get all module configs and technicians for the form
    module_configs = ModuleConfigType.objects.all().order_by('name')
    technicians = User.objects.filter(groups__name='module_test_group').distinct()
    
    context = {
        'module_configs': module_configs,
        'technicians': technicians,
    }
    return render(request, 'module_app/module_create.html', context)

@login_required
@permission_required('module_app.change_module', raise_exception=True)
def module_update(request, pk):
    """Update an existing Module"""
    module = get_object_or_404(Module, pk=pk)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        config_id = request.POST.get('module_config_id')
        serial_number = request.POST.get('serial_number', '')
        technician_id = request.POST.get('technician_id')
        
        # Get the module config and technician
        module_config = get_object_or_404(ModuleConfigType, pk=config_id)
        technician = get_object_or_404(User, pk=technician_id) if technician_id else None
        
        # Check if name already exists (excluding current item)
        if Module.objects.filter(name__iexact=name).exclude(pk=pk).exists():
            messages.error(request, 'A Module with this name already exists.')
            return redirect('module_list')
        
        module.name = name
        module.module_config = module_config
        module.serial_number = serial_number
        module.technician = technician
        module.save()
        
        messages.success(request, f'Module "{module.name}" updated successfully.')
        return redirect('module_list')
    
    # Return JSON for modal
    if request.GET.get('format') == 'json':
        return JsonResponse({
            'id': module.id,
            'name': module.name,
            'module_config_id': module.module_config.id,
            'serial_number': module.serial_number or '',
            'technician_id': module.technician.id if module.technician else '',
        })
    
    # Get all module configs and technicians for the form
    module_configs = ModuleConfigType.objects.all().order_by('name')
    technicians = User.objects.filter(groups__name='module_test_group').distinct()
    
    context = {
        'module': module,
        'module_configs': module_configs,
        'technicians': technicians,
    }
    return render(request, 'module_app/module_update.html', context)

@login_required
@permission_required('module_app.delete_module', raise_exception=True)
def module_delete(request, pk):
    """Delete a Module"""
    module = get_object_or_404(Module, pk=pk)
    
    # Check if confirmation name matches
    confirm_name = request.POST.get('confirm_name', '')
    if confirm_name != module.name:
        messages.error(request, 'Confirmation name does not match. Deletion cancelled.')
        return redirect('module_list')
    
    module_name = module.name
    module.delete()
    messages.success(request, f'Module "{module_name}" deleted successfully.')
    return redirect('module_list')

@login_required
@permission_required('module_app.view_module', raise_exception=True)
def module_detail(request, pk):
    """View details of a specific Module including test results and status"""
    module = get_object_or_404(Module, pk=pk)
    
    # Get related reports
    atp_reports = module.atp_reports.all().order_by('-timestamp')
    ess_reports = module.ess_reports.all().order_by('-timestamp')
    
    context = {
        'module': module,
        'atp_reports': atp_reports,
        'ess_reports': ess_reports,
    }
    return render(request, 'module_app/module_detail.html', context)

@login_required
def module_status_change(request, pk):
    """Change the status of a module during testing workflow"""
    module = get_object_or_404(Module, pk=pk)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        allowed_statuses = [choice[0] for choice in Module.STATUS_CHOICES]
        if new_status in allowed_statuses:
            # Check if user has appropriate permissions based on status transition
            # Technicians can move modules forward in the process
            if request.user.groups.filter(name='module_test_group').exists() or request.user.has_perm('module_app.change_module'):
                # Allow technician to move forward in the workflow, but not backwards
                current_index = next((i for i, (code, name) in enumerate(Module.STATUS_CHOICES) if code == module.status), -1)
                new_index = next((i for i, (code, name) in enumerate(Module.STATUS_CHOICES) if code == new_status), -1)
                
                if new_index > current_index or new_index == current_index:  # Only forward or same status
                    module.status = new_status
                    module.save()
                    messages.success(request, f'Module "{module.name}" status updated to {new_status}.')
                else:
                    messages.error(request, 'Cannot change status to a previous stage.')
            else:
                messages.error(request, 'You do not have permission to change module status.')
        else:
            messages.error(request, 'Invalid status value.')
        return redirect('module_detail', pk=pk)
    return redirect('module_list')

@login_required
def module_add_atp_report(request, pk):
    """Add an ATP report for a module"""
    module = get_object_or_404(Module, pk=pk)
    
    if not (request.user.groups.filter(name='module_test_group').exists() or request.user.has_perm('module_app.change_module')):
        messages.error(request, 'You do not have permission to add ATP reports.')
        return redirect('module_detail', pk=pk)
    
    if request.method == 'POST':
        test_phase = request.POST.get('test_phase')
        report_file = request.FILES.get('report_file')
        report_data = request.POST.get('report_data', '')
        
        # Validate test phase
        valid_phases = [choice[0] for choice in ATPReport.TEST_PHASE_CHOICES]
        if test_phase not in valid_phases:
            messages.error(request, 'Invalid test phase.')
            return redirect('module_detail', pk=pk)
        
        # Create the ATP report
        atp_report = ATPReport.objects.create(
            module=module,
            test_phase=test_phase,
            report_data=report_data,
        )
        
        # Handle file upload if present
        if report_file:
            atp_report.report_file = report_file
            atp_report.save()
            
        messages.success(request, f'ATP report added for {module.name} - {test_phase}.')
        return redirect('module_detail', pk=pk)
    
    return redirect('module_detail', pk=pk)

@login_required
def module_add_ess_report(request, pk):
    """Add an ESS report for a module"""
    module = get_object_or_404(Module, pk=pk)
    
    if not (request.user.groups.filter(name='module_test_group').exists() or request.user.has_perm('module_app.change_module')):
        messages.error(request, 'You do not have permission to add ESS reports.')
        return redirect('module_detail', pk=pk)
    
    if request.method == 'POST':
        report_file = request.FILES.get('report_file')
        report_data = request.POST.get('report_data', '')
        
        # Create the ESS report
        ess_report = ESSReport.objects.create(
            module=module,
            report_data=report_data,
        )
        
        # Handle file upload if present
        if report_file:
            ess_report.report_file = report_file
            ess_report.save()
            
        messages.success(request, f'ESS report added for {module.name}.')
        return redirect('module_detail', pk=pk)
    
    return redirect('module_detail', pk=pk)

@login_required
def module_signoff_report(request, report_type, report_id):
    """Sign off on a report as QA"""
    if not (request.user.groups.filter(name='qa_module_sign_off').exists() or 
            request.user.has_perm('module_app.change_atpreport') or 
            request.user.has_perm('module_app.change_essreport')):
        messages.error(request, 'You do not have permission to sign off on reports.')
        return redirect('module_list')
    
    if report_type == 'atp':
        report = get_object_or_404(ATPReport, pk=report_id)
    elif report_type == 'ess':
        report = get_object_or_404(ESSReport, pk=report_id)
    else:
        messages.error(request, 'Invalid report type.')
        return redirect('module_list')
    
    if request.method == 'POST':
        report.qa_signoff = True
        report.signed_off_by = request.user
        report.save()
        messages.success(request, f'QA signoff completed for {report_type.upper()} report.')
        return redirect('module_detail', pk=report.module.id)
    
    return redirect('module_list')
