import { Component, inject, input, output, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../services/api';

@Component({
  selector: 'app-reset-password-modal',
  imports: [FormsModule],
  templateUrl: './reset-password-modal.html',
  styleUrl: './reset-password-modal.scss',
})
export class ResetPasswordModal {
  token = input.required<string>();
  close = output();
  switchToLogin = output();

  private api = inject(ApiService);

  password = '';
  confirmPassword = '';
  loading = signal(false);
  error = signal('');
  success = signal(false);

  onSubmit(): void {
    if (this.password !== this.confirmPassword) {
      this.error.set('Passwords do not match');
      return;
    }
    this.error.set('');
    this.loading.set(true);
    this.api.post<{ message: string }>('/auth/reset-password', {
      token: this.token(),
      password: this.password,
    }).subscribe({
      next: () => {
        this.loading.set(false);
        this.success.set(true);
      },
      error: (err) => {
        this.loading.set(false);
        this.error.set(err.error?.detail || 'Reset failed. The link may have expired.');
      },
    });
  }

  onBackdropClick(event: MouseEvent): void {
    if ((event.target as HTMLElement).classList.contains('modal-backdrop')) {
      this.close.emit();
    }
  }
}
