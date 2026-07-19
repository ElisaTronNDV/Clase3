import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';

export interface ExtractedPiece {
  pieza: string;
  descripcion: string;
  cantidad: number;
}

export interface ExtractedScrap {
  pieza: string;
  largo_mm: number;
  ancho_mm: number;
  cantidad: number;
}

export interface ExtractedNest {
  page_index: number;
  nombre_nest: string | null;
  multiplicidad: number | null;
  largo_mm: number | null;
  ancho_mm: number | null;
  espesor_mm: number | null;
  material: string | null;
  tiempo_ejecucion_estimado: string | null;
  piezas: ExtractedPiece[];
  recortes: ExtractedScrap[];
}

export interface PdfExtractionResult {
  nests: ExtractedNest[];
}

export interface WorkOrderPieceInput {
  pieza: string;
  descripcion: string;
  cantidad: number;
}

export interface WorkOrderScrapInput {
  pieza: string;
  largo_mm: number;
  ancho_mm: number;
  cantidad: number;
}

export interface WorkOrderInput {
  nombre_nest: string | null;
  material: string;
  thickness_mm: number;
  length_mm: number;
  width_mm: number;
  multiplicidad: number;
  tiempo_ejecucion_estimado: string | null;
  piezas: WorkOrderPieceInput[];
  recortes: WorkOrderScrapInput[];
  create_missing_product: boolean;
}

export interface WorkOrder {
  id: number;
  nest_code: string;
  status: string;
  nombre_nest: string | null;
  material: string;
  thickness_mm: number;
  length_mm: number;
  width_mm: number;
  multiplicidad: number;
  tiempo_ejecucion_estimado: string | null;
  low_stock_warning: boolean;
  piezas: WorkOrderPieceInput[];
  recortes: WorkOrderScrapInput[];
}

@Injectable({ providedIn: 'root' })
export class OrdersService {
  private readonly http = inject(HttpClient);

  extractPdf(file: File): Observable<PdfExtractionResult> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post<PdfExtractionResult>(`${environment.apiUrl}/orders/extract-pdf`, formData);
  }

  confirmOrder(order: WorkOrderInput): Observable<WorkOrder> {
    return this.http.post<WorkOrder>(`${environment.apiUrl}/orders`, order);
  }

  getOrder(id: number): Observable<WorkOrder> {
    return this.http.get<WorkOrder>(`${environment.apiUrl}/orders/${id}`);
  }

  getOrderByNestCode(nestCode: string): Observable<WorkOrder> {
    return this.http.get<WorkOrder>(`${environment.apiUrl}/orders/by-nest-code/${nestCode}`);
  }

  closeOrder(id: number): Observable<WorkOrder> {
    return this.http.post<WorkOrder>(`${environment.apiUrl}/orders/${id}/close`, {});
  }

  getBarcodeBlob(id: number): Observable<Blob> {
    return this.http.get(`${environment.apiUrl}/orders/${id}/barcode`, { responseType: 'blob' });
  }
}
