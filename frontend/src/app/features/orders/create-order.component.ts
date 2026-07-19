import { HttpErrorResponse } from '@angular/common/http';
import { Component, inject, signal } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';

import { ExtractedNest, OrdersService } from '../../core/orders/orders.service';

@Component({
  selector: 'app-create-order',
  standalone: true,
  imports: [ReactiveFormsModule],
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

  forms: FormGroup[] = [];

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!file) {
      return;
    }

    this.errorMessage.set(null);
    this.nests.set([]);
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
      },
      error: (error: HttpErrorResponse) => {
        this.isUploading.set(false);
        this.errorMessage.set(error.error?.detail ?? 'No se pudo procesar el archivo PDF.');
      }
    });

    input.value = '';
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
