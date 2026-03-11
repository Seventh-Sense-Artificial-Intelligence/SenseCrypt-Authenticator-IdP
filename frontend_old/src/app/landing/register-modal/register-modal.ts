import { Component, inject, output, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../services/auth';

type Step = 'register' | 'email-sent';

@Component({
  selector: 'app-register-modal',
  imports: [FormsModule],
  templateUrl: './register-modal.html',
  styleUrl: './register-modal.scss',
})
export class RegisterModal {
  close = output();
  switchToLogin = output();

  private auth = inject(AuthService);

  step = signal<Step>('register');
  fullName = '';
  email = '';
  password = '';
  confirmPassword = '';
  error = signal('');
  loading = signal(false);

  onRegister(): void {
    if (this.password !== this.confirmPassword) {
      this.error.set('Passwords do not match');
      return;
    }
    this.error.set('');
    this.loading.set(true);
    this.auth.register(this.fullName, this.email, this.password).subscribe({
      next: () => {
        this.loading.set(false);
        this.error.set('');
        this.step.set('email-sent');
      },
      error: (err) => {
        this.loading.set(false);
        this.error.set(err.error?.detail || 'Registration failed');
      },
    });
  }

  onBackdropClick(event: MouseEvent): void {
    if ((event.target as HTMLElement).classList.contains('modal-backdrop')) {
      this.close.emit();
    }
  }
}
