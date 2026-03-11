import { Routes } from '@angular/router';
import { authGuard } from './guards/auth-guard';
import { productRoutes } from './product/product.routes';

export const routes: Routes = [
  {
    path: '',
    loadComponent: () => import('./components/pages/landing/landing').then((m) => m.Landing),
  },
  {
    path: 'dashboard',
    loadComponent: () => import('./components/pages/dashboard/dashboard').then((m) => m.Dashboard),
    canActivate: [authGuard],
    children: [
      { path: '', loadComponent: () => import('./components/pages/dashboard/overview/overview').then((m) => m.Overview) },
      { path: 'profile', loadComponent: () => import('./components/pages/dashboard/profile/profile').then((m) => m.Profile) },
      ...productRoutes,
    ],
  },
  {
    path: 'verify-email',
    loadComponent: () => import('./components/pages/verify-email/verify-email').then((m) => m.VerifyEmail),
  },
  { path: '**', redirectTo: '' },
];
