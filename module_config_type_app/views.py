from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Q
from .models import ModuleConfigType, ModuleConfigPcb
from pcb_type_app.models import PcbType

@login_required
@permission_required('module_config_type_app.view_moduleconfigtype', raise_exception=True)
def module_config_type_list(request):
    """Display list of Module Configuration Types with search and pagination"""
    module_config_types = ModuleConfigType.objects.prefetch_related('moduleconfigpcb_set__pcb_type').all().order_by('name')
    
    # Handle search/filter
    search_query = request.GET.get('search', '')
    if search_query:
        module_config_types = module_config_types.filter(
            Q(name__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(module_config_types, 10)  # Show 10 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    pcb_types = PcbType.objects.all().order_by('name')

    context = {
        'module_config_types': page_obj,
        'search_query': search_query,
        'pcb_types': pcb_types,
    }
    return render(request, 'module_config_type_app/module_config_type_list.html', context)

@login_required
@permission_required('module_config_type_app.add_moduleconfigtype', raise_exception=True)
def module_config_type_create(request):
    """Create a new Module Configuration Type"""
    if request.method == 'POST':
        name = request.POST.get('name')
        
        # Check if name already exists
        if ModuleConfigType.objects.filter(name__iexact=name).exists():
            messages.error(request, 'A Module Config Type with this name already exists.')
            return redirect('module_config_type_list')

        module_config = ModuleConfigType.objects.create(name=name)
        
        # Handle PCBs and quantities
        pcb_data = {}
        for key, value in request.POST.items():
            if key.startswith('pcb_type_') and value:
                pcb_id = key.replace('pcb_type_', '')
                quantity = request.POST.get(f'quantity_{pcb_id}', 1)
                try:
                    pcb_data[int(pcb_id)] = int(quantity)
                except ValueError:
                    messages.error(request, 'Invalid quantity provided for a PCB.')
                    module_config.delete()  # Rollback
                    return redirect('module_config_type_list')

        for pcb_id, quantity in pcb_data.items():
            pcb_type = get_object_or_404(PcbType, pk=pcb_id)
            ModuleConfigPcb.objects.create(
                module_config_type=module_config,
                pcb_type=pcb_type,
                quantity=quantity
            )
        
        messages.success(request, f'Module Config Type "{module_config.name}" created successfully.')
        return redirect('module_config_type_list')

    return redirect('module_config_type_list')

@login_required
@permission_required('module_config_type_app.change_moduleconfigtype', raise_exception=True)
def module_config_type_update(request, pk):
    """Update an existing Module Configuration Type"""
    module_config = get_object_or_404(ModuleConfigType, pk=pk)

    if request.method == 'POST':
        name = request.POST.get('name')
        
        # Check if name already exists (excluding current item)
        if ModuleConfigType.objects.filter(name__iexact=name).exclude(pk=pk).exists():
            messages.error(request, 'A Module Config Type with this name already exists.')
            return redirect('module_config_type_list')

        module_config.name = name
        module_config.save()

        # Clear existing PCBs and add new ones
        module_config.moduleconfigpcb_set.all().delete()
        
        pcb_data = {}
        for key, value in request.POST.items():
            if key.startswith('pcb_type_') and value:
                pcb_id = key.replace('pcb_type_', '')
                quantity = request.POST.get(f'quantity_{pcb_id}', 1)
                try:
                    pcb_data[int(pcb_id)] = int(quantity)
                except ValueError:
                    messages.error(request, 'Invalid quantity provided for a PCB.')
                    return redirect('module_config_type_list')

        for pcb_id, quantity in pcb_data.items():
            pcb_type = get_object_or_404(PcbType, pk=pcb_id)
            ModuleConfigPcb.objects.create(
                module_config_type=module_config,
                pcb_type=pcb_type,
                quantity=quantity
            )

        messages.success(request, f'Module Config Type "{module_config.name}" updated successfully.')
        return redirect('module_config_type_list')

    # Return JSON for modal
    if request.GET.get('format') == 'json':
        pcbs_with_quantities = []
        for mcp in module_config.moduleconfigpcb_set.all():
            pcbs_with_quantities.append({
                'id': mcp.pcb_type.id,
                'name': mcp.pcb_type.name,
                'quantity': mcp.quantity
            })
        return JsonResponse({
            'id': module_config.id,
            'name': module_config.name,
            'pcbs': pcbs_with_quantities,
        })

    return redirect('module_config_type_list')

@login_required
@permission_required('module_config_type_app.delete_moduleconfigtype', raise_exception=True)
def module_config_type_delete(request, pk):
    """Delete a Module Configuration Type"""
    module_config = get_object_or_404(ModuleConfigType, pk=pk)
    
    # Check if confirmation name matches
    confirm_name = request.POST.get('confirm_name', '')
    if confirm_name != module_config.name:
        messages.error(request, 'Confirmation name does not match. Deletion cancelled.')
        return redirect('module_config_type_list')

    module_config_name = module_config.name
    module_config.delete()
    messages.success(request, f'Module Config Type "{module_config_name}" deleted successfully.')
    return redirect('module_config_type_list')

@login_required
@permission_required('module_config_type_app.view_moduleconfigtype', raise_exception=True)
def module_config_type_detail(request, pk):
    """View details of a specific Module Configuration Type"""
    module_config = get_object_or_404(ModuleConfigType, pk=pk)
    
    # Get related PCBs
    pcb_configs = module_config.moduleconfigpcb_set.all().select_related('pcb_type')
    
    context = {
        'module_config': module_config,
        'pcb_configs': pcb_configs,
    }
    return render(request, 'module_config_type_app/module_config_type_detail.html', context)
