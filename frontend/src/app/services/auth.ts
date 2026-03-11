import { Injectable, inject, signal } from '@angular/core';
import { ApiService } from './api';
import { Router } from '@angular/router';
import { tap } from 'rxjs';

interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface UserProfile {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  private api = inject(ApiService);
  private router = inject(Router);

  user = signal<UserProfile | null>(null);

  login(email: string, password: string) {
    return this.api.post<TokenResponse>('/auth/login', { email, password }).pipe(
      tap((res) => {
        localStorage.setItem('token', res.access_token);
        this.loadUser();
      }),
    );
  }

  register(full_name: string, email: string, password: string) {
    return this.api.post<{ message: string }>('/auth/register', { email, password, full_name });
  }

  verifyEmail(token: string) {
    return this.api.get<TokenResponse>(`/auth/verify-email?token=${token}`).pipe(
      tap((res) => {
        localStorage.setItem('token', res.access_token);
        this.loadUser();
      }),
    );
  }

  forgotPassword(email: string) {
    return this.api.post<{ message: string }>('/auth/forgot-password', { email });
  }

  resetPassword(token: string, password: string) {
    return this.api.post<{ message: string }>('/auth/reset-password', { token, password });
  }

  logout(): void {
    localStorage.removeItem('token');
    this.user.set(null);
    this.router.navigate(['/']);
  }

  isAuthenticated(): boolean {
    const token = localStorage.getItem('token');
    if (!token) return false;
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      return payload.exp * 1000 > Date.now();
    } catch {
      return false;
    }
  }

  getToken(): string | null {
    return localStorage.getItem('token');
  }

  loadUser(): void {
    if (this.isAuthenticated()) {
      this.api.get<UserProfile>('/users/me').subscribe({
        next: (user) => this.user.set(user),
        error: () => this.logout(),
      });
    }
  }
}
