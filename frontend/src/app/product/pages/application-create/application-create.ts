import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { ApplicationService, OAuthApplicationCreateResponse } from '../../services/application.service';
import { InfoTip } from '../../../components/common/info-tip/info-tip';

@Component({
  selector: 'app-application-create',
  imports: [FormsModule, RouterLink, InfoTip],
  templateUrl: './application-create.html',
  styles: ``,
})
export class ApplicationCreate {
  private appService = inject(ApplicationService);
  private router = inject(Router);

  loading = signal(false);
  error = signal('');
  createdApp = signal<OAuthApplicationCreateResponse | null>(null);

  // Tooltip content
  tips = {
    name: '<span class="tip-title">Application Name</span><span class="tip-desc">A friendly label to help you identify this application in the dashboard. Only visible to administrators.</span>',
    type: '<span class="tip-title">Application Type</span><span class="tip-desc">Determines how your app communicates with the identity provider:</span><ul class="tip-list"><li><strong>Web</strong> &mdash; Server-side apps (e.g. Node, Python, PHP) that can securely store secrets</li><li><strong>SPA</strong> &mdash; Browser-only apps (e.g. Angular, React) that run entirely in the user\'s browser</li><li><strong>Native</strong> &mdash; Mobile or desktop apps installed on a user\'s device</li><li><strong>Machine to Machine</strong> &mdash; Backend services that talk to each other with no user involved</li></ul>',
    redirectUris: '<span class="tip-title">Redirect URIs</span><span class="tip-desc">After a user logs in, the browser is sent back to one of these URLs. Your app receives the login result here. The URL must match exactly &mdash; including the path and any query parameters.</span>',
    postLogoutRedirectUris: '<span class="tip-title">Post-Logout Redirect URIs</span><span class="tip-desc">After a user logs out, the browser can be sent to one of these URLs. Useful for showing a &ldquo;You have been logged out&rdquo; page or redirecting back to your homepage.</span>',
    scopes: '<span class="tip-title">Allowed Scopes</span><span class="tip-desc">Controls what user information this application is allowed to request:</span><ul class="tip-list"><li><strong>OpenID</strong> &mdash; Required. Proves the user\'s identity (always on)</li><li><strong>Profile</strong> &mdash; Access to the user\'s name and basic profile details</li><li><strong>Email</strong> &mdash; Access to the user\'s email address</li></ul>',
    grantTypes: '<span class="tip-title">Grant Types</span><span class="tip-desc">The login and token methods this application is allowed to use:</span><ul class="tip-list"><li><strong>Authorization Code</strong> &mdash; The standard login flow. The user signs in, and your app receives a one-time code to exchange for tokens. Recommended for most apps.</li><li><strong>Refresh Token</strong> &mdash; Lets your app get new access tokens without making the user log in again. Keeps sessions alive in the background.</li><li><strong>Client Credentials</strong> &mdash; For server-to-server communication with no user involved. The app authenticates using its own ID and secret.</li></ul>',
    authMethod: '<span class="tip-title">Token Endpoint Auth Method</span><span class="tip-desc">How your app proves its identity when exchanging codes for tokens:</span><ul class="tip-list"><li><strong>Client Secret (POST)</strong> &mdash; Sends the secret in the request body. Most common for server-side apps.</li><li><strong>Client Secret (Basic)</strong> &mdash; Sends the secret in an HTTP header. An alternative for server-side apps.</li><li><strong>None (Public Client)</strong> &mdash; No secret is used. Required for SPAs and mobile apps that cannot securely store a secret.</li></ul>',
  };

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
