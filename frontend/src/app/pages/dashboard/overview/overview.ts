import { Component, inject } from '@angular/core';
import { AuthService } from '../../../services/auth';

@Component({
  selector: 'app-overview',
  imports: [],
  templateUrl: './overview.html',
  styles: ``,
})
export class Overview {
  auth = inject(AuthService);
}
