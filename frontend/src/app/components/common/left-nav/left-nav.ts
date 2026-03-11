import { Component } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';

@Component({
  selector: 'app-left-nav',
  imports: [RouterLink, RouterLinkActive],
  templateUrl: './left-nav.html',
  styles: `:host { display: contents; }`,
})
export class LeftNav {}
