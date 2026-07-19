import { Component, OnInit, inject, signal } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

import { OrdersService, WorkOrder } from '../../core/orders/orders.service';

@Component({
  selector: 'app-print-order',
  standalone: true,
  templateUrl: './print-order.component.html',
  styleUrl: './print-order.component.scss'
})
export class PrintOrderComponent implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly ordersService = inject(OrdersService);

  readonly order = signal<WorkOrder | null>(null);
  readonly barcodeUrl = signal<string | null>(null);
  readonly errorMessage = signal<string | null>(null);

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));

    this.ordersService.getOrder(id).subscribe({
      next: (order) => this.order.set(order),
      error: () => this.errorMessage.set('No se pudo cargar la orden.')
    });

    this.ordersService.getBarcodeBlob(id).subscribe({
      next: (blob) => this.barcodeUrl.set(URL.createObjectURL(blob))
    });
  }

  print(): void {
    window.print();
  }
}
