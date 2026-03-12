import { Injectable, inject } from '@angular/core';
import { ApiService } from '../../services/api';

export interface OAuthApplication {
  id: string;
  name: string;
  client_id: string;
  application_type: string;
  redirect_uris: string[];
  post_logout_redirect_uris: string[];
  allowed_scopes: string[];
  grant_types: string[];
  token_endpoint_auth_method: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface OAuthApplicationCreate {
  name: string;
  application_type: string;
  redirect_uris: string[];
  post_logout_redirect_uris?: string[];
  allowed_scopes?: string[];
  grant_types?: string[];
  token_endpoint_auth_method?: string;
}

export interface OAuthApplicationCreateResponse extends OAuthApplication {
  client_secret: string;
}

@Injectable({ providedIn: 'root' })
export class ApplicationService {
  private api = inject(ApiService);

  list() { return this.api.get<OAuthApplication[]>('/product/applications'); }
  create(data: OAuthApplicationCreate) { return this.api.post<OAuthApplicationCreateResponse>('/product/applications', data); }
  get(id: string) { return this.api.get<OAuthApplication>(`/product/applications/${id}`); }
  update(id: string, data: Partial<OAuthApplication>) { return this.api.put<OAuthApplication>(`/product/applications/${id}`, data); }
  delete(id: string) { return this.api.delete(`/product/applications/${id}`); }
  rotateSecret(id: string) { return this.api.post<{client_secret: string}>(`/product/applications/${id}/rotate-secret`, {}); }
}
