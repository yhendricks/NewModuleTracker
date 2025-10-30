from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Q
from .models import Batch, Pcb, create_batch_management_group
from pcb_type_app.models import PcbType
from test_config_type_app.models import TestConfigType


@login_required
@permission_required('batch_app.view_batch', raise_exception=True)
def batch_list(request):
    """Display list of Batches with search and pagination"""
    batches = Batch.objects.all().order_by('name')
    
    # Handle search/filter
    search_query = request.GET.get('search', '')
    if search_query:
        batches = batches.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(hardware_version__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(batches, 10)  # Show 10 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'batches': page_obj,
        'search_query': search_query,
    }
    return render(request, 'batch_app/batch_list.html', context)


@login_required
@permission_required('batch_app.add_batch', raise_exception=True)
def batch_create(request):
    """Create a new Batch"""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        pcb_type_id = request.POST.get('pcb_type')
        test_config_type_id = request.POST.get('test_config_type')
        hardware_version = request.POST.get('hardware_version')
        
        # Check if name already exists
        if Batch.objects.filter(name__iexact=name).exists():
            messages.error(request, 'A Batch with this name already exists.')
            return redirect('batch_list')
        
        try:
            batch = Batch.objects.create(
                name=name,
                description=description,
                pcb_type_id=pcb_type_id,
                test_config_type_id=test_config_type_id,
                hardware_version=hardware_version
            )
            
            messages.success(request, f'Batch "{batch.name}" created successfully.')
            return redirect('batch_list')
        except Exception as e:
            messages.error(request, f'Error creating batch: {str(e)}')
            return redirect('batch_list')
    
    return redirect('batch_list')


@login_required
@permission_required('batch_app.change_batch', raise_exception=True)
def batch_update(request, pk):
    """Update an existing Batch"""
    batch = get_object_or_404(Batch, pk=pk)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        pcb_type_id = request.POST.get('pcb_type')
        test_config_type_id = request.POST.get('test_config_type')
        hardware_version = request.POST.get('hardware_version')
        
        # Check if name already exists (excluding current item)
        if Batch.objects.filter(name__iexact=name).exclude(pk=pk).exists():
            messages.error(request, 'A Batch with this name already exists.')
            return redirect('batch_list')
        
        try:
            batch.name = name
            batch.description = description
            batch.pcb_type_id = pcb_type_id
            batch.test_config_type_id = test_config_type_id
            batch.hardware_version = hardware_version
            batch.save()
            
            messages.success(request, f'Batch "{batch.name}" updated successfully.')
            return redirect('batch_list')
        except Exception as e:
            messages.error(request, f'Error updating batch: {str(e)}')
            return redirect('batch_list')
    
    # Return JSON for modal
    if request.GET.get('format') == 'json':
        return JsonResponse({
            'id': batch.id,
            'name': batch.name,
            'description': batch.description,
            'pcb_type': batch.pcb_type.id,
            'test_config_type': batch.test_config_type.id,
            'hardware_version': batch.hardware_version
        })
    
    return redirect('batch_list')


@login_required
@permission_required('batch_app.delete_batch', raise_exception=True)
def batch_delete(request, pk):
    """Delete a Batch"""
    batch = get_object_or_404(Batch, pk=pk)
    
    # Check if confirmation name matches
    confirm_name = request.POST.get('confirm_name', '')
    if confirm_name != batch.name:
        messages.error(request, 'Confirmation name does not match. Deletion cancelled.')
        return redirect('batch_list')
    
    batch_name = batch.name
    batch.delete()
    messages.success(request, f'Batch "{batch_name}" deleted successfully.')
    return redirect('batch_list')


@login_required
@permission_required('batch_app.view_batch', raise_exception=True)
def batch_detail(request, pk):
    """View details of a specific Batch"""
    batch = get_object_or_404(Batch, pk=pk)
    context = {
        'batch': batch
    }
    return render(request, 'batch_app/batch_detail.html', context)


@login_required
@permission_required('batch_app.add_pcb', raise_exception=True)
def batch_pcb_create(request):
    """Create a new PCB"""
    if request.method == 'POST':
        batch_id = request.POST.get('batch_id')
        serial_number = request.POST.get('serial_number')
        hardware_modified = request.POST.get('hardware_modified') == 'on'
        modified_hardware_version = request.POST.get('modified_hardware_version', '')
        
        # Check if serial number already exists
        if Pcb.objects.filter(serial_number__iexact=serial_number).exists():
            messages.error(request, 'A PCB with this serial number already exists.')
            return redirect('batch_detail', pk=batch_id)
        
        try:
            batch = get_object_or_404(Batch, pk=batch_id)
            pcb = Pcb.objects.create(
                serial_number=serial_number,
                batch=batch,
                hardware_modified=hardware_modified,
                modified_hardware_version=modified_hardware_version if hardware_modified else None
            )
            
            messages.success(request, f'PCB "{pcb.serial_number}" created successfully.')
            return redirect('batch_detail', pk=batch_id)
        except Exception as e:
            messages.error(request, f'Error creating PCB: {str(e)}')
            return redirect('batch_detail', pk=batch_id)
    
    return redirect('batch_list')


# Create the management group when the app is loaded
create_batch_management_group()