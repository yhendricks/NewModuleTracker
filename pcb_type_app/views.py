from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Q
from .models import PcbType

@login_required
@permission_required('pcb_type_app.view_pcbtype', raise_exception=True)
def pcb_type_list(request):
    """Display list of PCB Types with search and pagination"""
    pcb_types = PcbType.objects.all().order_by('name')
    
    # Handle search/filter
    search_query = request.GET.get('search', '')
    if search_query:
        pcb_types = pcb_types.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(pcb_types, 10)  # Show 10 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'pcb_types': page_obj,
        'search_query': search_query,
    }
    return render(request, 'pcb_type_app/pcb_type_list.html', context)

@login_required
@permission_required('pcb_type_app.add_pcbtype', raise_exception=True)
def pcb_type_create(request):
    """Create a new PCB Type"""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        
        # Check if name already exists
        if PcbType.objects.filter(name__iexact=name).exists():
            messages.error(request, 'A PCB Type with this name already exists.')
            return redirect('pcb_type_list')
        
        pcb_type = PcbType.objects.create(name=name, description=description)
        messages.success(request, f'PCB Type "{pcb_type.name}" created successfully.')
        return redirect('pcb_type_list')
    
    return redirect('pcb_type_list')

@login_required
@permission_required('pcb_type_app.change_pcbtype', raise_exception=True)
def pcb_type_update(request, pk):
    """Update an existing PCB Type"""
    pcb_type = get_object_or_404(PcbType, pk=pk)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        
        # Check if name already exists (excluding current item)
        if PcbType.objects.filter(name__iexact=name).exclude(pk=pk).exists():
            messages.error(request, 'A PCB Type with this name already exists.')
            return redirect('pcb_type_list')
        
        pcb_type.name = name
        pcb_type.description = description
        pcb_type.save()
        
        messages.success(request, f'PCB Type "{pcb_type.name}" updated successfully.')
        return redirect('pcb_type_list')
    
    # Return JSON for modal
    if request.GET.get('format') == 'json':
        return JsonResponse({
            'id': pcb_type.id,
            'name': pcb_type.name,
            'description': pcb_type.description
        })
    
    return redirect('pcb_type_list')

@login_required
@permission_required('pcb_type_app.delete_pcbtype', raise_exception=True)
def pcb_type_delete(request, pk):
    """Delete a PCB Type"""
    pcb_type = get_object_or_404(PcbType, pk=pk)
    
    # Check if confirmation name matches
    confirm_name = request.POST.get('confirm_name', '')
    if confirm_name != pcb_type.name:
        messages.error(request, 'Confirmation name does not match. Deletion cancelled.')
        return redirect('pcb_type_list')
    
    pcb_type_name = pcb_type.name
    pcb_type.delete()
    messages.success(request, f'PCB Type "{pcb_type_name}" deleted successfully.')
    return redirect('pcb_type_list')

@login_required
@permission_required('pcb_type_app.view_pcbtype', raise_exception=True)
def pcb_type_detail(request, pk):
    """View details of a specific PCB Type"""
    pcb_type = get_object_or_404(PcbType, pk=pk)
    context = {
        'pcb_type': pcb_type
    }
    return render(request, 'pcb_type_app/pcb_type_detail.html', context)