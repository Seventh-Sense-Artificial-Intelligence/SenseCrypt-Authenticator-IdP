import { Component, inject, OnInit } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { TopNav } from '../../common/top-nav/top-nav';
import { LeftNav } from '../../common/left-nav/left-nav';
import { AuthService } from '../../../services/auth';

@Component({
  selector: 'app-dashboard',
  imports: [RouterOutlet, TopNav, LeftNav],
  templateUrl: './dashboard.html',
  styles: ``,
})
export class Dashboard implements OnInit {
  private auth = inject(AuthService);

  ngOnInit(): void {
    this.auth.loadUser();
  }
}
