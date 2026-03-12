import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { ApplicationService, OAuthApplicationCreateResponse } from '../../services/application.service';

@Component({
  selector: 'app-application-create',
  imports: [FormsModule, RouterLink],
  templateUrl: './application-create.html',
  styles: ``,
})
export class ApplicationCreate {
  private appService = inject(ApplicationService);
  private router = inject(Router);

  loading = signal(false);
  error = signal('');
  createdApp = signal<OAuthApplicationCreateResponse | null>(null);

  name = '';
  applicationType = 'web';
  redirectUris = '';
  postLogoutRedirectUris = '';
  allowedScopes: string[] = ['openid', 'profile', 'email'];
  grantTypes: string[] = ['authorization_code', 'refresh_token'];
  tokenEndpointAuthMethod = 'client_secret_post';

  toggleScope(scope: string): void {
    if (scope === 'openid') return;
    const idx = this.allowedScopes.indexOf(scope);
    if (idx >= 0) {
      this.allowedScopes = this.allowedScopes.filter(s => s !== scope);
    } else {
      this.allowedScopes = [...this.allowedScopes, scope];
    }
  }

  toggleGrantType(gt: string): void {
    const idx = this.grantTypes.indexOf(gt);
    if (idx >= 0) {
      this.grantTypes = this.grantTypes.filter(g => g !== gt);
    } else {
      this.grantTypes = [...this.grantTypes, gt];
    }
  }

  hasScope(scope: string): boolean {
    return this.allowedScopes.includes(scope);
  }

  hasGrantType(gt: string): boolean {
    return this.grantTypes.includes(gt);
  }

  submit(): void {
    this.error.set('');

    if (!this.name.trim()) {
      this.error.set('Application name is required.');
      return;
    }

    const redirectUris = this.redirectUris
      .split('\n')
      .map(u => u.trim())
      .filter(u => u.length > 0);

    if (redirectUris.length === 0) {
      this.error.set('At least one redirect URI is required.');
      return;
    }

    const postLogoutRedirectUris = this.postLogoutRedirectUris
      .split('\n')
      .map(u => u.trim())
      .filter(u => u.length > 0);

    this.loading.set(true);

    this.appService.create({
      name: this.name.trim(),
      application_type: this.applicationType,
      redirect_uris: redirectUris,
      post_logout_redirect_uris: postLogoutRedirectUris.length > 0 ? postLogoutRedirectUris : undefined,
      allowed_scopes: this.allowedScopes,
      grant_types: this.grantTypes,
      token_endpoint_auth_method: this.tokenEndpointAuthMethod,
    }).subscribe({
      next: (app) => {
        this.loading.set(false);
        this.createdApp.set(app);
      },
      error: () => {
        this.loading.set(false);
        this.error.set('Failed to create application. Please try again.');
      },
    });
  }

  copyToClipboard(text: string): void {
    navigator.clipboard.writeText(text);
  }

  goToApplication(): void {
    const app = this.createdApp();
    if (app) {
      this.router.navigate(['/dashboard/applications', app.id]);
    }
  }
}
