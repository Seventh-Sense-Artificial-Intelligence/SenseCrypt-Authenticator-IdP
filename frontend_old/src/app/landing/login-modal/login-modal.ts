import { Component, inject, output, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../services/auth';
import { Router } from '@angular/router';

@Component({
  selector: 'app-login-modal',
  imports: [FormsModule],
  templateUrl: './login-modal.html',
  styleUrl: './login-modal.scss',
})
export class LoginModal {
  close = output();
  switchToRegister = output();

  private auth = inject(AuthService);
  private router = inject(Router);

  email = '';
  password = '';
  forgotEmail = '';
  error = signal('');
  showForgot = signal(false);
  forgotMessage = signal('');
  loading = signal(false);

  onLogin(): void {
    this.error.set('');
    this.loading.set(true);
    this.auth.login(this.email, this.password).subscribe({
      next: () => {
        this.loading.set(false);
        this.close.emit();
        this.router.navigate(['/dashboard']);
      },
      error: (err) => {
        this.loading.set(false);
        this.error.set(err.error?.detail || 'Login failed');
      },
    });
  }

  onForgotPassword(): void {
    this.auth.forgotPassword(this.forgotEmail).subscribe({
      next: (res) => this.forgotMessage.set(res.message),
      error: () => this.forgotMessage.set('Something went wrong. Please try again.'),
    });
  }

  onBackdropClick(event: MouseEvent): void {
    if ((event.target as HTMLElement).classList.contains('modal-backdrop')) {
      this.close.emit();
    }
  }
}
