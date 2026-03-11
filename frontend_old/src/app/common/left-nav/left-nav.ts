import { Component } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';

@Component({
  selector: 'app-left-nav',
  imports: [RouterLink, RouterLinkActive],
  templateUrl: './left-nav.html',
  styleUrl: './left-nav.scss',
})
export class LeftNav {
  links = [
    { path: '/dashboard', label: 'Dashboard', icon: '\u{1F4CA}', exact: true },
    { path: '/dashboard/profile', label: 'Profile', icon: '\u{1F464}', exact: false },
  ];
}
