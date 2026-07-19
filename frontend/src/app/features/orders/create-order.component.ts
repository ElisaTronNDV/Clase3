import { HttpErrorResponse } from '@angular/common/http';
import { Component, inject, signal } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { RouterLink } from '@angular/router';

import { ExtractedNest, OrdersService, WorkOrder } from '../../core/orders/orders.service';

@Component({
  selector: 'app-create-order',
  standalone: true,
  imports: [ReactiveFormsModule, RouterLink],
  templateUrl: './create-order.component.html',
  styleUrl: './create-order.component.scss'
})
export class CreateOrderComponent {
  private readonly ordersService = inject(OrdersService);
  private readonly fb = inject(FormBuilder);

  readonly selectedFileName = signal<string | null>(null);
  readonly isUploading = signal(false);
  readonly errorMessage = signal<string | null>(null);
  readonly nests = signal<ExtractedNest[]>([]);
  readonly confirmedOrders = signal<(WorkOrder | null)[]>([]);
  readonly confirmErrors = signal<(string | null)[]>([]);
  readonly confirmingIndex = signal<number | null>(null);

  forms: FormGroup[] = [];

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!file) {
      return;
    }

    this.errorMessage.set(null);
    this.nests.set([]);
    this.confirmedOrders.set([]);
    this.confirmErrors.set([]);
    this.forms = [];

    if (!file.name.toLowerCase().endsWith('.pdf')) {
      this.errorMessage.set('Solo se admiten archivos PDF.');
      input.value = '';
      return;
    }

    this.selectedFileName.set(file.name);
    this.isUploading.set(true);

    this.ordersService.extractPdf(file).subscribe({
      next: (result) => {
        this.isUploading.set(false);
        this.nests.set(result.nests);
        this.forms = result.nests.map((nest) => this.buildForm(nest));
        this.confirmedOrders.set(result.nests.map(() => null));
        this.confirmErrors.set(result.nests.map(() => null));
      },
      error: (error: HttpErrorResponse) => {
        this.isUploading.set(false);
        this.errorMessage.set(error.error?.detail ?? 'No se pudo procesar el archivo PDF.');
      }
    });

    input.value = '';
  }

  confirmNest(index: number, createMissingProduct = false): void {
    const form = this.forms[index];
    if (form.invalid) {
      form.markAllAsTouched();
      return;
    }

    const nest = this.nests()[index];
    const values = form.getRawValue();

    this.setConfirmError(index, null);
    this.confirmingIndex.set(index);

    this.ordersService
      .confirmOrder({
        nombre_nest: nest.nombre_nest,
        material: values.material,
        thickness_mm: values.espesor_mm,
        length_mm: values.largo_mm,
        width_mm: values.ancho_mm,
        multiplicidad: values.multiplicidad,
        tiempo_ejecucion_estimado: values.tiempo_ejecucion_estimado,
        piezas: nest.piezas,
        recortes: nest.recortes,
        create_missing_product: createMissingProduct
      })
      .subscribe({
        next: (order) => {
          this.confirmingIndex.set(null);
          const updated = [...this.confirmedOrders()];
          updated[index] = order;
          this.confirmedOrders.set(updated);
        },
        error: (error: HttpErrorResponse) => {
          this.confirmingIndex.set(null);

          if (error.status === 409 && error.error?.detail?.code === 'product_not_found') {
            const wantsToCreate = window.confirm(
              'El producto no existe en el maestro de Inventario. ¿Querés crearlo automáticamente ' +
                'con estos datos técnicos (stock físico en cero)?'
            );
            if (wantsToCreate) {
              this.confirmNest(index, true);
              return;
            }
            this.setConfirmError(index, 'No se confirmó: el producto no existe en el maestro.');
            return;
          }

          this.setConfirmError(index, 'No se pudo confirmar la orden.');
        }
      });
  }

  private setConfirmError(index: number, message: string | null): void {
    const updated = [...this.confirmErrors()];
    updated[index] = message;
    this.confirmErrors.set(updated);
  }

  private buildForm(nest: ExtractedNest): FormGroup {
    return this.fb.nonNullable.group({
      multiplicidad: [nest.multiplicidad ?? 0, [Validators.required, Validators.min(1)]],
      largo_mm: [nest.largo_mm ?? 0, [Validators.required, Validators.min(0.01)]],
      ancho_mm: [nest.ancho_mm ?? 0, [Validators.required, Validators.min(0.01)]],
      espesor_mm: [nest.espesor_mm ?? 0, [Validators.required, Validators.min(0.01)]],
      material: [nest.material ?? '', [Validators.required]],
      tiempo_ejecucion_estimado: [nest.tiempo_ejecucion_estimado ?? '']
    });
  }
}
