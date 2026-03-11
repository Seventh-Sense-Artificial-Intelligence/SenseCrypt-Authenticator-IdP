import { Component } from '@angular/core';

@Component({
  selector: 'app-how-it-works',
  imports: [],
  templateUrl: './how-it-works.html',
  styleUrl: './how-it-works.scss',
})
export class HowItWorks {
  steps = [
    {
      title: 'Scan',
      desc: 'A quick face scan captures your unique facial geometry using your device camera.',
    },
    {
      title: 'Generate',
      desc: 'Your private key is generated on-the-fly from your face \u2014 never stored, never transmitted.',
    },
    {
      title: 'Authenticate',
      desc: 'Prove your identity cryptographically without exposing any biometric data.',
    },
  ];
}
