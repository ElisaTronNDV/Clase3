import { Routes } from '@angular/router';

import { authGuard } from './core/auth/auth.guard';

export const routes: Routes = [
  { path: '', pathMatch: 'full', redirectTo: 'home' },
  {
    path: 'login',
    loadComponent: () => import('./features/auth/login/login.component').then((m) => m.LoginComponent)
  },
  {
    path: 'register',
    loadComponent: () =>
      import('./features/auth/register/register.component').then((m) => m.RegisterComponent)
  },
  {
    path: '',
    canActivate: [authGuard],
    loadComponent: () => import('./layout/shell.component').then((m) => m.ShellComponent),
    children: [
      {
        path: 'home',
        loadComponent: () => import('./features/home/home.component').then((m) => m.HomeComponent)
      },
      {
        path: 'configuracion',
        loadComponent: () => import('./features/config/config.component').then((m) => m.ConfigComponent)
      },
      {
        path: 'inventario',
        loadComponent: () =>
          import('./features/inventory/inventory-list.component').then((m) => m.InventoryListComponent)
      },
      {
        path: 'inventario/nuevo',
        loadComponent: () =>
          import('./features/inventory/inventory-form.component').then((m) => m.InventoryFormComponent)
      },
      {
        path: 'inventario/:id/editar',
        loadComponent: () =>
          import('./features/inventory/inventory-form.component').then((m) => m.InventoryFormComponent)
      },
      {
        path: 'oficina/nueva-orden',
        loadComponent: () =>
          import('./features/orders/create-order.component').then((m) => m.CreateOrderComponent)
      },
      {
        path: 'oficina/ordenes/:id/imprimir',
        loadComponent: () =>
          import('./features/orders/print-order.component').then((m) => m.PrintOrderComponent)
      },
      {
        path: 'taller/finalizar-orden',
        loadComponent: () =>
          import('./features/taller/scan-order.component').then((m) => m.ScanOrderComponent)
      }
    ]
  },
  { path: '**', redirectTo: 'home' }
];
