import { Component, inject, signal, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink, ActivatedRoute } from '@angular/router';
import { ApplicationService, OAuthApplication } from '../../services/application.service';

@Component({
  selector: 'app-application-detail',
  imports: [FormsModule, RouterLink],
  templateUrl: './application-detail.html',
  styles: ``,
})
export class ApplicationDetail implements OnInit {
  private appService = inject(ApplicationService);
  private router = inject(Router);
  private route = inject(ActivatedRoute);

  app = signal<OAuthApplication | null>(null);
  loading = signal(true);
  saving = signal(false);
  message = signal('');
  messageType = signal<'success' | 'error'>('success');
  showDeleteConfirm = signal(false);
  showRotateConfirm = signal(false);
  newSecret = signal('');

  // Form fields
  name = '';
  redirectUris = '';
  postLogoutRedirectUris = '';
  allowedScopes: string[] = [];
  grantTypes: string[] = [];
  tokenEndpointAuthMethod = '';
  isActive = true;

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.appService.get(id).subscribe({
        next: (app) => {
          this.app.set(app);
          this.populateForm(app);
          this.loading.set(false);
        },
        error: () => {
          this.loading.set(false);
        },
      });
    }
  }

  private populateForm(app: OAuthApplication): void {
    this.name = app.name;
    this.redirectUris = (app.redirect_uris || []).join('\n');
    this.postLogoutRedirectUris = (app.post_logout_redirect_uris || []).join('\n');
    this.allowedScopes = [...(app.allowed_scopes || [])];
    this.grantTypes = [...(app.grant_types || [])];
    this.tokenEndpointAuthMethod = app.token_endpoint_auth_method;
    this.isActive = app.is_active;
  }

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

  save(): void {
    const currentApp = this.app();
    if (!currentApp) return;

    this.message.set('');
    this.saving.set(true);

    const redirectUris = this.redirectUris
      .split('\n')
      .map(u => u.trim())
      .filter(u => u.length > 0);

    const postLogoutRedirectUris = this.postLogoutRedirectUris
      .split('\n')
      .map(u => u.trim())
      .filter(u => u.length > 0);

    this.appService.update(currentApp.id, {
      name: this.name.trim(),
      redirect_uris: redirectUris,
      post_logout_redirect_uris: postLogoutRedirectUris,
      allowed_scopes: this.allowedScopes,
      grant_types: this.grantTypes,
      token_endpoint_auth_method: this.tokenEndpointAuthMethod,
      is_active: this.isActive,
    }).subscribe({
      next: (updated) => {
        this.saving.set(false);
        this.app.set(updated);
        this.messageType.set('success');
        this.message.set('Application updated successfully.');
      },
      error: () => {
        this.saving.set(false);
        this.messageType.set('error');
        this.message.set('Failed to update application.');
      },
    });
  }

  confirmDelete(): void {
    this.showDeleteConfirm.set(true);
  }

  cancelDelete(): void {
    this.showDeleteConfirm.set(false);
  }

  deleteApp(): void {
    const currentApp = this.app();
    if (!currentApp) return;

    this.appService.delete(currentApp.id).subscribe({
      next: () => {
        this.router.navigate(['/dashboard/applications']);
      },
      error: () => {
        this.showDeleteConfirm.set(false);
        this.messageType.set('error');
        this.message.set('Failed to delete application.');
      },
    });
  }

  confirmRotateSecret(): void {
    this.showRotateConfirm.set(true);
  }

  cancelRotateSecret(): void {
    this.showRotateConfirm.set(false);
  }

  rotateSecret(): void {
    const currentApp = this.app();
    if (!currentApp) return;

    this.appService.rotateSecret(currentApp.id).subscribe({
      next: (result) => {
        this.showRotateConfirm.set(false);
        this.newSecret.set(result.client_secret);
      },
      error: () => {
        this.showRotateConfirm.set(false);
        this.messageType.set('error');
        this.message.set('Failed to rotate secret.');
      },
    });
  }

  copyToClipboard(text: string): void {
    navigator.clipboard.writeText(text);
  }
}
