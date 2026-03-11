import { Component, inject, OnInit, AfterViewInit, OnDestroy, signal, viewChild, ElementRef } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { ThemeService } from '../../../services/theme';
import { AuthService } from '../../../services/auth';

type Modal = null | 'login' | 'register' | 'forgot' | 'reset' | 'email-sent';

@Component({
  selector: 'app-landing',
  imports: [FormsModule],
  templateUrl: './landing.html',
  styles: ``,
})
export class Landing implements OnInit, AfterViewInit, OnDestroy {
  private route = inject(ActivatedRoute);
  private auth = inject(AuthService);
  private router = inject(Router);
  theme = inject(ThemeService);

  slideContainer = viewChild<ElementRef>('slideContainer');
  featuresInner = viewChild<ElementRef>('featuresInner');
  stepsInner = viewChild<ElementRef>('stepsInner');
  private resizeObserver?: ResizeObserver;
  private baseDpr = window.devicePixelRatio;
  modalZoom = signal(1);

  modal = signal<Modal>(null);
  resetToken = '';

  loginEmail = '';
  loginPassword = '';
  regName = '';
  regEmail = '';
  regPassword = '';
  regCompany = '';
  forgotEmail = '';
  newPassword = '';
  newConfirm = '';

  showRegPassword = signal(false);
  showLoginPassword = signal(false);

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

  ngAfterViewInit(): void {
    this.resizeObserver = new ResizeObserver(() => this.onResize());
    const container = this.slideContainer()?.nativeElement;
    if (container) this.resizeObserver.observe(container);
    // Also scale on window resize (zoom changes)
    window.addEventListener('resize', this.onResize);
    setTimeout(() => this.onResize(), 0);
  }

  ngOnDestroy(): void {
    this.resizeObserver?.disconnect();
    window.removeEventListener('resize', this.onResize);
  }

  private onResize = (): void => {
    this.scaleSlide();
    this.fitModal();
  };

  private scaleSlide = (): void => {
    // Only apply slide scaling on desktop (lg breakpoint)
    if (window.innerWidth < 1024) {
      this.resetZoom(this.featuresInner()?.nativeElement);
      this.resetZoom(this.stepsInner()?.nativeElement);
      return;
    }
    this.scaleSection(this.featuresInner()?.nativeElement);
    this.scaleSection(this.stepsInner()?.nativeElement);
  };

  private scaleSection(inner: HTMLElement | undefined): void {
    if (!inner) return;
    const section = inner.parentElement!;
    // Reset zoom to measure natural content height
    (inner.style as any).zoom = '1';
    void inner.offsetHeight;
    const sectionH = section.clientHeight;
    const contentH = inner.scrollHeight;
    if (contentH > sectionH && sectionH > 0) {
      (inner.style as any).zoom = `${sectionH / contentH}`;
    } else {
      (inner.style as any).zoom = '1';
    }
  }

  private resetZoom(inner: HTMLElement | undefined): void {
    if (!inner) return;
    (inner.style as any).zoom = '1';
  }

  scrollTo(id: string): void {
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
  }

  openModal(m: Modal): void {
    this.error.set('');
    this.success.set('');
    this.loading.set(false);
    this.modal.set(m);
    setTimeout(() => this.fitModal(), 0);
  }

  private fitModal(): void {
    const box = document.querySelector('.modal-box') as HTMLElement;
    if (!box) {
      this.modalZoom.set(this.baseDpr / window.devicePixelRatio);
      return;
    }
    // Measure natural height at zoom 1
    (box.style as any).zoom = '1';
    void box.offsetHeight;
    const naturalH = box.scrollHeight;
    const availableH = window.innerHeight - 48; // generous padding for Safari rounding
    const dprZoom = this.baseDpr / window.devicePixelRatio;
    const fitZoom = naturalH > availableH ? availableH / naturalH : 1;
    this.modalZoom.set(Math.min(dprZoom, fitZoom));
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
    this.error.set('');
    this.loading.set(true);
    this.auth.register(this.regName, this.regEmail, this.regPassword, this.regCompany).subscribe({
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
