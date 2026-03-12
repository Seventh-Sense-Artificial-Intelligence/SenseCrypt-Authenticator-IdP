import { Component, inject, signal, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink, ActivatedRoute } from '@angular/router';
import { ApplicationService, OAuthApplication } from '../../services/application.service';
import { InfoTip } from '../../../components/common/info-tip/info-tip';

@Component({
  selector: 'app-application-detail',
  imports: [FormsModule, RouterLink, InfoTip],
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
  copiedField = signal('');

  // Tooltip content
  tips = {
    clientId: '<span class="tip-title">Client ID</span><span class="tip-desc">A unique public identifier assigned to your application. You\'ll include this in login URLs and token requests so the identity provider knows which app is making the request.</span>',
    name: '<span class="tip-title">Application Name</span><span class="tip-desc">A friendly label for this application. This name is shown to users during login so they know which app is asking for access.</span>',
    type: '<span class="tip-title">Application Type</span><span class="tip-desc">Defines how your app runs and what security rules apply:</span><ul class="tip-list"><li><strong>Web</strong> &mdash; Traditional server-side app (e.g. Django, Express). Secrets are stored securely on your server.</li><li><strong>SPA</strong> &mdash; Runs entirely in the browser (e.g. Angular, React). Cannot safely store secrets, so uses PKCE instead.</li><li><strong>Native</strong> &mdash; Mobile or desktop app installed on a device.</li><li><strong>Machine to Machine</strong> &mdash; Backend service that talks directly to APIs with no user involved.</li></ul>',
    redirectUris: '<span class="tip-title">Redirect URIs</span><span class="tip-desc">After a user logs in, the browser sends them back to one of these URLs with an authorization code. The URI in the login request must <strong>exactly match</strong> one listed here &mdash; even a trailing slash difference will cause an error.</span>',
    postLogoutRedirectUris: '<span class="tip-title">Post-Logout Redirect URIs</span><span class="tip-desc">When a user signs out, the browser can redirect them to one of these URLs. Useful for taking the user back to your app\'s homepage or a &ldquo;You\'ve been logged out&rdquo; page.</span>',
    scopes: '<span class="tip-title">Allowed Scopes</span><span class="tip-desc">Scopes control what user information your app can access:</span><ul class="tip-list"><li><strong>OpenID</strong> &mdash; Required. Proves the user\'s identity and returns a unique user ID.</li><li><strong>Profile</strong> &mdash; Access the user\'s display name.</li><li><strong>Email</strong> &mdash; Access the user\'s email address and whether it has been verified.</li></ul>',
    grantTypes: '<span class="tip-title">Grant Types</span><span class="tip-desc">The methods your app can use to get access tokens:</span><ul class="tip-list"><li><strong>Authorization Code</strong> &mdash; The standard and most secure login flow. The user signs in via the browser, and your app receives a short-lived code it exchanges for tokens behind the scenes.</li><li><strong>Refresh Token</strong> &mdash; Lets your app get a new access token when the current one expires, without making the user sign in again.</li><li><strong>Client Credentials</strong> &mdash; For server-to-server communication with no user involved. The app authenticates using its own Client ID and secret. Only available for Machine to Machine apps.</li></ul>',
    authMethod: '<span class="tip-title">Token Endpoint Auth Method</span><span class="tip-desc">How your app proves its identity when exchanging codes for tokens:</span><ul class="tip-list"><li><strong>Client Secret (POST)</strong> &mdash; Sends the Client ID and secret in the request body. Most common for web apps.</li><li><strong>Client Secret (Basic)</strong> &mdash; Sends credentials in an HTTP Basic Authorization header.</li><li><strong>None (Public Client)</strong> &mdash; No secret is sent. Used by SPAs and native apps that cannot safely store secrets &mdash; relies on PKCE for security instead.</li></ul>',
  };

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

  formatType(type: string): string {
    const map: Record<string, string> = {
      web: 'Web',
      spa: 'Single Page Application (SPA)',
      native: 'Native',
      machine_to_machine: 'Machine to Machine',
    };
    return map[type] || type;
  }

  copyToClipboard(field: string, text: string): void {
    navigator.clipboard.writeText(text);
    this.copiedField.set(field);
    setTimeout(() => this.copiedField.set(''), 1500);
  }
}
