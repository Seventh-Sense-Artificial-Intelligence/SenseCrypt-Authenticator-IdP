import { Component, inject, OnInit, signal } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Hero } from './landing/hero/hero';
import { Features } from './landing/features/features';
import { HowItWorks } from './landing/how-it-works/how-it-works';
import { LoginModal } from './landing/login-modal/login-modal';
import { RegisterModal } from './landing/register-modal/register-modal';
import { ResetPasswordModal } from './landing/reset-password-modal/reset-password-modal';
import { ThemeService } from './services/theme';

@Component({
  selector: 'app-landing',
  imports: [Hero, Features, HowItWorks, LoginModal, RegisterModal, ResetPasswordModal],
  templateUrl: './landing.html',
  styleUrl: './landing.scss',
})
export class Landing implements OnInit {
  private route = inject(ActivatedRoute);

  showLogin = signal(false);
  showRegister = signal(false);
  showResetPassword = signal(false);
  resetToken = signal('');
  theme = new ThemeService();

  ngOnInit(): void {
    const token = this.route.snapshot.queryParamMap.get('resetToken');
    if (token) {
      this.resetToken.set(token);
      this.showResetPassword.set(true);
    }
  }

  openLogin(): void {
    this.closeModals();
    this.showLogin.set(true);
  }

  openRegister(): void {
    this.closeModals();
    this.showRegister.set(true);
  }

  closeModals(): void {
    this.showLogin.set(false);
    this.showRegister.set(false);
    this.showResetPassword.set(false);
  }
}
