import { Routes } from '@angular/router';

export const productRoutes: Routes = [
  {
    path: 'applications',
    loadComponent: () => import('./pages/applications/applications').then(m => m.Applications),
  },
  {
    path: 'applications/new',
    loadComponent: () => import('./pages/application-create/application-create').then(m => m.ApplicationCreate),
  },
  {
    path: 'applications/:id',
    loadComponent: () => import('./pages/application-detail/application-detail').then(m => m.ApplicationDetail),
  },
];
