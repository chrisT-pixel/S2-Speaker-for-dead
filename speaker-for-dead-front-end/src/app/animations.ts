import { trigger, transition, style, animate } from '@angular/animations';

export const fadeAnimation = trigger('routeAnimations', [
  transition('* <=> *', [
    style({ opacity: 0 }), // Initial state
    animate('1500ms', style({ opacity: 1 })), // Final state and animation duration
  ]),
]);