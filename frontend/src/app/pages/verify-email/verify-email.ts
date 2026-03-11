import { Component, inject, OnInit, signal } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { AuthService } from '../../services/auth';

@Component({
  selector: 'app-verify-email',
  imports: [],
  templateUrl: './verify-email.html',
  styles: ``,
})
export class VerifyEmail implements OnInit {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private auth = inject(AuthService);

  status = signal<'verifying' | 'success' | 'error'>('verifying');
  errorMessage = signal('');

  ngOnInit(): void {
    const token = this.route.snapshot.queryParamMap.get('token');
    if (!token) {
      this.status.set('error');
      this.errorMessage.set('No verification token provided.');
      return;
    }
    this.auth.verifyEmail(token).subscribe({
      next: () => {
        this.status.set('success');
        setTimeout(() => this.router.navigate(['/dashboard']), 2000);
      },
      error: (e) => {
        this.status.set('error');
        this.errorMessage.set(e.error?.detail || 'Verification failed. The link may have expired.');
      },
    });
  }
}
