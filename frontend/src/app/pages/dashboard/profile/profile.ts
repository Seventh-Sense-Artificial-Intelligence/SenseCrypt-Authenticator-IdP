import { Component, inject, signal, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../../services/auth';
import { ApiService } from '../../../services/api';

@Component({
  selector: 'app-profile',
  imports: [FormsModule],
  templateUrl: './profile.html',
  styles: ``,
})
export class Profile implements OnInit {
  auth = inject(AuthService);
  private api = inject(ApiService);

  fullName = '';
  message = signal('');
  loading = signal(false);

  ngOnInit(): void {
    this.fullName = this.auth.user()?.full_name || '';
  }

  save(): void {
    this.loading.set(true);
    this.api.put('/users/me', { full_name: this.fullName }).subscribe({
      next: () => {
        this.loading.set(false);
        this.message.set('Profile updated successfully');
        this.auth.loadUser();
      },
      error: () => {
        this.loading.set(false);
        this.message.set('Failed to update profile');
      },
    });
  }
}
