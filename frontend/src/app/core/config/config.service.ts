import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';

export interface SystemConfig {
  tolerance_mm: number;
}

@Injectable({ providedIn: 'root' })
export class ConfigService {
  private readonly http = inject(HttpClient);

  getConfig(): Observable<SystemConfig> {
    return this.http.get<SystemConfig>(`${environment.apiUrl}/config`);
  }

  updateConfig(toleranceMm: number): Observable<SystemConfig> {
    return this.http.put<SystemConfig>(`${environment.apiUrl}/config`, { tolerance_mm: toleranceMm });
  }
}
