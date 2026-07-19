import { HttpErrorResponse } from '@angular/common/http';
import { Component, OnInit, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';

import { InventoryService, Product } from '../../core/inventory/inventory.service';

@Component({
  selector: 'app-inventory-form',
  standalone: true,
  imports: [ReactiveFormsModule, RouterLink],
  templateUrl: './inventory-form.component.html',
  styleUrl: './inventory-form.component.scss'
})
export class InventoryFormComponent implements OnInit {
  private readonly fb = inject(FormBuilder);
  private readonly inventoryService = inject(InventoryService);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);

  private readonly productId = this.route.snapshot.paramMap.get('id');
  readonly isEditMode = this.productId !== null;

  readonly form = this.fb.nonNullable.group({
    material: ['', [Validators.required]],
    thickness_mm: [0, [Validators.required, Validators.min(0.01)]],
    length_mm: [0, [Validators.required, Validators.min(0.01)]],
    width_mm: [0, [Validators.required, Validators.min(0.01)]],
    stock: [0, [Validators.required, Validators.min(0)]],
    reorder_point: [0, [Validators.required, Validators.min(0)]]
  });

  readonly committedStock = signal<number | null>(null);
  readonly isLoading = signal(false);
  readonly isSubmitting = signal(false);
  readonly errorMessage = signal<string | null>(null);

  ngOnInit(): void {
    if (!this.isEditMode) {
      return;
    }

    this.isLoading.set(true);
    this.inventoryService.get(Number(this.productId)).subscribe({
      next: (product: Product) => {
        this.form.patchValue(product);
        this.committedStock.set(product.committed_stock);
        this.isLoading.set(false);
      },
      error: () => {
        this.errorMessage.set('No se pudo cargar el producto.');
        this.isLoading.set(false);
      }
    });
  }

  submit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    this.errorMessage.set(null);
    this.isSubmitting.set(true);
    const product = this.form.getRawValue();

    const request = this.isEditMode
      ? this.inventoryService.update(Number(this.productId), product)
      : this.inventoryService.create(product);

    request.subscribe({
      next: () => {
        this.isSubmitting.set(false);
        this.router.navigateByUrl('/inventario');
      },
      error: (error: HttpErrorResponse) => {
        this.isSubmitting.set(false);
        this.errorMessage.set(
          error.status === 409
            ? 'Ya existe un producto con ese material, espesor y dimensiones.'
            : 'No se pudo guardar el producto.'
        );
      }
    });
  }
}
