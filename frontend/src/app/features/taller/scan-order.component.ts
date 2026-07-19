import { HttpErrorResponse } from '@angular/common/http';
import { AfterViewInit, Component, ElementRef, OnDestroy, ViewChild, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { BarcodeFormat } from '@zxing/library';
import { ZXingScannerModule } from '@zxing/ngx-scanner';
import { Modal } from 'bootstrap';

import { OrdersService, WorkOrder } from '../../core/orders/orders.service';

@Component({
  selector: 'app-scan-order',
  standalone: true,
  imports: [FormsModule, ZXingScannerModule],
  templateUrl: './scan-order.component.html',
  styleUrl: './scan-order.component.scss'
})
export class ScanOrderComponent implements AfterViewInit, OnDestroy {
  private readonly ordersService = inject(OrdersService);

  @ViewChild('scanModal') private readonly scanModalRef!: ElementRef<HTMLElement>;
  private modal: Modal | null = null;

  private readonly onModalShown = (): void => {
    this.cameraAvailable.set(true);
    this.scannerModalOpen.set(true);
  };

  private readonly onModalHidden = (): void => {
    this.scannerModalOpen.set(false);
  };

  readonly allowedFormats = [BarcodeFormat.CODE_128];

  readonly scannerModalOpen = signal(false);
  readonly cameraAvailable = signal(true);
  readonly manualCode = signal('');
  readonly order = signal<WorkOrder | null>(null);
  readonly isLoading = signal(false);
  readonly errorMessage = signal<string | null>(null);
  readonly isClosing = signal(false);
  readonly closeSuccessMessage = signal<string | null>(null);

  ngAfterViewInit(): void {
    const element = this.scanModalRef.nativeElement;
    this.modal = new Modal(element);
    element.addEventListener('shown.bs.modal', this.onModalShown);
    element.addEventListener('hidden.bs.modal', this.onModalHidden);
  }

  ngOnDestroy(): void {
    const element = this.scanModalRef?.nativeElement;
    element?.removeEventListener('shown.bs.modal', this.onModalShown);
    element?.removeEventListener('hidden.bs.modal', this.onModalHidden);
    this.modal?.dispose();
  }

  openScanner(): void {
    this.errorMessage.set(null);
    this.modal?.show();
  }

  onCamerasFound(): void {
    this.cameraAvailable.set(true);
  }

  onCamerasNotFound(): void {
    this.cameraAvailable.set(false);
  }

  onScanSuccess(code: string): void {
    if (this.isLoading()) {
      return;
    }
    const trimmed = code.trim();
    this.manualCode.set(trimmed);
    this.modal?.hide();
    this.lookupOrder(trimmed);
  }

  submitManualCode(): void {
    const code = this.manualCode().trim();
    if (!code) {
      return;
    }
    this.lookupOrder(code);
  }

  scanAnother(): void {
    this.order.set(null);
    this.errorMessage.set(null);
    this.closeSuccessMessage.set(null);
    this.manualCode.set('');
  }

  finalizeOrder(): void {
    const order = this.order();
    if (!order) {
      return;
    }

    const confirmed = window.confirm(
      `¿Confirmás finalizar la orden ${order.nest_code}? Se descontará el stock comprometido y físico.`
    );
    if (!confirmed) {
      return;
    }

    this.isClosing.set(true);
    this.errorMessage.set(null);

    this.ordersService.closeOrder(order.id).subscribe({
      next: (updated) => {
        this.isClosing.set(false);
        this.order.set(updated);
        this.closeSuccessMessage.set('Orden cerrada. Stock actualizado.');
      },
      error: (error: HttpErrorResponse) => {
        this.isClosing.set(false);
        this.errorMessage.set(error.error?.detail ?? 'No se pudo finalizar la orden.');
      }
    });
  }

  private lookupOrder(nestCode: string): void {
    this.isLoading.set(true);
    this.errorMessage.set(null);
    this.closeSuccessMessage.set(null);

    this.ordersService.getOrderByNestCode(nestCode).subscribe({
      next: (order) => {
        this.isLoading.set(false);
        this.order.set(order);
      },
      error: (error: HttpErrorResponse) => {
        this.isLoading.set(false);
        this.errorMessage.set(
          error.status === 404
            ? `No se encontró ninguna orden con el código "${nestCode}".`
            : 'No se pudo buscar la orden.'
        );
      }
    });
  }
}
