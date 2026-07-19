import { DatePipe } from '@angular/common';
import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';

import { OrdersService, WorkOrderStatus, WorkOrderSummary } from '../../core/orders/orders.service';

type OrderFilter = 'todas' | WorkOrderStatus;

@Component({
  selector: 'app-order-list',
  standalone: true,
  imports: [RouterLink, DatePipe, FormsModule],
  templateUrl: './order-list.component.html',
  styleUrl: './order-list.component.scss'
})
export class OrderListComponent implements OnInit {
  private readonly ordersService = inject(OrdersService);

  readonly orders = signal<WorkOrderSummary[]>([]);
  readonly isLoading = signal(true);
  readonly errorMessage = signal<string | null>(null);
  readonly filter = signal<OrderFilter>('todas');
  readonly searchTerm = signal('');

  readonly filteredOrders = computed(() => {
    const term = this.searchTerm().trim().toLowerCase();
    if (!term) {
      return this.orders();
    }
    return this.orders().filter((order) => order.nest_code.toLowerCase().includes(term));
  });

  ngOnInit(): void {
    this.loadOrders();
  }

  setFilter(filter: OrderFilter): void {
    if (this.filter() === filter) {
      return;
    }
    this.filter.set(filter);
    this.loadOrders();
  }

  private loadOrders(): void {
    this.isLoading.set(true);
    this.errorMessage.set(null);

    const currentFilter = this.filter();
    const status = currentFilter === 'todas' ? undefined : currentFilter;
    this.ordersService.listOrders(status).subscribe({
      next: (orders) => {
        this.orders.set(orders);
        this.isLoading.set(false);
      },
      error: () => {
        this.errorMessage.set('No se pudo cargar el listado de órdenes.');
        this.isLoading.set(false);
      }
    });
  }
}
