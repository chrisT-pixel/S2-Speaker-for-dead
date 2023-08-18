import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http'; 

@Component({
  selector: 'app-interact',
  templateUrl: './interact.component.html',
  styleUrls: ['./interact.component.scss']
})
export class InteractComponent {

  textToSend: string | undefined;
  responseText: string | undefined;

  constructor(private http: HttpClient) { } 

  sendAndReceiveText(): void {
    const apiUrl = 'http://localhost:5000/api/data';  
    const data = { text: this.textToSend };

    this.http.post<any>(apiUrl, data).subscribe(
      (response) => {
        this.responseText = response.response_text; // Store the response text
        
      },
      (error) => {  
        console.error('Error occurred:', error);
      }
    );
    
  }
  
}
