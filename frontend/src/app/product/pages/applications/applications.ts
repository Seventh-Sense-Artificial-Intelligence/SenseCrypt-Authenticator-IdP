import { Component, inject, signal, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { ApplicationService, OAuthApplication } from '../../services/application.service';

@Component({
  selector: 'app-applications',
  imports: [FormsModule],
  templateUrl: './applications.html',
  styles: ``,
})
export class Applications implements OnInit {
  private appService = inject(ApplicationService);
  private router = inject(Router);

  applications = signal<OAuthApplication[]>([]);
  loading = signal(true);

  ngOnInit(): void {
    this.appService.list().subscribe({
      next: (apps) => {
        this.applications.set(apps);
        this.loading.set(false);
      },
      error: () => {
        this.loading.set(false);
      },
    });
  }

  navigateToCreate(): void {
    this.router.navigate(['/dashboard/applications/new']);
  }

  navigateToDetail(id: string): void {
    this.router.navigate(['/dashboard/applications', id]);
  }

  copyToClipboard(text: string, event: Event): void {
    event.stopPropagation();
    navigator.clipboard.writeText(text);
  }

  formatDate(dateStr: string): string {
    return new Date(dateStr).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  }

  formatType(type: string): string {
    const map: Record<string, string> = {
      web: 'Web',
      spa: 'SPA',
      native: 'Native',
      machine_to_machine: 'M2M',
    };
    return map[type] || type;
  }
}
