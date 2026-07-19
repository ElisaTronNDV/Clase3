import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';

export interface Product {
  id: number;
  material: string;
  thickness_mm: number;
  length_mm: number;
  width_mm: number;
  stock: number;
  committed_stock: number;
  reorder_point: number;
}

export interface ProductInput {
  material: string;
  thickness_mm: number;
  length_mm: number;
  width_mm: number;
  stock: number;
  reorder_point: number;
}

@Injectable({ providedIn: 'root' })
export class InventoryService {
  private readonly http = inject(HttpClient);

  list(): Observable<Product[]> {
    return this.http.get<Product[]>(`${environment.apiUrl}/products`);
  }

  get(id: number): Observable<Product> {
    return this.http.get<Product>(`${environment.apiUrl}/products/${id}`);
  }

  create(product: ProductInput): Observable<Product> {
    return this.http.post<Product>(`${environment.apiUrl}/products`, product);
  }

  update(id: number, product: ProductInput): Observable<Product> {
    return this.http.put<Product>(`${environment.apiUrl}/products/${id}`, product);
  }
}
