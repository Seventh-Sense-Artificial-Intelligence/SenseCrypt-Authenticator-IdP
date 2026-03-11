import { Component, inject, OnInit, signal } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { ThemeService } from '../../services/theme';
import { AuthService } from '../../services/auth';

type Modal = null | 'login' | 'register' | 'forgot' | 'reset' | 'email-sent';

@Component({
  selector: 'app-landing',
  imports: [FormsModule],
  templateUrl: './landing.html',
  styles: ``,
})
export class Landing implements OnInit {
  private route = inject(ActivatedRoute);
  private auth = inject(AuthService);
  private router = inject(Router);
  theme = inject(ThemeService);

  modal = signal<Modal>(null);
  resetToken = '';

  loginEmail = '';
  loginPassword = '';
  regName = '';
  regEmail = '';
  regPassword = '';
  regConfirm = '';
  forgotEmail = '';
  newPassword = '';
  newConfirm = '';

  error = signal('');
  success = signal('');
  loading = signal(false);

  features = [
    { icon: 'key', title: 'Passwordless MFA', desc: 'Your face generates a cryptographic key on-the-fly. Nothing stored, nothing stolen.' },
    { icon: 'shield', title: 'Account Recovery', desc: 'No passwords means no phishing, no credential stuffing, no breaches.' },
    { icon: 'camera', title: 'Step-up Auth', desc: 'Works with any camera-equipped device. No hardware tokens, no dongles.' },
    { icon: 'building', title: 'Enterprise Ready', desc: 'SOC2 compliant, GDPR ready. Integrates with your existing identity stack.' },
  ];

  steps = [
    { num: '01', title: 'Scan', desc: 'A quick face scan captures your unique facial geometry using your device camera.' },
    { num: '02', title: 'Generate', desc: 'Your private key is generated on-the-fly from your face — never stored, never transmitted.' },
    { num: '03', title: 'Authenticate', desc: 'Prove your identity cryptographically without exposing any biometric data.' },
  ];

  ngOnInit(): void {
    const token = this.route.snapshot.queryParamMap.get('resetToken');
    if (token) {
      this.resetToken = token;
      this.openModal('reset');
    }
  }

  scrollTo(id: string): void {
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
  }

  openModal(m: Modal): void {
    this.error.set('');
    this.success.set('');
    this.loading.set(false);
    this.modal.set(m);
  }

  closeModal(): void {
    this.modal.set(null);
  }

  onBackdrop(e: MouseEvent): void {
    if ((e.target as HTMLElement).classList.contains('modal-overlay')) this.closeModal();
  }

  onLogin(): void {
    this.error.set('');
    this.loading.set(true);
    this.auth.login(this.loginEmail, this.loginPassword).subscribe({
      next: () => { this.closeModal(); this.router.navigate(['/dashboard']); },
      error: (e) => { this.loading.set(false); this.error.set(e.error?.detail || 'Login failed'); },
    });
  }

  onRegister(): void {
    if (this.regPassword !== this.regConfirm) { this.error.set('Passwords do not match'); return; }
    this.error.set('');
    this.loading.set(true);
    this.auth.register(this.regName, this.regEmail, this.regPassword).subscribe({
      next: () => { this.loading.set(false); this.openModal('email-sent'); },
      error: (e) => { this.loading.set(false); this.error.set(e.error?.detail || 'Registration failed'); },
    });
  }

  onForgot(): void {
    this.error.set('');
    this.auth.forgotPassword(this.forgotEmail).subscribe({
      next: (r) => this.success.set(r.message),
      error: () => this.success.set('If an account exists, a reset email has been sent'),
    });
  }

  onResetPassword(): void {
    if (this.newPassword !== this.newConfirm) { this.error.set('Passwords do not match'); return; }
    this.error.set('');
    this.loading.set(true);
    this.auth.resetPassword(this.resetToken, this.newPassword).subscribe({
      next: () => { this.loading.set(false); this.success.set('Password reset. You can now sign in.'); },
      error: (e) => { this.loading.set(false); this.error.set(e.error?.detail || 'Reset failed'); },
    });
  }
}
