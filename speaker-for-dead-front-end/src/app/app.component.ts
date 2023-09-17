import { Component } from '@angular/core';
import { ActivatedRoute } from '@angular/router';


@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {
  title = 'speaker-for-dead-front-end';
  isHomePage!: boolean;

  constructor(private route: ActivatedRoute) {
    this.route.url.subscribe(urlSegments => {
      // Check if the current route is the home page ('')
      this.isHomePage = urlSegments.length === 0;
    });
  }
}
