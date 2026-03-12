import { Component, Input } from '@angular/core';
import { NgxTippyModule } from 'ngx-tippy-wrapper';

@Component({
  selector: 'info-tip',
  standalone: true,
  imports: [NgxTippyModule],
  template: `
    <i class="fa-solid fa-circle-info info-tip"
       [ngxTippy]="content"
       [tippyProps]="{ allowHTML: true, theme: 'info', placement: 'top', interactive: true, maxWidth: 320 }">
    </i>
  `,
})
export class InfoTip {
  @Input({ required: true }) content!: string;
}
