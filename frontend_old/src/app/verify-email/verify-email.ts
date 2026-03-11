import { Component, inject, OnInit, signal } from '@angular/core';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { AuthService } from '../services/auth';

@Component({
  selector: 'app-verify-email',
  imports: [RouterLink],
  template: `
    <div class="flex items-center justify-center min-h-screen p-6">
      <div class="text-center bg-white dark:bg-surface-dark-elevated rounded-2xl p-8 max-w-md w-full shadow-lg">
        @if (loading()) {
          <h2 class="font-display text-2xl font-bold mb-2 text-body dark:text-white">Verifying your email...</h2>
          <p class="text-muted">Please wait while we verify your account.</p>
        }
        @if (error()) {
          <h2 class="font-display text-2xl font-bold mb-2 text-body dark:text-white">Verification failed</h2>
          <p class="text-red-500 mb-6">{{ error() }}</p>
          <a routerLink="/" class="btn-cta">Back to Home</a>
        }
      </div>
    </div>
  `,
  styles: `:host { display: block; }`,
})
export class VerifyEmail implements OnInit {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private auth = inject(AuthService);

  loading = signal(true);
  error = signal('');

  ngOnInit(): void {
    const token = this.route.snapshot.queryParamMap.get('token');
    if (!token) {
      this.loading.set(false);
      this.error.set('Missing verification token.');
      return;
    }

    this.auth.verifyEmail(token).subscribe({
      next: () => {
        this.router.navigate(['/dashboard']);
      },
      error: (err) => {
        this.loading.set(false);
        this.error.set(err.error?.detail || 'Verification failed. The link may have expired.');
      },
    });
  }
}
