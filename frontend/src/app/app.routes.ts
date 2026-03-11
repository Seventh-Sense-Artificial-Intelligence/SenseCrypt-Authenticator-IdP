import { Routes } from '@angular/router';
import { authGuard } from './guards/auth-guard';

export const routes: Routes = [
  {
    path: '',
    loadComponent: () => import('./pages/landing/landing').then((m) => m.Landing),
  },
  {
    path: 'dashboard',
    loadComponent: () => import('./pages/dashboard/dashboard').then((m) => m.Dashboard),
    canActivate: [authGuard],
    children: [
      { path: '', loadComponent: () => import('./pages/dashboard/overview/overview').then((m) => m.Overview) },
      { path: 'profile', loadComponent: () => import('./pages/dashboard/profile/profile').then((m) => m.Profile) },
    ],
  },
  {
    path: 'verify-email',
    loadComponent: () => import('./pages/verify-email/verify-email').then((m) => m.VerifyEmail),
  },
  { path: '**', redirectTo: '' },
];
