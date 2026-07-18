import { Component, OnInit, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { RouterLink } from '@angular/router';

import { ConfigService } from '../../core/config/config.service';

@Component({
  selector: 'app-config',
  standalone: true,
  imports: [ReactiveFormsModule, RouterLink],
  templateUrl: './config.component.html',
  styleUrl: './config.component.scss'
})
export class ConfigComponent implements OnInit {
  private readonly fb = inject(FormBuilder);
  private readonly configService = inject(ConfigService);

  readonly form = this.fb.nonNullable.group({
    tolerance_mm: [1, [Validators.required, Validators.min(0.01)]]
  });

  readonly isLoading = signal(true);
  readonly isSubmitting = signal(false);
  readonly errorMessage = signal<string | null>(null);
  readonly successMessage = signal<string | null>(null);

  ngOnInit(): void {
    this.configService.getConfig().subscribe({
      next: (config) => {
        this.form.patchValue({ tolerance_mm: config.tolerance_mm });
        this.isLoading.set(false);
      },
      error: () => {
        this.errorMessage.set('No se pudo cargar la configuración.');
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
    this.successMessage.set(null);
    this.isSubmitting.set(true);
    const { tolerance_mm } = this.form.getRawValue();

    this.configService.updateConfig(tolerance_mm).subscribe({
      next: () => {
        this.isSubmitting.set(false);
        this.successMessage.set('Configuración guardada.');
      },
      error: () => {
        this.isSubmitting.set(false);
        this.errorMessage.set('No se pudo guardar la configuración.');
      }
    });
  }
}
