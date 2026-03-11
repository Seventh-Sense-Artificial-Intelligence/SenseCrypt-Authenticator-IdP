import { Component } from '@angular/core';

@Component({
  selector: 'app-features',
  imports: [],
  templateUrl: './features.html',
  styleUrl: './features.scss',
})
export class Features {
  features = [
    {
      icon: 'images/sic7.jpg',
      title: 'Passwordless MFA',
      desc: '0% Biometrics, 100% Privacy. Your face generates a cryptographic key on-the-fly. Nothing is stored, nothing can be stolen.',
    },
    {
      icon: 'images/sic6.jpg',
      title: 'Account Recovery',
      desc: 'Eliminate the #1 attack vector. No passwords means no phishing, no credential stuffing, no breaches.',
    },
    {
      icon: 'images/sic5.jpg',
      title: 'Step-up Auth',
      desc: 'Works with any device that has a camera. No special hardware, no dongles, no friction.',
    },
    {
      icon: 'images/sic4.jpg',
      title: 'Enterprise Ready',
      desc: 'SOC2 compliant, GDPR ready. Seamless integration with your existing identity infrastructure.',
    },
  ];
}
