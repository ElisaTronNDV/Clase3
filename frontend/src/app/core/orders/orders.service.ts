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

@Injectable({ providedIn: 'root' })
export class OrdersService {
  private readonly http = inject(HttpClient);

  extractPdf(file: File): Observable<PdfExtractionResult> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post<PdfExtractionResult>(`${environment.apiUrl}/orders/extract-pdf`, formData);
  }
}
