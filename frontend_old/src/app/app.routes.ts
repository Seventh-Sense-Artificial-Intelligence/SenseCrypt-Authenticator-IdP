import { Routes } from '@angular/router';
import { authGuard } from './guards/auth-guard';

export const routes: Routes = [
  {
    path: '',
    loadComponent: () => import('./landing').then((m) => m.Landing),
  },
  {
    path: 'dashboard',
    loadComponent: () => import('./dashboard').then((m) => m.Dashboard),
    canActivate: [authGuard],
    children: [
      { path: '', loadComponent: () => import('./dashboard/overview/overview').then((m) => m.Overview) },
      { path: 'profile', loadComponent: () => import('./dashboard/profile/profile').then((m) => m.Profile) },
    ],
  },
  {
    path: 'verify-email',
    loadComponent: () => import('./verify-email/verify-email').then((m) => m.VerifyEmail),
  },
  { path: '**', redirectTo: '' },
];
